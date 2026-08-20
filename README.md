<h1 align="center">Creator Buddy</h1>

<p align="center"><code>creator-buddy.skill</code></p>

<p align="center"><em>「从一个选题，到一篇能发的成品」</em></p>

<p align="center">
  <img alt="License MIT" src="https://img.shields.io/badge/License-MIT-c8a500?style=for-the-badge">
  <img alt="Agent Skills Standard" src="https://img.shields.io/badge/Agent%20Skills-Standard-5aa524?style=for-the-badge">
  <img alt="skills.sh Compatible" src="https://img.shields.io/badge/skills.sh-Compatible-1888c8?style=for-the-badge">
  <img alt="Runtime" src="https://img.shields.io/badge/Runtime-Claude%20Code%20%C2%B7%20Codex%20%C2%B7%20Cursor%20%C2%B7%20OpenClaw%20%C2%B7%20Hermes-7b2bd9?style=for-the-badge">
</p>

<p align="center">
  公众号 / 小红书 / B站 / 知乎：<strong>空格的键盘</strong> ｜ <a href="mailto:wzfh520@gmail.com">wzfh520@gmail.com</a>
</p>

Creator Buddy 是一套给内容创作者、运营和自媒体作者用的**全栈创作 Skill 工具箱**。

它覆盖三个平台的创作全流程——**公众号、小红书、视频**：从平台情报（搜热点、挖爆款、看评论、拆竞品），到成品产出（起标题、写正文、做配图、剪视频、配音配乐、出封面）。

基于开放的 Agent Skills 协议，可在 Claude Code、Codex、Cursor、OpenClaw、Hermes Agent、CodeBuddy、Workbuddy、Gemini CLI、OpenCode 等兼容 runtime 中运行。

不是让 AI 凭感觉给你编选题，也不是给你一个「一键起号」按钮。

而是先把平台上的真实内容和数据拉回来，再帮你一步步做成能发的东西——**内容永远是你的**。

---

## 三大板块

```text
gzh-Skills/     公众号   ── 搜爆款 · 起标题 · 出配图 · 整篇排版
xhs-Skills/     小红书   ── 定位 · 选题 · 标题 · 正文 · 封面 · 图文 · 复盘
video-Skills/   视频     ── 选题 · 脚本 · 剪辑 · B-roll · 字幕 · 配音配乐 · 封面
```

### 📰 公众号 · `gzh-Skills`

从赛道情报到配图排版。

| Skill | 干什么 |
|---|---|
| `baokuan-article-analysis` | 按赛道/关键词抓公众号爆款，做数据洞察 |
| `gzh-explosive-content-detector` | 每日爆款收录（低粉高阅读、数据增长中） |
| `global-content-search` | 全域内容搜索（小红书/B站/抖音关键词、详情、评论） |
| `baokuan-title-generator` | 科技/AI 领域 10万+ 爆款标题生成、评分、A/B |
| `space-chart-image` | **配图**：10 类图表（流程/架构/思维导图/SWOT…） |
| `space-text-logic-diagram` | **配图**：文本逻辑拆解 → 逻辑关系图 |
| `space-wechat-layout` | **排版**：整篇文章 → 公众号 HTML（一键复制） |

> 三个配图 Skill 都是「用户给内容 → 输出 HTML 或用 Codex/workbuddy 内置出图模型生成图片」。

### 📕 小红书 · `xhs-Skills`

把起号拆成 10 个环节，一个总控串起来。

| Skill | 干什么 |
|---|---|
| `space-xhs-buddy` | **总控台**：判断你卡在哪一环，路由并串工作流 |
| `space-xhs-positioning` | 起号定位：赛道、定位句、人设、内容支柱、冷启动 |
| `space-xhs-hotspot` | 热点选题：拉高互动笔记、判趋势、爆款共性 |
| `space-xhs-title` | 爆款标题：15 种小红书方法批量出候选、评分、合规 |
| `space-xhs-writer` | 笔记正文：7 种笔记类型、标签策略、发布前 14 项体检 |
| `space-xhs-cover` | 封面：Codex 内置生图，3:4，单张或多版测试 |
| `xhs-html` | 图文排版：6+ 张 3:4 单文件 HTML，62 种风格 |
| `space-xhs-image` | AI 信息图：Codex 生图，单图或 6–9 张组图 |
| `space-xhs-account-audit` | 账号体检：八维打分、竞品对标、卡点定位 |
| `space-xhs-note-analytics` | 笔记复盘：六层漏斗归因、多篇横向找规律 |

### 🎬 视频 · `video-Skills`

一条视频从想法到成片的流水线，`space-video` 总控调度。

| Skill | 干什么 |
|---|---|
| `space-video` | **总控/导演**：判断走哪步、路由子技能、成片后复盘 |
| `space-video-topic` | 选题：下载参考去水印 · 逐字稿 · 标题 · 正文 |
| `space-video-transcript` | **链接转字幕**：YouTube/小宇宙/B站/抖音/小红书 → Markdown + SRT，完成后再按需下载源文件 |
| `space-video-script` | 脚本：去 AI 味口播 + 精确到秒分镜 |
| `space-video-edit` | 剪辑：剪口播（删前保后 + 风险分层）+ 成片 |
| `space-video-broll` | B-roll：HTML→确定性 MP4，多风格、Anti-PPT |
| `space-video-broll-sketch` | B-roll：文章转手绘图解，调 Seedance/libtv 生成 |
| `space-video-subtitle` | 字幕：转写 · 断句 · AI 校对 · 烧录 |
| `space-video-audio` | 配音配乐：TTS 旁白 · 找 BGM · 压音混音 |
| `space-video-cover` | 封面：家族气质 + 平台比例 + 高点击缩略图 |

---

## 效果示例

**先做情报**——把平台语境还原出来，而不是泛泛「帮我想 10 个选题」：

```text
用户  ❯ 帮我看看最近 Codex 在小红书上有什么爆款

助手  ❯ 已搜索小红书热门笔记，近 7 天 39 条筛出 10 条高相关：
        1. 低成本玩转 Claude Code：6w+ 互动
        2. Codex 写文献综述：1w+ 互动
        3. 5 分钟安装 Codex：1w+ 互动
        结论：小红书用户不关心「模型多强」，更关心怎么装、怎么省钱、
        怎么避坑、普通人能不能用、能不能马上做 PPT/论文/剪视频。
```

**再做成品**——从选题继续做到能发的东西：

```text
用户  ❯ 把这篇文章做成一支手绘图解 B-roll，垫在口播下面

助手  ❯ 已抽取原文 5 张配图 → 拆成 8 帧分镜（放射/流程/结论卡）
        → 逐帧生成手绘线稿静帧 → 调 Seedance 做「手绘生长」动效
        → 硬切拼接 + 无人声氛围乐压低 → broll_final.mp4（4:3，48s）
```

---

## 安装

Creator Buddy 基于开放的 Agent Skills 协议，可在任何 skills-compatible 的 AI agent runtime 中运行。

### 方式一：一行命令（推荐，跨 runtime）

打开你正在用的 agent，告诉它：

```text
帮我安装这个 skill：https://github.com/SpaceZephyr/creator-buddy
```

或者用通用 CLI 安装器（vercel-labs/skills，支持多 runtime）：

```bash
npx skills add SpaceZephyr/creator-buddy
```

它会自动识别当前 runtime 并放到正确目录。需要指定时加 `-a codex` / `-a claude-code` / `-a cursor`。

### 方式二：手动安装

克隆仓库，把需要的 skill 目录复制到你的 runtime skills 目录：

```bash
git clone https://github.com/SpaceZephyr/creator-buddy.git
```

仓库结构：

```text
gzh-Skills/       公众号：搜索分析 + 标题 + 配图
xhs-Skills/       小红书：起号全流程（10 个 Skill）
video-Skills/     视频创作：选题→脚本→剪辑→B-roll→字幕→配音→封面
```

每个子目录都是一个独立 Skill（一份 `SKILL.md` + 可选脚本/references）。

### 方式三：作为参考资料使用

即使 runtime 不支持自动加载，也可以直接打开对应目录的 `SKILL.md`，把内容粘贴进对话。

---

## 使用

装好后，直接用自然语言告诉 agent：

```text
帮我搜一下小红书最近 Codex 的热门笔记
查一下公众号里 AI Agent 相关爆款
这篇文章帮我起 10 个爆款标题，标好方法和风险
把这段内容做成公众号配图
帮我把这条口播视频从头做到发：选题、脚本、剪辑、字幕、配乐、封面
把这个 YouTube / 小宇宙 / B站 / 抖音 / 小红书链接提取成字幕
给这篇文章做一支手绘图解 B-roll
```

也可以手动运行脚本，例如公众号赛道分析：

```bash
python3 gzh-Skills/baokuan-article-analysis/scripts/daily_sector_trends.py \
  --sector "AI Coding=Codex,Claude Code,AI编程" --days 7 --output-dir ./reports
```

---

## 工作原理

Creator Buddy 不是一个单一爬虫，而是一组内容创作 Skill，分两半：

| 半 | 做什么 |
|---|---|
| **情报** | 通过 Redfox、Agent Reach、OpenCLI、bili-cli、公开 API 等读取公开内容 → 去重排序评分 → 出结构化报告 → 让 Agent 提炼选题方向 |
| **产出** | 把选题继续做成标题、正文、配图、排版、视频、字幕、配乐、封面。配图/视频优先用 Codex/workbuddy 内置出图模型或本地确定性渲染 |

其中 `global-content-search` 的访问顺序是 Agent Reach 优先、Guaikei API 兜底（小红书需 `GUAIKEI_API_TOKEN`；B站走 `bili-cli`/公开 API；抖音预留 `DOUYIN_COMMAND` 只读 CLI）。

---

## 适合谁

- **公众号作者**：找近期爆款、判断方向、起标题、出配图、整篇排版
- **小红书运营**：定位、选题、写笔记、做封面图文、账号体检与复盘
- **视频/口播创作者**：选题脚本、剪口播、B-roll 动效、字幕配乐封面
- **自媒体 / 增长团队**：跨平台监控内容趋势、拆爆款、还原用户语境

---

## 风控与安全性说明

Creator Buddy 的定位是公开内容研究与创作辅助，不是账号自动化工具。

- **只读公开数据**：默认只读公开页面、公开 API、只读 CLI 或你本机已授权的只读工具。
- **不做账号动作**：不发帖、点赞、收藏、评论、关注、私信、批量加好友。
- **不绕过限制**：不绕登录、验证码、权限校验、付费墙、平台风控或反爬。
- **凭据不入库**：`GUAIKEI_API_TOKEN`、各类 API Key、Cookie、登录态、`.env`、带 token 的链接都不提交到仓库。
- **本地优先**：需要登录态的访问只在本机工具链完成；配图/视频的出图 Key 也走本地环境变量。
- **低频使用**：评论、详情页、批量搜索易触发限制，建议小批量、低并发、按需采样。
- **分享前脱敏**：公开报告前移除 `xsec_token`、Cookie、邮箱、手机号、后台链接。

---

## 诚实边界

每个创作工具都应该说明自己做不到什么。

- **不是实时后台数据**：平台数据来自公开页面、第三方数据源或入库快照。
- **不替你做账号运营**：不做发帖等写操作，不承诺绕过验证码或风控。
- **热门不等于适合你**：爆款只说明平台上什么在传播，不能替代你的定位判断。
- **AI 出图有上限**：生成式配图/视频可能出错别字或画面瑕疵，交付前需人工检查。
- **小红书受 `xsec_token` 影响**：详情页通常需用搜索结果返回的完整 URL。
- **抖音当前是扩展入口**：仓库只提供接口，需你接入本地只读 CLI。

一个不告诉你边界在哪的创作工具，不值得信任。

---

## 参考与致谢

平台访问、创作方法论和视频/配图能力参考了以下项目：

- [Agent Reach](https://github.com/Panniantong/Agent-Reach)：Agent 操作浏览器/本地环境访问平台内容
- [xiaohongshu-openclaw-skill](https://github.com/um-why/xiaohongshu-openclaw-skill)：小红书搜索、详情、评论工作流
- [SpaceZephyr/design-buddy](https://github.com/SpaceZephyr/design-buddy)：`gzh-Skills` 三个配图 Skill 的原型（图表/逻辑图/公众号排版）
- [HyperFrames](https://github.com/heygen-com/hyperframes)：视频 B-roll 的 HTML→确定性 MP4 渲染思路
- 火山引擎 **Seedance 2.0**（火山方舟 Ark）与 **libtv Agent**：生成式 B-roll 的视频模型通道
- Pluviobyte/rnskill 与 chengfeng-videocut：口播剪辑「删前保后 / 风险分层」等方法论

## 许可证

MIT
