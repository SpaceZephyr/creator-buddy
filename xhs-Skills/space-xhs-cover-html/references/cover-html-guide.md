# 封面 HTML 制作规范（写第一张前必读）

固定画布 **1080×1440（3:4）**，一张封面 = 一个自包含 HTML 文件。基底是 `assets/cover-template.html`。

---

## 一、页面骨架铁律

1. **固定画布**：`html,body{width:1080px;height:1440px}` + `overflow:hidden`。溢出等于交付事故——宁可删字，不许缩到规定字号以下。
2. **纵向 flex 流，禁止用绝对定位堆内容**。body 是 `display:flex;flex-direction:column`，`padding` 就是安全区，`.stage{flex:1;min-height:0}` 吃掉剩余高度，`.handle` 是最后一个流式子元素。
   > 这是旧版模板的真实 bug：`.handle` 用 `position:absolute;bottom:...` 钉在底部，`.stage` 内容一变多就顶下来把账号名压穿。只有背景层（`.rail`、蒙版）才允许绝对定位。
3. **不引外部资源**：不 `<link>` Google Fonts（渲染时可能拉不到导致字体回退、行数变化），不引外链图片。字体只用本机可用的：`PingFang SC` / `Hiragino Sans GB` / `Noto Sans SC` / `Songti SC` / `华文琥珀`。
4. **token 即法律**：颜色、字重、字间距、圆角全写进 `:root`，正文里不出现硬编码色值。改风格 = 只改 `:root`。
5. **一张封面只有一个视觉焦点**：主标题。目录/副标题是解释，不许和主标题抢字号。

---

## 二、品牌 DESIGN.md → 封面 token 的「放大映射」

这是本 skill 最容易做错的一步。品牌规范是给 **网页**（正文 16px、标题 40–80px）写的；封面主标题要 **100–150px**，是网页的 2–3 倍。

### 抄什么、不抄什么

| DESIGN.md 里的东西 | 怎么处理 |
|---|---|
| `colors.*` 十六进制值 | **原样抄**。canvas / ink / accent 直接映射，不许四舍五入 |
| `typography.*.fontSize` | **不要抄绝对值**。只抄层级"比例"：display-xl : body ≈ 4.5:1 → 封面 t1 : t3 也走这个数量级 |
| `fontWeight` | **原样抄**。Linear 600、Stripe 300、Nike 900——字重是品牌辨识度的大头 |
| `letterSpacing` | **换算成 em 再抄**。规范写 `-3.0px @ 80px` → `-0.0375em` → 126px 主标题上就是 -4.7px |
| `lineHeight` | **原样抄**（本来就是无单位比例）。中文再放宽 0.05–0.1 |
| `radius` / `borderRadius` | 原样抄，映射到 `--radius`（胶囊标签、卡片式目录） |
| `shadow` | 封面上**基本不用**。缩略图看不见阴影，只会让文字发灰 |
| 装饰母题（渐变条/网格/细线/三角） | 挑 **1 个** 复刻，做成识别锤，别全上 |

### 映射清单（拉到 DESIGN.md 后逐项填）

```
--canvas    ← colors.canvas（浅色风格）或 colors.surface-1（深色风格）
--canvas-2  ← colors.surface-1 / surface-2；品牌不用渐变就写成和 --canvas 相同
--ink       ← colors.ink
--ink-2     ← colors.ink-muted
--ink-3     ← colors.ink-subtle
--accent    ← colors.primary（**必须过对比度检查，见下**）
--on-accent ← colors.on-primary
--hairline  ← colors.hairline
--title-weight   ← typography.display-xl.fontWeight
--title-tracking ← display-xl.letterSpacing ÷ display-xl.fontSize，写成 em
--title-leading  ← display-xl.lineHeight（中文 +0.05）
--radius    ← 品牌卡片/按钮圆角
--font/--font-display ← 品牌字体多半是自有字体拿不到，用本机中文字体替代，
                        但保留"衬线 vs 无衬线""是否超粗"的气质判断
```

### 对比度硬闸门（品牌色不是免罪符）

品牌 primary 大多是给小面积按钮设计的，放到封面上常常不够。**规则优先级：小红书可读性 > 品牌还原度。**

```bash
python3 scripts/check_contrast.py --tokens cover.html
```

- 主标题主体色 vs 背景 **≥ 7:1** —— 不达标就换 `--ink`，不许妥协。
- `--accent` 作为**标题里的强调词** ≥ 4.5:1 即可（它和 7:1 的主体字同字号并列，形状本身给了可读性）。
- `--accent` 作为**唯一承载信息的大字**（整行标题都是 accent 色）→ 按 7:1 要求。
- 目录条目 / 副标题 ≥ 4.5:1。
- 品牌色不达标时的正确做法：**加深同色相**（HSL 保持 H/S，降 L）而不是换个色相。例：Claude 赭石 `#CC785C`（3.0:1）→ `#A34527`（5.6:1），气质不变、达标。
- 渐变底色算对比度时取**对比最差的那一端**，别用平均值。

---

## 三、字号与行数（1080×1440 基准）

| 层级 | token | 字号 | 字重 | 约束 |
|---|---|---|---|---|
| 主标题 | `--t1` | **100–150px** | 品牌 display 字重（≥700 优先） | ≤3 行、≤18 字、每行 6–9 字 |
| 副标题 | `--t2` | **56–72px** | 600 | ≤2 行、≤24 字 |
| 目录条目 | `--t3` | **48–60px** | 600 | 3–5 条，每条 ≤12 字 |
| 标签/角标/账号名 | `--t4` | **36–48px** | 700 | 各 ≤8 字 |

**下限红线**：主标题任何时候 **≥ 90px**。不重要到能小于 36px 的字，直接删掉，别当装饰。

字数与字号联动（主标题）：

| 主标题字数 | 建议 `--t1` | 行数 |
|---|---|---|
| ≤6 字 | 150px | 1–2 |
| 7–10 字 | 132px | 2 |
| 11–14 字 | 118px | 2–3 |
| 15–18 字 | 104px | 3 |
| >18 字 | 砍字，不是缩字号 | — |

**手动断行**：中文标题一律用 `<br>` 显式断行，按语义断（"内容生产的 / 五步" 而不是 "内容生产 / 的五步"）。别指望浏览器自动换行断在对的地方。

---

## 四、深色风格的额外注意

Linear / Vercel / Tesla / NVIDIA / Spotify 这类深色品牌在小红书信息流里**很吃香**（一片白花花的双列里最跳），但：

- 深色底 + 浅字的对比度天然容易过 7:1，重点反而是**别让 accent 发光过头**：霓虹色（`#76B900`、`#1ED760`）在缩略图里会糊成一团，只用在小面积（序号、细线、标签），不要用作主标题主体色。
- 深色底必须是**真的深**（L ≤ 12%），中灰底（#333 上下）既不够对比又显脏。
- 深色封面别加大面积渐变光晕，缩略图里只会变成一块灰雾。`--canvas-2` 与 `--canvas` 差值控制在 6% 明度内。

---

## 五、每张出图后的自查清单

- [ ] 尺寸正好 1080×1440
- [ ] 无溢出、无重叠（尤其账号名与目录最后一条）
- [ ] `check_contrast.py --tokens` 全绿
- [ ] `--guides` 渲染一张：所有文字在 左80/上100/下200 的框内
- [ ] `--scale 0.24` 缩略图：主标题一眼读全
- [ ] 强调只有 1 处、信息层级 ≤3 层
- [ ] 颜色/字重/字间距与 `design-tokens.md` 记录一致
- [ ] 无外链资源（离线打开效果一致）
