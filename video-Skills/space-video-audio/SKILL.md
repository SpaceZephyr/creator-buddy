---
name: space-video-audio
description: 视频配音与配乐。三件事——(1) 配音：把口播稿用 TTS 生成旁白音频；(2) 配乐：根据视频内容/节奏匹配合适的 BGM，从免版权曲库找到并下载；(3) 混音：把 BGM + 旁白 + 视频用 ffmpeg 合成，自动压音(BGM 在人声下自动变小)、响度归一、淡入淡出、对齐视频长度。当用户说「配音」「配乐」「加 BGM」「背景音乐」「找音乐」「给视频配旁白」「TTS 口播」「混音」「audio」时触发。
---

# space-video-audio · 配音与配乐

给视频补上声音：**旁白(TTS) + 背景音乐(BGM) + 混音**。三块可单用，也能一次做完。

## 一、配音（TTS 旁白）

把口播稿变成旁白音频。按可用后端分档，**优先质量高的**：

| 档 | 后端 | 说明 |
|---|---|---|
| 高 | IndexTTS2 / 克隆音色 | 有本地模型/配置时用，最像真人、可定制音色 |
| **中（默认）** | `edge-tts` | 免费、自然，中文音色好。`uvx edge-tts` 直接跑 |
| 兜底 | macOS `say` | 无网络/无依赖时用，机械感强 |

edge-tts 生成（推荐中文音色 `zh-CN-XiaoxiaoNeural` / `zh-CN-YunxiNeural`）：

```bash
uvx edge-tts --voice zh-CN-YunxiNeural --rate=+8% \
  --text "$(cat 02_脚本/口播.txt)" --write-media 05_音频/voice.mp3
```

- 长稿按句/段分段生成再拼接，避免一句错整条重来
- 生成后走 `space-video-subtitle` 用**旁白音频**重转写做字幕对齐（TTS 段时长只是规划元数据，不能当字幕时间轴）
- 语速：口播偏快更精神，中文 `+8%~+15%` 常用

## 二、配乐（找 BGM 并下载）

### 选曲：先定情绪，再找曲

根据视频内容和节奏定 BGM 的情绪与 BPM：

| 视频类型 | BGM 方向 |
|---|---|
| 干货/教程 | 轻快 lo-fi / 简约电子，低存在感，不抢话 |
| 产品/科技 | 干净的合成器 pad / 节奏感电子 |
| 生活/小红书 | 明亮 ukulele / 轻流行 / 暖钢琴 |
| 观点/严肃 | 极简钢琴 / 环境氛围 |
| 快节奏盘点 | 有鼓点的 upbeat，卡点用 |

### 免版权来源（务必看授权）

见 `references/music-sources.md`。核心几个：
- **Pixabay Music**：免费、多数免署名（需网页/API）
- **YouTube Audio Library**：免费，部分需署名（需登录）
- **Free Music Archive / ccMixter**：CC 授权，多数需署名
- **Incompetech**（Kevin MacLeod）：CC-BY，需署名

### 下载

- 有直链的 → `curl -L -o 05_音频/bgm.mp3 "<直链>"`
- YouTube/B站 的免版权曲目 → `yt-dlp -x --audio-format mp3 -o 05_音频/bgm.mp3 "<URL>"`

**红线**：只用有权使用的曲目；需署名的记下来放视频简介；不搬运受版权保护的流行音乐；不确定授权就不用。选曲/授权是用户的决定，拿不准先问。

## 三、混音（合成到视频）

用 `scripts/mix.sh`，一条命令把 BGM(+旁白) 压进视频：

```bash
bash scripts/mix.sh --video in.mp4 --bgm bgm.mp3 [--voice voice.mp3] \
  --out out.mp4 [--bgm-db -20] [--fade 1.0] [--duck]
```

管线做的事（见 `references/mixing-recipes.md` 全套 ffmpeg）：
1. **对齐长度**：BGM 太短自动循环，太长裁切到视频时长
2. **响度归一**：`loudnorm` 把整体拉到 -14 LUFS 左右（平台友好）
3. **压音 ducking**：有旁白时用 `sidechaincompress`，人声一响 BGM 自动下沉，人声停 BGM 回来
4. **淡入淡出**：首尾 `afade`，别硬切
5. **BGM 音量**：无旁白约 -12~-16dB，有旁白垫底约 -20~-26dB
6. **封装**：`-c:v copy` 不重编码画面，只替换/混合音轨

## 交接

- 上游：`space-video-script` 的口播稿（→旁白）、`space-video-edit` 的成片、`space-video-broll` 的 B-roll
- 下游：带声音的成片 → 发布，或回 `space-video-edit` 做最终封装

## 依赖

`ffmpeg`（需带 loudnorm/sidechaincompress，本机已支持）、`yt-dlp`、`uvx`（跑 edge-tts）；克隆音色档需 IndexTTS2 环境。

## 核心原则

- **BGM 垫底不抢话**：有旁白必开 ducking，BGM 只做氛围
- **响度归一**：别让视频忽大忽小，统一到 -14 LUFS
- **授权优先**：只用免版权/有权曲目，需署名的记下来
- **不重编码画面**：混音只动音轨，`-c:v copy` 保画质
