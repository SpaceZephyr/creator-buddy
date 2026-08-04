#!/usr/bin/env bash
# 把各帧片段按顺序硬切拼成一条 B-roll。
# 用法: bash concat.sh out.mp4 frame01.mp4 frame02.mp4 ...
set -euo pipefail
OUT="${1:?需要输出路径}"; shift
[ $# -ge 1 ] || { echo "至少给一个片段"; exit 1; }
TMP=$(mktemp)
for f in "$@"; do echo "file '$(python3 -c "import os,sys;print(os.path.abspath(sys.argv[1]))" "$f")'" >> "$TMP"; done
# 统一重编码，保证不同来源片段能无缝拼接（硬切）
ffmpeg -y -f concat -safe 0 -i "$TMP" \
  -c:v libx264 -preset veryfast -crf 20 -pix_fmt yuv420p -r 30 \
  -c:a aac -b:a 128k "$OUT" 2>/dev/null
rm -f "$TMP"
echo "✅ $OUT"
ffprobe -v error -show_entries format=duration -of default=nk=1:nw=1 "$OUT" | xargs printf "总时长 %.1fs\n"
