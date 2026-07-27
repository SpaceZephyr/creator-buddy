# 12 套现成图文风格 TOKEN（离线可用，已过对比度验证）

`npx getdesign` 拉不到时（无网络 / 无 Node）用这里的块**兜底**；能联网时优先拉真规范，这里的值是近似还原。

用法：整块替换 `assets/xhs-template.html` 的 `:root{...}` 颜色与排版段，其余不动。
每套下方标注了实测对比度（用 `scripts/check_contrast.py` 算的，主标题 ≥7:1、accent ≥4.5:1 全部达标）。

**深色套装记得同时设 `<body data-mood="dark">`。**

---

## 1. Apple 苹果 — 极致留白，产品发布会气质
```css
--canvas:#F5F5F7; --canvas-2:#F5F5F7; --ink:#1D1D1F; --ink-2:#4A4A4F; --ink-3:#86868B;
--accent:#0058B8; --on-accent:#FFFFFF; --hairline:rgba(0,0,0,.08);
--title-weight:700; --title-tracking:-0.03em; --title-leading:1.08; --radius:16px; --rhythm:56px;
```
ink 15.5:1 · accent 6.3:1 ｜ 首页留白最大；内页使用浅灰卡片和蓝色细节

## 2. Notion — 纸感暖极简，知识工具
```css
--canvas:#F6F5F4; --canvas-2:#EFEDEA; --ink:#0D0D0D; --ink-2:#4B4B48; --ink-3:#8C8780;
--accent:#8A5A3B; --on-accent:#FFFFFF; --hairline:rgba(0,0,0,.10);
--title-weight:700; --title-tracking:-0.015em; --title-leading:1.2; --radius:8px; --rhythm:40px;
```
ink 17.9:1 · accent 5.4:1 ｜ 清单页使用 `card` 或 `line`；标题可用 `"Songti SC"` 增加编辑感

## 3. Claude — 赭石暖调 + 编辑感，人文智识
```css
--canvas:#FAF9F5; --canvas-2:#F2EFE7; --ink:#191919; --ink-2:#5A554D; --ink-3:#8C8780;
--accent:#A34527; --on-accent:#FFFFFF; --hairline:rgba(0,0,0,.10);
--title-weight:800; --title-tracking:-0.02em; --title-leading:1.16; --radius:999px; --rhythm:40px;
```
ink 16.7:1 · accent 5.8:1（品牌原色 #CC785C 只有 3.0:1，已按同色相加深）

## 4. Linear — 近黑底 + 薰衣草紫，效率工具天花板
```css
--canvas:#010102; --canvas-2:#0F1011; --ink:#F7F8F8; --ink-2:#D0D6E0; --ink-3:#8A8F98;
--accent:#828FFF; --on-accent:#0B0B0F; --hairline:#23252A;
--title-weight:600; --title-tracking:-0.037em; --title-leading:1.1; --radius:10px; --rhythm:44px;
```
ink 19.6:1 · accent 7.3:1 ｜ **深色首图在白花花的信息流里最跳**；目录用 `num`

## 5. Vercel — 纯黑白精准，前端极简
```css
--canvas:#000000; --canvas-2:#0A0A0A; --ink:#FFFFFF; --ink-2:#A1A1A1; --ink-3:#7A7A7A;
--accent:#4DA2FF; --on-accent:#000000; --hairline:#2A2A2A;
--title-weight:800; --title-tracking:-0.04em; --title-leading:1.05; --radius:8px; --rhythm:48px;
```
ink 21:1 · accent 7.9:1 ｜ Vercel 的强调靠**字重和留白**，accent 只点一个词就够

## 6. Stripe — 靛蓝渐变 + 优雅细字，商业金融
```css
--canvas:#FFFFFF; --canvas-2:#F6F9FC; --ink:#0A2540; --ink-2:#425466; --ink-3:#8898AA;
--accent:#5A52E0; --on-accent:#FFFFFF; --hairline:rgba(10,37,64,.10);
--title-weight:700; --title-tracking:-0.025em; --title-leading:1.15; --radius:12px; --rhythm:44px;
```
ink 15.5:1 · accent 5.7:1 ｜ Stripe 网页用 300 字重，封面**不要照抄**——细字在缩略图里必糊

## 7. Tesla — 全黑 + 品牌红，激进减法
```css
--canvas:#050505; --canvas-2:#101010; --ink:#FFFFFF; --ink-2:#B8B8B8; --ink-3:#8A8A8A;
--accent:#F0393E; --on-accent:#FFFFFF; --hairline:rgba(255,255,255,.14);
--title-weight:600; --title-tracking:-0.03em; --title-leading:1.06; --radius:4px; --rhythm:56px;
```
ink 20.4:1 · accent 5.2:1 ｜ 首页字越少越对；内页用细线和大数字保持力量感

## 8. NVIDIA — 荧光绿 + 纯黑，硬核算力
```css
--canvas:#050705; --canvas-2:#0C0F0C; --ink:#FFFFFF; --ink-2:#B4B4B4; --ink-3:#8A8A8A;
--accent:#76B900; --on-accent:#050705; --hairline:rgba(255,255,255,.12);
--title-weight:800; --title-tracking:-0.025em; --title-leading:1.1; --radius:6px; --rhythm:40px;
```
ink 20.2:1 · accent 8.4:1 ｜ 荧光绿**只给序号和细线**，别做主标题主体色（缩略图会糊）

## 9. Airbnb — 珊瑚暖调 + 圆润，生活方式
```css
--canvas:#FFF8F6; --canvas-2:#FFEDE8; --ink:#222222; --ink-2:#5C5350; --ink-3:#8E8480;
--accent:#D0173C; --on-accent:#FFFFFF; --hairline:rgba(0,0,0,.10);
--title-weight:800; --title-tracking:-0.015em; --title-leading:1.2; --radius:999px; --rhythm:40px;
```
ink 15.2:1 · accent 5.2:1 ｜ 目录用 `dot`；种草/旅行/探店类首选

## 10. Spotify — 深色 + 荧光绿，年轻内容
```css
--canvas:#121212; --canvas-2:#1A1A1A; --ink:#FFFFFF; --ink-2:#B3B3B3; --ink-3:#8A8A8A;
--accent:#1ED760; --on-accent:#0A0A0A; --hairline:rgba(255,255,255,.12);
--title-weight:800; --title-tracking:-0.03em; --title-leading:1.1; --radius:999px; --rhythm:40px;
```
ink 18.7:1 · accent 9.8:1 ｜ 音乐/娱乐/年轻向；目录用 `num` 像歌单

## 11. Figma — 亮底多彩，设计创意
```css
--canvas:#F7F7F8; --canvas-2:#F0F0F2; --ink:#1E1E1E; --ink-2:#55555A; --ink-3:#8A8A90;
--accent:#C4361C; --on-accent:#FFFFFF; --hairline:rgba(0,0,0,.10);
--title-weight:800; --title-tracking:-0.02em; --title-leading:1.15; --radius:12px; --rhythm:40px;
```
ink 15.6:1 · accent 5.0:1 ｜ 多彩是 Figma 的特征，但封面上**最多两个彩色**，其余交给留白

## 12. Miro — 明黄底 + 黑字，工作坊能量
```css
--canvas:#FFD02F; --canvas-2:#FFC400; --ink:#0A0A0A; --ink-2:#3D3211; --ink-3:#6B5A1E;
--accent:#7A0F1A; --on-accent:#FFD02F; --hairline:rgba(0,0,0,.18);
--title-weight:900; --title-tracking:-0.02em; --title-leading:1.12; --radius:16px; --rhythm:40px;
```
ink 13.5:1 · accent 7.5:1 ｜ **大面积高饱和底色在双列信息流里点击率很好**，但一个账号别混用两种底色

---

## 快速套用

```bash
# 1) 复制模板
cp assets/xhs-template.html work/index.html
# 2) 把上面某一块贴进 :root（颜色 + 排版段）
# 3) 深色套装额外改 <body data-mood="dark">
# 4) 验证 + 出图
python3 scripts/check_contrast.py --tokens work/index.html
node scripts/render_xhs.mjs --html work/index.html --out-dir /tmp/xhs-check --strict
```

**这 12 套之外的品牌**（共 62 个）见 `references/style-registry.md`，联网时用 getdesign 拉真规范。
