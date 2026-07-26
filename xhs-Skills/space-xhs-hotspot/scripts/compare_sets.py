#!/usr/bin/env python3
"""
小红书笔记集合对比器。

把多次查询的原始 JSON 归一成同一张表，做横向对比：
  - 多赛道横向：同一时间窗，A 赛道 vs B 赛道 vs C 赛道
  - 单赛道纵向：同一关键词，本周 vs 上周（两次查询的结果文件）

输入 = 已经落盘的 JSON 文件，本脚本不联网、不需要任何 API Key。
支持两种输入格式，自动识别：
  1. 红狐路线：scripts/fetch_xhs_hot_articles.py 的 stdout（含 items[]）
  2. 怪壳路线：xiaohongshu-content-tools/src/xiaohongshu/search-cli.js --output json（含 results[]）

怪壳的 stdout 里会混入「查询任务重试 N/60 次」之类的日志行，本脚本会跳过
非 JSON 前缀，直接定位到第一个完整 JSON 对象。

用法：
  python3 compare_sets.py 通勤穿搭=a.json 老钱风=b.json --top 20
  python3 compare_sets.py 本周=this.json 上周=last.json --label-kind time
  python3 compare_sets.py a.json b.json --json > compare.json

设计参考：creator-buddy/skills/baokuan-article-analysis/scripts/daily_sector_trends.py
（赛道合并 / 去重 / 排序 / 标题高频词 / 形态归类的思路），字段按小红书改写。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

# ---------- 数值解析 ----------

def parse_count(value: Any) -> int:
    """'1.2万' / '5000+' / '3.4w' / 1234 -> int。无法解析返回 0。"""
    if value is None:
        return 0
    if isinstance(value, (int, float)):
        return int(value)
    text = str(value).strip().replace(",", "").replace("+", "")
    if not text:
        return 0
    mult = 1
    for unit in ("万", "w", "W"):
        if unit in text:
            text = text.replace(unit, "")
            mult = 10000
            break
    if "k" in text.lower():
        text = text.lower().replace("k", "")
        mult = 1000
    try:
        return int(float(text) * mult)
    except ValueError:
        return 0


def load_json_loose(path: Path) -> Any:
    """跳过日志前缀，取出文件里第一个完整 JSON 对象/数组。"""
    raw = path.read_text(encoding="utf-8", errors="ignore")
    decoder = json.JSONDecoder()
    for i, ch in enumerate(raw):
        if ch in "{[":
            try:
                obj, _ = decoder.raw_decode(raw[i:])
                return obj
            except ValueError:
                continue
    raise ValueError(f"{path}: 找不到可解析的 JSON")


# ---------- 归一化 ----------

def normalize(obj: Any) -> tuple[list[dict[str, Any]], str]:
    """返回 (归一后的笔记列表, 识别到的路线名)。"""
    if isinstance(obj, list):
        raw_items, route = obj, "unknown"
    elif "items" in obj:
        raw_items, route = obj.get("items") or [], "redfox"
    elif "results" in obj:
        raw_items, route = obj.get("results") or [], "guaikei"
    else:
        raise ValueError("无法识别的 JSON 结构：既没有 items[] 也没有 results[]")

    out: list[dict[str, Any]] = []
    for it in raw_items:
        if not isinstance(it, dict):
            continue
        user = it.get("user") if isinstance(it.get("user"), dict) else {}
        liked = parse_count(it.get("likedCount", it.get("liked_count")))
        collected = parse_count(it.get("collectedCount", it.get("collected_count")))
        commented = parse_count(it.get("commentsCount", it.get("comment_count")))
        shared = parse_count(it.get("sharedCount", it.get("shared_count")))
        interactive = parse_count(it.get("interactiveCount"))
        if not interactive:
            interactive = liked + collected + commented + shared
        out.append({
            "title": str(it.get("title") or it.get("desc") or "").strip(),
            "desc": str(it.get("desc") or "")[:120],
            "url": it.get("noteLink") or it.get("url") or "",
            "author": it.get("authorNickname") or user.get("nickname") or "",
            "fans": parse_count(it.get("authorFans")) if it.get("authorFans") else None,
            "publish": it.get("createTime") or it.get("publish_time") or "",
            "liked": liked,
            "collected": collected,
            "commented": commented,
            "shared": shared,
            "interactive": interactive,
            "score": it.get("totalScore"),
            "route": route,
        })
    # 去重：url 优先，其次标题
    seen: set[str] = set()
    deduped: list[dict[str, Any]] = []
    for it in sorted(out, key=lambda x: x["interactive"], reverse=True):
        key = it["url"] or it["title"]
        if not key or key in seen:
            continue
        seen.add(key)
        deduped.append(it)
    return deduped, route


# ---------- 分析 ----------

FORMAT_RULES = [
    ("清单盘点", r"\d+\s*(个|款|条|种|件|招|本|部)|合集|盘点|必看|清单"),
    ("教程步骤", r"教程|怎么|如何|步骤|保姆级|手把手|从0到1|从 0 到 1|攻略"),
    ("测评对比", r"测评|实测|对比|vs|VS|哪个好|开箱|试色"),
    ("避雷吐槽", r"避雷|别买|翻车|后悔|劝退|拔草|智商税|踩坑"),
    ("个人经历", r"我的|第\d+天|复盘|记录|亲测|自述|裸辞|上岸"),
    ("资源合集", r"网盘|模板|素材|资料|整理好了|免费"),
    ("身份背书", r"医生|护士|律师|HR|老师|设计师|\d+年经验|从业"),
]

HOOK_RULES = [
    ("数字", r"\d"),
    ("人群标签", r"打工人|学生党|新手|小白|宝妈|上班族|敏感肌|小个子|微胖|i人|e人"),
    ("反差", r"没想到|原来|居然|竟然|越.{1,4}越|才知道|不是.{1,6}而是"),
    ("痛点原话", r"[“\"].{2,20}[”\"]|救命|崩溃|破防|谁懂|绝了"),
    ("时效", r"20\d{2}|最新|今年|本季|换季|刚刚"),
    ("收藏指令", r"收藏|码住|存了|抄作业|直接抄"),
]

STOPWORDS = set("的了和与在是我你他这那一个一种我们就都很也还有把被为对到从")


def tag(text: str, rules: list[tuple[str, str]]) -> list[str]:
    return [name for name, pat in rules if re.search(pat, text)]


def distribution(items: list[dict[str, Any]], rules: list[tuple[str, str]], single: bool,
                 use_desc: bool = False) -> dict[str, int]:
    """形态判定看 标题+正文摘要（小红书标题很短，形态信号常在话题标签里）；
    钩子判定只看标题（钩子是标题的点击机制，掺进正文会大量误判）。"""
    counts: dict[str, int] = {}
    for it in items:
        text = it["title"] + (" " + it.get("desc", "") if use_desc else "")
        hits = tag(text, rules)
        if single:
            hits = hits[:1] or ["其他"]
        for h in hits:
            counts[h] = counts.get(h, 0) + 1
    return dict(sorted(counts.items(), key=lambda x: -x[1]))


def title_words(items: list[dict[str, Any]], limit: int = 12, label: str = "") -> list[tuple[str, int]]:
    """无分词依赖：对标题里的中文连续段做 2~4 字滑窗 n-gram，英文/数字整词保留。
    同一标题内同词只计一次；最后去掉被更长高频词完全包含的短词（避免
    「老钱风 / 式老钱风 / 老钱风的」这类切片噪音）。"""
    counts: dict[str, int] = {}
    for it in items:
        seen_here: set[str] = set()
        for run in re.findall(r"[A-Za-z][A-Za-z0-9+#.-]{1,}|[一-鿿]+", it["title"]):
            if run[0].isascii():
                cands = [run]
            else:
                cands = [run[i:i + n] for n in (2, 3, 4) for i in range(len(run) - n + 1)]
            for token in cands:
                if token in STOPWORDS or len(token) > 8 or all(c in STOPWORDS for c in token):
                    continue
                seen_here.add(token)
        for token in seen_here:
            counts[token] = counts.get(token, 0) + 1

    # 查询词本身必然高频，不是发现，剔除（含与查询词互为子串的切片）
    seed = label.strip()
    ranked = sorted(((k, v) for k, v in counts.items() if v > 1), key=lambda x: (-x[1], -len(x[0]), x[0]))
    kept: list[tuple[str, int]] = []
    for token, cnt in ranked:
        # 与查询词有 2 字以上重叠的都算查询词的切片（如 seed=老钱风 → 式老钱、钱风的）
        if seed and (token in seed or seed in token
                     or any(token[i:i + 2] in seed for i in range(len(token) - 1))):
            continue
        # 与已保留词互为子串且不更高频的，是同一个词的切片噪音
        if any(token != k and (token in k or k in token) and cnt <= c for k, c in kept):
            continue
        kept.append((token, cnt))
        if len(kept) >= limit:
            break
    return kept


def median(nums: list[int]) -> int:
    if not nums:
        return 0
    s = sorted(nums)
    mid = len(s) // 2
    return s[mid] if len(s) % 2 else (s[mid - 1] + s[mid]) // 2


def summarize(label: str, items: list[dict[str, Any]], route: str, top: int) -> dict[str, Any]:
    items = items[:top]
    n = len(items)
    inter = [i["interactive"] for i in items]
    liked = sum(i["liked"] for i in items)
    collected = sum(i["collected"] for i in items)
    commented = sum(i["commented"] for i in items)
    fans = [i["fans"] for i in items if i["fans"] is not None]
    return {
        "label": label,
        "route": route,
        "n": n,
        "interactive_median": median(inter),
        "interactive_max": max(inter) if inter else 0,
        "collect_like_ratio": round(collected / liked, 2) if liked else None,
        "comment_like_ratio": round(commented / liked, 2) if liked else None,
        "small_account_count": sum(1 for f in fans if f < 10000) if fans else None,
        "fans_known": bool(fans),
        "formats": distribution(items, FORMAT_RULES, single=True, use_desc=True),
        "hooks": distribution(items, HOOK_RULES, single=False),
        "words": title_words(items, label=label),
        "top_note": ({"title": items[0]["title"], "url": items[0]["url"],
                      "interactive": items[0]["interactive"]} if items else None),
    }


# ---------- 输出 ----------

def pct(part: int, whole: int) -> str:
    return f"{round(part / whole * 100)}%" if whole else "-"


def render(summaries: list[dict[str, Any]], kind: str) -> str:
    head = "时间窗" if kind == "time" else "赛道"
    lines = [f"## 集合对比（{head}）", ""]
    lines.append(f"| {head} | 样本 | 互动中位数 | 互动最高 | 藏/赞 | 评/赞 | 小号(<1w) | 主形态 | 主钩子 |")
    lines.append("|---|---:|---:|---:|---:|---:|---|---|---|")
    for s in summaries:
        fmt = next(iter(s["formats"].items()), ("-", 0))
        hook = next(iter(s["hooks"].items()), ("-", 0))
        small = "字段缺失" if not s["fans_known"] else f"{s['small_account_count']}/{s['n']}"
        lines.append(
            f"| {s['label']} | {s['n']} | {s['interactive_median']} | {s['interactive_max']} | "
            f"{s['collect_like_ratio'] if s['collect_like_ratio'] is not None else '-'} | "
            f"{s['comment_like_ratio'] if s['comment_like_ratio'] is not None else '-'} | {small} | "
            f"{fmt[0]} {pct(fmt[1], s['n'])} | {hook[0]} {pct(hook[1], s['n'])} |"
        )
    lines.append("")
    for s in summaries:
        lines.append(f"### {s['label']}（路线 {s['route']}，样本 {s['n']}）")
        lines.append("- 形态分布：" + "｜".join(f"{k} {v}" for k, v in s["formats"].items()))
        lines.append("- 钩子分布：" + "｜".join(f"{k} {v}" for k, v in s["hooks"].items()))
        lines.append("- 标题高频词（已剔除查询词，n-gram 近似，个别词可能是切片）："
                     + ("、".join(f"{k}({v})" for k, v in s["words"]) or "无重复词"))
        if s["top_note"]:
            lines.append(f"- 最高互动：《{s['top_note']['title']}》 {s['top_note']['interactive']} {s['top_note']['url']}")
        if s["n"] < 8:
            lines.append("- ⚠️ 样本 < 8 条，占比不可用作趋势判断，仅供定性参考。")
        lines.append("")
    # 交集/差集词
    if len(summaries) > 1:
        sets = [set(w for w, _ in s["words"]) for s in summaries]
        common = set.intersection(*sets)
        lines.append("### 词层对比")
        lines.append("- 共有高频词：" + ("、".join(sorted(common)) or "无"))
        for s, ws in zip(summaries, sets):
            only = ws - set.union(*[o for o2, o in zip(summaries, sets) if o2 is not s]) if len(sets) > 1 else ws
            lines.append(f"- 「{s['label']}」独有：" + ("、".join(sorted(only)) or "无"))
        lines.append("")
    lines.append("> 口径提醒：互动数为各数据源入库/抓取时刻的快照；粉丝数仅红狐路线提供，怪壳路线该字段为空时显示「字段缺失」，不要估算。")
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser(description="小红书笔记集合对比（离线，读已落盘 JSON）")
    ap.add_argument("inputs", nargs="+", help="标签=文件路径，或直接给文件路径（用文件名当标签）")
    ap.add_argument("--top", type=int, default=20, help="每个集合取前 N 条参与统计，默认 20")
    ap.add_argument("--label-kind", choices=["sector", "time"], default="sector",
                    help="sector=多赛道横向对比（默认），time=同赛道跨时间对比")
    ap.add_argument("--json", action="store_true", help="输出 JSON 而非 Markdown")
    args = ap.parse_args()

    summaries = []
    for spec in args.inputs:
        label, _, path_str = spec.partition("=")
        if not path_str:
            path_str, label = label, Path(label).stem
        path = Path(path_str).expanduser()
        if not path.exists():
            print(f"跳过：{path} 不存在", file=sys.stderr)
            continue
        try:
            items, route = normalize(load_json_loose(path))
        except Exception as exc:
            print(f"跳过 {path}：{exc}", file=sys.stderr)
            continue
        summaries.append(summarize(label, items, route, args.top))

    if not summaries:
        print("没有可用输入。", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(summaries, ensure_ascii=False, indent=2))
    else:
        print(render(summaries, args.label_kind))


if __name__ == "__main__":
    main()
