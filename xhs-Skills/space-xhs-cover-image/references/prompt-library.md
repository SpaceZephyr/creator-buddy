# Prompt 模板库（简约手绘 × Notion 风 × 白底 × PPT 排版）

所有模板共用一个 **BASE 块**。BASE 定义"这个账号长什么样"，模板定义"这张图讲什么"。
**同一组图里 BASE 必须逐字相同**——这是组图视觉一致性的唯一来源，比任何后期调整都有效。

---

## 一、BASE 块（每个 prompt 的开头，必抄）

```
A minimalist hand-drawn illustration in the style of clean Notion-like editorial
graphics. Pure white background (#FFFFFF), flat, no gradient, no paper texture,
no vignette, no drop shadows. Single-weight black ink line art (#1A1A1A) with a
slight hand-drawn wobble, as if sketched with a fine marker. Generous negative
space. Everything aligned to an invisible grid, laid out like a well-designed
presentation slide: one clear focal element, clear visual hierarchy, calm and
uncluttered. At most ONE accent color used sparingly for emphasis: {ACCENT}.
Vertical 3:4 portrait composition. Keep the outer 8% margin on left and right,
the top 7%, and the BOTTOM 15% of the canvas as empty white space with no
content. No photorealism, no 3D render, no heavy shading, no busy background
patterns, no watermark, no logo, no border frame around the canvas edge.
```

`{ACCENT}` 从下表选 **一个**，写进账号模板后就别再换：

| accent | hex | 气质 | 适合赛道 |
|---|---|---|---|
| warm orange | `#E8734A` | 暖、有活力、不吵 | 生活方式、效率、个人成长 |
| muted blue | `#4A7FB5` | 理性、可信 | 职场、工具、知识科普 |
| sage green | `#6B9B7A` | 松弛、自然 | 健康、饮食、家居 |
| dusty pink | `#D98BA0` | 柔、女性向 | 美妆、情感、穿搭 |
| ochre yellow | `#D9A441` | 明亮、提示感 | 清单、避坑、干货 |
| ink only | 无 | 最克制、最像 Notion | 严肃内容、技术、长期主义账号 |

**为什么只给一个 accent**：缩略图状态下，两个以上强调色 = 没有强调色。

---

## 二、封面模板（首图，KPI = 点击率）

### C1 · 单主体符号封面 —— 大留白 + 一个符号

**适用**：观点输出、单一概念、个人故事。内容说不清但情绪很强的时候用这个。
**文字策略**：底图无字 → 交 `space-xhs-cover-html` 叠字（推荐）；或只画 1 个英文短词。

```
{BASE}
Composition: a single hand-drawn symbol placed in the upper-center of the frame,
occupying about 40% of the canvas width. The symbol is {SYMBOL}. Everything else
is empty white space. No text anywhere in the image.
```

`{SYMBOL}` 举例：`a half-open cardboard box with one item floating out`（断舍离）、
`a tangled ball of yarn with one thread pulled straight out`（理清思路）、
`a small figure standing at a fork of two paths`（选择）。
**写法要点**：符号要能一句话说清、能画成线稿、和内容有直接隐喻关系。别写抽象名词（"growth"、"freedom"），模型会画出一堆糊的东西。

---

### C2 · 图标网格封面 —— PPT 式 2×2 / 2×3

**适用**：工具合集、多品类清单、"N 个 XX"。收藏率高。
**文字策略**：格子里的标签建议留空 → HTML 叠字。非要模型画就只画英文/数字。

```
{BASE}
Composition: a {2x2 | 2x3} grid of evenly spaced cells occupying the middle 60%
of the canvas, generous gutters between cells. Each cell contains one simple
hand-drawn line icon, centered, all icons the same visual weight and same line
thickness. Icons: {ICON1}, {ICON2}, {ICON3}, {ICON4}. Below each icon leave an
empty horizontal band of white space for a caption to be added later. No text
anywhere in the image.
```

**要点**：图标数量写死（4 或 6），别写"several"。所有图标一次生成（同一张图里），不要分别生成再拼——分开生成线条粗细必然对不上。

---

### C3 · 人物场景封面 —— 极简小人

**适用**：个人经历、职场故事、生活状态、"我踩过的坑"。人物比符号更有代入感。

```
{BASE}
Composition: a minimal hand-drawn figure (simple line-art person, no facial
detail beyond two dots and a small line, gender-neutral, no specific real
person) shown {ACTION}, placed in the lower-left third of the canvas. A few
sparse contextual props around them: {PROPS}. The upper half of the canvas is
left as empty white space. No text anywhere in the image.
```

`{ACTION}` 例：`sitting cross-legged in front of a laptop`、`carrying a stack of boxes that is slightly too tall`。
**红线**：绝不要求生成特定真人/明星/网红的形象。

---

### C4 · 对比封面 —— 左右分栏

**适用**：踩坑 vs 正解、before/after、平替对比。
```
{BASE}
Composition: the canvas is split into two vertical halves by a single thin
hand-drawn vertical line down the middle. Left half: {LEFT_SCENE}, drawn with
slightly loose, messy lines. Right half: {RIGHT_SCENE}, drawn with clean, tidy
lines, and the {ACCENT} color used only on this side. Both scenes are simple
line icons of the same size, vertically centered. No text anywhere in the image.
```
**要点**：让"乱 vs 整"通过线条质感表达，而不是靠文字标注。这是这类图能不能免文字的关键。

---

### C5 · 流程封面 —— 竖向步骤

**适用**：教程、方法论、"三步搞定"。3:4 竖版天然适合竖向流程。
```
{BASE}
Composition: {N} simple hand-drawn line icons stacked vertically down the center
of the canvas, evenly spaced, connected by short downward arrows. Icons from top
to bottom: {ICON1}, {ICON2}, {ICON3}. To the right of each icon, leave an empty
white band for a caption to be added later. Numbers 01, 02, 03 drawn in thin
line style to the left of each icon. No other text in the image.
```
**要点**：`01/02/03` 是阿拉伯数字，模型画得住，可以让它画。其余中文留空叠字。

---

### C6 · 单物件特写 —— 手绘"实物"

**适用**：好物分享、单品种草、书影音。替代真实拍照，不涉及版权和真人肖像。
```
{BASE}
Composition: one object drawn large and centered in the upper two-thirds:
{OBJECT}, hand-drawn line art with light {ACCENT} color fill on one or two
areas only. A few short motion/emphasis strokes around it. Bottom third empty
white. No text anywhere in the image.
```
**红线**：不要求复刻具体品牌的产品外观、包装、Logo。写品类（"a wide-mouth insulated bottle"），不写品牌名。

---

## 三、内容图模板（内页，KPI = 留人 / 价值兑现）

内页在**全屏详情页**被看，允许比封面小的字和更密的信息——别用封面的字号红线限制内页。

### P1 · 图解卡（一张图讲一个概念）
```
{BASE}
Composition: laid out like a single clean presentation slide. An empty title band
across the top 20% of the canvas (leave it white, no text). In the middle, a
{concept diagram | 2x2 matrix | layered stack | radial map} made of simple
hand-drawn line shapes: {STRUCTURE}. Leave a small empty white band next to each
node for labels to be added later. Bottom 15% empty white.
```

### P2 · 清单页（3–5 条）
```
{BASE}
Composition: {N} horizontal rows evenly stacked in the middle 65% of the canvas.
Each row: a small hand-drawn line icon on the left ({ICON1}, {ICON2}, {ICON3}),
then a wide empty white band to its right reserved for a text line. Thin light
gray hairline separators between rows. Top 20% and bottom 15% empty white.
```

### P3 · 引用页 / 金句页
```
{BASE}
Composition: an oversized hand-drawn opening quotation mark in {ACCENT} in the
upper-left area, and a large empty white area beneath it reserved for a quote to
be typeset later. One tiny decorative line flourish in the lower-right. No text.
```

### P4 · 结尾页（关注 / 收藏引导）
```
{BASE}
Composition: a minimal hand-drawn figure waving, small, in the lower-center. Above
them, a large empty white area reserved for text. Three tiny hand-drawn icons in
a row near the bottom: a bookmark, a heart, a plus-sign in a circle, all in thin
line style, {ACCENT} on the bookmark only. No text.
```

---

## 四、变体与迭代话术

改图时**只改一个变量**，其余逐字保留。改多个变量出来的图没法归因，会来回打转。

| 症状 | 往 prompt 里追加 |
|---|---|
| 背景发灰 / 有纸纹 | `flat pure white #FFFFFF background, no texture, no paper grain, no vignette` |
| 线条太粗糙 / 像油画 | `thin consistent 3px ink line weight, vector-like clarity` |
| 颜色太多 | `strictly two colors total: black ink and {ACCENT}. No other hue anywhere.` |
| 太挤 | `at least 45% of the canvas must remain empty white space` |
| 主体太小 | `the main subject occupies 45% of the canvas width, centered` |
| 加了看不懂的字 | `absolutely no text, no letters, no numbers, no glyphs, no signage anywhere` |
| 下方被塞满 | `the bottom 15% of the canvas is completely empty white` |
| 加了边框 | `no border, no frame, the illustration bleeds to the canvas edges` |
| 组图风格飘 | 检查 BASE 是否逐字一致；用第一张作 `--ref` 参考图 |

**组图一致性做法（按有效性排序）**：
1. BASE 块逐字复用 + accent 写死 hex
2. 用已通过的第一张做 `--ref` 参考图（baoyu-image-gen 的 `--ref` 走 Google 多模态或 OpenAI edits）
3. 同一批一次跑完，不要隔天补图（模型版本可能变）
