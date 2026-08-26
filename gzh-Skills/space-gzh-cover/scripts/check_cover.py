#!/usr/bin/env python3
"""校验公众号 2.35:1 头图，并导出分享场景的裁切预览。

公众号封面会被裁两次：
  1. 消息列表 / 文章顶部 —— 显示完整 2.35:1
  2. 分享到朋友圈 / 聊天 —— 只抓取正中央的 1:1 方形

第 2 种裁切只保留宽度的 1/2.35（约 42.6%）。标题铺满全宽的封面，
分享出去两头就没了。本脚本把那个方形裁出来，让你直接看见。
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw
except ImportError:  # pragma: no cover
    print("ERROR: 需要 Pillow，请先 pip install Pillow", file=sys.stderr)
    raise SystemExit(2)


TARGET_RATIO = 2.35
TARGET_SIZE = (1175, 500)
RATIO_TOLERANCE = 0.01
MAX_BYTES = 5 * 1024 * 1024


def safe_zone(width: int, height: int) -> tuple[int, int, int, int]:
    """正中央的 1:1 安全区（分享时唯一保得住的部分）。"""
    side = min(width, height)
    left = (width - side) // 2
    top = (height - side) // 2
    return left, top, left + side, top + side


def main() -> int:
    ap = argparse.ArgumentParser(description="校验公众号 2.35:1 封面并导出裁切预览")
    ap.add_argument("image", type=Path)
    ap.add_argument("--share-preview", action="store_true",
                    help="导出分享场景看到的正中央 1:1 裁切图")
    ap.add_argument("--safe-zone", action="store_true",
                    help="导出带安全区标注的图，用于检查标题是否越界")
    ap.add_argument("--thumbnail", action="store_true",
                    help="导出 260px 宽缩略图，检查信息流下的可读性")
    args = ap.parse_args()

    path = args.image.expanduser().resolve()
    if not path.is_file():
        print(f"ERROR: 文件不存在: {path}", file=sys.stderr)
        return 2

    errors: list[str] = []
    warnings: list[str] = []

    try:
        with Image.open(path) as im:
            im.load()
            w, h = im.size
            fmt = (im.format or "unknown").upper()
            ratio = w / h

            if abs(ratio - TARGET_RATIO) > RATIO_TOLERANCE:
                errors.append(
                    f"比例是 {w}:{h}（{ratio:.4f}），期望 2.35:1。"
                    f"上传时会被微信自行裁切"
                )
            if (w, h) != TARGET_SIZE:
                warnings.append(f"尺寸是 {w}x{h}，推荐 {TARGET_SIZE[0]}x{TARGET_SIZE[1]}")
            if fmt != "PNG":
                warnings.append(f"格式是 {fmt}，推荐 PNG")

            size_bytes = path.stat().st_size
            if size_bytes > MAX_BYTES:
                warnings.append(f"文件 {size_bytes / 1024 / 1024:.2f} MB，建议不超过 5 MB")

            l, t, r, b = safe_zone(w, h)
            pct = (r - l) / w * 100

            if args.share_preview:
                out = path.with_name(f"{path.stem}-share-1x1.jpg")
                im.convert("RGB").crop((l, t, r, b)).save(out, "JPEG", quality=90, optimize=True)
                print(f"分享预览（朋友圈看到的）: {out}")

            if args.safe_zone:
                marked = im.convert("RGB").copy()
                d = ImageDraw.Draw(marked, "RGBA")
                # 左右两翼压暗——这两块在分享时会被切掉
                d.rectangle([0, 0, l, h], fill=(0, 0, 0, 110))
                d.rectangle([r, 0, w, h], fill=(0, 0, 0, 110))
                d.rectangle([l, t, r - 1, b - 1], outline=(255, 60, 60), width=4)
                out = path.with_name(f"{path.stem}-safezone.jpg")
                marked.save(out, "JPEG", quality=90, optimize=True)
                print(f"安全区标注（压暗处分享时会被切掉）: {out}")

            if args.thumbnail:
                th = im.convert("RGB")
                th.thumbnail((260, round(h * 260 / w)), Image.Resampling.LANCZOS)
                out = path.with_name(f"{path.stem}-thumb.jpg")
                th.save(out, "JPEG", quality=88, optimize=True)
                print(f"信息流缩略图: {out}")

    except Exception as exc:
        print(f"ERROR: 无法读取图片: {exc}", file=sys.stderr)
        return 2

    print(f"文件: {path}")
    print(f"格式: {fmt}")
    print(f"尺寸: {w}x{h}")
    print(f"比例: {ratio:.4f}")
    print(f"体积: {size_bytes / 1024:.1f} KB")
    print(f"分享安全区: x {l}–{r}（居中 {r - l}px，占宽度 {pct:.1f}%）")
    print("  → 主标题和主体必须落在这个范围内，否则分享到朋友圈会被切掉")

    for m in warnings:
        print(f"WARNING: {m}")
    for m in errors:
        print(f"ERROR: {m}", file=sys.stderr)

    if errors:
        return 1

    print("PASS: 比例符合公众号头图 2.35:1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
