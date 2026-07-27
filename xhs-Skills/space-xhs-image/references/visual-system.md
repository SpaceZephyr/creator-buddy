# 轻盈 AI 产品信息图视觉系统

这套视觉系统从参考图中提炼“信息层级、卡片组件、线性科技图标、紫绿强调”的共同规律，但必须生成原创页面，不复制参考图的账号、Logo、水印、文案、插画或具体版式。

## 1. 画布

- 竖版 3:4。
- 最终文件：1080×1440 PNG。
- 画布外边距约 7%–9%，四边都要留出呼吸空间。
- 背景以 `#FCFBFF`、`#FAFAFD` 或纯白为主，可有非常轻的薰衣草柔光。
- 不使用纸张纹理、噪点、暗角、摄影背景或大面积高饱和底色。

## 2. 色板

主色：

- 墨黑：`#181A24`，标题和正文。
- 科技紫：`#6C35E8`，编号、线条、重点词。
- 电光蓝：`#4563F2`，紫色的相邻过渡色。
- 青柠绿：`#A4E927`，结果、通过、提升、关键动作。

辅助色：

- 浅薰衣草：`#F1ECFF`，卡片底和轻柔光。
- 浅蓝：`#EEF3FF`，信息卡底。
- 浅青绿：`#F1F9E8`，完成态卡片。
- 浅橙：`#FFF0E7`，只用于警告、限制或对比中的次要强调。
- 细分隔线：`#DED9EF`。

规则：

- 约 72% 白/浅底，18% 黑字与线条，10% 彩色强调。
- 单页最多三个强调色；紫与绿为主，蓝只做过渡。
- 渐变只用于 1–2 个关键词、圆形编号或小面积图标，不铺满整张图。

## 3. 字体与层级

要求模型使用现代中文无衬线字形，类似粗体系统黑体；不要手写体、书法体或衬线体。

- 顶部标签：小号粗体，放在细边框胶囊内。
- 主标题：页面最大元素，黑色粗体；1–2 个关键词可用紫蓝渐变或青柠绿。
- 副标题：中等字重，墨黑或深灰，最多两行。
- 模块标题：粗体，明显大于模块正文。
- 模块正文：短句，不写长段落。
- 数字编号：白字紫色圆点，或紫色数字配细连接线。

视觉占比：

- 主标题约占页面高度 14%–23%。
- 主内容区约占 48%–66%。
- 页脚结论或验收区约占 8%–16%。

## 4. 组件

### 圆角卡片

- 白底，大圆角，边缘干净。
- 轻柔紫灰阴影，不用重黑阴影。
- 卡片之间间距一致，避免层层嵌套超过两层。

### 线性图标

- 细线、圆角端点、统一线宽。
- 图标来自主题：浏览器窗口、代码、流程节点、清单、文档、目标、盾牌、机器人、用户、权限、图表。
- 紫色描边为主，完成态可用青柠绿；少量橙色只表示风险。
- 不混用写实插画、emoji、卡通贴纸和复杂 3D。

### 流程线

- 紫色细线连接编号或节点。
- 箭头简洁，保持方向明确。
- 一条流程最多 5 个主节点；超过 5 个拆页。

### 装饰

- 可使用低对比度浏览器线稿、流程节点、点阵、小星芒、细短线。
- 装饰透明度低，只放在角落和空白区。
- 不放无意义英文、不放重复章节名、不在内页重复账号名。

## 5. 信息密度

目标是“丰富但可扫读”：

- 一页一个中心结论。
- 一页 3–6 个信息模块。
- 一个模块优先使用 1 个图标 + 1 个短标题 + 0–1 行说明。
- 文字占画面不超过约 35%。
- 卡片覆盖画面不超过约 68%，留出背景呼吸区。
- 信息多时增加页面，不把字号压小。

## 6. Style Lock

系列图每一页都要逐字复用下面这段，只替换后面的页面内容和构图：

```text
Create an original premium AI-product infographic for Xiaohongshu in a 3:4 portrait canvas. Use a clean white to very pale lavender background with generous outer margins and breathable negative space. The main headline uses bold modern simplified-Chinese sans-serif typography in near-black, with only one or two key phrases highlighted by a controlled violet-to-electric-blue gradient or vivid lime green. Organize information in large white rounded cards with subtle lavender-gray shadows, precise spacing, and clear visual hierarchy. Use a coherent set of thin rounded line icons related to software, workflow, documents, checklists, targets, permissions, data, and AI. Add only a few low-contrast schematic decorations near the edges. The result should feel polished, intelligent, practical, and easy to scan at phone size—information-rich but never crowded. Keep icon line weight, corner radius, shadow softness, margins, and accent colors consistent across the series.
```

固定负向约束：

```text
Do not copy any reference image layout. No copied creator name, no AI_walker, no logo, no watermark, no signature, no fake interface screenshot, no garbled text, no invented Chinese characters, no long paragraphs, no tiny dense type, no photorealism, no glossy 3D mascot, no scrapbook collage, no childish stickers, no heavy black shadows, no dark full-bleed background, and no excessive decoration.
```

## 7. 参考图使用规则

若用户提供参考图：

1. 在提示词里逐张标注“视觉语言参考”。
2. 只借鉴色彩关系、信息层级、卡片结构、线性图标和留白节奏。
3. 明确要求原创构图。
4. 不读取或复用参考图中的账号名、水印、标题、段落、数据、标语和品牌元素。
5. 参考图有多个版式时，为不同页面选择不同结构，但保持同一 Style Lock。

## 8. 账号名

- 默认只在封面右上角出现一次。
- 使用用户提供的准确账号名；用户没提供则不擅自添加。
- 账号名是小号辅助信息，不与主标题争抢。
- 内页不重复账号名、英文口号或章节名，除非用户明确要求。
