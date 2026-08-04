#!/usr/bin/env bash
# libtv Agent 图生视频一站式：上传首帧图 → 发"图生视频"消息 → 轮询 → 下载 MP4。
# 复用全局 libtv-skill 的脚本。
# 用法:
#   export LIBTV_ACCESS_KEY=xxx
#   bash libtv_i2v.sh --image frame01.png --prompt "手绘线稿逐笔画出，元素依次生长，白底，镜头静止" --out clip.mp4
set -euo pipefail

LIBTV_DIR="$HOME/.claude/skills/libtv-skill/scripts"
IMAGE="" PROMPT="" OUT="" SESSION=""
while [ $# -gt 0 ]; do case "$1" in
  --image) IMAGE="$2";shift 2;; --prompt) PROMPT="$2";shift 2;;
  --out) OUT="$2";shift 2;; --session) SESSION="$2";shift 2;;
  *) echo "未知参数 $1";exit 1;; esac; done
: "${PROMPT:?需要 --prompt}"; : "${OUT:?需要 --out}"
: "${LIBTV_ACCESS_KEY:?需要 export LIBTV_ACCESS_KEY}"
[ -f "$LIBTV_DIR/create_session.py" ] || { echo "找不到 libtv-skill，先安装它"; exit 1; }

MSG="$PROMPT"
if [ -n "$IMAGE" ]; then
  echo "上传首帧图 $IMAGE ..."
  IMG_URL=$(python3 "$LIBTV_DIR/upload_file.py" "$IMAGE" | python3 -c 'import sys,json;print(json.load(sys.stdin)["url"])')
  echo "  OSS: $IMG_URL"
  MSG="参考这张图做图生视频。图片：$IMG_URL 。要求：$PROMPT"
fi

echo "发送生视频消息 ..."
if [ -n "$SESSION" ]; then
  python3 "$LIBTV_DIR/create_session.py" "$MSG" --session-id "$SESSION" >/tmp/libtv_cs.json
else
  python3 "$LIBTV_DIR/create_session.py" "$MSG" >/tmp/libtv_cs.json
  SESSION=$(python3 -c 'import json;print(json.load(open("/tmp/libtv_cs.json"))["sessionId"])')
fi
echo "  sessionId: $SESSION"

echo "轮询结果（最多 ~10 分钟）..."
SEQ=0
for i in $(seq 1 120); do
  sleep 5
  python3 "$LIBTV_DIR/query_session.py" "$SESSION" --after-seq "$SEQ" >/tmp/libtv_q.json 2>/dev/null || continue
  # 从消息里找 mp4 URL
  VURL=$(grep -oE 'https?://[^"[:space:]]+\.mp4' /tmp/libtv_q.json | head -1 || true)
  if [ -n "$VURL" ]; then
    echo "  拿到视频: $VURL"
    curl -sL -o "$OUT" "$VURL"
    echo "✅ $OUT"
    exit 0
  fi
  printf "  ...等待中 (%d)\r" "$i"
done
echo "轮询超时，去项目画布看：https://www.liblib.tv/canvas"; exit 1
