#!/usr/bin/env python3
"""WCAG 对比度计算器 —— 小红书图文交付前验证字色/底色是否达标。

硬指标（见 SKILL.md 二）：主标题 vs 背景 ≥ 7:1，副标题/目录条目 ≥ 4.5:1。

用法：
    python3 check_contrast.py "#1A1A18" "#F6F5F4"              # 单对
    python3 check_contrast.py --pairs "#1A1A18/#F6F5F4:title" "#5F5B55/#F6F5F4:sub"
    python3 check_contrast.py --tokens cover.html              # 从 :root 里抓 token 自动全查

只依赖标准库。渐变底色请用**较浅的那一端**（浅底深字）或**较深的那一端**（深底浅字）来算，
也就是取对比度最差的一端，别拿平均值糊弄。
"""

import argparse
import re
import sys

ROLE_MIN = {"title": 7.0, "sub": 4.5, "toc": 4.5, "tag": 4.5, "badge": 3.0, "handle": 3.0}


def parse_hex(s: str):
    s = s.strip().lstrip("#")
    if len(s) == 3:
        s = "".join(c * 2 for c in s)
    if len(s) != 6:
        raise ValueError(f"不是合法的 hex 颜色：{s}")
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


def luminance(rgb):
    def ch(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (ch(v) for v in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(fg: str, bg: str) -> float:
    a, b = luminance(parse_hex(fg)), luminance(parse_hex(bg))
    hi, lo = max(a, b), min(a, b)
    return (hi + 0.05) / (lo + 0.05)


def report(fg, bg, role=None) -> bool:
    r = ratio(fg, bg)
    need = ROLE_MIN.get(role or "", 4.5)
    ok = r >= need
    label = f"[{role}]" if role else ""
    print(f"{'✓' if ok else '✗'} {fg} on {bg} {label} = {r:.2f}:1  (需 ≥ {need}:1)")
    if not ok:
        print(f"    → 不达标。加深字色 / 提亮底色，或给文字块加实色底再重算。")
    return ok


TOKEN_RE = re.compile(r"--([a-z0-9-]+)\s*:\s*(#[0-9A-Fa-f]{3,6})\s*;")
# token 名 → (前景 token, 背景 token, 角色)
AUTO_PAIRS = [
    ("ink", "canvas", "title"),
    ("ink-2", "canvas", "sub"),
    ("ink-3", "canvas", "handle"),
    ("accent", "canvas", "tag"),
    ("on-accent", "accent", "tag"),
]


def from_tokens(path: str) -> bool:
    text = open(path, encoding="utf-8").read()
    tok = dict(TOKEN_RE.findall(text))
    if not tok:
        sys.exit(f"{path} 里没找到 --xxx: #hex 形式的 token（渐变/rgba 值请手动传两个颜色）")
    all_ok = True
    for fg, bg, role in AUTO_PAIRS:
        if fg in tok and bg in tok:
            all_ok &= report(tok[fg], tok[bg], role)
        else:
            print(f"– 跳过 {fg}/{bg}：token 缺失或非 hex（rgba/渐变需手动检查）")
    return all_ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("colors", nargs="*", help="前景色 背景色")
    ap.add_argument("--pairs", nargs="*", default=[], help='形如 "#111/#fff:title"')
    ap.add_argument("--tokens", help="从 HTML/CSS 的 :root token 自动检查")
    a = ap.parse_args()

    ok = True
    if a.tokens:
        ok &= from_tokens(a.tokens)
    for p in a.pairs:
        pair, _, role = p.partition(":")
        fg, _, bg = pair.partition("/")
        ok &= report(fg, bg, role or None)
    if len(a.colors) == 2:
        ok &= report(a.colors[0], a.colors[1], "title")
    elif a.colors:
        sys.exit("直接传颜色时需要正好 2 个：前景 背景")
    if not (a.tokens or a.pairs or a.colors):
        ap.print_help()
        return
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
