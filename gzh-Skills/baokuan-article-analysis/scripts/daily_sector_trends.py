#!/usr/bin/env python3
"""
Fetch WeChat Official Account hot article data by sector keywords and
generate daily JSON / Markdown / HTML reports with writing analysis.
"""

from __future__ import annotations

import argparse
import datetime as dt
import gzip
import html
import json
import math
import re
import socket
import ssl
from pathlib import Path
from typing import Any
from urllib.parse import quote, urlparse


API_HOST_PATH = "onetotenvip.com/skill/cozeSkill/getWxCozeSkillData"
SOURCE = "公众号爆款文章洞察-SkillHub"

DEFAULT_SECTORS = {
    "AI Agent": ["AI Agent", "Agent框架", "智能体"],
    "Skill": ["skill", "Skills", "AI Skill"],
    "Claude Code / Codex": ["Claude Code", "Codex", "AI编程"],
    "AI知识管理": ["AI知识管理", "知识库", "个人知识管理"],
}


def parse_count(value: Any) -> int:
    if value is None:
        return 0
    if isinstance(value, int):
        return value
    text = str(value).replace("+", "").replace(",", "").strip()
    if not text:
        return 0
    if "w" in text.lower():
        try:
            return int(float(text.lower().replace("w", "")) * 10000)
        except Exception:
            return 0
    try:
        return int(float(text))
    except Exception:
        return 0


def display_count(value: Any) -> str:
    if value is None or value == "":
        return "0"
    return str(value)


def sanitize_http_url(url: Any) -> str:
    if url is None:
        return ""
    url = str(url).strip()
    if not url or len(url) > 4096:
        return ""
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return ""
    return url


def decode_chunked(data: bytes) -> bytes:
    chunks: list[bytes] = []
    idx = 0
    while idx < len(data):
        line_end = data.find(b"\r\n", idx)
        if line_end == -1:
            break
        try:
            size = int(data[idx:line_end], 16)
        except Exception:
            break
        if size == 0:
            break
        start = line_end + 2
        end = start + size
        if end > len(data):
            break
        chunks.append(data[start:end])
        idx = end + 2
    return b"".join(chunks)


def fetch_no_sni(params: dict[str, str], timeout: int = 60) -> dict[str, Any]:
    host, path = API_HOST_PATH.split("/", 1)
    query = "&".join(f"{quote(k)}={quote(v)}" for k, v in params.items())
    request_path = f"/{path}?{query}"
    headers = {
        "Host": host,
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "close",
    }

    sock = socket.create_connection((host, 443), timeout=timeout)
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    ssl_sock = context.wrap_socket(sock, server_hostname=None)
    try:
        lines = [f"GET {request_path} HTTP/1.1"]
        lines.extend(f"{k}: {v}" for k, v in headers.items())
        lines.extend(["", ""])
        ssl_sock.send("\r\n".join(lines).encode("utf-8"))

        response = b""
        while True:
            chunk = ssl_sock.recv(8192)
            if not chunk:
                break
            response += chunk
    finally:
        ssl_sock.close()

    first_line = response.split(b"\r\n", 1)[0].decode("utf-8", errors="ignore")
    if " " not in first_line:
        raise RuntimeError("Invalid HTTP response")
    status = int(first_line.split()[1])
    if status >= 400:
        raise RuntimeError(f"HTTP status {status}")

    header_end = response.find(b"\r\n\r\n")
    header_bytes = response[:header_end] if header_end != -1 else b""
    body = response[header_end + 4 :] if header_end != -1 else b""
    header_text = header_bytes.decode("utf-8", errors="ignore").lower()
    if "transfer-encoding: chunked" in header_text:
        body = decode_chunked(body)
    if "content-encoding: gzip" in header_text:
        try:
            body = gzip.decompress(body)
        except Exception:
            pass
    return json.loads(body.decode("utf-8", errors="ignore"))


def fetch_keyword(keyword: str, start_date: str | None, timeout: int) -> list[dict[str, Any]]:
    params = {"keyword": keyword, "source": SOURCE}
    if start_date:
        params["startDate"] = start_date
    data = fetch_no_sni(params, timeout=timeout)
    result_data = data.get("data", {})
    categories = [
        ("lowPowderExplosiveArticle", "低粉高阅读"),
        ("tenWReadingRank", "阅读靠前"),
        ("originalRank", "原创靠前"),
        ("oneWReadingRank", "数据增长中"),
    ]
    items: list[dict[str, Any]] = []
    for key, category in categories:
        for item in result_data.get(key, []) or []:
            item = dict(item)
            item["category"] = category
            item["matchedKeyword"] = keyword
            items.append(normalize_item(item))
    return items


def normalize_item(item: dict[str, Any]) -> dict[str, Any]:
    title = str(item.get("title") or "").strip()
    summary = str(item.get("summary") or "").strip()
    if not title:
        title = summary[:42] + ("..." if len(summary) > 42 else "")
    url = sanitize_http_url(item.get("oriUrl") or item.get("noteLink") or "")
    photo_id = str(item.get("photoId") or "").strip()
    if not url and photo_id:
        url = f"https://mp.weixin.qq.com/s/{photo_id}"
    out = {
        "category": item.get("category", ""),
        "matchedKeyword": item.get("matchedKeyword", ""),
        "photoId": photo_id,
        "title": title or "无标题",
        "summary": summary,
        "accountId": item.get("accountId", ""),
        "accountName": item.get("accountName", ""),
        "fans": item.get("fans", ""),
        "publicTime": item.get("publicTime", ""),
        "noteLink": url,
        "interactiveCount": parse_count(item.get("interactiveCount", 0)),
        "likeCount": parse_count(item.get("likeCount", 0)),
        "commentCount": parse_count(item.get("useCommentCount", item.get("commentCount", 0))),
        "shareCount": parse_count(item.get("shareCount", 0)),
        "clicksCount": item.get("clicksCount", "0"),
        "watchCount": item.get("watchCount", "0"),
    }
    out["dataScore"] = score_item(out)
    return out


def score_item(item: dict[str, Any]) -> float:
    clicks = parse_count(item.get("clicksCount"))
    like = parse_count(item.get("likeCount"))
    comment = parse_count(item.get("commentCount"))
    share = parse_count(item.get("shareCount"))
    interactive = parse_count(item.get("interactiveCount"))
    score = (
        math.log10(clicks + 1) * 18
        + math.log10(share + 1) * 22
        + math.log10(like + 1) * 16
        + math.log10(comment + 1) * 14
        + math.log10(interactive + 1) * 10
    )
    return round(min(100, score), 2)


def dedupe_and_rank(items: list[dict[str, Any]], max_items: int, keywords: list[str] | None = None) -> list[dict[str, Any]]:
    if keywords:
        relevant = [item for item in items if is_relevant_to_keywords(item, keywords)]
        if relevant:
            items = relevant
    seen: set[str] = set()
    deduped: list[dict[str, Any]] = []
    for item in sorted(items, key=lambda x: x.get("dataScore", 0), reverse=True):
        key = item.get("photoId") or item.get("noteLink") or item.get("title")
        if key in seen:
            continue
        seen.add(str(key))
        deduped.append(item)
    return deduped[:max_items]


def is_relevant_to_keywords(item: dict[str, Any], keywords: list[str]) -> bool:
    haystack = f"{item.get('title', '')} {item.get('summary', '')}".lower()
    terms: list[str] = []
    broad_terms = {"ai", "人工智能", "科技", "内容", "写作"}
    for keyword in keywords:
        raw = str(keyword).strip()
        if not raw:
            continue
        lowered = raw.lower()
        if lowered not in broad_terms and len(raw) >= 2:
            terms.append(lowered)
        for token in re.findall(r"[A-Za-z][A-Za-z0-9.+#-]{1,}|[\u4e00-\u9fff]{2,}", raw):
            token_lower = token.lower()
            if token_lower not in broad_terms and len(token) >= 2:
                terms.append(token_lower)
    terms = sorted(set(terms), key=len, reverse=True)
    return any(term in haystack for term in terms)


def parse_sector_args(raw: list[str] | None) -> dict[str, list[str]]:
    if not raw:
        return DEFAULT_SECTORS
    sectors: dict[str, list[str]] = {}
    for spec in raw:
        if "=" not in spec:
            raise ValueError(f"Invalid sector spec: {spec}. Use '赛道=关键词1,关键词2'.")
        name, keywords = spec.split("=", 1)
        name = name.strip()
        values = [x.strip() for x in keywords.split(",") if x.strip()]
        if not name or not values:
            raise ValueError(f"Invalid sector spec: {spec}")
        sectors[name] = values
    return sectors


def load_sector_config(path: str | None) -> dict[str, list[str]] | None:
    if not path:
        return None
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(data, dict):
        return {str(k): [str(x) for x in v] for k, v in data.items()}
    raise ValueError("Sector config must be a JSON object: {\"赛道\": [\"关键词\"]}")


def build_markdown(report: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append(f"# 爆款文章分析 {report['reportDate']}")
    lines.append("")
    lines.append(f"> 数据窗口：{report['startDate']} 至 {report['reportDate']}")
    lines.append("> 数据来源：公众号爆款文章洞察接口。字段中的阅读量、点赞、分享、评论来自该接口快照，可能与公众号后台实时数据存在延迟。")
    lines.append("")
    for sector in report["sectors"]:
        lines.append(f"## {sector['name']}")
        lines.append("")
        lines.append(f"- 查询关键词：{', '.join(sector['keywords'])}")
        lines.append(f"- 命中文章：{len(sector['items'])} 篇")
        if sector["items"]:
            top = sector["items"][0]
            lines.append(f"- 最高阅读：{top['clicksCount']}，《{top['title']}》")
        lines.append("")
        lines.append("| # | 标题 | 公众号 | 粉丝 | 发布时间 | 阅读 | 点赞 | 分享 | 评论 | 类别 | 爆款原因初判 | 链接 |")
        lines.append("|---:|---|---|---|---|---:|---:|---:|---:|---|---|---|")
        for idx, item in enumerate(sector["items"], 1):
            title = md_escape(item["title"])
            account = md_escape(item.get("accountName") or item.get("accountId") or "")
            link = item.get("noteLink") or ""
            lines.append(
                f"| {idx} | {title} | {account} | {md_escape(str(item.get('fans', '')))} | "
                f"{item.get('publicTime', '')} | {display_count(item.get('clicksCount'))} | "
                f"{item.get('likeCount', 0)} | {item.get('shareCount', 0)} | {item.get('commentCount', 0)} | "
                f"{md_escape(item.get('category', ''))} | {md_escape(infer_hot_reason(item))} | "
                f"[原文]({link}) |"
            )
        lines.append("")
        lines.extend(build_sector_insights(sector))
        lines.append("")
        lines.extend(build_writing_style_analysis(sector))
        lines.append("")
        lines.extend(build_hot_reason_analysis(sector))
        lines.append("")
        lines.extend(build_writing_reference(sector))
        lines.append("")
    lines.append("## 使用建议")
    lines.append("")
    lines.append("- 优先看“分享/阅读”比值高的文章：更可能代表可传播标题或选题角度。")
    lines.append("- 低粉高阅读文章适合拆标题和结构；阅读靠前文章适合看大号热点；数据增长中文章适合看正在发酵的方向。")
    lines.append("- 若某赛道命中少，补充更宽泛或更贴近平台热词的关键词。")
    lines.append("")
    return "\n".join(lines)


def md_escape(text: str) -> str:
    return str(text).replace("|", "\\|").replace("\n", " ").strip()


def build_sector_insights(sector: dict[str, Any]) -> list[str]:
    items = sector["items"]
    lines = ["### 快速分析", ""]
    if not items:
        lines.append("- 暂无命中数据。建议扩大关键词或延长数据窗口。")
        return lines
    accounts: dict[str, int] = {}
    categories: dict[str, int] = {}
    for item in items:
        accounts[item.get("accountName") or item.get("accountId") or "未知"] = accounts.get(item.get("accountName") or item.get("accountId") or "未知", 0) + 1
        categories[item.get("category") or "未知"] = categories.get(item.get("category") or "未知", 0) + 1
    top_accounts = sorted(accounts.items(), key=lambda x: x[1], reverse=True)[:3]
    top_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)
    avg_share = round(sum(parse_count(x.get("shareCount")) for x in items) / len(items), 1)
    title_words = extract_title_patterns([x.get("title", "") for x in items])
    lines.append(f"- 高频账号：{', '.join(f'{k}({v})' for k, v in top_accounts)}")
    lines.append(f"- 榜单分布：{', '.join(f'{k}({v})' for k, v in top_categories)}")
    lines.append(f"- 平均分享数：{avg_share}")
    if title_words:
        lines.append(f"- 标题高频词：{', '.join(title_words[:8])}")
    lines.append("- 选题建议：优先拆解前 3 篇的标题结构、开头冲突、案例密度和行动号召。")
    return lines


def build_writing_style_analysis(sector: dict[str, Any]) -> list[str]:
    items = sector["items"]
    lines = ["### 写作风格分析", ""]
    if not items:
        lines.append("- 暂无可分析文章。")
        return lines
    style_counts: dict[str, int] = {}
    examples: dict[str, list[str]] = {}
    for item in items:
        style = infer_style(item)
        style_counts[style] = style_counts.get(style, 0) + 1
        examples.setdefault(style, []).append(item["title"])
    lines.append("| 风格类型 | 数量 | 典型文章 | 适合参考 |")
    lines.append("|---|---:|---|---|")
    for style, count in sorted(style_counts.items(), key=lambda x: (-x[1], x[0])):
        sample = "；".join(examples[style][:2])
        lines.append(f"| {style} | {count} | {md_escape(sample)} | {style_reference(style)} |")
    lines.append("")
    lines.append("- 整体判断：爆款更偏“明确结论 + 具体场景 + 可转述隐喻”，纯概念科普占比低。")
    return lines


def build_hot_reason_analysis(sector: dict[str, Any]) -> list[str]:
    items = sector["items"]
    lines = ["### 爆款原因分析", ""]
    if not items:
        lines.append("- 暂无可分析文章。")
        return lines
    top_reads = max(items, key=lambda x: parse_count(x.get("clicksCount")))
    top_shares = max(items, key=lambda x: parse_count(x.get("shareCount")))
    top_comments = max(items, key=lambda x: parse_count(x.get("commentCount")))
    lines.append(f"- 阅读最高：`{display_count(top_reads.get('clicksCount'))}`，《{top_reads['title']}》。原因通常是大热点、大厂动作、强行业判断或高公众相关性。")
    lines.append(f"- 分享最高：`{top_shares.get('shareCount', 0)}`，《{top_shares['title']}》。原因通常是标题可转述、工具可直接试、结论有传播价值。")
    lines.append(f"- 评论最高：`{top_comments.get('commentCount', 0)}`，《{top_comments['title']}》。原因通常是立场鲜明、实测细节多，或容易引发补充/争议。")
    lines.append("")
    lines.append("| 爆款机制 | 表现 | 写作启发 |")
    lines.append("|---|---|---|")
    lines.append("| 新鲜感 | 新模型、新项目、新平台动作 | 标题直接告诉读者“新在哪里” |")
    lines.append("| 结果感 | 排名、阅读、成本、效率、漏洞数量等可量化结果 | 开头 3 段内给数字或明确结论 |")
    lines.append("| 场景感 | 编程、安全、企业落地、内容生产、支付等具体场景 | 少讲概念，多讲任务和收益 |")
    lines.append("| 隐喻感 | 军队、江湖、钱包、连续体、神器等强画面词 | 给读者一句能复述给别人的话 |")
    lines.append("| 立场感 | 旧指标失效、新范式登场、国产路线等判断 | 不只搬运新闻，要给判断框架 |")
    return lines


def build_writing_reference(sector: dict[str, Any]) -> list[str]:
    items = sector["items"]
    lines = ["### 写作参考", ""]
    if not items:
        lines.append("- 暂无可参考文章。")
        return lines
    title_words = extract_title_patterns([x.get("title", "") for x in items])
    sector_name = sector.get("name", "该赛道")
    lines.append("#### 选题公式")
    lines.append("")
    lines.append("| 公式 | 可套用标题 |")
    lines.append("|---|---|")
    lines.append(f"| 新工具 + 强结论 | `{sector_name} 新工具实测：真正厉害的不是会聊天，而是能交付任务` |")
    lines.append(f"| 旧指标失效 + 新指标登场 | `别再只看参数/Token 了，{sector_name} 时代要看交付结果` |")
    lines.append(f"| 开源项目 + 个人效率跃迁 | `推荐一个刚开源的 {sector_name} 工具，一个人也能跑多条工作流` |")
    lines.append(f"| 大厂动作 + 行业拐点 | `大厂开始押注 {sector_name}，说明落地方式变了` |")
    lines.append(f"| 技术竞赛 + 路线选择 | `{sector_name} 进入体系战，拼的不只是模型大小` |")
    lines.append("")
    lines.append("#### 文章结构模板")
    lines.append("")
    lines.append("1. 开头给结论：发生了什么，为什么重要。")
    lines.append("2. 给一个具体场景：它帮谁解决了什么任务。")
    lines.append("3. 拆 3 个关键能力：每个能力配场景、数据或截图。")
    lines.append("4. 加数据锚点：排名、成本、效率、阅读、分享、案例数量。")
    lines.append("5. 给作者判断：旧模式哪里失效，新模式是什么。")
    lines.append("6. 给行动建议：适合谁用、不适合谁、下一步怎么试。")
    if title_words:
        lines.append("")
        lines.append(f"#### 标题词库：{', '.join(title_words[:12])}")
    return lines


def infer_style(item: dict[str, Any]) -> str:
    text = f"{item.get('title', '')} {item.get('summary', '')}"
    if re.search(r"实测|测评|对比|排名|世界第|能力", text):
        return "工具实测型"
    if re.search(r"开源|神器|推荐|GitHub|框架|项目", text, re.I):
        return "工具推荐型"
    if re.search(r"时代|结束|开始|范式|趋势|江湖|上半年|下半场", text):
        return "趋势判断型"
    if re.search(r"安全|竞赛|底牌|漏洞|攻防|战场|军备", text):
        return "战略叙事型"
    if re.search(r"官宣|发布|高通|支付宝|阿里|腾讯|百度|字节|大厂|企业", text):
        return "大厂生态型"
    if re.search(r"教程|保姆|从0到1|速通|指南", text):
        return "教程攻略型"
    return "资讯解读型"


def style_reference(style: str) -> str:
    mapping = {
        "工具实测型": "用榜单/数据建立可信度，再用个人场景证明价值。",
        "工具推荐型": "用一句强隐喻建立画面，再拆功能和适用人群。",
        "趋势判断型": "提出旧指标失效和新指标登场，给判断框架。",
        "战略叙事型": "把技术问题放进竞争格局，适合产业和安全议题。",
        "大厂生态型": "借大厂动作切入，解释商业化和落地路径。",
        "教程攻略型": "强调步骤、门槛、避坑和可复制清单。",
        "资讯解读型": "补足背景、影响和下一步观察点，避免只转述新闻。",
    }
    return mapping.get(style, "提炼清晰结论，补具体场景和数据。")


def infer_hot_reason(item: dict[str, Any]) -> str:
    title = item.get("title", "")
    summary = item.get("summary", "")
    text = f"{title} {summary}"
    reasons: list[str] = []
    if parse_count(item.get("clicksCount")) >= 100000:
        reasons.append("高阅读")
    if parse_count(item.get("shareCount")) >= 1000:
        reasons.append("高分享")
    if re.search(r"开源|神器|推荐|GitHub", text, re.I):
        reasons.append("工具可试")
    if re.search(r"世界第|排名|实测|对比|数据|Token|成本", text):
        reasons.append("数据结论")
    if re.search(r"官宣|发布|大厂|高通|支付宝|阿里|腾讯|百度|字节", text):
        reasons.append("大厂热点")
    if re.search(r"竞赛|底牌|江湖|军队|时代|结束|来了", text):
        reasons.append("强叙事")
    if not reasons:
        reasons.append("赛道热点")
    return " + ".join(reasons[:3])


def extract_title_patterns(titles: list[str]) -> list[str]:
    stop = {"的", "了", "和", "与", "在", "是", "一个", "一种", "我们", "这个", "那个"}
    counts: dict[str, int] = {}
    for title in titles:
        for token in re.findall(r"[A-Za-z][A-Za-z0-9.+#-]{1,}|[\u4e00-\u9fff]{2,}", title):
            if token in stop or len(token) > 18:
                continue
            counts[token] = counts.get(token, 0) + 1
    return [k for k, _ in sorted(counts.items(), key=lambda x: (-x[1], x[0]))]


def esc(value: Any) -> str:
    return html.escape(str(value or ""), quote=True)


def pct(value: float) -> str:
    return f"{max(0, min(100, value)):.0f}%"


def top_metric_items(items: list[dict[str, Any]]) -> tuple[dict[str, Any] | None, dict[str, Any] | None, dict[str, Any] | None]:
    if not items:
        return None, None, None
    return (
        max(items, key=lambda x: parse_count(x.get("clicksCount"))),
        max(items, key=lambda x: parse_count(x.get("shareCount"))),
        max(items, key=lambda x: parse_count(x.get("commentCount"))),
    )


def category_counts(items: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in items:
        category = item.get("category") or "未知"
        counts[category] = counts.get(category, 0) + 1
    return counts


def style_counts(items: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in items:
        style = infer_style(item)
        counts[style] = counts.get(style, 0) + 1
    return counts


def build_bar_rows(counts: dict[str, int], total: int) -> str:
    if not counts:
        return '<p class="muted">暂无数据</p>'
    rows: list[str] = []
    for name, count in sorted(counts.items(), key=lambda x: (-x[1], x[0])):
        ratio = count / max(1, total) * 100
        rows.append(
            f"""<div class="bar-row">
  <div class="bar-label"><span>{esc(name)}</span><b>{count}</b></div>
  <div class="bar-track"><div class="bar-fill" style="width:{pct(ratio)}"></div></div>
</div>"""
        )
    return "\n".join(rows)


def build_article_cards(items: list[dict[str, Any]]) -> str:
    if not items:
        return '<div class="empty">暂无命中文章。建议扩大关键词或延长数据窗口。</div>'
    max_reads = max(parse_count(item.get("clicksCount")) for item in items) or 1
    max_shares = max(parse_count(item.get("shareCount")) for item in items) or 1
    max_comments = max(parse_count(item.get("commentCount")) for item in items) or 1
    cards: list[str] = []
    for idx, item in enumerate(items, 1):
        link = sanitize_http_url(item.get("noteLink"))
        title = esc(item.get("title"))
        account = esc(item.get("accountName") or item.get("accountId") or "未知公众号")
        reason = esc(infer_hot_reason(item))
        style = esc(infer_style(item))
        reads = display_count(item.get("clicksCount"))
        share = parse_count(item.get("shareCount"))
        comments = parse_count(item.get("commentCount"))
        cards.append(
            f"""<article class="article-card">
  <div class="rank">#{idx}</div>
  <div class="article-main">
    <div class="article-title">{f'<a href="{esc(link)}" target="_blank" rel="noreferrer">{title}</a>' if link else title}</div>
    <div class="article-meta">{account} · {esc(item.get("publicTime"))} · {esc(item.get("category"))}</div>
    <div class="tags"><span>{reason}</span><span>{style}</span></div>
    <div class="mini-bars">
      <div><span>阅读 {esc(reads)}</span><i><b style="width:{pct(parse_count(item.get("clicksCount")) / max_reads * 100)}"></b></i></div>
      <div><span>分享 {share}</span><i><b style="width:{pct(share / max_shares * 100)}"></b></i></div>
      <div><span>评论 {comments}</span><i><b style="width:{pct(comments / max_comments * 100)}"></b></i></div>
    </div>
  </div>
</article>"""
        )
    return "\n".join(cards)


def build_formula_cards(sector_name: str, title_words: list[str]) -> str:
    formulas = [
        ("新工具 + 强结论", f"{sector_name} 新工具实测：真正厉害的不是会聊天，而是能交付任务"),
        ("旧指标失效 + 新指标登场", f"别再只看参数/Token 了，{sector_name} 时代要看交付结果"),
        ("开源项目 + 个人效率跃迁", f"推荐一个刚开源的 {sector_name} 工具，一个人也能跑多条工作流"),
        ("大厂动作 + 行业拐点", f"大厂开始押注 {sector_name}，说明落地方式变了"),
    ]
    cards = "\n".join(
        f"""<div class="formula-card"><div>{esc(label)}</div><strong>{esc(title)}</strong></div>"""
        for label, title in formulas
    )
    words = "".join(f"<span>{esc(word)}</span>" for word in title_words[:14])
    return f"""{cards}
<div class="word-cloud">{words}</div>"""


def build_sector_html(sector: dict[str, Any]) -> str:
    items = sector["items"]
    top_reads, top_shares, top_comments = top_metric_items(items)
    title_words = extract_title_patterns([x.get("title", "") for x in items])
    avg_share = round(sum(parse_count(x.get("shareCount")) for x in items) / max(1, len(items)), 1)
    max_share = parse_count(top_shares.get("shareCount")) if top_shares else 0
    max_comment = parse_count(top_comments.get("commentCount")) if top_comments else 0
    top_title = top_reads.get("title") if top_reads else "暂无"
    top_read_count = display_count(top_reads.get("clicksCount")) if top_reads else "0"
    return f"""<section class="sector">
  <div class="section-head">
    <div>
      <p class="eyebrow">Sector</p>
      <h2>{esc(sector["name"])}</h2>
    </div>
    <div class="keywords">{", ".join(esc(k) for k in sector["keywords"])}</div>
  </div>

  <div class="kpi-grid">
    <div class="kpi"><span>命中文章</span><strong>{len(items)}</strong><small>篇</small></div>
    <div class="kpi"><span>最高阅读</span><strong>{esc(top_read_count)}</strong><small>{esc(top_title)}</small></div>
    <div class="kpi"><span>最高分享</span><strong>{max_share}</strong><small>{esc(top_shares.get("title") if top_shares else "暂无")}</small></div>
    <div class="kpi"><span>最高评论</span><strong>{max_comment}</strong><small>{esc(top_comments.get("title") if top_comments else "暂无")}</small></div>
  </div>

  <div class="viz-grid">
    <div class="panel">
      <h3>榜单分布</h3>
      {build_bar_rows(category_counts(items), len(items))}
    </div>
    <div class="panel">
      <h3>写作风格</h3>
      {build_bar_rows(style_counts(items), len(items))}
    </div>
    <div class="panel span-2">
      <h3>爆款判断</h3>
      <div class="insight-line"><b>平均分享</b><span>{avg_share}</span></div>
      <div class="insight-line"><b>整体倾向</b><span>明确结论 + 具体场景 + 可转述标题</span></div>
      <div class="insight-line"><b>优先拆解</b><span>分享/阅读比高、低粉高阅读、评论高的文章</span></div>
    </div>
  </div>

  <div class="panel">
    <h3>热门文章排行</h3>
    <div class="article-list">{build_article_cards(items)}</div>
  </div>

  <div class="panel">
    <h3>写作参考</h3>
    <div class="formula-grid">{build_formula_cards(sector["name"], title_words)}</div>
    <ol class="structure">
      <li>开头 3 段内给结论和数据锚点。</li>
      <li>用一个具体任务场景承接读者焦虑。</li>
      <li>拆 3 个关键能力，每个能力配案例、截图或成本收益。</li>
      <li>最后给判断：适合谁、不适合谁、下一步怎么试。</li>
    </ol>
  </div>
</section>"""


def build_html(report: dict[str, Any]) -> str:
    sectors_html = "\n".join(build_sector_html(sector) for sector in report["sectors"])
    total_items = sum(len(sector["items"]) for sector in report["sectors"])
    sector_count = len(report["sectors"])
    all_items = [item for sector in report["sectors"] for item in sector["items"]]
    top_reads, top_shares, _ = top_metric_items(all_items)
    top_read_text = display_count(top_reads.get("clicksCount")) if top_reads else "0"
    top_share_text = str(parse_count(top_shares.get("shareCount"))) if top_shares else "0"
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>爆款文章分析</title>
<style>
:root{{
  --bg:#f6f4ef;
  --paper:#fffdf8;
  --ink:#20201d;
  --muted:#746f66;
  --line:#e5ded1;
  --accent:#0f766e;
  --accent-2:#b45309;
  --soft:#e8f4f1;
}}
*{{box-sizing:border-box}}
body{{
  margin:0;
  background:var(--bg);
  color:var(--ink);
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;
  line-height:1.65;
}}
a{{color:inherit;text-decoration:none}}
.page{{max-width:1180px;margin:0 auto;padding:40px 22px 64px}}
.hero{{
  border-bottom:1px solid var(--line);
  padding:16px 0 30px;
  display:grid;
  grid-template-columns:minmax(0,1.4fr) minmax(280px,.6fr);
  gap:28px;
  align-items:end;
}}
.eyebrow{{margin:0 0 10px;color:var(--accent);font-size:12px;letter-spacing:.08em;text-transform:uppercase;font-weight:700}}
h1{{font-size:44px;line-height:1.08;margin:0 0 16px;letter-spacing:0}}
h2{{font-size:30px;line-height:1.18;margin:0;letter-spacing:0}}
h3{{font-size:18px;margin:0 0 16px;letter-spacing:0}}
.hero p{{margin:0;color:var(--muted);max-width:760px}}
.summary-grid,.kpi-grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}}
.summary-card,.kpi,.panel,.article-card,.formula-card{{
  background:var(--paper);
  border:1px solid var(--line);
  border-radius:8px;
}}
.summary-card,.kpi{{padding:18px}}
.summary-card span,.kpi span{{display:block;color:var(--muted);font-size:13px}}
.summary-card strong,.kpi strong{{display:block;font-size:30px;line-height:1.1;margin:8px 0 6px}}
.summary-card small,.kpi small{{display:block;color:var(--muted);font-size:12px;line-height:1.45}}
.sector{{padding-top:34px}}
.section-head{{display:flex;justify-content:space-between;gap:24px;align-items:flex-end;margin-bottom:16px}}
.keywords{{color:var(--muted);font-size:13px;max-width:520px;text-align:right}}
.viz-grid{{display:grid;grid-template-columns:repeat(2,1fr);gap:14px;margin:14px 0}}
.panel{{padding:20px}}
.span-2{{grid-column:span 2}}
.bar-row{{margin:14px 0}}
.bar-label{{display:flex;justify-content:space-between;color:var(--muted);font-size:13px;margin-bottom:7px}}
.bar-label b{{color:var(--ink)}}
.bar-track{{height:10px;background:#eee8dc;border-radius:99px;overflow:hidden}}
.bar-fill{{height:100%;background:linear-gradient(90deg,var(--accent),#67b6a9);border-radius:99px}}
.insight-line{{display:grid;grid-template-columns:120px 1fr;gap:12px;padding:10px 0;border-top:1px solid var(--line)}}
.insight-line:first-of-type{{border-top:0}}
.insight-line b{{color:var(--accent-2)}}
.article-list{{display:grid;gap:10px}}
.article-card{{display:grid;grid-template-columns:56px 1fr;gap:14px;padding:14px}}
.rank{{width:42px;height:42px;border-radius:50%;background:var(--soft);display:grid;place-items:center;color:var(--accent);font-weight:800}}
.article-title{{font-size:17px;font-weight:750;line-height:1.35}}
.article-title a:hover{{color:var(--accent)}}
.article-meta{{color:var(--muted);font-size:12px;margin-top:6px}}
.tags{{display:flex;flex-wrap:wrap;gap:6px;margin:10px 0}}
.tags span,.word-cloud span{{font-size:12px;background:#f1eadf;border:1px solid var(--line);border-radius:999px;padding:4px 9px;color:#5d554b}}
.mini-bars{{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-top:10px}}
.mini-bars span{{display:block;color:var(--muted);font-size:12px;margin-bottom:4px}}
.mini-bars i{{display:block;height:7px;background:#eee8dc;border-radius:99px;overflow:hidden}}
.mini-bars b{{display:block;height:100%;background:var(--accent);border-radius:99px}}
.formula-grid{{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}}
.formula-card{{padding:14px}}
.formula-card div{{color:var(--accent-2);font-size:12px;font-weight:700;margin-bottom:8px}}
.formula-card strong{{font-size:15px;line-height:1.45}}
.word-cloud{{grid-column:span 2;display:flex;flex-wrap:wrap;gap:8px;margin-top:8px}}
.structure{{margin:16px 0 0;padding-left:22px;color:#3b3832}}
.empty,.muted{{color:var(--muted)}}
.footer{{margin-top:34px;padding-top:20px;border-top:1px solid var(--line);color:var(--muted);font-size:13px}}
@media (max-width: 820px){{
  .hero,.section-head{{display:block}}
  h1{{font-size:34px}}
  .summary-grid,.kpi-grid,.viz-grid,.formula-grid,.mini-bars{{grid-template-columns:1fr}}
  .span-2,.word-cloud{{grid-column:auto}}
  .keywords{{text-align:left;margin-top:8px}}
}}
</style>
</head>
<body>
<main class="page">
  <header class="hero">
    <div>
      <p class="eyebrow">WeChat Hot Article Radar</p>
      <h1>爆款文章分析</h1>
      <p>数据窗口：{esc(report["startDate"])} 至 {esc(report["reportDate"])}。阅读、点赞、分享、评论来自公众号爆款文章洞察接口快照，适合做趋势判断和写作参考。</p>
    </div>
    <div class="summary-grid">
      <div class="summary-card"><span>赛道数</span><strong>{sector_count}</strong><small>本次分析范围</small></div>
      <div class="summary-card"><span>文章数</span><strong>{total_items}</strong><small>去重后样本</small></div>
      <div class="summary-card"><span>最高阅读</span><strong>{esc(top_read_text)}</strong><small>{esc(top_reads.get("title") if top_reads else "暂无")}</small></div>
      <div class="summary-card"><span>最高分享</span><strong>{esc(top_share_text)}</strong><small>{esc(top_shares.get("title") if top_shares else "暂无")}</small></div>
    </div>
  </header>
  {sectors_html}
  <footer class="footer">生成时间：{esc(report.get("generatedAt"))} · 数据源：{esc(report.get("source"))}</footer>
</main>
</body>
</html>"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch and analyze WeChat hot articles by sector.")
    parser.add_argument("--sector", action="append", help="Sector spec: 赛道=关键词1,关键词2. Can repeat.")
    parser.add_argument("--sector-config", help="JSON file: {\"赛道\": [\"关键词\"]}.")
    parser.add_argument("--days", type=int, default=7, help="Lookback days. Default: 7.")
    parser.add_argument("--start-date", help="Explicit start date YYYY-MM-DD. Overrides --days.")
    parser.add_argument("--max-items-per-sector", type=int, default=10)
    parser.add_argument("--output-dir", default="baokuan-article-analysis")
    parser.add_argument("--report-date", default=dt.date.today().isoformat())
    parser.add_argument("--timeout", type=int, default=60)
    args = parser.parse_args()

    config = load_sector_config(args.sector_config) or parse_sector_args(args.sector)
    report_date = dt.date.fromisoformat(args.report_date)
    start_date = args.start_date or (report_date - dt.timedelta(days=max(1, args.days))).isoformat()

    report: dict[str, Any] = {
        "reportDate": report_date.isoformat(),
        "startDate": start_date,
        "generatedAt": dt.datetime.now().isoformat(timespec="seconds"),
        "source": SOURCE,
        "sectors": [],
    }

    for name, keywords in config.items():
        all_items: list[dict[str, Any]] = []
        errors: list[str] = []
        for keyword in keywords:
            try:
                all_items.extend(fetch_keyword(keyword, start_date, timeout=args.timeout))
            except Exception as exc:
                errors.append(f"{keyword}: {exc}")
        items = dedupe_and_rank(all_items, args.max_items_per_sector, keywords)
        report["sectors"].append({
            "name": name,
            "keywords": keywords,
            "items": items,
            "errors": errors,
        })

    out_root = Path(args.output_dir).expanduser().resolve() / report_date.isoformat()
    out_root.mkdir(parents=True, exist_ok=True)
    json_path = out_root / "data.json"
    html_path = out_root / "report.html"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    html_path.write_text(build_html(report), encoding="utf-8")

    print(f"Saved JSON: {json_path}")
    print(f"Saved HTML: {html_path}")


if __name__ == "__main__":
    main()
