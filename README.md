<h1 align="center">Creator Buddy</h1>

<p align="center"><code>creator-buddy.skill</code></p>

<p align="center"><em>「你想追的下一个热点，何必靠刷信息流」</em></p>

<p align="center">
  <img alt="License MIT" src="https://img.shields.io/badge/License-MIT-c8a500?style=for-the-badge">
  <img alt="Agent Skills Standard" src="https://img.shields.io/badge/Agent%20Skills-Standard-5aa524?style=for-the-badge">
  <img alt="skills.sh Compatible" src="https://img.shields.io/badge/skills.sh-Compatible-1888c8?style=for-the-badge">
  <img alt="Runtime" src="https://img.shields.io/badge/Runtime-Claude%20Code%20%C2%B7%20Codex%20%C2%B7%20Cursor%20%C2%B7%20OpenClaw%20%C2%B7%20Hermes-7b2bd9?style=for-the-badge">
</p>

<p align="center">
  公众号 / 小红书 / B站 / 知乎：<strong>空格的键盘</strong> ｜ <a href="mailto:wzfh520@gmail.com">wzfh520@gmail.com</a>
</p>

Creator Buddy 是一套给内容创作者、运营、增长和自媒体作者用的运营情报 Skill 集合。

它帮你从小红书、公众号、B站等内容平台里搜索热点、挖爆款、看评论、查竞品、找选题，把“今天写什么”从玄学变成一套可复用的数据工作流。

基于开放的 Agent Skills 协议，可在 Claude Code、Codex、Cursor、OpenClaw、Hermes Agent、CodeBuddy、Workbuddy、Gemini CLI、OpenCode 等兼容 runtime 中运行。

不是让 AI 凭感觉给你编选题。

是先把平台上的真实内容、互动数据、标题结构和传播信号拉回来，再让 Agent 帮你判断：

- 哪些话题正在涨
- 哪些标题值得拆
- 哪些内容形式在被收藏
- 哪些爆款只是噪声
- 你的下一篇文章、小红书笔记、B站视频该往哪里打

看效果 · 安装 · 它能搜索什么 · 工作原理 · 诚实边界

## 效果示例

```text
用户      ❯ 帮我看看最近 Codex 在小红书上有什么爆款

助手      ❯ 已搜索小红书热门笔记，关键词：Codex / OpenAI Codex / AI编程 / Claude Code

            近 7 天返回 39 条，筛选出 10 条高相关结果。

            最高互动方向：
            1. 低成本玩转 Claude Code：6w+ 互动
            2. Codex 写文献综述：1w+ 互动
            3. 5 分钟安装 Codex：1w+ 互动
            4. Codex 小白教程：5000+ 互动
            5. Codex 磁盘日志避坑：5000+ 互动

            结论：
            小红书用户不关心“模型多强”，更关心：
            - 怎么安装
            - 怎么省钱
            - 怎么避坑
            - 普通人能不能用
            - 能不能马上做 PPT、论文、剪视频
```

再看公众号：

```text
用户      ❯ 搜一下公众号里 Codex 相关爆款

助手      ❯ 已生成公众号赛道报告。

            强相关爆款包括：
            - 阿里版 Codex 正式发布：7w+ 阅读，3075 分享
            - 你的 Codex 可能只解锁了 1%：3w+ 阅读，2012 分享
            - 用 Codex 搭建 Karpathy 同款知识库：1w+ 阅读，2527 分享
            - 往 Codex 里塞块无限画布：1w+ 阅读，2173 分享

            公众号更吃“Codex + 具体生产场景”：
            知识库、PPT、视频、画布改图、国产替代。
```

再看跨平台搜索：

```text
用户      ❯ B站搜一下 AI 编程，看哪些视频在起量

助手      ❯ 已通过 B站公开搜索 API 返回结果：

            1. 一口气学会 AI 编程
               播放 17w+，收藏 1.7w+

            2. 黑马 Vibe Coding 零基础入门
               播放 6w+，覆盖 Claude Code / Cursor / Codex / Agent

            3. Trae 保姆级教程
               播放 95w+，收藏 2.9w+

            结论：
            B站教程内容更吃“长课 + 工具合集 + 零基础 + 项目实操”。
```

这不是泛泛的“帮我想 10 个选题”。  
它先搜索，再筛选，再把平台语境还原出来。

## 安装

Creator Buddy 基于开放的 Agent Skills 协议，可在任何 skills-compatible 的 AI agent runtime 中运行。

### 方式一：一行命令（推荐，跨 runtime）

打开你正在用的 agent（Claude Code、Codex、Cursor、OpenClaw、Hermes、CodeBuddy、Workbuddy、Gemini CLI、OpenCode 等），告诉它：

```text
帮我安装这个 skill：https://github.com/zephyrwang6/creator-buddy
```

或者用通用 CLI 安装器（vercel-labs/skills，支持多 runtime）：

```bash
npx skills add zephyrwang6/creator-buddy
```

它会自动识别你当前的 runtime 并把 skill 放到正确目录。需要指定时可加 runtime 参数，例如 `-a codex` / `-a claude-code` / `-a cursor`。

### 方式二：手动安装

克隆仓库后，把需要的 skill 目录复制到你的 runtime skills 目录：

```bash
git clone https://github.com/zephyrwang6/creator-buddy.git
```

仓库结构：

```text
skills/
  xhs-hotnotes/
  global-content-search/
  gzh-explosive-content-detector/
  baokuan-article-analysis/
```

每个子目录都是一个独立 Skill。

### 方式三：作为参考资料使用

即使你的 runtime 不支持 Agent Skills 自动加载，也可以直接打开对应目录里的 `SKILL.md`，把内容粘贴进对话。  
它本质是一份 markdown + YAML frontmatter + 可运行脚本。

## 使用

装好后，可以直接告诉 agent：

```text
帮我搜一下小红书最近 Codex 的热门笔记
```

```text
查一下公众号里 AI Agent 相关爆款
```

```text
帮我看 B站上 AI 编程教程最近哪些视频起量
```

```text
找一下小红书某个博主最近发了什么，评论区在关心什么
```

如果你想手动运行脚本，也可以：

### 小红书热门笔记

```bash
export REDFOX_API_KEY="your_api_key_here"

python3 skills/xhs-hotnotes/scripts/fetch_xhs_hot_articles.py \
  --keyword "Codex,AI编程" \
  --start-date 2026-06-23
```

### 小红书 / B站 / 抖音内容分析

```bash
node skills/global-content-search/src/xiaohongshu/search-cli.js \
  --platform xiaohongshu \
  --keyword "AI编程" \
  --limit 20
```

```bash
node skills/global-content-search/src/xiaohongshu/search-cli.js \
  --platform bilibili \
  --keyword "AI编程" \
  --limit 10
```

抖音目前是扩展入口：

```bash
export DOUYIN_COMMAND="/path/to/douyin-readonly-cli"

node skills/global-content-search/src/xiaohongshu/search-cli.js \
  --platform douyin \
  --keyword "AI工具"
```

### 公众号爆款搜索

```bash
python3 skills/gzh-explosive-content-detector/scripts/fetch_gzh_trends.py \
  --keyword "AI编程,Codex,Claude Code" \
  --start-date 2026-06-23
```

### 公众号赛道分析

```bash
python3 skills/baokuan-article-analysis/scripts/daily_sector_trends.py \
  --sector "AI Coding=Codex,Claude Code,AI编程" \
  --days 7 \
  --output-dir ./reports
```

## 它能搜索什么

| Skill | 解决的问题 | 输出 |
| --- | --- | --- |
| `xhs-hotnotes` | 小红书热门笔记搜索、互动排序、相关性评分 | HTML 报告 + JSON |
| `global-content-search` | 全域内容搜索：小红书/B站/抖音扩展入口，查关键词、详情、评论、创作者作品；小红书支持 Guaikei API 兜底 | JSON / raw 输出 + logs |
| `gzh-explosive-content-detector` | 公众号关键词爆款搜索 | HTML 报告 |
| `baokuan-article-analysis` | 公众号赛道级爆款聚合、去重、排名、风格分析 | HTML 报告 + `data.json` |

## 搜索方式

你可以用自然语言直接触发总控 Skill，也可以调用单个分支 Skill。

| 方式 | 示例 | 会触发什么 |
| --- | --- | --- |
| 平台名 + 关键词 | `小红书 Codex`、`B站 AI编程`、`公众号 Agent`、`抖音 剪辑Agent` | 按平台搜索内容，返回热度、标题、链接、摘要和可用互动指标 |
| 全平台关键词 | `全平台搜 Codex`、`对比小红书和B站上的 AI编程` | 跨平台检索并对比内容形态、热度信号和选题角度 |
| 平台链接 | 小红书笔记/主页、B站视频/空间、公众号文章、抖音视频/主页链接 | 识别平台与对象类型，进入文章、视频、笔记或博主分析 |
| 博主/账号分析 | `分析这个博主`、`看这个UP主近期作品`、`拆这个小红书账号` | 分析作品结构、更新节奏、互动分布、标题和内容风格 |
| 内容风格拆解 | `拆这篇文章风格`、`分析这个爆款为什么火` | 提炼开头、标题、结构、论据、情绪钩子和转化方式 |
| 指标导向搜索 | `找点赞高的`、`看收藏最多的`、`按评论热度排序` | 优先按点赞、收藏、评论、阅读、播放等可用字段排序 |
| 指定输出 | `给我表格`、`生成选题建议`、`提炼标题公式`、`输出HTML报告` | 把搜索结果转成运营可用的表格、报告或创作建议 |

## 工作原理

Creator Buddy 不是一个单一爬虫，而是一组内容运营 Skill。

它把运营调研拆成四层：

| 层次 | 说明 |
| --- | --- |
| 平台访问 | 通过 Redfox、Agent Reach、OpenCLI、bili-cli、公开 API 等后端读取公开内容 |
| 数据整理 | 去重、排序、评分、截断、生成结构化 JSON |
| 报告生成 | 输出 HTML 报告、排名卡片、互动指标、标题样本 |
| 运营判断 | 让 Agent 基于数据提炼选题方向、标题机制、内容形式和传播原因 |

其中 `global-content-search` 的访问顺序是 Agent Reach 优先，Guaikei API 最后兜底：

- 小红书：优先走 Agent Reach 检测到的 `OpenCLI` / `xiaohongshu-mcp` / `xhs-cli`
- 小红书兜底：如果 Agent Reach 搜不了，配置 `GUAIKEI_API_TOKEN` 后使用 Guaikei API
- B站：优先走 `bili-cli` / `opencli bilibili`，否则走公开搜索/详情 API
- 抖音：预留 `DOUYIN_COMMAND` 自定义只读 CLI

## 适合谁

- 自媒体作者：找选题、拆标题、看评论区需求
- 公众号作者：找近期爆款、判断文章方向
- 小红书运营：查热点笔记、竞品账号、评论反馈
- B站创作者：看视频选题、教程形态和播放收藏信号
- 产品/增长团队：监控用户讨论、内容趋势和传播路径

## 风控与安全性说明

Creator Buddy 的定位是公开内容研究和选题分析，不是账号自动化工具。

- 只读公开数据：默认只读取公开页面、公开 API、只读 CLI 或你本机已授权的只读工具。
- 不做账号动作：不执行发帖、点赞、收藏、评论、关注、私信、批量加好友等写操作。
- 不绕过限制：不帮助绕过登录、验证码、权限校验、付费墙、平台风控或反爬规则。
- 凭据不入库：`GUAIKEI_API_TOKEN`、Cookie、登录态、`.env`、原始日志和带 token 的链接都不应提交到仓库。
- 本地优先：需要登录态的平台访问只在用户本机工具链中完成，Skill 仓库不收集、不上传账号信息。
- 低频使用：评论、详情页和批量搜索容易触发平台限制，建议小批量、低并发、按需采样。
- 抖音扩展需只读：`DOUYIN_COMMAND` 只应接入本地只读查询 CLI，不应绑定任何账号操作能力。
- 分享前脱敏：公开报告前移除 `xsec_token`、Cookie、邮箱、手机号、后台链接和未公开账号信息。

## 诚实边界

每个运营工具都应该说明自己做不到什么。

- 不是实时后台数据：平台数据来自公开页面、第三方数据源或入库快照。
- 不绕过平台限制：不做发帖、点赞、评论等写操作，不承诺绕过验证码或风控。
- 小红书受 `xsec_token` 机制影响：详情页通常需要使用搜索结果返回的完整 URL。
- 抖音当前不是内置可用后端：仓库只提供扩展入口，需你接入本地只读 CLI。
- 热门不等于适合你：爆款数据只能说明平台上什么在传播，不能替代你的定位判断。
- 公开表达不等于真实需求：评论和互动是信号，不是用户内心的完整答案。

一个不告诉你边界在哪的运营工具，不值得信任。

## 参考

Creator Buddy 的平台访问和小红书分析能力参考了以下项目与 Skill 设计：

- [Agent Reach](https://github.com/Panniantong/Agent-Reach)：参考其通过 Agent 操作浏览器/本地环境访问平台内容的思路。
- [xiaohongshu-tools / xiaohongshu-openclaw-skill](https://github.com/um-why/xiaohongshu-openclaw-skill)：参考小红书搜索、详情、评论和分析工作流。

## 许可证

MIT
