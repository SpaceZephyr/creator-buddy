#!/usr/bin/env python3
"""Validate a 3:4 social cover and optionally export a mobile-size preview."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image


TARGET_SIZE = (1080, 1440)
TARGET_RATIO = 3 / 4
MAX_BYTES = 5 * 1024 * 1024


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check aspect ratio, dimensions, format, and file size."
    )
    parser.add_argument("image", type=Path)
    parser.add_argument(
        "--thumbnail",
        action="store_true",
        help="Export a 260 px wide preview beside the source image.",
    )
    args = parser.parse_args()

    path = args.image.expanduser().resolve()
    if not path.is_file():
        print(f"ERROR: file not found: {path}", file=sys.stderr)
        return 2

    try:
        with Image.open(path) as image:
            image.load()
            width, height = image.size
            image_format = (image.format or "unknown").upper()
            ratio = width / height

            errors: list[str] = []
            warnings: list[str] = []

            if abs(ratio - TARGET_RATIO) > 0.005:
                errors.append(
                    f"aspect ratio is {width}:{height} ({ratio:.4f}), expected 3:4"
                )
            if (width, height) != TARGET_SIZE:
                warnings.append(
                    f"dimensions are {width}x{height}; recommended 1080x1440"
                )
            if image_format != "PNG":
                warnings.append(f"format is {image_format}; PNG is recommended")

            size_bytes = path.stat().st_size
            if size_bytes > MAX_BYTES:
                warnings.append(
                    f"file size is {size_bytes / 1024 / 1024:.2f} MB; "
                    "recommended maximum is 5 MB"
                )

            if args.thumbnail:
                preview_width = 260
                preview_height = round(height * preview_width / width)
                preview = image.convert("RGB")
                preview.thumbnail(
                    (preview_width, preview_height), Image.Resampling.LANCZOS
                )
                preview_path = path.with_name(f"{path.stem}-preview.jpg")
                preview.save(preview_path, "JPEG", quality=88, optimize=True)
                print(f"Preview: {preview_path}")

    except Exception as exc:
        print(f"ERROR: could not read image: {exc}", file=sys.stderr)
        return 2

    print(f"File: {path}")
    print(f"Format: {image_format}")
    print(f"Dimensions: {width}x{height}")
    print(f"Ratio: {ratio:.4f}")
    print(f"Size: {size_bytes / 1024:.1f} KB")

    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)

    if errors:
        return 1

    print("PASS: cover has a 3:4 aspect ratio")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
