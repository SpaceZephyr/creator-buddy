# 风格注册表（小红书多页图文适配版）

风格规范来自 `getdesign`：`npx -y getdesign@latest add <slug>` 会在当前目录生成 `DESIGN.md`（含精确 colors / typography / radius / shadow）。**本机实测可用**（无需 API Key，需联网 + Node）。

拉不到时用 `references/style-presets.md` 的 12 套离线 token 兜底。

---

整组图文只选一套主风格：所有页面共用颜色、字体气质和圆角，布局可以随内容变化。

## 一、小红书赛道 → 风格推荐

小红书图文不是网页，选风格时**先看赛道人群，再看内容气质**。

| 赛道 / 内容 | 首选 3 个 | 为什么 |
|---|---|---|
| AI 工具 / 效率提效 | `linear.app`、`raycast`、`claude` | 深色科技感在生活类信息流里极其显眼 |
| 职场 / 求职 / 转行 | `notion`、`ibm`、`stripe` | 规整可信，不轻浮 |
| 学习 / 考证 / 知识整理 | `notion`、`mintlify`、`claude` | 纸感暖调，适合长目录 |
| 编程 / 技术教程 | `vercel`、`supabase`、`warp` | 黑底 + 等宽气质，人群自认同 |
| 创业 / 副业 / 商业分析 | `stripe`、`shopify`、`intercom` | 商业感强，数字醒目 |
| 理财 / 记账 / 消费降级 | `wise`、`coinbase`、`stripe` | 明快可信，不土 |
| 穿搭 / 美妆 / 生活方式 | `airbnb`、`pinterest`、`nike` | 暖色摄影气质 / 大字宣言 |
| 探店 / 旅行 / 美食 | `airbnb`、`spotify`、`miro` | 暖色或高饱和，信息流里跳 |
| 健身 / 运动 / 自律 | `nike`、`tesla`、`nvidia` | 高对比大字，力量感 |
| 家居 / 收纳 / 改造 | `apple`、`notion`、`clay` | 克制留白，显得"高级" |
| 情感 / 个人成长 / 随笔 | `claude`、`apple`、`cohere` | 温和人文，不咄咄逼人 |
| 设计 / 创意 / 作品集 | `figma`、`framer`、`runwayml` | 本身就是设计人群的母语 |
| 育儿 / 母婴 | `airbnb`、`lovable`、`miro` | 柔和友好，圆润 |
| 数码测评 / 硬件 | `apple`、`nvidia`、`bmw` | 产品发布会质感 |

**兜底万金油**（内容气质不明显时）：`notion`（暖·稳）、`linear.app`（冷·跳）、`claude`（人文）、`apple`（高级）、`airbnb`（生活）。

---

## 二、全部 slug（62 个）

拉规范时用 slug，不要用中文名。

**科技 / AI**：`apple` `claude` `cursor` `elevenlabs` `figma` `framer` `lovable` `meta` `minimax` `mintlify` `mistral.ai` `notion` `ollama` `opencode.ai` `posthog` `raycast` `replicate` `resend` `runwayml` `sanity` `sentry` `supabase` `superhuman` `together.ai` `vercel` `voltagent` `warp` `webflow` `x.ai` `zapier`

**开发者 / 基础设施**：`airtable` `cal` `clay` `clickhouse` `cohere` `composio` `expo` `hashicorp` `ibm` `intercom` `linear.app` `miro` `mongodb` `nvidia` `pinterest` `stripe`

**金融 / 加密**：`binance` `coinbase` `kraken` `revolut` `wise`

**消费 / 汽车**：`airbnb` `bmw` `ferrari` `lamborghini` `nike` `renault` `shopify` `spacex` `spotify` `tesla` `uber`

> 完整的品牌别名、一句话风格描述、通用匹配标签见
> `~/.claude/skills/space-multi-design-ppt/references/brand-registry.md`（本机已装，同一套 slug）。

---

## 三、哪些风格需要调整后再用于小红书图文

| 风格特征 | 问题 | 怎么救 |
|---|---|---|
| 超细字重（Stripe 300、Shopify 100） | 封面缩到 260px 直接消失 | 字重下限拉到 600，只保留颜色和间距气质 |
| 低对比柔和（Clay、Cohere、Lovable） | 主标题达不到 7:1 | 加深 `--ink`，把柔和留给底色和圆角 |
| 高密度信息（Binance、ClickHouse） | 封面本来就只放 ≤60 字，密度无处施展 | 只取配色，版式按本 skill 的两种形态走 |
| 依赖产品截图 / 摄影（Tesla、Nike、Airbnb 网页版） | 本 skill 不生成图片 | 用大面积色块 + 超大字 + 留白复刻气质 |
| 装饰母题复杂（Figma 多彩、PostHog 插画） | CSS 复刻成本高且缩略图看不清 | 只挑 1 个母题（一条线 / 一个色块），其余留白 |

---

## 四、推荐话术（Step 2 用）

未指定风格时，给用户 **5 + 1**：

```
根据你的内容（AI 工具清单 · 职场人群），我推荐这几种图文风格：

1. Linear — 近黑底 + 薰衣草紫编号，效率工具的高级感，在信息流里最跳
2. Notion — 米色纸感 + 柔和分隔线，像一页笔记，适合长目录
3. Claude — 赭石暖调 + 编辑级排版，温暖不说教
4. Vercel — 纯黑白 + 超大字，锋利、开发者友好
5. Apple — 极致留白 + 居中大字，克制高级

6. 智能匹配 — 我直接按内容气质替你选（含混搭）

回编号或品牌名都行，也可以说其他品牌（共 62 个）。
```

要求：5 个推荐必须**真的和赛道匹配**（美妆内容别推 NVIDIA）；每条一句话说清"选它会得到什么视觉效果"；选「智能匹配」时要**告知选了什么和理由**再开工。
