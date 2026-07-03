# Space Ops Assistant

AI-powered content operations assistants for trend discovery, hot article mining, and publishing research across Chinese content platforms.

This repository bundles several Codex/OpenAI-style skills that help creators and operators find high-performing topics, inspect viral patterns, and generate data-backed writing references.

## Skills

| Skill | Purpose | Main artifact |
| --- | --- | --- |
| `xhs-hotnotes` | Search Xiaohongshu/RedNote hot notes by keyword and rank them by relevance, popularity, and recency. | HTML report + JSON output |
| `xiaohongshu-content-tools` | Analyze Xiaohongshu note details, comments, creator posts, and keyword results through the Guaikei API. | JSON/Markdown output + local logs |
| `gzh-explosive-content-detector` | Search WeChat Official Account explosive articles by keyword. | HTML report |
| `baokuan-article-analysis` | Analyze hot WeChat articles by sector, merge keyword groups, deduplicate results, and generate a visual report. | HTML report + `data.json` |

## Repository Layout

```text
skills/
  xhs-hotnotes/
  xiaohongshu-content-tools/
  gzh-explosive-content-detector/
  baokuan-article-analysis/
```

Each skill is self-contained and includes its own `SKILL.md`, scripts, and references.

## Quick Start

### Xiaohongshu hot notes

```bash
export REDFOX_API_KEY="your_api_key_here"
python3 skills/xhs-hotnotes/scripts/fetch_xhs_hot_articles.py \
  --keyword "Codex,AI编程" \
  --start-date 2026-06-23
```

### WeChat explosive article search

```bash
python3 skills/gzh-explosive-content-detector/scripts/fetch_gzh_trends.py \
  --keyword "AI编程,Codex,Claude Code" \
  --start-date 2026-06-23
```

### Xiaohongshu content analysis

```bash
export GUAIKEI_API_TOKEN="your_api_token_here"

node skills/xiaohongshu-content-tools/src/xiaohongshu/search-cli.js \
  --keyword "夏季穿搭" \
  --sort 2 \
  --limit 20

node skills/xiaohongshu-content-tools/src/xiaohongshu/detail-cli.js \
  --url "https://www.xiaohongshu.com/explore/xxx?xsec_token=yyy" \
  --limit 100

node skills/xiaohongshu-content-tools/src/xiaohongshu/post-cli.js \
  --url "https://www.xiaohongshu.com/user/profile/xxx?xsec_token=yyy" \
  --limit 20
```

### WeChat sector analysis

```bash
python3 skills/baokuan-article-analysis/scripts/daily_sector_trends.py \
  --sector "AI Coding=Codex,Claude Code,AI编程" \
  --days 7 \
  --output-dir ./reports
```

## Notes

- Runtime API keys must be supplied through environment variables. Do not commit local keys, cookies, raw platform tokens, or generated logs.
- Generated reports and local caches are ignored by default.
- Public platform data belongs to the original authors and platforms. Use this repository for research, analysis, and content planning.
