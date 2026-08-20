import json
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import platforms
from platforms import (
    detect_platform,
    extract_episode_from_html,
    validate_url,
    youtube_id,
)


class PlatformTests(unittest.TestCase):
    def test_detect_supported_platforms(self):
        cases = {
            "https://youtu.be/dQw4w9WgXcQ": "youtube",
            "https://www.xiaoyuzhoufm.com/episode/abc123": "xiaoyuzhou",
            "https://www.bilibili.com/video/BV123": "bilibili",
            "https://v.douyin.com/abc": "douyin",
            "https://xhslink.com/a1b2": "xiaohongshu",
        }
        for url, expected in cases.items():
            with self.subTest(url=url):
                self.assertEqual(detect_platform(url), expected)

    def test_reject_show_and_unknown_pages(self):
        with self.assertRaisesRegex(ValueError, "单集"):
            validate_url("https://www.xiaoyuzhoufm.com/podcast/abc")
        with self.assertRaisesRegex(ValueError, "仅支持"):
            validate_url("https://example.com/video")

    def test_youtube_id(self):
        self.assertEqual(youtube_id("https://youtu.be/dQw4w9WgXcQ"), "dQw4w9WgXcQ")
        self.assertEqual(
            youtube_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=1"),
            "dQw4w9WgXcQ",
        )
        with self.assertRaisesRegex(ValueError, "视频 ID"):
            youtube_id("https://www.youtube.com/channel/example")

    def test_extract_episode_next_data(self):
        html = """<html><head><meta property="og:title" content="一期播客"></head>
        <script id="__NEXT_DATA__" type="application/json">
        {"props":{"episode":{"title":"内部标题","enclosureUrl":"https://media.xyzcdn.net/a.m4a","podcast":{"title":"节目名"}}}}
        </script></html>"""
        episode = extract_episode_from_html(html)
        self.assertEqual(episode.title, "一期播客")
        self.assertEqual(episode.audio_url, "https://media.xyzcdn.net/a.m4a")
        self.assertEqual(episode.podcast, "节目名")

    def test_extract_episode_regex_fallback(self):
        html = '<meta property="og:title" content="标题"><p>https://media.xyzcdn.net/fallback.mp3</p>'
        episode = extract_episode_from_html(html)
        self.assertEqual(episode.title, "标题")
        self.assertEqual(episode.audio_url, "https://media.xyzcdn.net/fallback.mp3")
        with self.assertRaisesRegex(RuntimeError, "无法解析"):
            extract_episode_from_html("<html></html>")

    def test_ytdlp_command_and_cookie_args(self):
        with patch("platforms.shutil.which", return_value="/bin/yt-dlp"):
            self.assertEqual(platforms.ytdlp_command(), "/bin/yt-dlp")
        with (
            patch("platforms.shutil.which", return_value=None),
            self.assertRaisesRegex(RuntimeError, "未找到 yt-dlp"),
        ):
            platforms.ytdlp_command()
        self.assertEqual(
            platforms.cookie_args("chrome"), ["--cookies-from-browser", "chrome"]
        )
        self.assertEqual(platforms.cookie_args(None), [])
        self.assertIn(
            "--cookies-from-browser chrome",
            platforms.failure_message(
                "视频下载", "Sign in; use --cookies-from-browser"
            ),
        )

    def test_metadata_success_and_fallbacks(self):
        good = Mock(
            returncode=0, stdout=json.dumps({"title": "视频", "language": "zh"})
        )
        with (
            patch("platforms.ytdlp_command", return_value="yt-dlp"),
            patch("platforms.subprocess.run", return_value=good),
        ):
            self.assertEqual(
                platforms.metadata("https://youtu.be/dQw4w9WgXcQ")["title"], "视频"
            )
        failed = Mock(returncode=1, stdout="", stderr="error")
        with (
            patch("platforms.ytdlp_command", return_value="yt-dlp"),
            patch("platforms.subprocess.run", return_value=failed),
        ):
            self.assertEqual(
                platforms.metadata("https://youtu.be/dQw4w9WgXcQ")["title"],
                "视频逐字稿",
            )

    def test_subtitle_and_audio_download_helpers(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)

            def subtitle_run(*_args, **_kwargs):
                (root / "platform.zh.srt").write_text(
                    "1\n00:00:00,000 --> 00:00:01,000\n你好\n", encoding="utf-8"
                )
                return Mock(returncode=0, stdout="", stderr="")

            with (
                patch("platforms.ytdlp_command", return_value="yt-dlp"),
                patch("platforms.subprocess.run", side_effect=subtitle_run),
            ):
                self.assertEqual(
                    len(
                        platforms.download_platform_subtitles(
                            "https://youtu.be/x", root, "zh"
                        )
                    ),
                    1,
                )

            def audio_run(*_args, **_kwargs):
                (root / "audio.mp3").write_bytes(b"audio")
                return Mock(returncode=0, stdout="", stderr="")

            with (
                patch("platforms.ytdlp_command", return_value="yt-dlp"),
                patch("platforms.subprocess.run", side_effect=audio_run),
            ):
                self.assertEqual(
                    platforms.download_audio("https://v.douyin.com/x", root).name,
                    "audio.mp3",
                )


if __name__ == "__main__":
    unittest.main()
