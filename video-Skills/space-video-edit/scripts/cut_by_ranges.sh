#!/usr/bin/env bash
# 按「保留区间」无损拼接口播视频，避免逐段删导致的误差累积。
#
# 用法:
#   bash cut_by_ranges.sh <输入.mp4> <keep_ranges.json> <输出.mp4>
#
# keep_ranges.json 格式（单位秒，只列要保留的区间）:
#   [ {"start": 0.0, "end": 12.3}, {"start": 13.1, "end": 40.7} ]
#
# 依赖: ffmpeg, jq

set -euo pipefail

IN="${1:?需要输入视频}"
RANGES="${2:?需要 keep_ranges.json}"
OUT="${3:?需要输出路径}"

command -v ffmpeg >/dev/null || { echo "缺 ffmpeg"; exit 1; }
command -v jq >/dev/null || { echo "缺 jq"; exit 1; }

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

LIST="$TMP/concat.txt"
: > "$LIST"

n=$(jq 'length' "$RANGES")
echo "保留区间数: $n"

for i in $(seq 0 $((n-1))); do
  s=$(jq -r ".[$i].start" "$RANGES")
  e=$(jq -r ".[$i].end" "$RANGES")
  seg="$TMP/seg_$i.mp4"
  # 精确剪切: 放在 -i 后做精确到帧的裁切并重编码，保证拼接点无花屏
  ffmpeg -y -i "$IN" -ss "$s" -to "$e" \
    -c:v libx264 -preset veryfast -crf 18 -c:a aac -avoid_negative_ts make_zero \
    "$seg" 2>/dev/null
  echo "file '$seg'" >> "$LIST"
  printf "  段 %2d: %s → %s\n" "$i" "$s" "$e"
done

ffmpeg -y -f concat -safe 0 -i "$LIST" -c copy "$OUT" 2>/dev/null
echo "✅ 输出: $OUT"
ffprobe -v error -show_entries format=duration -of default=nk=1:nw=1 "$OUT" \
  | xargs printf "成片时长: %.2fs\n"
