#!/usr/bin/env python3
"""把一个 HTML 文件渲染成小红书封面尺寸的 PNG。

依赖：playwright（Python 包）+ 本机 Google Chrome（channel="chrome"）。
不需要 API Key，不需要 playwright install chromium —— 直接借用系统 Chrome。

用法：
    python3 render_cover.py --html cover.html --out cover.png
    python3 render_cover.py --html cover.html --out cover.png --ratio 1:1
    python3 render_cover.py --html cover.html --out cover.png --guides   # 叠加安全区参考线
    python3 render_cover.py --html-dir pages/ --out-dir out/            # 批量（组图）
"""

import argparse
import pathlib
import sys

RATIOS = {
    "3:4": (1080, 1440),
    "1:1": (1080, 1080),
    "4:5": (1080, 1350),
    "9:16": (1080, 1920),
}

# 安全区参考线：与 SKILL.md 的数值保持一致（以 1080 宽为基准）
GUIDE_CSS = """
#__xhs_guides__ {
  position: fixed; inset: 0; z-index: 999999; pointer-events: none;
  font: 500 20px/1 -apple-system, "PingFang SC", sans-serif;
}
#__xhs_guides__ .box {
  position: absolute; left: 80px; right: 80px; top: 100px; bottom: 200px;
  border: 2px dashed rgba(255,0,80,.85);
}
#__xhs_guides__ .bottom {
  position: absolute; left: 0; right: 0; bottom: 0; height: 200px;
  background: repeating-linear-gradient(45deg,
    rgba(255,0,80,.10) 0 12px, rgba(255,0,80,.02) 12px 24px);
  border-top: 2px dashed rgba(255,0,80,.85);
}
#__xhs_guides__ .tag {
  position: absolute; left: 84px; bottom: 208px; color: #ff0050;
  background: rgba(255,255,255,.85); padding: 4px 8px; border-radius: 4px;
}
"""

GUIDE_HTML = (
    '<div id="__xhs_guides__"><div class="bottom"></div><div class="box"></div>'
    '<div class="tag">安全区：左右 80 / 上 100 / 下 200</div></div>'
)


OVERFLOW_JS = """
() => {
  const out = [];
  const b = document.documentElement;
  if (document.body.scrollHeight > window.innerHeight + 2)
    out.push(`页面纵向溢出 ${document.body.scrollHeight - window.innerHeight}px`);
  if (document.body.scrollWidth > window.innerWidth + 2)
    out.push(`页面横向溢出 ${document.body.scrollWidth - window.innerWidth}px`);
  document.querySelectorAll('.stage, [data-fit]').forEach(el => {
    if (el.scrollHeight > el.clientHeight + 2)
      out.push(`.${el.className || 'data-fit'} 内容被裁掉 ${el.scrollHeight - el.clientHeight}px`);
  });
  return out;
}
"""


def check_overflow(page, html_path: pathlib.Path) -> list:
    """检测内容溢出/被裁。安全区靠 body padding 保证，这里查的是内容是否放得下。"""
    try:
        return page.evaluate(OVERFLOW_JS)
    except Exception:
        return []


def render_one(page, html_path: pathlib.Path, out_path: pathlib.Path, guides: bool):
    page.goto(html_path.resolve().as_uri(), wait_until="networkidle")
    if guides:
        page.add_style_tag(content=GUIDE_CSS)
        page.evaluate(
            "html => document.body.insertAdjacentHTML('beforeend', html)", GUIDE_HTML
        )
    page.wait_for_timeout(300)  # 等字体/动画落定
    problems = check_overflow(page, html_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(out_path), type="png")
    print(f"✓ {out_path}")
    for p in problems:
        print(f"  ⚠ {html_path.name}: {p}  → 砍字数 / 降字号 / 减目录条数，别硬塞")
    return problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--html", help="单个 HTML 文件")
    ap.add_argument("--html-dir", help="批量：目录下所有 *.html 按文件名排序渲染")
    ap.add_argument("--out", help="单图输出路径 (.png)")
    ap.add_argument("--out-dir", help="批量输出目录")
    ap.add_argument("--ratio", default="3:4", choices=list(RATIOS), help="默认 3:4")
    ap.add_argument("--width", type=int, help="覆盖宽度")
    ap.add_argument("--height", type=int, help="覆盖高度")
    ap.add_argument("--scale", type=float, default=1.0, help="设备像素比：2 = 2 倍图；0.24 = 信息流缩略图自检")
    ap.add_argument("--guides", action="store_true", help="叠加安全区参考线（仅自检用）")
    ap.add_argument("--strict", action="store_true", help="有溢出告警时以非 0 退出（可用于批量把关）")
    args = ap.parse_args()

    w, h = RATIOS[args.ratio]
    w, h = args.width or w, args.height or h

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.exit("缺少依赖：pip3 install playwright")

    jobs = []
    if args.html:
        if not args.out:
            sys.exit("--html 必须配 --out")
        jobs.append((pathlib.Path(args.html), pathlib.Path(args.out)))
    elif args.html_dir:
        if not args.out_dir:
            sys.exit("--html-dir 必须配 --out-dir")
        d = pathlib.Path(args.html_dir)
        for f in sorted(d.glob("*.html")):
            jobs.append((f, pathlib.Path(args.out_dir) / f"{f.stem}.png"))
        if not jobs:
            sys.exit(f"{d} 下没有 .html")
    else:
        sys.exit("需要 --html 或 --html-dir")

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome")
        page = browser.new_page(
            viewport={"width": w, "height": h}, device_scale_factor=args.scale
        )
        bad = 0
        for src, dst in jobs:
            if render_one(page, src, dst, args.guides):
                bad += 1
        browser.close()

    print(f"完成 {len(jobs)} 张，尺寸 {int(w*args.scale)}×{int(h*args.scale)}"
          + (f"，其中 {bad} 张有溢出告警" if bad else ""))
    if bad and args.strict:
        sys.exit(1)


if __name__ == "__main__":
    main()
