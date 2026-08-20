"""Platform detection, metadata and source acquisition."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from formats import Segment, clean_text

SUPPORTED = ("youtube", "xiaoyuzhou", "bilibili", "douyin", "xiaohongshu")


@dataclass(frozen=True)
class Episode:
    title: str
    audio_url: str
    podcast: str = ""


def detect_platform(url: str) -> str:
    parsed = urlparse(url)
    host = parsed.netloc.lower()
    path = parsed.path.lower()
    if host in {"youtu.be", "www.youtu.be"} or host.endswith("youtube.com"):
        return "youtube"
    if host.endswith("xiaoyuzhoufm.com"):
        return "xiaoyuzhou" if "/episode/" in path else "xiaoyuzhou-page"
    if host.endswith("bilibili.com") or host == "b23.tv":
        return "bilibili"
    if host.endswith("douyin.com"):
        return "douyin"
    if host.endswith("xiaohongshu.com") or host == "xhslink.com":
        return "xiaohongshu"
    return "unsupported"


def validate_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("请输入完整的 http/https 链接")
    platform = detect_platform(url)
    if platform == "xiaoyuzhou-page":
        raise ValueError("小宇宙节目主页不是单集，请提供包含 /episode/ 的单集链接")
    if platform not in SUPPORTED:
        raise ValueError("仅支持 YouTube、小宇宙、B站、抖音和小红书链接")
    return platform


def youtube_id(url: str) -> str:
    parsed = urlparse(url)
    if parsed.netloc.lower().endswith("youtu.be"):
        return parsed.path.strip("/").split("/")[0]
    match = re.search(r"(?:[?&]v=|/embed/|/shorts/)([A-Za-z0-9_-]{11})", url)
    if not match:
        raise ValueError("无法从链接提取 YouTube 视频 ID")
    return match.group(1)


def youtube_api_captions(url: str, languages: tuple[str, ...]) -> tuple[Segment, ...]:
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
    except ImportError:
        return ()
    try:
        transcript = (
            YouTubeTranscriptApi()
            .list(youtube_id(url))
            .find_transcript(list(languages))
        )
        fetched = transcript.fetch()
    except Exception:  # noqa: BLE001 - platform/API failures must fall through to yt-dlp/ASR
        return ()
    return tuple(
        Segment(
            float(item.start), float(item.start + item.duration), clean_text(item.text)
        )
        for item in fetched
        if clean_text(item.text)
    )


def _walk(value: Any):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk(child)


def extract_episode_from_html(html: str) -> Episode:
    title = "小宇宙播客"
    podcast = ""
    audio_url = ""
    match = re.search(
        r'<script[^>]+id=["\']__NEXT_DATA__["\'][^>]*>(.*?)</script>', html, re.DOTALL
    )
    if match:
        try:
            payload = json.loads(match.group(1))
            for item in _walk(payload):
                possible_audio = (
                    item.get("enclosureUrl")
                    or item.get("audioUrl")
                    or item.get("mediaUrl")
                )
                if isinstance(possible_audio, str) and possible_audio.startswith(
                    "http"
                ):
                    audio_url = possible_audio
                    title = str(item.get("title") or title)
                    podcast_value = item.get("podcast")
                    if isinstance(podcast_value, dict):
                        podcast = str(
                            podcast_value.get("title")
                            or podcast_value.get("name")
                            or ""
                        )
                    break
        except json.JSONDecodeError:
            pass
    if not audio_url:
        audio_match = re.search(
            r'https://media\.xyzcdn\.net/[^"\'\\]+?\.(?:m4a|mp3)(?:\?[^"\'\\]*)?',
            html,
            re.IGNORECASE,
        )
        if audio_match:
            audio_url = audio_match.group(0).replace("\\u0026", "&")
    meta_title = re.search(
        r'<meta[^>]+(?:property|name)=["\']og:title["\'][^>]+content=["\']([^"\']+)',
        html,
        re.IGNORECASE,
    )
    if meta_title:
        title = clean_text(meta_title.group(1)) or title
    if not audio_url:
        raise RuntimeError("无法解析小宇宙音频直链，平台页面结构可能已变化")
    return Episode(title=title, audio_url=audio_url, podcast=podcast)


def fetch_xiaoyuzhou_episode(url: str) -> Episode:
    request = Request(
        url, headers={"User-Agent": "Mozilla/5.0 space-video-transcript/1.0"}
    )
    with urlopen(request, timeout=30) as response:
        html = response.read(10_000_000).decode("utf-8", errors="replace")
    return extract_episode_from_html(html)


def ytdlp_command() -> str:
    command = shutil.which("yt-dlp")
    if not command:
        raise RuntimeError("未找到 yt-dlp；请先安装：python3 -m pip install -U yt-dlp")
    return command


def metadata(url: str) -> dict[str, Any]:
    command = [
        ytdlp_command(),
        "--dump-single-json",
        "--skip-download",
        "--no-warnings",
        url,
    ]
    result = subprocess.run(
        command, capture_output=True, text=True, check=False, timeout=120
    )
    if result.returncode != 0:
        return {"title": "视频逐字稿", "language": "unknown"}
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"title": "视频逐字稿", "language": "unknown"}
    return {
        "title": data.get("title") or "视频逐字稿",
        "language": data.get("language") or "unknown",
    }


def cookie_args(browser: str | None) -> list[str]:
    return ["--cookies-from-browser", browser] if browser else []


def failure_message(action: str, detail: str) -> str:
    lowered = detail.lower()
    if "not a bot" in lowered or "cookies-from-browser" in lowered:
        return (
            f"{action}失败：平台要求浏览器登录态。请先在 Chrome 打开并登录该平台，"
            "得到用户允许后加 --cookies-from-browser chrome 重试"
        )
    return f"{action}失败：{detail[-600:]}"


def download_platform_subtitles(
    url: str, work_dir: Path, languages: str, browser: str | None = None
) -> tuple[Path, ...]:
    template = str(work_dir / "platform.%(ext)s")
    command = [
        ytdlp_command(),
        "--skip-download",
        "--write-subs",
        "--write-auto-subs",
        "--sub-langs",
        languages,
        "--convert-subs",
        "srt",
        "--no-warnings",
        "-o",
        template,
        *cookie_args(browser),
        url,
    ]
    subprocess.run(command, capture_output=True, text=True, check=False, timeout=180)
    candidates = sorted(work_dir.glob("platform*.srt")) + sorted(
        work_dir.glob("platform*.vtt")
    )
    return tuple(dict.fromkeys(candidates))


def download_audio(url: str, work_dir: Path, browser: str | None = None) -> Path:
    output = str(work_dir / "audio.%(ext)s")
    command = [
        ytdlp_command(),
        "-x",
        "--audio-format",
        "mp3",
        "--audio-quality",
        "5",
        "--no-playlist",
        "--no-warnings",
        "-o",
        output,
        *cookie_args(browser),
        url,
    ]
    result = subprocess.run(
        command, capture_output=True, text=True, check=False, timeout=1800
    )
    matches = sorted(work_dir.glob("audio.*"))
    if result.returncode != 0 or not matches:
        detail = (result.stderr or result.stdout)[-600:]
        raise RuntimeError(failure_message("音频提取", detail))
    return matches[0]


def download_direct(url: str, output: Path) -> Path:
    request = Request(
        url, headers={"User-Agent": "Mozilla/5.0 space-video-transcript/1.0"}
    )
    with urlopen(request, timeout=60) as response, output.open("wb") as handle:
        shutil.copyfileobj(response, handle)
    return output


def download_media(
    url: str, output_dir: Path, browser: str | None = None
) -> tuple[Path, ...]:
    platform = validate_url(url)
    output_dir.mkdir(parents=True, exist_ok=True)
    if platform == "xiaoyuzhou":
        episode = fetch_xiaoyuzhou_episode(url)
        suffix = Path(urlparse(episode.audio_url).path).suffix or ".m4a"
        return (
            download_direct(
                episode.audio_url, output_dir / f"xiaoyuzhou-audio{suffix}"
            ),
        )
    template = str(output_dir / "%(title).80s [%(id)s].%(ext)s")
    command = [
        ytdlp_command(),
        "-f",
        "bv*+ba/b",
        "--merge-output-format",
        "mp4",
        "--no-playlist",
        "--no-warnings",
        "--print",
        "after_move:filepath",
        "-o",
        template,
        *cookie_args(browser),
        url,
    ]
    result = subprocess.run(
        command, capture_output=True, text=True, check=False, timeout=3600
    )
    files = tuple(
        Path(line.strip()) for line in result.stdout.splitlines() if line.strip()
    )
    if result.returncode != 0 or not files:
        detail = (result.stderr or result.stdout)[-600:]
        raise RuntimeError(failure_message("视频下载", detail))
    return files
