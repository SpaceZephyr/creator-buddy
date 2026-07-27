#!/usr/bin/env python3
"""检查小红书信息图的基础交付规格，并导出信息流缩略图。

检查：
1. 是否为 3:4，是否为推荐的 1080×1440。
2. 画布边缘是否保持白色或极浅色。
3. 文件是否小于 5MB。
4. 导出 260px 宽缩略图供人工检查标题、错字和信息层级。

用法：
  python3 check_image.py 01-cover.png
  python3 check_image.py out/*.png
"""

from __future__ import annotations

import argparse
import os
import sys

try:
    from PIL import Image, ImageStat
except ImportError:
    sys.exit("需要 Pillow：python3 -m pip install Pillow")

TARGET_W = 1080
TARGET_H = 1440
TARGET_RATIO = 3 / 4
THUMB_W = 260


def edge_lightness(image: Image.Image) -> float:
    """Return the mean RGB brightness of thin strips around the canvas."""
    w, h = image.size
    strip = max(2, round(min(w, h) * 0.01))
    regions = [
        image.crop((0, 0, w, strip)),
        image.crop((0, h - strip, w, h)),
        image.crop((0, 0, strip, h)),
        image.crop((w - strip, 0, w, h)),
    ]
    means = []
    for region in regions:
        stat = ImageStat.Stat(region)
        means.append(sum(stat.mean[:3]) / 3)
    return sum(means) / len(means)


def check(path: str, thumb_path: str | None) -> bool:
    print(f"\n=== {path} ===")
    ok = True
    image = Image.open(path).convert("RGB")
    w, h = image.size
    ratio = w / h

    if abs(ratio - TARGET_RATIO) <= 0.005:
        label = "PASS"
        size_note = "推荐尺寸" if (w, h) == (TARGET_W, TARGET_H) else "比例正确，发布前缩放到 1080×1440"
    else:
        label = "FAIL"
        size_note = f"比例 {ratio:.3f}，目标 0.750；优先重出，或确认安全后裁切"
        ok = False
    print(f"  [{label}] 画布 {w}×{h}：{size_note}")

    brightness = edge_lightness(image)
    if brightness >= 230:
        print(f"  [PASS] 边缘保持浅色（平均亮度 {brightness:.0f}）")
    elif brightness >= 185:
        print(f"  [WARN] 边缘含装饰或文字（平均亮度 {brightness:.0f}），确认没有主体被裁")
    else:
        print(f"  [FAIL] 边缘过暗或主体贴边（平均亮度 {brightness:.0f}）")
        ok = False

    size_mb = os.path.getsize(path) / 1024 / 1024
    if size_mb < 5:
        print(f"  [PASS] 文件 {size_mb:.2f}MB")
    else:
        print(f"  [FAIL] 文件 {size_mb:.2f}MB，超过 5MB")
        ok = False

    destination = thumb_path or os.path.splitext(path)[0] + ".thumb.png"
    thumb_h = round(THUMB_W * h / w)
    image.resize((THUMB_W, thumb_h), Image.Resampling.LANCZOS).save(destination)
    print(f"  [人工] 缩略图：{destination}")
    print("         检查：主标题是否一眼读完、中文是否正确、页面是否拥挤。")
    return ok


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("images", nargs="+")
    parser.add_argument("--thumb", default=None, help="单张图片的缩略图输出路径")
    args = parser.parse_args()

    all_ok = True
    for image_path in args.images:
        if not os.path.isfile(image_path):
            print(f"\n[FAIL] 文件不存在：{image_path}")
            all_ok = False
            continue
        one_thumb = args.thumb if len(args.images) == 1 else None
        all_ok = check(image_path, one_thumb) and all_ok

    print("\n" + ("基础规格通过；文字和版式仍需人工复核。" if all_ok else "存在失败项，不要作为完成稿交付。"))
    raise SystemExit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
