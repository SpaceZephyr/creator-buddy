#!/usr/bin/env bash
# 把 BGM(+可选旁白) 混进视频：循环/裁切对齐 → 响度归一 → 压音ducking → 淡入淡出。
# 用法:
#   bash mix.sh --video in.mp4 --bgm bgm.mp3 [--voice voice.mp3] --out out.mp4 \
#        [--bgm-db -18] [--fade 1.0] [--duck]
# 说明:
#   前景音 = --voice(有则用) 或 视频自带音轨(有则用)；BGM 垫在其下。
#   --duck: 前景一响 BGM 自动下沉（sidechaincompress）。无前景音时忽略。
set -euo pipefail

VIDEO="" BGM="" VOICE="" OUT="" BGM_DB="" FADE="1.0" DUCK=0
while [ $# -gt 0 ]; do case "$1" in
  --video) VIDEO="$2";shift 2;; --bgm) BGM="$2";shift 2;;
  --voice) VOICE="$2";shift 2;; --out) OUT="$2";shift 2;;
  --bgm-db) BGM_DB="$2";shift 2;; --fade) FADE="$2";shift 2;;
  --duck) DUCK=1;shift;; *) echo "未知参数 $1";exit 1;; esac; done
: "${VIDEO:?需要 --video}"; : "${BGM:?需要 --bgm}"; : "${OUT:?需要 --out}"

DUR=$(ffprobe -v error -show_entries format=duration -of default=nk=1:nw=1 "$VIDEO")
FOUT=$(echo "$DUR - $FADE" | bc -l)
# 视频是否自带音轨
HAS_VA=$(ffprobe -v error -select_streams a -show_entries stream=index -of csv=p=0 "$VIDEO" | head -1)

# 前景音来源
FG_INPUT=""; FG_IDX=""
if [ -n "$VOICE" ]; then FG_INPUT="-i $VOICE"; fi

# 默认 BGM 音量：有前景音垫底更低
if [ -z "$BGM_DB" ]; then
  if [ -n "$VOICE" ] || [ -n "$HAS_VA" ]; then BGM_DB="-24"; else BGM_DB="-14"; fi
fi

# 组装输入： 0=video  1=bgm(循环)  [2=voice]
INPUTS=(-i "$VIDEO" -stream_loop -1 -i "$BGM")
[ -n "$VOICE" ] && INPUTS+=(-i "$VOICE")

# BGM 处理链
BG="[1:a]afade=t=in:st=0:d=$FADE,afade=t=out:st=$FOUT:d=$FADE,volume=${BGM_DB}dB[bg]"

# 前景音 label
FG=""; FGLABEL=""
if [ -n "$VOICE" ]; then
  FG="[2:a]loudnorm=I=-16:TP=-1.5:LRA=11[fg]"; FGLABEL="[fg]"
elif [ -n "$HAS_VA" ]; then
  FG="[0:a]loudnorm=I=-16:TP=-1.5:LRA=11[fg]"; FGLABEL="[fg]"
fi

if [ -n "$FGLABEL" ]; then
  if [ "$DUCK" = "1" ]; then
    FILTER="$BG;$FG;${FGLABEL}[bg]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=300[bgd];${FGLABEL}[bgd]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1.0[aout]"
  else
    FILTER="$BG;$FG;${FGLABEL}[bg]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1.0[aout]"
  fi
else
  # 无前景音（如纯 B-roll）：只铺 BGM
  FILTER="$BG;[bg]loudnorm=I=-14:TP=-1.0[aout]"
fi

echo "视频 ${DUR}s | BGM ${BGM_DB}dB | duck=$DUCK | 前景音=$([ -n "$FGLABEL" ] && echo 有 || echo 无)"
ffmpeg -y "${INPUTS[@]}" \
  -filter_complex "$FILTER" \
  -map 0:v -map "[aout]" -t "$DUR" \
  -c:v copy -c:a aac -b:a 192k -shortest "$OUT" 2>/dev/null

echo "✅ $OUT"
ffprobe -v error -show_entries format=duration:stream=codec_type -of default=nk=1 "$OUT" 2>/dev/null | tr '\n' ' '; echo
