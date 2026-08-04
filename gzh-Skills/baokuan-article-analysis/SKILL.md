---
name: baokuan-article-analysis
description: Fetch and analyze WeChat Official Account hot articles / 公众号爆款文章 by sector or keywords. Use when the user asks for 爆款文章分析, 赛道爆款, 公众号爆款数据, reading counts, likes, shares, comments, title patterns, writing style, 爆款原因分析, or writing references for content creation.
---

# 爆款文章分析

## Overview

Use this skill to fetch hot WeChat Official Account article data by sector and generate a daily analysis report. It is for sector-level or keyword-level analysis, not exact historical scraping for one specific account.

The bundled script queries the hot-article data source, merges keywords by sector, deduplicates articles, ranks them, and writes:

- `data.json`: raw structured data
- `report.html`: a minimal visual analysis report with KPI cards, bar charts, ranked article cards, writing style analysis, hot reasons, and writing references

Do not default to Markdown reports. The primary user-facing artifact is `report.html`.

## Quick Start

Run with the default sectors:

```bash
python3 ~/.codex/skills/baokuan-article-analysis/scripts/daily_sector_trends.py \
  --output-dir ./output/baokuan-article-analysis
```

Run custom sectors:

```bash
python3 ~/.codex/skills/baokuan-article-analysis/scripts/daily_sector_trends.py \
  --sector 'AI Agent=AI Agent,智能体,Agent框架' \
  --sector 'Skill=skill,Skills,AI Skill' \
  --sector 'Claude Code=Claude Code,Codex,AI编程' \
  --output-dir ./output/baokuan-article-analysis
```

Run with a JSON config:

```bash
python3 ~/.codex/skills/baokuan-article-analysis/scripts/daily_sector_trends.py \
  --sector-config ~/.codex/skills/baokuan-article-analysis/references/default-sectors.json \
  --days 7 \
  --output-dir ./output/baokuan-article-analysis
```

## Workflow

1. Identify sectors and keywords from the user request.
2. If the user only gives broad sectors, use or adapt `references/default-sectors.json`.
3. Run `scripts/daily_sector_trends.py`.
4. Open the generated `report.html`.
5. Summarize for the user:
   - highest-reading and highest-sharing articles
   - writing style patterns
   - hot article reasons
   - title and topic formulas
   - practical writing references
6. Return the HTML file path as the main artifact.

## Script Options

| Option | Purpose |
|---|---|
| `--sector '赛道=关键词1,关键词2'` | Add one sector. Can repeat. |
| `--sector-config path.json` | Load sectors from JSON object. |
| `--days N` | Lookback window. Default is 7 days. |
| `--start-date YYYY-MM-DD` | Explicit start date. Overrides `--days`. |
| `--max-items-per-sector N` | Limit ranked articles per sector. Default is 10. |
| `--output-dir DIR` | Parent output directory. A date folder is created inside. |
| `--report-date YYYY-MM-DD` | Report date. Default is today. |

## Data Boundaries

- This skill returns hot-list data, not a specific account’s complete recent history.
- `clicksCount` is a public data-source snapshot and may lag behind live WeChat backend reads.
- If a specific account name returns no data, switch to that account’s topic keywords and compare same-sector articles.
- If today’s data is sparse, use `--days 7` or `--days 30`.

## Output Interpretation

Use reading count for reach, share count for spread, comments for discussion, and low-fan high-reading entries for title/structure references. Repeated accounts indicate strong competitors or content sources worth following.
