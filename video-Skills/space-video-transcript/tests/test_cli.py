import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "space_video_transcript.py"


class CliTests(unittest.TestCase):
    def test_detect_end_to_end(self):
        result = subprocess.run(
            [
                sys.executable,
                str(CLI),
                "detect",
                "https://www.bilibili.com/video/BV123",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0)
        marker = result.stdout.strip().split("=", 1)[1]
        self.assertEqual(json.loads(marker)["platform"], "bilibili")

    def test_invalid_url_end_to_end(self):
        result = subprocess.run(
            [sys.executable, str(CLI), "detect", "not-a-url"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn('"ok": false', result.stdout)

    def test_help_end_to_end(self):
        result = subprocess.run(
            [sys.executable, str(CLI), "--help"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("transcribe", result.stdout)
        self.assertIn("download", result.stdout)


if __name__ == "__main__":
    unittest.main()
