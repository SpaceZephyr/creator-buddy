---
name: space-video-broll
description: 动效导演 + B-roll 生成器。从一段文字/脚本/视频，一次性产出 30 秒以上的动效 B-roll 视频（HTML→确定性 MP4）。不做 PPT 式翻页，从「视觉隐喻 + 运动」出发；内置多种设计风格（暗色 SaaS 魔术、黑白打字机、暖色编辑、极简白、蓝图网格）；产出一律不用 emoji，用排版/几何/SVG 线性图标。当用户说「做 B-roll」「做个动效视频」「motion 开场」「文字动画」「概念动画」「HTML 转视频」「这段配个画面」「30秒 broll」时触发。
---

# space-video-broll · 动效导演

从一段文字/脚本/视频，产出一条**能当视频看、不像 PPT** 的动效 B-roll（默认 30 秒以上，一次成片）。

## 核心信条：从运动出发，不从页面出发

不要从「一页一页卡片」开始。先给内容找一个**能动起来的视觉隐喻**：

> 河流 / 网络 / 分支树 / 轨道 / 流水线 / 蜂群 / 坍缩 / 压缩 / 扫描 / 交接 / 增长循环 / 地图路径 / 堆栈 / 波形 / 时钟 / 透镜 / 机器

文字是锚点，不是主角。一个 beat 如果要靠读一大段字才成立，就把它改成运动、结构、符号或图形。

## 输入：文字 或 视频

- **文字/脚本**：直接抽 beats。
- **视频/逐字稿**：先读内容（`space-video-topic` 的逐字稿），抽出讲了哪几件事 → beats。
- 缺参数不追问，除非答案会改变产出路线。默认竖屏 720×896 或按 `space-video-edit` 配置，默认 30–40 秒。

## 工作流

### 1. 运动论点（一句话）

写死这一句再往下：

```
这条视频靠「<视觉隐喻>」从<起始状态>变成<结束状态>，来证明<核心主张>。
```

找不到能动的隐喻，就停下来先发明一个，别开始排场景。

### 2. Beat 图（连续时间轴，不是页）

排一条连续时间轴，每个 beat 写清：

| 字段 | 说明 |
|---|---|
| `time` | 起止秒 |
| `job` | 钩子 / 揭示 / 对比 / 机制 / 结果 / 证明 / 收尾 |
| `mover` | 这个 beat 里承载运动的主对象 |
| `change` | 屏幕上**物理上**发生了什么变化 |
| `camera` | 推/拉/摇/视差/环绕/裁切/稳定 |
| `text` | 标题/标签/计数/字幕/无 |
| `asset` | 代码SVG/生成图/截图/图标/无 |

### 3. Anti-PPT 质量门（硬性）

- **≥80% 的 beat 必须有「淡入/滑入」以外的可见状态变化**（生长、聚合、坍缩、路径绘制、替换、变形、点亮）。
- 不满足就退回重排——宁可少几个 beat，也不要一堆卡片轮流淡入。
- 主对象在它最显眼的那帧要**足够大**，不能像远处的小道具。

### 4. 选风格（见 `references/design-styles.md`）

内置风格，按内容/平台选一个，或用户指定：

| 风格 | 适合 | 关键词 |
|---|---|---|
| `dark-saas` | AI/产品/SaaS 演示 | 黑色星场、底部紫光、大字动态排版、青→品红 CTA |
| `bw-typewriter` | 观点/开场/悬念 | 纯黑白、大字逐字出现、打字节奏 |
| `warm-editorial` | 小红书/生活/自媒体 | 暖粉底、圆角、红色强调 |
| `minimal-light` | 教程/干货/极简 | 白底、细线、单一强调色 |
| `blueprint-grid` | 技术/架构/流程 | 深色网格、节点连线、扫描感 |

### 5. 无 Emoji 铁律

**产出一律不用 emoji。** 需要图标时用：几何形状、数字、SVG 线性图标（自己画 path）、纯文字 chip。emoji 在渲染里字重/对齐不可控，且廉价。

### 6. 渲染（一次成 30 秒+ 单片）

用自带渲染器把**一个多场景 HTML** 渲成一条完整 MP4：

```bash
node scripts/render.mjs <composition.html> <out.mp4> [fps=30]
```

- HTML 用 `scripts/timeline.js` 组织多个场景：每个场景声明 `start/dur` 和 `update(lt, p)`，`seek(t)` 自动分发。
- HTML 暴露 `window.DURATION`(秒) 和 `window.seek(t)`（纯函数、不依赖时钟，保证确定性）。
- 30 秒 = 900 帧，渲染放后台跑。示例见 `scripts/example-composition.html`。

## 时长预设（参考 rn 系列）

| 预设 | 时长 | beat 数 |
|---|---|---|
| `sting` | 8–12s | 3–4 |
| `standard` | 30–40s | 6–8 |
| `extended` | 50–70s | 9–12 |

默认 `standard`。

## 交接

- 上游：`space-video-script` 的 beats/画面需求，或用户一段文字/一条视频
- 下游：`04_broll/<名字>.mp4` → `space-video-edit` 合成，或直接单发

## 编排（复用已有能力）

- 有 hyperframes CLI → 走 `hyperframes` / `hyperframes-cli` / `hyperframes-media`
- 已有 Remotion 工程 → 走 `remotion-video` / `remotion-to-hyperframes`
- 复杂动画写法 → 走 `gsap` / `animejs` / `css-animations` / `waapi` / `three` / `lottie`
- 参考片复刻 + QC → 见 `references/replica-and-qc.md`

## 核心原则

- **运动优先**：先找会动的隐喻，再排场景
- **Anti-PPT**：≥80% beat 有真实状态变化，否则重排
- **无 emoji**：SVG 线性图标 / 几何 / 数字 / 文字
- **一次成片**：默认 30 秒+ 连续多场景，不是零散小片
- **确定性**：seek 驱动、相同输入相同输出
