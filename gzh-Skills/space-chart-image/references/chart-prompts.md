# 图表提示词模板

本文档定义每种图表类型的提示词生成模板。

---

## 风格前缀库

所有提示词开头根据选定风格添加对应前缀。共有 6 种视觉风格。

### blueprint 蓝图工程风（默认）

适合：流程图、架构图、ER 图、产品路线图

```
A precise technical blueprint-style {图表类型} diagram.
Background: Off-white (#FAF8F5) with subtle grid lines.
Colors: Engineering Blue (#2563EB), Deep Slate (#334155), Navy (#1E3A5F), Light Blue (#BFDBFE).
Line art with clean geometric shapes, dimension lines, precise connections.
Thin borders, subtle shadows for depth. Professional engineering drawing feel.

ALL text, labels, and annotations in the image MUST be in Chinese (Simplified Chinese, 中文).
Use clean sans-serif Chinese font. Technical terms (e.g. AI, API, SQL, HTTP) may remain in English.
No photography, no realistic elements, no complex gradients, no 3D effects.
```

### notion 简约风

适合：所有图表类型（百搭）

```
A clean minimal {图表类型} diagram in Notion style.
Background: Pure white (#FFFFFF) with subtle dot grid.
Colors: Dark text (#37352f), subtle borders (#E3E2E0), accent blue (#2383E2), light fills (#F7F7F5).
Clean rectangular shapes with rounded corners, thin 1px borders.
Generous whitespace, geometric alignment, information-dense but organized.

ALL text, labels, and annotations in the image MUST be in Chinese (Simplified Chinese, 中文).
Use clean sans-serif Chinese font. Technical terms (e.g. AI, API, SQL, HTTP) may remain in English.
No photography, no realistic elements, no complex gradients, no 3D effects.
```

### sketch-notes 手绘笔记风

适合：思维导图、用户旅程图、组织架构图

```
A hand-drawn sketch-notes style {图表类型} diagram.
Background: Warm off-white (#FFF8F0) with subtle paper texture.
Colors: Warm tones - terracotta (#C0562F), forest green (#2F7A5C), navy pen (#2D3748), amber highlight (#F6AD55).
Marker-style thick outlines, slightly wobbly organic lines.
Handwritten feel, doodle-style icons, sticky-note shapes, arrow doodles.

ALL text, labels, and annotations in the image MUST be in Chinese (Simplified Chinese, 中文).
Use friendly rounded Chinese font. Technical terms (e.g. AI, API, SQL, HTTP) may remain in English.
No photography, no realistic elements, no complex gradients, no 3D effects.
```

### corporate 商务正装风

适合：SWOT 分析、商业模式画布、竞品分析

```
A professional corporate-style {图表类型} diagram.
Background: White (#FFFFFF) with navy (#1E3A5F) header band and subtle pinstripe accents.
Colors: Navy (#1E3A5F), Gold (#C5A55A), Charcoal (#4A4A4A), Silver (#B0B0B0), Light Gray (#F5F5F5).
Sharp geometric shapes, gold accent lines, clean serif typography.
Executive dashboard feel, data-driven, investment-grade presentation.

ALL text, labels, and annotations in the image MUST be in Chinese (Simplified Chinese, 中文).
Use professional Chinese font (serif for titles). Technical terms (e.g. AI, API, SQL, HTTP) may remain in English.
No photography, no realistic elements, no complex gradients, no 3D effects.
```

### dark-atmospheric 深色霓虹风

适合：产品路线图、竞品分析、架构图

```
A dark atmospheric {图表类型} diagram with glowing neon elements.
Background: Deep dark (#0A0A0B) with subtle grid overlay.
Colors: Neon cyan (#00F5FF), electric purple (#A855F7), hot pink (#F472B6), amber glow (#FBBF24).
Glowing connection lines, luminous node borders, gradient light effects on edges.
Futuristic dashboard feel, cyberpunk-inspired, high-tech aesthetic.

ALL text, labels, and annotations in the image MUST be in Chinese (Simplified Chinese, 中文).
Use clean light-colored Chinese font on dark background. Technical terms (e.g. AI, API, SQL, HTTP) may remain in English.
No photography, no realistic elements, no complex gradients on flat surfaces, no 3D effects.
```

### watercolor 水彩柔和风

适合：思维导图、组织架构图、用户旅程图

```
A soft watercolor-style {图表类型} diagram.
Background: Warm cream (#FEFCF8) with subtle watercolor wash texture.
Colors: Soft pastels - rose pink (#FBBFCA), sky blue (#A3D5FF), lavender (#C4B5FD), sage green (#A7F3D0), peach (#FED7AA).
Watercolor paint fill for shapes, soft bleeding edges, gentle color transitions.
Organic flowing connections, hand-painted feel, warm and approachable.

ALL text, labels, and annotations in the image MUST be in Chinese (Simplified Chinese, 中文).
Use rounded friendly Chinese font. Technical terms (e.g. AI, API, SQL, HTTP) may remain in English.
No photography, no realistic elements, no sharp geometric shapes, no 3D effects.
```

---

## 1 流程图 Flowchart

### 必填信息
- 流程步骤列表（至少 3 个步骤）
- 是否有分支/判断
- 开始和结束节点

### 提示词模板

```
{通用风格前缀}

Layout: horizontal flow from left to right.

Nodes (rounded rectangles connected with arrows):
- {开始节点} (start node, oval shape)
- {步骤1} → {步骤2} → {步骤3}
{如果有分支}
- Decision node: {判断条件} (diamond shape)
  - If {条件A}: → {结果A}
  - If {条件B}: → {结果B}
- {结束节点} (end node, oval shape)

Labels above arrows: {关系标签（如有）}

中文标签：直接在节点中写中文，如 "开始"、"数据处理"、"判断"、"结束" 等。
```

### 示例

用户输入：用户注册流程，包括输入信息、验证码、验证成功后注册成功

提示词：
```
A minimal hand-drawn flowchart diagram with clean lines on white background.
Black outlines, minimal blue accents for emphasis.
No photography, no realistic elements, no complex gradients, no 3D effects.
Flat, simple, professional style suitable for business presentation.

ALL text, labels, and annotations in the image MUST be in Chinese (Simplified Chinese, 中文).
Use clean Chinese font for main text. Technical terms and abbreviations may remain in English.

Layout: horizontal flow from left to right.

Nodes (rounded rectangles connected with arrows):
- 开始 (start node, oval shape)
- 输入注册信息 → 发送验证码
- Decision: 验证码正确? (diamond shape)
  - If 否: → 重新输入
  - If 是: → 创建账户
- 注册完成 (end node, oval shape, green accent)

中文标签：开始、输入注册信息、发送验证码、验证码正确、否、重新输入、是、创建账户、注册完成
```

---

## 2 架构图 Architecture Diagram

### 必填信息
- 系统分层/模块列表
- 模块间的关系（数据流、调用关系）

### 提示词模板

```
{通用风格前缀}

Layout: layered architecture, horizontal arrangement from left to right.

Layers (separated with vertical dashed lines):
- {层1名称}: {模块列表}
- {层2名称}: {模块列表}
- {层3名称}: {模块列表}

Connections (arrows with labels):
- {模块A} → {模块B}: {数据/调用描述}

中文标签：层名、模块名使用中文，如 "前端层"、"用户服务"、"数据库" 等。
```

### 示例

用户输入：Web 应用架构，包括前端、后端 API、数据库

提示词：
```
A minimal hand-drawn architecture diagram with clean lines on white background.
Black outlines, minimal blue accents for emphasis.
No photography, no realistic elements, no complex gradients, no 3D effects.
Flat, simple, professional style suitable for business presentation.

ALL text, labels, and annotations in the image MUST be in Chinese (Simplified Chinese, 中文).
Use clean Chinese font for main text. Technical terms and abbreviations (e.g. API, HTTP, SQL) may remain in English.

Layout: layered architecture, horizontal arrangement from left to right.

Layers (separated with vertical dashed lines):
- 前端层: Web 页面, 移动 App
- API 层: 用户 API, 订单 API, 支付 API
- 数据层: 用户数据库, 订单数据库

Connections (arrows with labels):
- Web 页面 → 用户 API: HTTP/JSON
- 移动 App → 用户 API: HTTP/JSON
- 用户 API → 用户数据库: SQL 查询
- 订单 API → 订单数据库: SQL 查询
```

---

## 3 ER 图 ER Diagram

### 必填信息
- 实体列表（至少 2 个）
- 每个实体的主要字段
- 实体间的关系

### 提示词模板

```
{通用风格前缀}

Layout: entities scattered, connected with relationship lines.

Entities (rectangles with field lists):
- {实体名1}
  - {字段1} (PK, primary key, underline)
  - {字段2}
  - {字段3}
- {实体名2}
  - {字段1} (PK)
  - {字段2} (FK, foreign key)

Relationships (lines with cardinality labels):
- {实体A} 1:N {实体B}: {关系描述}

中文标签：实体名、字段名使用中文。
```

---

## 4 商业模式画布 Business Model Canvas

### 必填信息
- 价值主张（核心）
- 其他 8 个区块的内容

### 提示词模板

```
{通用风格前序，但使用 21:9 比例}

Layout: classic Business Model Canvas 9-grid layout (5 columns, 2 rows).

Nine blocks with Chinese labels:
Top row (left to right):
- 重要伙伴: {内容}
- 关键活动: {内容}
- 核心资源: {内容}
- 价值主张: {内容 - central, highlighted}
- 客户关系: {内容}

Bottom row (left to right):
- 渠道通路: {内容}
- 客户细分: {内容}
- 成本结构: {内容}
- 收入来源: {内容}

每个区块用浅色背景区分，区块内列出 3-5 条要点。
```

---

## 5 用户旅程图 User Journey Map

### 必填信息
- 用户阶段列表
- 每个阶段的行为和触点
- 情绪变化

### 提示词模板

```
{通用风格前缀}

Layout: horizontal timeline with stages, vertical layers for different aspects.

Stages (top row, horizontal):
- {阶段1} → {阶段2} → {阶段3} → {阶段4}

Layers (for each stage):
- 用户行为: {具体行为}
- 触点: {用户接触的界面/渠道}
- 情绪: {情绪评分 1-5，用曲线连接各阶段}

情绪曲线：用平滑曲线连接各阶段的情绪评分，高点用绿色，低点用红色。
```

---

## 6 思维导图 Mind Map

### 必填信息
- 中心主题
- 主要分支（至少 3 个）
- 每个分支的子节点

### 提示词模板

```
{通用风格前缀}

Layout: central topic in the middle, branches radiating outward.

Central node (center, large): {中心主题}

Primary branches (different colors for each):
- {分支1}: {子节点1-1}, {子节点1-2}
- {分支2}: {子节点2-1}, {子节点2-2}
- {分支3}: {子节点3-1}, {子节点3-2}
- {分支4}: {子节点4-1}, {子节点4-2}

Each branch uses a different accent color for visual distinction.
中文标签：中心主题和所有分支节点使用中文。
```

---

## 7 竞品分析图 Competitive Analysis

### 必填信息
- 竞品列表（至少 2 个）
- 对比维度
- 各产品在各维度的评分

### 提示词模板

```
{通用风格前缀}

Layout: comparison table or radar chart format.

Option 1 - Table format:
Columns: 产品, {维度1}, {维度2}, {维度3}, {维度4}
Rows: {产品1}, {产品2}, {产品3}
Each cell contains: 评分 1-10 (用条形图表示)

Option 2 - Positioning matrix:
X-axis: {维度1 (如价格)}
Y-axis: {维度2 (如品质)}
Each product plotted as a bubble with label: {产品名}

中文标签：产品名、维度名使用中文。
```

---

## 8 SWOT 分析 SWOT Analysis

### 必填信息
- 优势 Strengths (3-5 条)
- 劣势 Weaknesses (3-5 条)
- 机会 Opportunities (3-5 条)
- 威胁 Threats (3-5 条)

### 提示词模板

```
{通用风格前缀}

Layout: 2x2 matrix quadrants.

Top left - 优势 S:
- {优势1}
- {优势2}
- {优势3}
Background: light green tint

Top right - 劣势 W:
- {劣势1}
- {劣势2}
- {劣势3}
Background: light red tint

Bottom left - 机会 O:
- {机会1}
- {机会2}
- {机会3}
Background: light blue tint

Bottom right - 威胁 T:
- {威胁1}
- {威胁2}
- {威胁3}
Background: light yellow tint

中心标题：{分析对象} SWOT 分析
```

---

## 9 产品路线图 Product Roadmap

### 必填信息
- 时间线（季度或月份）
- 各版本/功能计划
- 里程碑

### 提示词模板

```
{通用风格前缀}

Layout: horizontal timeline at top, feature tracks below.

Timeline: Q1 → Q2 → Q3 → Q4 (或具体月份)

Tracks (horizontal swimlanes):
- 核心功能: {功能1} (Q1, 完成), {功能2} (Q2, 进行中), {功能3} (Q3, 规划)
- 优化项: {优化1} (Q2), {优化2} (Q3)
- 基础设施: {基建1} (Q1), {基建2} (Q4)

Status colors:
- 完成: 绿色
- 进行中: 蓝色
- 规划中: 灰色

里程碑：用菱形标记重要节点，标注里程碑名称。

中文标签：功能名、里程碑使用中文。
```

---

## 10 组织架构图 Org Chart

### 必填信息
- 组织层级结构
- 各角色/人名

### 提示词模板

```
{通用风格前缀}

Layout: tree structure, top to bottom.

Top level:
- {最高角色}: {人名（可选）}

Second level:
- {部门1负责人}: {人名}
- {部门2负责人}: {人名}
- {部门3负责人}: {人名}

Third level (under each department):
- {下级角色1}, {下级角色2}

连接线：实线表示直接汇报关系，虚线表示虚线汇报。
同级用浅色背景框分组。

中文标签：角色名、部门名使用中文。
```

---

## 提示词生成规则

1. **中文优先**：所有图表内容、标签必须使用中文
2. **专业术语保留英文**：如 API, SQL, HTTP, AI, JWT 等技术术语
3. **简洁精炼**：每个要点不超过 15 个字
4. **结构清晰**：明确层次关系，用缩进和符号表示层级
5. **视觉提示**：用颜色、形状、线条区分不同元素类型
