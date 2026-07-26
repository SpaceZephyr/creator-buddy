#!/usr/bin/env python3
"""生成图交付前的机器体检。

检查项：
  1. 尺寸是否 1080x1440（3:4）；不是则报告实际比例与建议裁法
  2. 底色是否白（四角 + 边缘采样）
  3. 下 200px 安全区是否"干净"（会被角标/指示点压住，不该有主体内容）
  4. 导出 260px 宽缩略图，供人眼做可读性检验
  5. 文件体积是否 < 5MB

用法：
  python3 check_image.py cover.png
  python3 check_image.py cover.png --thumb thumb.png
  python3 check_image.py out/*.png        # 批量

退出码：0 全过；1 有 FAIL
"""
import argparse
import os
import sys

try:
    from PIL import Image, ImageStat
except ImportError:
    sys.exit("需要 Pillow：pip3 install Pillow")

W, H = 1080, 1440
SAFE_BOTTOM = 200
THUMB_W = 260


def check(path: str, thumb_path: str | None) -> bool:
    print(f"\n=== {path} ===")
    ok = True
    im = Image.open(path).convert("RGB")
    w, h = im.size

    # 1. 尺寸 / 比例
    ratio = w / h
    target = 3 / 4
    if (w, h) == (W, H):
        print(f"  [PASS] 尺寸 {w}x{h}（3:4 标准）")
    elif abs(ratio - target) < 0.01:
        print(f"  [WARN] 尺寸 {w}x{h}，比例对但不是 1080x1440 —— 交付前 resize")
    else:
        ok = False
        print(f"  [FAIL] 尺寸 {w}x{h}，比例 {ratio:.3f} ≠ 0.750")
        if ratio > target:
            need = int(h * target)
            print(f"         偏宽。居中裁到 {need}x{h} 再 resize 到 1080x1440，"
                  f"左右各切 {(w - need) // 2}px —— 先确认没切掉主体")
        else:
            need = int(w / target)
            print(f"         偏高。裁到 {w}x{need}（**从顶部往下裁**，保住上半部主视觉），"
                  f"再 resize 到 1080x1440")

    # 2. 白底
    pts = [(4, 4), (w - 5, 4), (4, h - 5), (w - 5, h - 5),
           (w // 2, 4), (w // 2, h - 5), (4, h // 2), (w - 5, h // 2)]
    vals = [im.getpixel(p) for p in pts]
    mins = min(min(v) for v in vals)
    if mins >= 240:
        print(f"  [PASS] 白底（边缘采样最暗通道 {mins}）")
    elif mins >= 215:
        print(f"  [WARN] 底色偏灰/米白（最暗通道 {mins}）—— 想要纯白就在 prompt 里加 "
              f"'pure white background #FFFFFF, no paper texture, no vignette'")
    else:
        ok = False
        print(f"  [FAIL] 不是白底（最暗通道 {mins}）。模型很可能自作主张加了底纹或大色块")

    # 3. 下安全区
    sb = int(SAFE_BOTTOM * h / H)
    band = im.crop((0, h - sb, w, h))
    stat = ImageStat.Stat(band)
    var = sum(stat.stddev) / 3
    mean = sum(stat.mean) / 3
    if mean < 200:
        ok = False
        print(f"  [FAIL] 下 {sb}px 安全区是大片深色（均值 {mean:.0f}）。这里会被多图指示点和"
              f"标题遮罩压住，深色块会糊成一坨。prompt 里加 "
              f"'keep the bottom 15% of the canvas as empty white space'")
    elif var < 8:
        print(f"  [PASS] 下 {sb}px 安全区干净（stddev {var:.1f}）")
    elif var < 22:
        print(f"  [WARN] 下 {sb}px 安全区有内容（stddev {var:.1f}）—— "
              f"确认那里没有文字/关键主体，会被多图指示点和标题遮罩压住")
    else:
        ok = False
        print(f"  [FAIL] 下 {sb}px 安全区堆了主体内容（stddev {var:.1f}）。重出，"
              f"prompt 里加 'keep the bottom 15% of the canvas empty white space'")

    # 4. 体积
    mb = os.path.getsize(path) / 1024 / 1024
    print(f"  [{'PASS' if mb < 5 else 'FAIL'}] 体积 {mb:.2f}MB（上限 5MB）")
    if mb >= 5:
        ok = False

    # 5. 缩略图
    tp = thumb_path or os.path.splitext(path)[0] + ".thumb.png"
    im.resize((THUMB_W, int(THUMB_W * h / w)), Image.LANCZOS).save(tp)
    print(f"  [ ?  ] 缩略图已出：{tp}")
    print(f"         **人眼必须看这张**：主标题一眼读全吗？读不全就砍字或加大字号重出。")
    return ok


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("images", nargs="+")
    ap.add_argument("--thumb", default=None, help="缩略图输出路径（仅单图时生效）")
    a = ap.parse_args()
    all_ok = True
    for p in a.images:
        all_ok &= check(p, a.thumb if len(a.images) == 1 else None)
    print("\n" + ("全部通过（缩略图仍需人眼确认）" if all_ok else "有 FAIL 项，不要交付"))
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
