# Style Guide

Use this file after the user chooses a style.

## Shared Rules

- Copied article HTML must use inline styles.
- Preview app chrome may use normal CSS.
- Keep article width near WeChat's comfortable reading width: `max-width:677px`.
- Prefer `font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',Arial,sans-serif`.
- Use 15-16px body text, `line-height:1.8-1.95`.
- Keep decorative elements quiet; content must remain the focus.
- Do not add visible instructions inside the copied article body.

## Claude Style

Use for reflective essays, opinion pieces, cultural commentary, narratives, and longform analysis.

Visual language:
- Background: warm off-white `#fbfaf7` or `#f8f3ea`.
- Text: charcoal `#171717`, secondary `#6f6a62`.
- Accent: muted amber/brown `#a16207`, soft border `#e7e1d7`.
- Shape: 8px cards, fine borders, paper-like spacing, no heavy shadows in copied HTML.
- Layout: generous whitespace, editorial title block, subtle callouts.

Useful components:
- Top kicker in small uppercase English or Chinese label.
- Quote/callout: left border `3px solid #d8b37c`, background `#fffaf0`.
- Long body/essay window: white or `#fbfaf7` panel, border `#e8e3da`, `max-height:420px;overflow-y:auto`.

## OpenAI Style

Use for technical articles, product notes, tutorials, tool comparisons, API guides, and developer writing.

Visual language:
- Background: pure white `#ffffff`.
- Text: black `#111111`, secondary `#5f6368`.
- Accent: black or cool gray; avoid decorative color.
- Shape: crisp 6-8px panels, thin gray borders, documentation-style hierarchy.
- Layout: dense but scannable, clear headings, compact tables.

Useful components:
- Section heading with bottom border `2px solid #111`.
- Code/tool callout: `background:#f6f8fa;border:1px solid #e5e7eb`.
- Tables: simple gray header, compact cells, no heavy fills.

## Google Style

Use for educational explainers, ranking tables, model/product comparisons, data summaries, and broader public-facing analysis.

Visual language:
- Background: white `#ffffff` with very pale cards.
- Text: near-black `#202124`, secondary `#5f6368`.
- Accents: Google-like but restrained: blue `#1a73e8`, green `#188038`, yellow `#fbbc04`, red `#d93025`.
- Shape: modular cards with 8px radius, colored top bars or small badges.
- Layout: structured cards, comparison grids, score badges.

Useful components:
- Model/ranking card with small colored badge.
- Table header in pale blue `#e8f0fe`.
- Insight callout with left colored stripe.

## Choosing Components

- Articles with multiple evaluated works: use one card per work; put title, keyword, scores, and comments outside; put the long work body inside a scrollable preview window.
- Articles with ranking tables: render actual HTML tables, not screenshots.
- Articles with summary bullets: use styled numbered blocks or simple cards.
- Very long paragraphs: split at natural sentence boundaries only; do not change meaning.
