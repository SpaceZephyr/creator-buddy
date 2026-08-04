# 免版权 BGM 来源与授权

**只用有权使用的曲目。** 需署名的，把「曲名 + 作者 + 来源链接」记到视频简介。拿不准授权，就不用。

## 常用来源

| 来源 | 授权 | 是否需署名 | 获取方式 |
|---|---|---|---|
| **Pixabay Music** | Pixabay License | 多数否 | 网页下载 / API（需 key） |
| **YouTube Audio Library** | 各曲不同 | 部分需 | 需登录 YouTube 后台下载 |
| **Free Music Archive** | CC 各版本 | 多数需 | 网页有直链 |
| **ccMixter (dig.ccmixter.org)** | CC 各版本 | 多数需 | 网页有直链 |
| **Incompetech（Kevin MacLeod）** | CC-BY 4.0 | 需 | 网页直链 mp3 |
| **Uppbeat / Bensound** | 各家协议 | 免费档多需 | 网页下载 |

## 下载方式

```bash
# 有直链的曲目
curl -L -o 05_音频/bgm.mp3 "<mp3 直链>"

# 曲库放在 YouTube/B站 上的免版权曲目
yt-dlp -x --audio-format mp3 --audio-quality 0 -o "05_音频/bgm.%(ext)s" "<URL>"
```

### Pixabay 免登录取直链（实测可用）

Pixabay 下载按钮需登录，但**播放用的就是完整曲目**，可绕开登录拿直链：

1. 浏览器开 `pixabay.com/music/search/<vibe>/`（如 upbeat / happy / lo-fi）
2. 点某曲**播放键**（不是下载键），让它加载
3. 从播放器 `<audio>` 元素读 `currentSrc`，是形如 `https://cdn.pixabay.com/audio/YYYY/MM/DD/audio_<hash>.mp3` 的干净直链
4. `curl -L -o bgm.mp3 "<直链>"`

Pixabay License：免费商用、无需署名。下完把曲名/作者/链接记进选曲记录。

## 选曲清单（记录用）

每次选定 BGM，落一条：

```
曲名 / 作者 / 来源链接 / 授权类型 / 是否需署名 / 用在哪条视频
```

## 注意

- **不搬运受版权保护的流行音乐**（哪怕只做 BGM），平台会打版权、限流或静音。
- YouTube Audio Library 需要登录导出，属用户操作，不要代登录。
- Pixabay/多数曲库的 API 需要 key，没配就走网页人工下，或让用户提供直链/曲目。
- 选曲是主观 + 授权决定：拿不准先问用户要「情绪 + 一个可用来源/链接」。
