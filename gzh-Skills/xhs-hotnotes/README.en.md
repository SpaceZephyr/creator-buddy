# Xiaohongshu Trending Note Search

---

## Introduction

A Xiaohongshu trending note search tool that helps you quickly find trending notes with 1,000+ engagements, gain creative inspiration, and stay on top of content trends.

**Core Value**

Continuously indexing trending notes with 1,000+ engagements from Xiaohongshu across the web over the past 30 days, updated at 7 AM daily with yesterday's data. Articles are ranked by a weighted score across relevance, popularity, and timeliness, bringing together top trending content across all categories. Quickly find quality benchmark content across tracks, easily reference trending creative approaches from peers — no more scouring multiple sources for material. A one-stop solution for your daily topic research needs.

**Who it's for**

- 🎯 Brands — Ride trending topics for seeding content
- 🏢 MCNs — Discover high-engagement potential accounts
- ✍️ Creators — Find benchmark samples and creative inspiration
- 📊 Content ops — Weekly topic selection and competitor analysis

---

## Core capabilities

- **Keyword search**: Enter a track keyword to fetch the most matching Xiaohongshu trending notes
- **Data-scored ranking**: Weighted scoring across relevance, popularity, and timeliness to recommend optimal notes
- **Smart generic-keyword expansion**: Recognizes generic keywords and recommends 10 niche directions; retrieves only after user confirmation
- **Niche track suggestions**: After displaying results, proactively suggests deeper niche directions for step-by-step exploration
- **Subscription push**: Supports creating calendar subscriptions by keyword for daily push of latest trending notes

### Highlights

- **Flexible time window**: Last 1/3/7/30 days; auto-extends when data is thin and states clearly
- **Dual output format**: Markdown cards + local HTML visualization file (`{keyword}_trending_data.html`)

---

## API key source and security

- This skill requires the environment variable: `REDFOX_API_KEY`.
- `REDFOX_API_KEY` is issued by [Redfox Hub](https://redfox.hk/dashboard/keys?source=skillhub) (`https://redfox.hk`) for API authentication.
- Before providing the key, confirm its source, available scope, validity period, and whether reset/revocation is supported.
- Do not hard-code or expose the key in plaintext within code, prompts, logs, or output files.

---

## Prerequisites

### Register a Redfox Hub account to obtain REDFOX_API_KEY

- Get REDFOX_API_KEY (apply at [Redfox Hub](https://redfox.hk/dashboard/keys?source=skillhub))

### Environment variables

| Variable         | Required | Notes          |
| ---------------- | -------- | -------------- |
| `REDFOX_API_KEY` | Yes      | API access key |

**macOS (zsh)**

Append one line to the end of `~/.zshrc` (replace the value in quotes with your key):

```bash
export REDFOX_API_KEY="your_api_key_here"
```

Then run:

```bash
source ~/.zshrc
```

**Windows (PowerShell)**

- **Current terminal only**: Takes effect immediately after run, **no other commands needed**; lost when the window is closed.

```powershell
$env:REDFOX_API_KEY = "your_api_key_here"
```

- **Persist to user environment**: After running `setx`, the **current PowerShell window still won't have the variable**; you need to **close and reopen** the terminal (or restart Cursor / VS Code, etc.) for the new window to read `REDFOX_API_KEY`.

```powershell
setx REDFOX_API_KEY "your_api_key_here"
```

---

## Usage guide

Just describe your needs in natural language — no need to memorize any command format. When you enter a generic keyword, niche directions will be suggested for you to choose from.

### Quick phrase reference

| Intent                      | Example phrase                                   | Result                                                                         |
| --------------------------- | ------------------------------------------------ | ------------------------------------------------------------------------------ |
| Search by keyword           | "Find trending notes on fat-loss meals"          | Recognize keyword → query → TOP10 trending notes + HTML report                 |
| Site-wide trending          | "Show me what's trending on Xiaohongshu"         | Empty keyword site-wide query → trending leaderboard                           |
| Search by time range        | "Workplace fashion trending in the last 15 days" | Filter by specified time window → trending data with date range                |
| Generic keyword expansion   | "Search food trending notes"                     | Detect generic keyword → suggest 10 niche directions → await your confirmation |
| Niche keyword direct search | "Petite fashion trending notes"                  | Recognize niche keyword → direct search → precise results                      |

### Output example

📅 Query period: May 8 – May 19

| Note title                                                                        | Author                                                            | Engagement | Published  | Relevance | Popularity | Timeliness | **Total** |
| --------------------------------------------------------------------------------- | ----------------------------------------------------------------- | ---------- | ---------- | --------- | ---------- | ---------- | --------- |
| [5 tips for new hires to fit in quickly](https://www.xiaohongshu.com/explore/xxx) | [Career Growth Hub](https://www.xiaohongshu.com/user/profile/xxx) | 10.0w      | 2026-05-15 | 9.8       | 3.0        | 2.0        | **14.8**  |

🔤 Related searches: Workplace communication, Career advancement, Office worker

📬 Subscription
1️⃣ Would you like to subscribe to notes matching the current search criteria for scheduled push?
2️⃣ Not needed

---

## Use cases

| Scenario                           | Role            | Need                                                        | How to use                                                    |
| ---------------------------------- | --------------- | ----------------------------------------------------------- | ------------------------------------------------------------- |
| Cold-start topics for new accounts | Creator         | Can't find copyable trending samples                        | Keyword + last 7–30 days query                                |
| Brand milestone seeding            | Brand operator  | Need trending topics and format references before campaigns | Category keyword search; export HTML for internal review      |
| Pre-sign screening                 | MCN scout       | Want high-engagement trajectory, not one-off luck           | Multiple samples in a fixed window for comparison             |
| Pitches and weekly reports         | Content planner | Client wants "trends + samples" one-pager                   | Structured summary + HTML; conclusions must match data window |

---

## Important data notes

### Update schedule and data lookback

| Data type      | Update time                                 | Lookback range          |
| -------------- | ------------------------------------------- | ----------------------- |
| Trending notes | Updated at 7 AM daily with yesterday's data | Yesterday – 30 days ago |

### Supported tracks

Fashion, Food, Makeup, Film & TV, Workplace, Pets, Home, Travel, Transportation, Hobbies, Tech, Internet, Healthcare, Astrology & Relationships, Wedding, Photography, Education, Parenting, Personal Care, Trendy Shoes & Bags, Lifestyle, Science, News, Sports

### Inclusion criteria and data timeliness

Trending notes inclusion threshold is articles with 1,000+ engagements. Note engagement data is captured at indexing time and is not real-time; engagement may continue to grow after indexing. Displayed data reflects the indexing snapshot.

### Scoring rules

Keyword searches are sorted by composite score across three weighted dimensions:

| Dimension  | Max score | Description                                          |
| ---------- | --------- | ---------------------------------------------------- |
| Relevance  | 10 pts    | Title keyword, content topic, and search term match  |
| Popularity | 3 pts     | Likes / saves / comments / shares / total engagement |
| Timeliness | 2 pts     | Proximity of publish date to query time              |

Site-wide trending (no keyword) is sorted by engagement count with no scoring fields.
