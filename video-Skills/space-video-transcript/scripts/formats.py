"""Subtitle parsing and rendering helpers."""

from __future__ import annotations

import re
from dataclasses import dataclass
from html import unescape
from pathlib import Path


@dataclass(frozen=True)
class Segment:
    start: float
    end: float
    text: str


_TAG_RE = re.compile(r"<[^>]+>")
_TIMING_RE = re.compile(
    r"(?P<start>\d{1,2}:\d{2}:\d{2}[,.]\d{3}|\d{1,2}:\d{2}[,.]\d{3})\s*-->\s*"
    r"(?P<end>\d{1,2}:\d{2}:\d{2}[,.]\d{3}|\d{1,2}:\d{2}[,.]\d{3})"
)


def clean_text(value: str) -> str:
    text = unescape(_TAG_RE.sub("", value)).replace("\u200b", "")
    lines = [re.sub(r"\s+", " ", line).strip() for line in text.splitlines()]
    unique: list[str] = []
    for line in lines:
        if line and (not unique or line != unique[-1]):
            unique.append(line)
    return " ".join(unique).strip()


def parse_clock(value: str) -> float:
    parts = value.replace(",", ".").split(":")
    if len(parts) == 2:
        minutes, seconds = parts
        return int(minutes) * 60 + float(seconds)
    hours, minutes, seconds = parts
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)


def parse_subtitle_text(content: str) -> tuple[Segment, ...]:
    normalized = content.replace("\r\n", "\n").replace("\r", "\n")
    segments: list[Segment] = []
    lines = normalized.split("\n")
    index = 0
    while index < len(lines):
        match = _TIMING_RE.search(lines[index])
        if not match:
            index += 1
            continue
        text_lines: list[str] = []
        index += 1
        while index < len(lines) and lines[index].strip():
            text_lines.append(lines[index])
            index += 1
        text = clean_text("\n".join(text_lines))
        if text:
            candidate = Segment(
                start=parse_clock(match.group("start")),
                end=parse_clock(match.group("end")),
                text=text,
            )
            if not segments or candidate.text != segments[-1].text:
                segments.append(candidate)
        index += 1
    return tuple(segments)


def parse_subtitle_file(path: Path) -> tuple[Segment, ...]:
    return parse_subtitle_text(path.read_text(encoding="utf-8", errors="replace"))


def clock(seconds: float, *, srt: bool = False) -> str:
    millis = max(0, round(seconds * 1000))
    hours, remainder = divmod(millis, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    secs, ms = divmod(remainder, 1000)
    separator = "," if srt else "."
    return f"{hours:02d}:{minutes:02d}:{secs:02d}{separator}{ms:03d}"


def render_srt(segments: tuple[Segment, ...]) -> str:
    blocks = [
        f"{index}\n{clock(item.start, srt=True)} --> {clock(item.end, srt=True)}\n{item.text}"
        for index, item in enumerate(segments, start=1)
    ]
    return "\n\n".join(blocks) + ("\n" if blocks else "")


def render_markdown(
    *,
    title: str,
    url: str,
    platform: str,
    language: str,
    method: str,
    segments: tuple[Segment, ...],
) -> str:
    header = [
        f"# {title}",
        "",
        f"> 平台：{platform}  ",
        f"> 来源：{url}  ",
        f"> 语言：{language or 'unknown'}  ",
        f"> 提取方式：{method}",
        "",
        "## 逐字稿",
        "",
    ]
    body = [f"**[{clock(item.start)[:-4]}]** {item.text}" for item in segments]
    return "\n".join(header + body).rstrip() + "\n"


def safe_stem(value: str, fallback: str = "transcript") -> str:
    cleaned = re.sub(r"[\\/:*?\"<>|\s]+", "-", value).strip("-.")
    return (cleaned[:80] or fallback).strip("-.")
