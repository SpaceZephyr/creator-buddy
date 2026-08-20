import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from formats import Segment, parse_subtitle_text, render_markdown, render_srt, safe_stem


class FormatTests(unittest.TestCase):
    def test_parse_srt_and_remove_duplicate_cues(self):
        content = """1
00:00:01,000 --> 00:00:03,000
你好 <b>世界</b>

2
00:00:03,000 --> 00:00:04,000
你好 世界

3
00:00:04,000 --> 00:00:06,000
第二句
"""
        self.assertEqual(
            parse_subtitle_text(content),
            (Segment(1.0, 3.0, "你好 世界"), Segment(4.0, 6.0, "第二句")),
        )

    def test_parse_vtt(self):
        content = "WEBVTT\n\n00:01.000 --> 00:03.500\nhello\nworld\n"
        self.assertEqual(
            parse_subtitle_text(content), (Segment(1.0, 3.5, "hello world"),)
        )

    def test_render_outputs(self):
        segments = (Segment(1.2, 2.5, "测试"),)
        self.assertIn("00:00:01,200 --> 00:00:02,500", render_srt(segments))
        markdown = render_markdown(
            title="标题",
            url="https://example.com",
            platform="YouTube",
            language="zh",
            method="平台字幕",
            segments=segments,
        )
        self.assertIn("# 标题", markdown)
        self.assertIn("**[00:00:01]** 测试", markdown)

    def test_safe_stem(self):
        self.assertEqual(safe_stem("a/b: c?"), "a-b-c")


if __name__ == "__main__":
    unittest.main()
