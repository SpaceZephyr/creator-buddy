# 平台与依赖

## 路由

| 平台 | 字幕优先路径 | 无字幕路径 | 下载内容 |
|---|---|---|---|
| YouTube | `youtube-transcript-api`，再用 `yt-dlp` | 音频 → ASR | MP4 |
| B站 | `yt-dlp` 可用字幕 | 音频 → ASR | MP4 |
| 抖音 | 通常无公开字幕 | 音频 → ASR | MP4 |
| 小红书 | 通常无公开字幕 | 音频 → ASR | MP4 |
| 小宇宙 | 无平台字幕 | 单集音频 → ASR | M4A/MP3 |

## 基础依赖

- Python 3.10+
- 推荐安装 `uv`；启动脚本会用隔离环境加载 YouTube 字幕依赖，不污染系统 Python
- `ffmpeg` / `ffprobe`
- `yt-dlp`；平台变化频繁，建议保持最新版

没有 `uv` 时，YouTube 平台字幕可手动安装：

```bash
python3 -m pip install youtube-transcript-api
```

## ASR 后端

脚本的 `auto` 顺序：

1. 存在 `GROQ_API_KEY`：调用 Groq Whisper，适合现有小宇宙工作流。
2. 存在 `whisper` 命令：使用本地 OpenAI Whisper。
3. 存在 `agent-reach`：调用其 `transcribe` 路由。

可用 `--asr-backend groq|whisper|agent-reach` 强制指定。

## 浏览器登录态

抖音和小红书可能要求活跃浏览器会话。只有用户同意下载或重试后，才使用：

```bash
--cookies-from-browser chrome
```

此参数让 `yt-dlp` 在本机读取浏览器登录态。不要导出、打印或提交 Cookie。
