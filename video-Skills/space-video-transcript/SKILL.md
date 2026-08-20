---
name: space-video-transcript
description: 从 YouTube、小宇宙、B站、抖音和小红书链接提取字幕或逐字稿；优先读取平台字幕，无字幕时自动提取音频并调用可用 ASR，输出 Markdown 与 SRT。用户发送这些平台链接、要求提取字幕/文案/逐字稿/视频转文字，或在字幕完成后希望下载原视频时使用。字幕成功后必须询问用户是否下载原视频；小宇宙对应下载原音频。
---

# 视频链接字幕提取

收到支持的平台链接后立即提取字幕。先交付字幕，再询问是否下载源文件；不得在用户确认前下载完整视频。

## 定位 Skill

```bash
SVT_HOME="$(
  for dir in \
    "$HOME/.codex/skills/space-video-transcript" \
    "$HOME/.agents/skills/space-video-transcript" \
    "$HOME/.claude/skills/space-video-transcript" \
    "$(pwd)/video-Skills/space-video-transcript" \
    "$(pwd)/space-video-transcript"; do
    [ -f "$dir/SKILL.md" ] && printf '%s\n' "$dir" && break
  done
)"
```

若 `SVT_HOME` 为空，先让用户提供 Skill 路径。

## 工作流

1. 从用户消息中提取 URL；支持 YouTube、小宇宙单集、B站、抖音和小红书视频。
2. 首次使用或环境异常时运行体检：

```bash
bash "$SVT_HOME/scripts/run.sh" doctor
```

3. 立即提取字幕，不先询问是否下载：

```bash
bash "$SVT_HOME/scripts/run.sh" transcribe \
  "<URL>" --output-dir "<输出目录>"
```

默认输出目录为当前目录下的 `video-transcripts/`。脚本优先获取平台已有字幕；没有字幕时自动抽取音频并按 `Groq → 本地 Whisper → agent-reach` 的顺序选择 ASR。

4. 读取脚本最后一行 `SPACE_VIDEO_TRANSCRIPT_RESULT=...`：
   - 向用户展示字幕文件路径、来源平台、采用的平台字幕或 ASR。
   - 用户要求查看全文时，读取 Markdown 文件并展示；长稿可先给摘要和路径。
   - 然后必须询问：`字幕已提取。是否同时下载原视频？（小宇宙将下载原音频）`

5. 只有用户明确回答“是/下载”后才运行：

```bash
bash "$SVT_HOME/scripts/run.sh" download \
  "<同一 URL>" --output-dir "<输出目录>/media"
```

若平台要求登录态，先说明原因，再让用户自行在浏览器登录；得到允许后可加 `--cookies-from-browser chrome`。不要索取或回显 Cookie。

## 输出

- `*_transcript.md`：带来源、语言和时间戳的可读稿。
- `*_subtitles.srt`：存在可靠时间轴时生成。
- `media/`：仅在用户确认后保存原视频；小宇宙保存原音频。

## 语言与校对

- 中文字幕直接交付。
- 只有英文字幕且用户要求中文稿时，用当前 Agent 翻译，保留时间戳，不改事实。
- 专有名词明显错误时先列出低置信度修正，不静默改写原意。
- 成片字幕需要进一步做口播断句、ASS 样式或烧录时，交给 `space-video-subtitle`。

## 失败处理

- YouTube/B站无字幕：自动走 ASR，不要直接结束。
- 抖音/小红书抓取失败：提示用户先在 Chrome 打开或登录对应平台，再经允许使用浏览器登录态重试。
- 小宇宙只接受 `/episode/` 单集页；节目主页要求用户改发单集链接。
- 没有可用 ASR：说明可选方案——配置 `GROQ_API_KEY`、安装 `openai-whisper`，或配置 `agent-reach transcribe`。
- 不支持 DRM、付费或无权访问的内容，不绕过验证码、权限校验和平台限制。

平台差异和依赖说明见 [references/platforms.md](references/platforms.md)。
