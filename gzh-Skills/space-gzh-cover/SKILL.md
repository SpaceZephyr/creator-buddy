---
name: space-gzh-cover
description: 制作微信公众号 2.35:1 头图封面，使用 Codex 内置 image_gen 生成，视觉沿用「轻盈 AI 产品信息图」系统（白/浅薰衣草底、墨黑大标题、科技紫与青柠绿强调、圆角卡片、线性图标）。内置分享安全区校验——公众号封面分享到朋友圈时只保留正中央 1:1 方形，本 Skill 负责让标题不被切掉。用户说"做公众号封面""做头图""文章配首图""2.35:1 封面""公众号封面图""做几版封面"时触发。
---

# 公众号封面制作（2.35:1）

把一篇文章变成一张头图。默认 Codex 内置 `image_gen`，视觉沿用本仓库 `xhs-Skills/space-xhs-image` 的**轻盈 AI 产品信息图**系统，画幅换成公众号的 2.35:1。

本 Skill 只做头图。正文配图走 `space-chart-image` / `space-text-logic-diagram`，整篇排版走 `space-wechat-layout`。

---

## 最重要的一条：公众号封面会被裁两次

这是它和小红书 3:4 封面**最根本的区别**，先记住再动手。

| 场景 | 显示 |
|---|---|
| 订阅号消息列表 / 文章顶部 | 完整 2.35:1 |
| **分享到朋友圈 / 聊天** | **只抓取正中央的 1:1 方形** |

在 2.35:1 的画布上，正中央那个方形只占**宽度的 42.6%**。

```
|←── 左翼 28.7% ──→|←── 中央安全区 42.6% ──→|←── 右翼 28.7% ──→|
      分享时切掉            分享时唯一保得住的         分享时切掉
```

以推荐画布 1175×500 为例，安全区是 **x 337–837 这 500px**。

**实测后果**：一个 12 字标题铺满全宽，分享出去只剩中间 6 个字，首尾两字还被切一半，完全读不通。

**所以**：主标题的核心词组、主体、必须被看到的东西，**一律放进中央安全区**。左右两翼只放背景延伸、装饰、账号名、日期这类丢了也不影响的东西。

> ⚠️ **反直觉的地方**：横版画幅的设计直觉是"左右分栏"——文字在左、图在右。但在公众号封面上，**任何把信息平均分到左右两侧的版式都是陷阱**，因为分享时正好把两侧全切掉、只留中间。详见 `references/cover-layouts.md` 里每个版式的分享安全性评级。

---

## 默认设置

用户没指定时直接用，不为常规选项反复追问：

- 画幅：**2.35:1 横版**
- 成品：**1175 × 500 PNG**
- 数量：1 张
- 视觉系统：轻盈 AI 产品信息图（见下方 Style Lock）
- 文案：1 个主标题，可选 1 个短标签
- **主标题：6–14 个汉字，最多 2 行**（横版高度有限，3 行必挤）
- 标签：不超过 8 个汉字，放胶囊里
- 视觉顺序：主标题 → 强调词 → 装饰
- 安全区策略：核心词组必须落在中央 42.6%

用户说"直接做""你来定"时，直接作出合理选择并生成，不暂停等待。

---

## 三种安全区策略

| 策略 | 做法 | 分享效果 | 适合 |
|---|---|---|---|
| **A 全居中** | 标题全部塞进中央安全区，≤12 字分 2 行 | 完整无损 | 靠分享传播、追求稳的号 |
| **B 核心词居中**（默认） | 标题横向铺开，但把最关键的 4–6 字词组压在正中 | 核心词完整，修饰词被切 | 大多数情况 |
| **C 图文分离** | 中央放主体/图形，文字在两翼 | **分享后没有文字** | 只在文章顶部展示、不指望分享 |

**默认走 B。** 选 B 时必须明确指出"哪几个字是核心词组"，并在检查阶段验证它们在安全区内。

**C 要主动提醒风险**，用户确认了再做。

---

## 视觉系统（Style Lock）

沿用 `xhs-Skills/space-xhs-image/references/visual-system.md` 的色板与组件，画幅改为横版。

**色板**（与小红书系列保持一致，跨平台视觉统一）：

- 墨黑 `#181A24` —— 标题正文
- 科技紫 `#6C35E8` —— 编号、线条、重点词
- 电光蓝 `#4563F2` —— 紫的过渡色
- 青柠绿 `#A4E927` —— 结果、提升、关键动作
- 浅薰衣草 `#F1ECFF` / 浅蓝 `#EEF3FF` —— 卡片底
- 背景 `#FCFBFF` / `#FAFAFD` / 纯白

比例约 72% 白/浅底、18% 黑字线条、10% 彩色强调。单张最多三个强调色。

**横版专属的比例调整**（与竖版不同，务必按这套）：

- 外边距：左右约 5%–7%，上下约 10%–14%（横版上下更紧）
- 主标题高度：占画布高度 **28%–42%**
- 装饰簇：最多 **2 组**（竖版是 3 组，横版更扁，3 组必乱）
- 留白：≥ 30%

**Style Lock（生图时逐字复用）**：

```text
Create an original premium AI-product cover banner for a WeChat article in a 2.35:1 ultra-wide horizontal canvas. Use a clean white to very pale lavender background with generous margins and breathable negative space. Place the headline and all critical content inside the central square safe area (the middle 42.6% of the width), because this banner gets center-cropped to 1:1 when shared. Use modern simplified-Chinese sans-serif typography in near-black, with only one or two key phrases highlighted by a controlled violet-to-electric-blue gradient or vivid lime green. Optional supporting elements use large white rounded cards with subtle lavender-gray shadows. Use coherent thin rounded line icons related to software, workflow, documents, checklists, targets, and AI. Keep decorations sparse and confined to the left and right wings. The result should feel polished, calm, and instantly readable at small size in a message list.
```

**固定负向约束**：

```text
Do not copy any reference image layout. No copied creator name, no logo, no watermark, no signature, no fake interface screenshot, no garbled text, no invented Chinese characters, no long paragraphs, no tiny dense type, no photorealism, no glossy 3D mascot, no childish stickers, no heavy black shadows, no dark full-bleed background, no excessive decoration, and no critical text placed near the left or right edges.
```

---

## 工作流

### 1. 理解文章

读完内容，提取三件事：

- 读者最该记住的一句话
- 哪个词最能制造识别或兴趣（**这个词就是要压在安全区正中的**）
- 有没有适合成为画面主体的对象

### 2. 定标题

用户给了标题就保持原意。只给正文时，给 3 个短标题候选并推荐 1 个。

**横版标题规则**（比竖版更严）：

- 总长 6–14 字，最多 2 行
- **先圈出核心词组（4–6 字）**，这部分必须在安全区
- 一行只承载一个语义块，不要在词组中间断行
- 中英混排时保留完整英文词组不拆
- 标点尽量省

> 封面标题不等于文章标题。文章标题可以长、可以有钩子；封面标题要短、要能被一眼扫到。需要爆款文章标题走 `baokuan-title-generator`。

### 3. 选版式

从 `references/cover-layouts.md` 挑，**每个版式都标了分享安全性评级**。推荐 2–3 个方向并说明差异。

同一批变体保持标题和主体一致，可以改：构图、配色权重、装饰系统、背景处理。**不要只换个颜色就算一版**。

### 4. 生成

用 `references/prompt-recipes.md` 组装提示词。必须写明：

- `Use case: ads-marketing`
- 2.35:1 横版公众号头图
- 需要出现的文字**逐字列出**
- **哪几个字必须在中央安全区**
- 构图、配色、字体气质、装饰位置
- 缩小到消息列表尺寸仍要清楚
- 禁止新增水印、账号名、品牌、无关文字

一次 `image_gen` 调用只生成一个变体。要 3 张就调 3 次，每张写明差异。

### 5. 检查（两道，都不能跳）

**第一道：机器检查**

```bash
python3 scripts/check_cover.py 路径/cover-01.png --safe-zone --share-preview --thumbnail
```

它会输出：
- 比例是否 2.35:1、尺寸、体积
- 安全区的确切像素范围
- `-safezone.jpg`：把左右两翼压暗、安全区画红框，**一眼看出标题有没有越界**
- `-share-1x1.jpg`：分享到朋友圈实际长什么样
- `-thumb.jpg`：信息流缩略图

**第二道：肉眼检查**（机器查不了这些）

- 主标题是否逐字正确，有没有乱码、错字、多余文字
- **打开 `-share-1x1.jpg`：核心词组还读得通吗？**
- 打开 `-thumb.jpg`：2 秒内能读懂吗
- 主标题是否第一视觉
- 人脸、产品、关键标识是否完整
- 留白够不够，四边有没有安全边距
- 色板、圆角、线宽是否与本系列其他图一致

**分享预览读不通，就是不合格**，不管完整图多好看。

### 6. 修正

只有局部问题就定向编辑，不要整张重做：

> 仅把主标题第二行"Agent 接管 SaaS"整体向左移约 8%，使其完全落入画面正中央的方形区域；其他文字、构图、颜色和装饰全部保持不变。

同一段文字连续两次仍生不对时：

1. 先把文字压短再试一次
2. 仍不行则生成**无字底图**并预留明确标题区，告知用户文字将以可编辑方式叠加
3. 转 `space-wechat-layout` 或外部工具做逐字准确的文字层

**不要把有错字的图当成品交付。**

### 7. 保存与交付

```text
09 frames/gzh-cover/YYYY-MM-DD-主题/
├── cover-01.png
├── cover-01-safezone.jpg
├── cover-01-share-1x1.jpg
└── prompt.md
```

只生成一张时仍叫 `cover-01.png`。已有同名文件用 `-v2`，**不得静默覆盖**。生图结果若在临时目录，必须复制到项目目录再交付。

交付时给出：

- 成品绝对路径和可点击链接
- 实际尺寸与比例
- 采用的版式和安全区策略（A/B/C）
- **核心词组是哪几个字、是否验证在安全区内**
- 多版时说明每版差异
- 有限制直接说明

---

## 内容与视觉边界

- 不自动添加用户未要求的账号名、水印、二维码、平台标识
- 参考图只提取通用的布局、配色、材质、字体气质，不复制品牌签名、人物身份、专属角色
- 不捏造功效、收益、排名、专业背书
- 金融、医疗类主题不把免责声明塞进封面，提醒用户在正文补
- 未经要求不生成真人肖像或品牌商标

---

## 快速示例

用户说：

> 帮我做一张"Agent 接管 SaaS 时代已开启"的公众号封面。

执行：

1. 圈核心词组：**「接管 SaaS」**（4 字 + 1 英文词）
2. 标题拆行：`Agent 接管 SaaS` / `时代已开启`
3. 选版式：中央大字（分享安全性 ★★★）
4. 策略 B：核心词组压正中，`Agent` 和 `时代已开启` 允许溢出到两翼
5. 生成 1175×500，紫→蓝渐变只落在「接管」二字
6. 跑 `check_cover.py --safe-zone --share-preview`
7. 确认分享预览里「接管 SaaS」完整可读

---

## 与本仓库其他 Skill 的配合

| 场景 | 转到 |
|---|---|
| 要起文章标题 | `baokuan-title-generator` |
| 要正文配图 / 图表 | `space-chart-image` / `space-text-logic-diagram` |
| 要整篇排版 | `space-wechat-layout` |
| 要小红书 3:4 封面 | `xhs-Skills/space-xhs-cover` |
| 视觉系统原始定义 | `xhs-Skills/space-xhs-image/references/visual-system.md` |
