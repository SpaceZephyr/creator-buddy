import io
import json
import sys
import unittest
from argparse import Namespace
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import space_video_transcript as cli
from formats import Segment
from platforms import Episode


def args(url, output_dir, **overrides):
    values = {
        "url": url,
        "output_dir": output_dir,
        "force_asr": False,
        "subtitle_languages": "zh.*,en.*",
        "cookies_from_browser": None,
        "asr_backend": "auto",
    }
    values.update(overrides)
    return Namespace(**values)


class WorkflowTests(unittest.TestCase):
    def test_youtube_caption_workflow_and_download_prompt_marker(self):
        with TemporaryDirectory() as temp:
            segments = (Segment(0, 2, "平台字幕"),)
            output = io.StringIO()
            with (
                patch(
                    "space_video_transcript.metadata",
                    return_value={"title": "测试视频", "language": "zh"},
                ),
                patch(
                    "space_video_transcript.youtube_api_captions", return_value=segments
                ),
                redirect_stdout(output),
            ):
                self.assertEqual(
                    cli.transcribe_url(args("https://youtu.be/dQw4w9WgXcQ", temp)), 0
                )
            payload = json.loads(output.getvalue().strip().split("=", 1)[1])
            self.assertTrue(payload["ask_download"])
            self.assertEqual(payload["download_kind"], "video")
            self.assertTrue(Path(payload["markdown"]).exists())
            self.assertTrue(Path(payload["srt"]).exists())

    def test_douyin_asr_fallback(self):
        with TemporaryDirectory() as temp:
            audio = Path(temp) / "audio.mp3"
            audio.write_bytes(b"audio")
            segments = (Segment(0, 2, "转写结果"),)
            with (
                patch(
                    "space_video_transcript.metadata",
                    return_value={"title": "抖音视频", "language": "zh"},
                ),
                patch("space_video_transcript.download_audio", return_value=audio),
                patch(
                    "space_video_transcript.transcribe",
                    return_value=("whisper", segments),
                ),
                redirect_stdout(io.StringIO()),
            ):
                self.assertEqual(
                    cli.transcribe_url(args("https://v.douyin.com/abc", temp)), 0
                )

    def test_xiaoyuzhou_asr_and_audio_marker(self):
        with TemporaryDirectory() as temp:
            episode = Episode("播客标题", "https://media.xyzcdn.net/a.m4a", "节目")
            audio = Path(temp) / "audio.m4a"
            audio.write_bytes(b"audio")
            output = io.StringIO()
            with (
                patch(
                    "space_video_transcript.fetch_xiaoyuzhou_episode",
                    return_value=episode,
                ),
                patch("space_video_transcript.download_direct", return_value=audio),
                patch(
                    "space_video_transcript.transcribe",
                    return_value=("agent-reach", (Segment(0, 5, "播客内容"),)),
                ),
                redirect_stdout(output),
            ):
                cli.transcribe_url(
                    args("https://www.xiaoyuzhoufm.com/episode/abc", temp)
                )
            payload = json.loads(output.getvalue().strip().split("=", 1)[1])
            self.assertEqual(payload["download_kind"], "audio")

    def test_download_workflow(self):
        with TemporaryDirectory() as temp:
            media = Path(temp) / "video.mp4"
            with (
                patch("space_video_transcript.download_media", return_value=(media,)),
                redirect_stdout(io.StringIO()),
            ):
                self.assertEqual(
                    cli.download_url(
                        args("https://www.bilibili.com/video/BV123", temp)
                    ),
                    0,
                )

    def test_doctor_and_main_detect(self):
        with (
            patch("space_video_transcript.shutil.which", return_value="/bin/tool"),
            patch(
                "space_video_transcript.available_backends", return_value=("whisper",)
            ),
            redirect_stdout(io.StringIO()),
        ):
            self.assertEqual(cli.doctor(), 0)
        with (
            patch.object(sys, "argv", ["tool", "detect", "https://xhslink.com/a"]),
            redirect_stdout(io.StringIO()),
        ):
            self.assertEqual(cli.main(), 0)


if __name__ == "__main__":
    unittest.main()
