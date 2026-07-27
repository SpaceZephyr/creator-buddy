# XHS Skills — 小红书全流程 Agent Skills

把小红书运营拆成 8 个环节，每个环节一个 Skill，外加一个总控把它们串起来。

**不是"一键起号"按钮。** 只做分析和参谋：不自动发布、不抓取批量数据、不刷互动、不做批量起号和矩阵养号。内容永远是你的。

## 9 个 Skill

| Skill | 干什么 | 需要 Key |
|---|---|:---:|
| `space-xhs-buddy` | **总控台**：判断你卡在哪一环，路由并串成工作流 | — |
| `space-xhs-positioning` | 起号定位：赛道选择、定位句、人设三件套、内容支柱、前 20 篇、冷启动 | — |
| `space-xhs-hotspot` | 热点选题：拉高互动笔记、判趋势、爆款共性提取、跨赛道对比 | ✅ |
| `space-xhs-title` | 爆款标题：15 种小红书方法批量出候选、评分、合规校验、A/B 建议 | — |
| `space-xhs-writer` | 笔记正文：7 种笔记类型、标签策略、合规改写、发布前 14 项体检 | — |
| `space-xhs-cover-html` | 封面（**排版型**）：大字+目录 / 大字+副标题，品牌风格驱动，精确渲染 | — |
| `space-xhs-cover-image` | 封面与内页（**画面型**）：AI 生图，白底简约手绘 + Notion 风 | ✅ |
| `space-xhs-account-audit` | 账号体检：八维打分、竞品对标、卡点定位 | 可选 |
| `space-xhs-note-analytics` | 笔记复盘：六层漏斗归因、多篇横向找规律 | — |

## 安装

```bash
git clone https://github.com/SpaceZephyr/creator-buddy.git
cp -r creator-buddy/xhs-Skills/space-xhs-* ~/.claude/skills/
```

装完在 Claude Code 里说「帮我做小红书」会自动路由到总控，或直接点名环节，比如「帮我看看这条笔记数据」。

## 配置（可选）

5 个 Skill 零配置可用。需要真实平台数据时配置任一：

```bash
export REDFOX_API_KEY=...        # https://redfox.hk        近 30 天爆款库，带三维评分
export SOCIALDATAX_API_KEY=...   # https://socialdatax.com  近实时搜索
export GUAIKEI_API_TOKEN=...     # https://www.guaikei.com  详情 + 评论 + 博主作品，拆号必需
```

`hotspot` 和 `account-audit` 会**运行时探测并逐级降级**，三个都没有时走公开搜索兜底 —— 仍能跑完流程，只是拿不到互动数，且会明确标注"未经数据验证"，不靠猜补齐。

生图版封面另需后端，跑 `bash space-xhs-cover-image/scripts/detect_backend.sh` 一键探测。

## 三条标准工作流

```
链 A 从零起号   positioning → hotspot → writer → title → cover-html → 发布
                              ↳ 累计 20-30 篇后回 account-audit 复诊

链 B 日常产出   hotspot → writer → title → cover-html

链 C 诊断改进   note-analytics 定位卡在漏斗哪一层
                  ├ 曝光就低      → account-audit（标签/定位/权重）
                  ├ 曝光够 CTR 低 → title + cover-html
                  └ 点击够互动低  → writer（开头留人/价值兑现）
```

**链 C 的顺序不能反。** 跳过诊断直接改标题是最常见的浪费 —— 曝光就低的时候，标题不是问题。

## 两个封面 Skill 怎么选

- **默认 `cover-html`**：小红书大多数首图本来就是"大字 + 目录/副标题"。HTML/CSS 排版中文零错字、字号对比度安全区全部可量化、可固化成账号模板批量改字。
- **需要插画/手绘/氛围时用 `cover-image`**。
- **最强是两个一起用**：`cover-image` 出无字底图（prompt 预留文字区）→ `cover-html` 精确叠字。AI 画中文经常缺笔画串行，别让它画标题。

## 设计上的几个取舍

**合规优先于爆款。** 小红书的违规惩罚通常是**限流**而非删帖 —— 你看得见自己的笔记，但没有推荐流量，最难自查。所以功效词、绝对化用语、医疗表述在动笔阶段就拦，不等发布前体检。`writer` 里有一张高危词对照替换表，总原则是「把客观断言改写成主观体验」。

**规则要能约束生成本身，而不只是写给人看。** 例：`title` 的红线规定正文不是 step-by-step 就不许用"保姆级"—— 哪怕"保姆级"是这个赛道点击率最高的钩子，它也会把这类候选直接淘汰。

**纪律尽量写进代码。** `note-analytics` 的脚本会自动拒绝 n<3 分组的比较、在均值/中位数 >2 时告警"别引用平均值"；`cover-html` 的渲染脚本会检测内容溢出并支持 `--strict` 非 0 退出。写在文档里模型可能不看，写进代码就绕不过去。

**不编造。** 没有数据源就不报互动数字，没有对标笔记就不给选题，接口拿不到粉丝数就标"无法计算"而不是估算。

## 已知限制

- `hotspot` 的 `compare_sets.py` 高频词统计用的是 n-gram 滑窗（无中文分词依赖），会有切片噪音；形态分类在部分赛道命中率低。
- `cover-image` 的 codex 路线未经实测（作者机器未安装），文档里**故意没有给具体命令**，只写了"先探测再确认参数"。
- 所有第三方数据服务均为付费，按量计费，与本仓库无关联。

## 许可与免责

数据来源于第三方服务收录的公开笔记，版权归原作者所有，仅供学习和创作参考。使用者需自行遵守小红书平台规则。
