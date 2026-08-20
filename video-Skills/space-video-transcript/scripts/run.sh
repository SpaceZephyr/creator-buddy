#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT="$SCRIPT_DIR/space_video_transcript.py"

if command -v uv >/dev/null 2>&1; then
  exec uv run "$SCRIPT" "$@"
fi

exec python3 "$SCRIPT" "$@"
