# 小红书多页 HTML 制作规范

固定输出为一个完整 HTML，内部包含 6 张以上 1080×1440（3:4）页面。

## 目录

1. 单文件结构
2. 字号与密度
3. 页面安全区
4. 风格 token
5. 校验清单

## 一、单文件结构

```html
<body>
  <section class="sheet cover" id="p01">...</section>
  <section class="sheet" id="p02">...</section>
  <section class="sheet" id="p03">...</section>
</body>
```

必须满足：

1. `body` 是预览容器，只负责纵向排列，不固定为 1080×1440。
2. 每张 `.sheet` 固定 `width:1080px;height:1440px;overflow:hidden`。
3. 页面内容走正常文档流、Flex 或 Grid。绝对定位只用于装饰、页码和底部细线。
4. 所有页面共用一个 `:root` token 块，不在单页硬编码另一套配色。
5. 不使用外链字体、CSS、JavaScript 或在线图片。
6. 打印样式使用 `.sheet{page-break-after:always}`，并移除 body 的预览背景和间距。

推荐骨架：

```css
*{box-sizing:border-box;margin:0;padding:0}
html{background:#d9d9de}
body{
  min-width:1080px;
  padding:40px 0;
  display:flex;
  flex-direction:column;
  gap:40px;
}
.sheet{
  width:1080px;
  height:1440px;
  margin:0 auto;
  padding:90px;
  position:relative;
  overflow:hidden;
  background:var(--canvas);
}
@media print{
  html,body{background:#fff}
  body{display:block;padding:0}
  .sheet{margin:0;page-break-after:always}
}
```

## 二、字号与密度

| 层级 | 建议字号 | 约束 |
|---|---:|---|
| 封面标题 | 88–128px | 2–4 行，缩略图仍可识别 |
| 内页标题 | 60–76px | 1 个问题，通常不超过 2 行 |
| 强调数字 | 72–110px | 一页只设一个主数字 |
| 正文 | 36–44px | 行高 1.35–1.55 |
| 表格 / 字段 / 代码 | 30–38px | 不能靠缩小字体硬塞 |
| 标签 / 页码 | 28–34px | 只承载辅助信息 |

密度规则：

- 封面只放主题、结果和必要身份锚。
- 内页每页通常 70–150 个中文字符。
- 一页最多 1 个主标题、1 段解释和 1 个主要视觉组件。
- 表格超过 6 行时拆页；步骤超过 4 个时拆页；卡片超过 6 个时拆页。
- 卡片之间至少留 16–24px；主要区块之间至少留 32–56px。
- 内容放不下时依次处理：删重复 → 改短句 → 拆页 → 缩小非正文间距。最后才考虑字号。

## 三、页面安全区

1080×1440 基准：

- 左右：80–96px
- 顶部：80–100px
- 底部：96–140px

账号名默认只在首页。内页顶部在“章节标签、页码、标题”中最多保留两种；不要同时出现：

- `05｜上线检查`
- `P06 · 上线检查`
- `原件只读 · 发布前复核`
- `CODEX AGENT · FINANCE`

这些元素同时出现只会重复，不会增加信息。

底部规则线、圆点等装饰必须位于内容之后，不能挤占正文。正文与底部装饰建议至少保留 40px。

## 四、风格 token

把品牌风格映射为组图 token：

```css
:root{
  --canvas:#FFFFFF;
  --surface:#F5F5F7;
  --ink:#1D1D1F;
  --text:#424245;
  --muted:#86868B;
  --line:#E5E5EA;
  --accent:#0058B8;
  --on-accent:#FFFFFF;
  --radius:24px;
  --title-weight:760;
  --title-tracking:-.035em;
}
```

从品牌 DESIGN.md 复制：

- 颜色 hex
- 字重
- 字距比例
- 行高比例
- 圆角气质
- 一种装饰母题

不要直接复制网页的 16px 正文字号或 40px 标题字号。品牌规范决定气质，小红书画布决定尺寸。

对比度要求：

- 主标题与背景 ≥ 7:1
- 正文与背景 ≥ 4.5:1
- 强调色承载正文时 ≥ 4.5:1
- 强调色只做线条、圆点时可放宽，但不能影响识别

## 五、校验清单

生成后运行：

```bash
python3 scripts/check_contrast.py --tokens index.html
node scripts/render_xhs.mjs --html index.html --out-dir /tmp/xhs-check --strict
```

逐页检查：

- [ ] `.sheet` 数量与用户选择一致，且不少于 6
- [ ] 每页正好 1080×1440
- [ ] 无横向或纵向溢出
- [ ] 正文没有压住页码、装饰线或页面底部
- [ ] 封面缩小到 270px 宽仍能读懂主题
- [ ] 第 2 页没有复述封面
- [ ] 相邻页面不是同一套卡片阵列机械复制
- [ ] 账号名只在首页出现
- [ ] 风格 token 全组一致
- [ ] HTML 离线打开效果不变
