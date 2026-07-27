# 图上文字策略：什么时候让模型画字，什么时候出无字底图

这是本 skill 最重要的一个决策点。做错了，整张图作废。

---

## 一、先认清生图模型画中文的真实水平

现有主流生图模型（Gemini / GPT-Image / 通义万相）画中文的已知问题：

| 问题 | 表现 | 能不能通过 prompt 修 |
|---|---|---|
| 缺笔画 / 多笔画 | "赛" 少一横、"藏" 多一点 | ❌ 不能，重掷骰子而已 |
| 造字 | 生成不存在的、看着像汉字的字形 | ❌ |
| 串行 / 断行 | 换行位置随机，长句尤其严重 | ❌ |
| 字号不可控 | 说了"大字"也可能出来一行小字 | 部分，靠"occupies 60% of width"这类描述 |
| 位置不可控 | 无法固定角标在右上角 | ❌ |
| 字体不可控 | 无法指定 PingFang / 特定字重 | ❌ |
| 字数越多越崩 | 4 字尚可，12 字基本必崩 | 只能靠减字 |

**一句话结论：中文准确率随字数指数下降，且没有任何可靠的 prompt 手段能兜底。**
所以本 skill 的默认姿势是 **出无字底图**，而不是"试试看能不能画对"。

**重要提醒**：上表是行业内的普遍经验，本机没有可用生图后端，**未在本机实测**。
用户接上后端后，第一次出图应该先跑一次小样验证当前模型的中文水平，再决定放宽多少。

---

## 二、决策树（照这个走，不要凭感觉）

```
图上需要出现文字吗？
├─ 不需要 ────────────────────────→ 路线 A：纯插画（最省事，优先考虑）
└─ 需要
   ├─ 是中文吗？
   │  ├─ 否（英文单词 / 阿拉伯数字 / 符号）
   │  │  ├─ ≤ 2 个单词 or 01/02/03 类编号 ──→ 路线 B：让模型画（可接受）
   │  │  └─ 更长的英文句子 ────────────────→ 路线 C
   │  └─ 是中文
   │     ├─ 这是封面主标题 / 会被人读的信息 ─→ 路线 C：无字底图 + HTML 叠字（默认）
   │     └─ 纯装饰、糊了也无所谓、不承载信息
   │        （远景招牌、书脊上的字、背景涂鸦）→ 路线 B'：允许画，但明确告知用户"这里的字不保证正确"
```

---

## 三、三条路线的具体做法

### 路线 A：纯插画（无文字）

prompt 末尾**必须**加这句负向约束，否则模型会自作主张添字：

```
Absolutely no text, no letters, no Chinese characters, no numbers, no glyphs,
no signage, no watermark, no captions anywhere in the image.
```

出图后肉眼检查一遍：模型仍有一定概率画上字。有字就重出，别将就。

---

### 路线 B：让模型画少量英文/数字

允许的范围（超出就退回路线 C）：
- 单个英文词：`TIPS`、`STEP`、`NEW`、`VS`、`BEFORE` / `AFTER`
- 编号：`01` `02` `03`、`#1`
- 符号：`?` `!` `+` `→`

写法：
```
The word "TIPS" hand-lettered in simple uppercase sans-serif, small, in the
upper-left corner. This is the ONLY text in the image; no other letters,
no Chinese characters, no numbers anywhere else.
```

出图后**逐字核对拼写**（`RECOMMEND` 拼成 `RECCOMEND` 是常见事故）。

---

### 路线 C：无字底图 + `xhs-html` 叠字 ← 默认推荐

这是文字可控性和画面质感的唯一兼得方案。

**做法**：
1. 用本 skill 生成 1080×1440 的无字底图（路线 A 的约束全上），
   并在 prompt 里**预留出文字区**——这是最关键的一步：
   ```
   ... The upper 45% of the canvas is left completely empty white space,
   reserved for text to be added later. All illustration content is confined
   to the lower portion.
   ```
   预留区和后面 HTML 里放标题的位置必须对得上，否则叠出来会压到插画。
2. 跑 `scripts/check_image.py` 确认尺寸、白底、下安全区。
3. 移交 `xhs-html`：把底图保存为本地素材，在目标 `.sheet` 中用 `<img>` 铺底，再用 CSS 网格或定位叠字。
   白底图不需要蒙版；如果底图局部有色块导致对比度不够，那一块加半透明白蒙版。
4. 在 `xhs-html` 中运行 `check_contrast.py` 与 `render_xhs.mjs --strict`，再做缩略图检验。

**移交时要交代清楚**：底图路径、文字预留区的位置和大小（用画布百分比说）、accent 的 hex（HTML 那边要用同一个色，否则两层不像一张图）。

---

### 路线 B'：装饰性中文（允许，但要声明）

只在**这行字糊了完全不影响理解**时用。典型：画面深处的店招、书脊、便签背景纹理。

必须在交付时对用户明说："第 3 张图右下角书脊上的字是装饰，模型可能画错，介意的话我去掉。"
**不要**默默交付一张有错别字的图 —— 用户发出去了才发现，代价是他的。

提高中文准确率的写法（能提高一点，**不保证**）：
- 字数压到 **2–4 个字**
- 字用引号包起来，一次只出现一处：`a small sign reading "整理"`
- 明确字形要求：`written in clean simplified Chinese sans-serif characters, each stroke complete and clearly separated`
- 加负向：`no garbled or invented characters`
- 生成 2–3 张挑一张，不要指望一次对

---

## 四、常见误区

| 误区 | 事实 |
|---|---|
| "prompt 写得够详细中文就能对" | 不能。这是模型能力问题，不是提示词问题 |
| "生成几次总有一次对" | 4 字以内成立，12 字基本不成立，而且每次构图都会变 |
| "字小一点看不出错" | 小红书用户会点开放大看 |
| "用 HTML 叠字就失去插画感了" | 恰恰相反，底图负责质感、文字层负责信息，是最强组合 |
| "英文封面显得高级" | 小红书是中文场景，英文标题会直接损失搜索流量和理解成本 |
