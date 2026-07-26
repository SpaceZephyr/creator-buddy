#!/usr/bin/env python3
"""小红书笔记后台导出数据处理辅助脚本。

设计原则（对齐 data-analysis skill）：
  - probe 只读元数据 + 5 行样本，绝不把全表打进上下文
  - metrics / group 只输出聚合结果，不输出原始行（异常值除外，且限条数）
  - 列名别名映射 + 单位自适应，识别不了的列一律列出来让人确认，不猜

用法：
  python3 xhs_notes.py probe   notes.xlsx
  python3 xhs_notes.py metrics notes.xlsx [--out notes_metrics.csv]
  python3 xhs_notes.py group   notes.xlsx --by 选题类型 [--metric ctr]
"""

import argparse
import os
import sys

try:
    import pandas as pd
except ImportError:
    sys.exit("需要 pandas：pip install pandas openpyxl")

# ---------- 列名别名 ----------
ALIASES = {
    "title":      ["标题", "笔记标题", "笔记名称", "note_title", "title"],
    "publish_at": ["发布时间", "发布日期", "创建时间", "时间", "publish_time", "date"],
    "impression": ["曝光量", "曝光", "展现量", "展现", "浏览量", "推荐量", "impression", "views"],
    "read":       ["阅读量", "阅读", "观看量", "观看", "点击量", "笔记浏览量", "read", "clicks"],
    "like":       ["点赞量", "点赞数", "点赞", "赞", "like", "likes"],
    "collect":    ["收藏量", "收藏数", "收藏", "藏", "collect", "favorites"],
    "comment":    ["评论量", "评论数", "评论", "comment", "comments"],
    "share":      ["分享量", "分享数", "分享", "转发", "share", "shares"],
    "follow":     ["涨粉数", "新增关注", "涨粉", "新增粉丝", "关注数", "follow", "new_followers"],
    "finish":     ["完播率", "播放完成率", "完播", "finish_rate"],
    "duration":   ["平均阅读时长", "人均阅读时长", "平均播放时长", "阅读时长", "avg_duration"],
    "search_pct": ["搜索流量占比", "搜索占比", "搜索来源占比", "search_ratio"],
    "rec_pct":    ["推荐流量占比", "推荐占比", "发现页占比", "recommend_ratio"],
    "type":       ["笔记类型", "类型", "形式", "note_type"],
}

RATE_COLS = {"finish", "search_pct", "rec_pct"}


def read_any(path, nrows=None):
    ext = os.path.splitext(path)[1].lower()
    if ext in (".xlsx", ".xls", ".xlsm"):
        return pd.read_excel(path, nrows=nrows)
    for enc in ("utf-8-sig", "utf-8", "gbk", "latin1"):
        try:
            return pd.read_csv(path, nrows=nrows, encoding=enc)
        except UnicodeDecodeError:
            continue
        except Exception:
            break
    return pd.read_csv(path, nrows=nrows, encoding="utf-8", sep=None, engine="python")


def norm(s):
    return str(s).strip().lower().replace(" ", "").replace("（", "(").replace("）", ")")


def map_columns(cols):
    """返回 (mapping: canonical->原列名, unknown: 未识别的原列名列表)"""
    mapping, used = {}, set()
    for canon, names in ALIASES.items():
        for c in cols:
            if c in used:
                continue
            nc = norm(c)
            if any(norm(n) == nc for n in names):
                mapping[canon] = c
                used.add(c)
                break
        if canon in mapping:
            continue
        for c in cols:                       # 退化为包含匹配
            if c in used:
                continue
            nc = norm(c)
            if any(norm(n) in nc for n in names):
                mapping[canon] = c
                used.add(c)
                break
    return mapping, [c for c in cols if c not in used]


def to_num(s):
    """把 '1,234' / '5.2%' / '1.2万' 转成数值。"""
    if s.dtype.kind in "if":
        return s
    t = s.astype(str).str.strip()
    wan = t.str.contains("万|w$", case=False, regex=True, na=False)
    pct = t.str.contains("%", na=False)
    t = t.str.replace(r"[,，%万wW\s]", "", regex=True)
    v = pd.to_numeric(t, errors="coerce")
    v = v.mask(wan, v * 10000)
    return v.mask(pct, v / 100)


def normalize_rate(s):
    """比率列单位自适应：中位数 > 1 视为百分数形式，除以 100 统一成小数。"""
    v = to_num(s)
    m = v.dropna().median()
    return v / 100 if pd.notna(m) and m > 1 else v


def load(path):
    df = read_any(path)
    mapping, unknown = map_columns(list(df.columns))
    out = pd.DataFrame(index=df.index)
    for canon, col in mapping.items():
        if canon in ("title", "type"):
            out[canon] = df[col].astype(str)
        elif canon == "publish_at":
            out[canon] = pd.to_datetime(df[col], errors="coerce")
        elif canon in RATE_COLS:
            out[canon] = normalize_rate(df[col])
        else:
            out[canon] = to_num(df[col])
    for c in unknown:                        # 未识别列原样保留，可用于分组
        out[c] = df[c]
    return df, out, mapping, unknown


def add_rates(d):
    def div(a, b):
        if a not in d or b not in d:
            return None
        return (d[a] / d[b].replace(0, pd.NA)).astype(float)

    for name, (a, b) in {
        "ctr":         ("read", "impression"),
        "like_rate":   ("like", "read"),
        "collect_rate":("collect", "read"),
        "comment_rate":("comment", "read"),
        "share_rate":  ("share", "read"),
        "follow_rate": ("follow", "read"),
    }.items():
        r = div(a, b)
        if r is not None:
            d[name] = r
    parts = [c for c in ("like", "collect", "comment", "share") if c in d]
    if parts and "read" in d:
        d["engage_rate"] = d[parts].sum(axis=1) / d["read"].replace(0, pd.NA)
    if "collect" in d and "like" in d:
        d["collect_like_ratio"] = d["collect"] / d["like"].replace(0, pd.NA)
    return d


def quality_report(d, cols=None):
    lines = []
    n = len(d)
    lines.append(f"总行数: {n}")
    for c in (cols if cols is not None else d.columns):
        miss = d[c].isna().sum()
        if miss:
            lines.append(f"  缺失: {c} {miss}/{n} ({miss/n:.0%})")
    if "title" in d and d["title"].duplicated().any():
        lines.append(f"  重复标题: {int(d['title'].duplicated().sum())} 条（可能重复导出）")
    if {"read", "impression"}.issubset(d.columns):
        bad = int((d["read"] > d["impression"]).sum())
        if bad:
            lines.append(f"  阅读>曝光: {bad} 条（口径差异，常见，不必当错误但比率会失真）")
    if "impression" in d:
        low = int((d["impression"] < 1000).sum())
        if low:
            lines.append(f"  曝光<1000: {low} 条 —— 这些笔记的比率是噪声，慎用")
    if "publish_at" in d and d["publish_at"].notna().any():
        lo, hi = d["publish_at"].min(), d["publish_at"].max()
        lines.append(f"  时间范围: {lo:%Y-%m-%d} ~ {hi:%Y-%m-%d}")
        recent = int((pd.Timestamp.now() - d["publish_at"] < pd.Timedelta(days=7)).sum())
        if recent:
            lines.append(f"  发布<7天: {recent} 条 —— 数据未跑满，不要与老笔记直接比较")
    if n < 5:
        lines.append("  ⚠ 样本 <5 篇：只能逐篇诊断，不得给出任何规律性结论")
    elif n < 15:
        lines.append("  ⚠ 样本 5-15 篇：只能找极端值、提假设，不能断言因果")
    return "\n".join(lines)


def describe(s):
    s = s.dropna()
    if s.empty:
        return None
    return dict(n=len(s), p25=s.quantile(.25), median=s.median(),
                p75=s.quantile(.75), mean=s.mean(), max=s.max())


def fmt(v, pct=False):
    if v is None or pd.isna(v):
        return "-"
    return f"{v*100:.2f}%" if pct else (f"{v:,.0f}" if abs(v) >= 100 else f"{v:,.2f}")


PCT = {"ctr", "like_rate", "collect_rate", "comment_rate", "share_rate",
       "follow_rate", "engage_rate", "finish", "search_pct", "rec_pct"}


def cmd_probe(a):
    df = read_any(a.file, nrows=5)
    mapping, unknown = map_columns(list(df.columns))
    print("=== 前 5 行 ===")
    print(df.head().to_string(index=False))
    print("\n=== 列与类型 ===")
    for c in df.columns:
        print(f"  {c}  ({df[c].dtype})")
    print("\n=== 识别到的指标列 ===")
    for k, v in mapping.items():
        print(f"  {k:<14} <- {v}")
    if unknown:
        print("\n=== 未识别的列（请与用户确认含义，不要自行猜测）===")
        for c in unknown:
            print(f"  {c}")
    missing = [k for k in ("impression", "read", "like", "collect") if k not in mapping]
    if missing:
        print(f"\n⚠ 缺少核心列: {', '.join(missing)} —— 相应漏斗层无法诊断")


def cmd_metrics(a):
    _, d, mapping, unknown = load(a.file)
    raw_cols = list(d.columns)
    d = add_rates(d)
    print("=== 数据质量体检 ===")
    print(quality_report(d, raw_cols))
    print("\n=== 指标分布（用中位数，不用平均值）===")
    print(f"{'指标':<18}{'n':>4}{'P25':>10}{'中位数':>12}{'P75':>10}{'均值':>10}{'最大':>12}")
    for c in ["impression", "read", "ctr", "engage_rate", "like_rate", "collect_rate",
              "comment_rate", "share_rate", "follow", "follow_rate", "finish",
              "collect_like_ratio", "search_pct", "rec_pct"]:
        if c not in d:
            continue
        st = describe(d[c])
        if not st:
            continue
        p = c in PCT
        print(f"{c:<18}{st['n']:>4}{fmt(st['p25'],p):>10}{fmt(st['median'],p):>12}"
              f"{fmt(st['p75'],p):>10}{fmt(st['mean'],p):>10}{fmt(st['max'],p):>12}")
    if "impression" in d:
        st = describe(d["impression"])
        if st and st["median"] and st["mean"] / st["median"] > 2:
            print("\n⚠ 曝光均值 / 中位数 > 2：流量高度依赖少数爆款，一切平均值都不要引用")
    if a.out:
        d.to_csv(a.out, index=False, encoding="utf-8-sig")
        print(f"\n已写出明细: {a.out}")


def cmd_group(a):
    _, d, mapping, _ = load(a.file)
    d = add_rates(d)
    by = a.by
    if by not in d.columns:                  # 允许用原始列名分组（已被映射成规范名）
        rev = {v: k for k, v in mapping.items()}
        by = rev.get(by, by)
    if by not in d.columns:
        sys.exit(f"没有列 '{a.by}'。可用列: {', '.join(map(str, d.columns))}")
    metrics = [m for m in (a.metric.split(",") if a.metric else
                           ["impression", "ctr", "engage_rate", "collect_rate", "follow_rate"])
               if m in d.columns]
    g = d.groupby(d[by].astype(str), dropna=True)
    print(f"=== 按「{a.by}」分组（组内中位数）===")
    head = f"{'分组':<16}{'n':>4}" + "".join(f"{m:>16}" for m in metrics)
    print(head)
    small = []
    for k, sub in g:
        n = len(sub)
        row = f"{k[:15]:<16}{n:>4}"
        for m in metrics:
            row += f"{fmt(sub[m].median(), m in PCT):>16}"
        print(row)
        if n < 3:
            small.append(f"{k}(n={n})")
    if small:
        print(f"\n⚠ 样本不足 3 篇的组，仅列出、不得参与比较: {', '.join(small)}")
    print("\n⚠ 分组对比只说明相关，不说明因果；若某维度与其他维度高度重合（如某类选题都用同款封面），"
          "必须在结论中点明混淆因素。")

    sort_m = metrics[0]
    if sort_m in d and "title" in d:
        s = d.dropna(subset=[sort_m]).sort_values(sort_m, ascending=False)
        k = min(3, len(s) // 3) or 1
        print(f"\n=== 异常值（按 {sort_m}）===")
        print("Top:")
        for _, r in s.head(k).iterrows():
            print(f"  {fmt(r[sort_m], sort_m in PCT):>10}  {str(r['title'])[:40]}")
        print("Bottom:")
        for _, r in s.tail(k).iterrows():
            print(f"  {fmt(r[sort_m], sort_m in PCT):>10}  {str(r['title'])[:40]}")
        print("  → 逐条问：它和其他篇唯一的不同是什么？是否有不可复制的外因（热点/平台推流）？")


def main():
    p = argparse.ArgumentParser(description="小红书笔记数据处理")
    sub = p.add_subparsers(dest="cmd", required=True)
    for name, fn in (("probe", cmd_probe), ("metrics", cmd_metrics), ("group", cmd_group)):
        sp = sub.add_parser(name)
        sp.add_argument("file")
        if name == "metrics":
            sp.add_argument("--out")
        if name == "group":
            sp.add_argument("--by", required=True)
            sp.add_argument("--metric")
        sp.set_defaults(func=fn)
    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
