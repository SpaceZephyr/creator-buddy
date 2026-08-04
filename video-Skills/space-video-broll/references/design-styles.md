# 内置设计风格库

每种风格给一套可直接用的设计 token（背景/强调色/字体/圆角/运动感）。选一个，贯穿整条 B-roll。**全部不用 emoji。**

无 emoji 的图标方案（通用）：
- 数字、几何形状（圆/方/环/三角）
- SVG 线性图标：自己画 `<path>`，1.5–2px stroke，`stroke-linecap:round`
- 纯文字 chip / 标签
- 抽象 UI 卡片（圆角矩形 + 线条占位）

---

## 1. dark-saas —— 暗色 SaaS 魔术

```css
--bg: radial-gradient(120% 90% at 50% 100%, #241a3d 0%, #0c0912 55%);
--stage: #0c0912;        /* 黑色空间舞台 + 细星点颗粒 */
--glow: #7c4dff;         /* 底部紫色地平线光 */
--accent-a: #22e3d6;     /* 青 */
--accent-b: #ff3fa4;     /* 品红，CTA 用青→品红渐变 */
--text: #ffffff;         /* 大字动态排版，白 */
--muted: #9a93b5;
--font: "PingFang SC","Inter",sans-serif;
--radius: 20px;
```
硬规则：黑色星场 + 底部弱紫光；大白字当叙事节拍；至少一个青→品红 CTA 触发可见变化；主对象（prompt 卡/CTA/UI 板/环）在最显眼帧要大；大转场用速度模糊/缩放冲刺/白色速度擦除；UI 物件像从黑暗中被「召唤」出来。忌：持续的水平霓虹线背景、无解释的全屏纯色闪。

## 2. bw-typewriter —— 黑白打字机

```css
--bg: #000000;
--text: #ffffff;
--accent: #ffffff;       /* 纯黑白，强调靠字重/尺寸 */
--font: "PingFang SC","SF Mono",monospace;
--radius: 0;
```
大白字**逐字出现**，打字节奏（每字 40–70ms）；可做词替换/对比词；结尾定格一句或引到下一场景。可选打字 click 音效（后期加）。极简，不加装饰。

## 3. warm-editorial —— 暖色编辑（小红书/自媒体）

```css
--bg: radial-gradient(120% 90% at 50% 12%, #fff3f4 0%, #ffe3e8 50%, #ffd0dd 100%);
--accent: #ff2442;       /* 小红书红 */
--text: #22252a;
--muted: #7a7370;
--card: #ffffff;
--font: "PingFang SC","Heiti SC",sans-serif;
--radius: 22px;
--shadow: 0 12px 34px rgba(255,36,66,.18);
```
圆角卡片、留白足、红色只点睛；数字大、成品感强；亲和不炫技。

## 4. minimal-light —— 极简白（教程/干货）

```css
--bg: #f7f7f5;
--accent: #111111;       /* 单一强调色，默认黑，可换品牌色 */
--text: #1a1a1a;
--muted: #8a8a86;
--line: #e2e2dd;
--font: "PingFang SC","Inter",sans-serif;
--radius: 14px;
```
细线（1px）、大量留白、克制；靠版式和位移讲逻辑，不靠颜色。

## 5. blueprint-grid —— 蓝图网格（技术/架构/流程）

```css
--bg: #0b1220;
--grid: rgba(90,140,255,.10);   /* 背景网格线 */
--accent: #5b9dff;
--text: #e8f0ff;
--muted: #6b7a99;
--node: #12203a;
--font: "PingFang SC","JetBrains Mono",monospace;
--radius: 10px;
```
深色网格底、节点+正交连线、扫描/绘制感；连线**画出来**（path draw），节点依次点亮。

---

## 选风格速查

| 内容 | 建议风格 |
|---|---|
| AI 工具 / 产品演示 | dark-saas |
| 观点 / 悬念开场 | bw-typewriter |
| 小红书 / 生活 / 个人 IP | warm-editorial |
| 教程 / 方法论 / 干货 | minimal-light |
| 架构 / 流程 / 技术拆解 | blueprint-grid |

用户指定风格时以用户为准；混合场景可分场景切风格，但整条要有统一基因（同一套字体+强调色逻辑）。
