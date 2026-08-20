#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10,<3.14"
# dependencies = ["youtube-transcript-api>=1.2.3,<2"]
# ///
"""Unified transcript extraction for five video and podcast platforms."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

from asr import available_backends, transcribe
from formats import parse_subtitle_file, render_markdown, render_srt, safe_stem
from platforms import (
    download_audio,
    download_direct,
    download_media,
    download_platform_subtitles,
    fetch_xiaoyuzhou_episode,
    metadata,
    validate_url,
    youtube_api_captions,
)

PLATFORM_NAMES = {
    "youtube": "YouTube",
    "xiaoyuzhou": "小宇宙",
    "bilibili": "B站",
    "douyin": "抖音",
    "xiaohongshu": "小红书",
}
DEFAULT_LANGUAGES = (
    "zh-Hans",
    "zh-Hant",
    "zh",
    "zh-CN",
    "zh-TW",
    "en",
    "en-US",
    "en-GB",
)


def emit(payload: dict) -> None:
    print("SPACE_VIDEO_TRANSCRIPT_RESULT=" + json.dumps(payload, ensure_ascii=False))


def write_outputs(
    *,
    output_dir: Path,
    title: str,
    url: str,
    platform: str,
    language: str,
    method: str,
    segments: tuple,
) -> tuple[Path, Path | None]:
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = safe_stem(title)
    markdown_path = output_dir / f"{stem}_transcript.md"
    srt_path = output_dir / f"{stem}_subtitles.srt"
    markdown_path.write_text(
        render_markdown(
            title=title,
            url=url,
            platform=PLATFORM_NAMES[platform],
            language=language,
            method=method,
            segments=segments,
        ),
        encoding="utf-8",
    )
    if segments:
        srt_path.write_text(render_srt(segments), encoding="utf-8")
    else:
        srt_path = None
    return markdown_path, srt_path


def transcribe_url(args: argparse.Namespace) -> int:
    platform = validate_url(args.url)
    output_dir = Path(args.output_dir).expanduser().resolve()
    with tempfile.TemporaryDirectory(prefix="space-video-transcript-") as temp:
        work_dir = Path(temp)
        info = {"title": "视频逐字稿", "language": "unknown"}
        episode = None
        if platform == "xiaoyuzhou":
            episode = fetch_xiaoyuzhou_episode(args.url)
            info = {"title": episode.title, "language": "zh"}
        else:
            info = metadata(args.url)

        segments = ()
        method = ""
        if not args.force_asr and platform == "youtube":
            segments = youtube_api_captions(args.url, DEFAULT_LANGUAGES)
            if segments:
                method = "YouTube 平台字幕"
        if not args.force_asr and not segments and platform in {"youtube", "bilibili"}:
            files = download_platform_subtitles(
                args.url,
                work_dir,
                args.subtitle_languages,
                args.cookies_from_browser,
            )
            if files:
                segments = parse_subtitle_file(files[0])
                if segments:
                    method = "平台字幕（yt-dlp）"

        if not segments:
            if episode:
                suffix = Path(episode.audio_url.split("?", 1)[0]).suffix or ".m4a"
                audio = download_direct(episode.audio_url, work_dir / f"audio{suffix}")
            else:
                audio = download_audio(args.url, work_dir, args.cookies_from_browser)
            backend, segments = transcribe(audio, work_dir, args.asr_backend)
            method = f"ASR（{backend}）"

        if not segments:
            raise RuntimeError("没有提取到字幕内容")
        markdown_path, srt_path = write_outputs(
            output_dir=output_dir,
            title=str(info["title"]),
            url=args.url,
            platform=platform,
            language=str(info.get("language") or "unknown"),
            method=method,
            segments=segments,
        )
    emit(
        {
            "ok": True,
            "action": "transcribe",
            "platform": platform,
            "method": method,
            "title": info["title"],
            "markdown": str(markdown_path),
            "srt": str(srt_path) if srt_path else None,
            "segment_count": len(segments),
            "ask_download": True,
            "download_kind": "audio" if platform == "xiaoyuzhou" else "video",
        }
    )
    return 0


def download_url(args: argparse.Namespace) -> int:
    platform = validate_url(args.url)
    files = download_media(
        args.url,
        Path(args.output_dir).expanduser().resolve(),
        args.cookies_from_browser,
    )
    emit(
        {
            "ok": True,
            "action": "download",
            "platform": platform,
            "files": [str(path) for path in files],
        }
    )
    return 0


def doctor() -> int:
    checks = {
        "python>=3.10": sys.version_info >= (3, 10),
        "ffmpeg": bool(shutil.which("ffmpeg")),
        "ffprobe": bool(shutil.which("ffprobe")),
        "yt-dlp": bool(shutil.which("yt-dlp")),
        "ASR": bool(available_backends()),
    }
    for name, ok in checks.items():
        print(f"{'✓' if ok else '✗'} {name}")
    print("可用 ASR：" + (", ".join(available_backends()) or "无"))
    return 0 if all(checks.values()) else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    detect = subparsers.add_parser("detect", help="识别链接平台")
    detect.add_argument("url")

    extract = subparsers.add_parser("transcribe", help="提取字幕或逐字稿")
    extract.add_argument("url")
    extract.add_argument(
        "--output-dir", default=os.path.join(os.getcwd(), "video-transcripts")
    )
    extract.add_argument("--subtitle-languages", default="zh.*,zh-Hans,zh-CN,zh,en.*")
    extract.add_argument(
        "--asr-backend",
        choices=("auto", "groq", "whisper", "agent-reach"),
        default="auto",
    )
    extract.add_argument("--force-asr", action="store_true")
    extract.add_argument("--cookies-from-browser")

    download = subparsers.add_parser("download", help="下载用户确认后的原视频或音频")
    download.add_argument("url")
    download.add_argument(
        "--output-dir", default=os.path.join(os.getcwd(), "video-transcripts", "media")
    )
    download.add_argument("--cookies-from-browser")
    subparsers.add_parser("doctor", help="检查依赖")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        if args.command == "doctor":
            return doctor()
        if args.command == "detect":
            platform = validate_url(args.url)
            emit({"ok": True, "action": "detect", "platform": platform})
            return 0
        if args.command == "transcribe":
            return transcribe_url(args)
        return download_url(args)
    except (RuntimeError, ValueError) as exc:
        emit({"ok": False, "action": args.command, "error": str(exc)})
        print(f"错误：{exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
