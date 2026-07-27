#!/usr/bin/env bash
# 生图后端探测：按优先级 codex → baoyu-image-gen(google/openai/dashscope) → 无
# 只做探测和上报，不发起任何生图请求，不打印任何 Key 的值。
# 退出码：0 = 至少有一条可用路线；1 = 全部不可用
set -u

BOLD=""; DIM=""; RST=""
if [ -t 1 ]; then BOLD=$'\033[1m'; DIM=$'\033[2m'; RST=$'\033[0m'; fi

route=""
echo "${BOLD}生图后端探测${RST}"
echo "----------------------------------------"

# ---------- 1. codex CLI ----------
if command -v codex >/dev/null 2>&1; then
  echo "[1] codex CLI      : 已安装  ($(command -v codex))"
  echo "    ${DIM}⚠ 生图子命令未知。调用前先跑 \`codex --help\`（必要时 \`codex <子命令> --help\`）${RST}"
  echo "    ${DIM}  确认它是否真的有 imagen/image 生图能力及其参数，再决定用不用。${RST}"
  echo "    ${DIM}  确认不了就跳到路线 2，不要猜参数。${RST}"
  route="codex"
else
  echo "[1] codex CLI      : 未安装"
fi

# ---------- 2. baoyu-image-gen ----------
GEN="${HOME}/.claude/skills/baoyu-image-gen/scripts/main.ts"
keys=""
[ -n "${GOOGLE_API_KEY:-}" ]    && keys="${keys}google "
[ -n "${OPENAI_API_KEY:-}" ]    && keys="${keys}openai "
[ -n "${DASHSCOPE_API_KEY:-}" ] && keys="${keys}dashscope "

# baoyu-image-gen 也会从这两个 .env 兜底读 Key
envfiles=""
[ -f "./.baoyu-skills/.env" ]        && envfiles="${envfiles}./.baoyu-skills/.env "
[ -f "${HOME}/.baoyu-skills/.env" ]  && envfiles="${envfiles}~/.baoyu-skills/.env "

if [ ! -f "$GEN" ]; then
  echo "[2] baoyu-image-gen: 未安装 (缺 $GEN)"
elif ! command -v npx >/dev/null 2>&1; then
  echo "[2] baoyu-image-gen: 脚本在，但缺 npx/node，跑不起来"
else
  if [ -n "$keys" ]; then
    echo "[2] baoyu-image-gen: 可用  provider = ${keys}"
    [ -z "$route" ] && route="baoyu-image-gen"
  elif [ -n "$envfiles" ]; then
    echo "[2] baoyu-image-gen: 脚本就绪，环境变量无 Key，但发现 ${envfiles}"
    echo "    ${DIM}它可能从 .env 里读到 Key —— 先试跑一张再判定不可用${RST}"
    [ -z "$route" ] && route="baoyu-image-gen?"
  else
    echo "[2] baoyu-image-gen: 脚本就绪，但 GOOGLE_API_KEY / OPENAI_API_KEY / DASHSCOPE_API_KEY 都未配置"
  fi
fi

# ---------- 3. 兜底 ----------
HTMLSKILL="${HOME}/.claude/skills/xhs-html/SKILL.md"
if [ -f "$HTMLSKILL" ]; then
  echo "[3] 兜底           : xhs-html 已安装（纯 HTML 排版，不需要任何 Key）"
else
  echo "[3] 兜底           : xhs-html 未安装"
fi

echo "----------------------------------------"
if [ -n "$route" ]; then
  echo "${BOLD}→ 本次走：${route}${RST}"
  exit 0
fi

cat <<'EOF'
→ 没有任何生图后端可用。

配置任一即可（推荐第 1 个，中文出图相对最好）：
  export GOOGLE_API_KEY=...      # https://aistudio.google.com/apikey
  export OPENAI_API_KEY=...      # https://platform.openai.com/api-keys
  export DASHSCOPE_API_KEY=...   # https://bailian.console.aliyun.com/  （通义万相，国内直连）
写进 ~/.zshrc 后重开终端。

不想配 Key 的话：纯文字型封面用 xhs-html，HTML/CSS 精确排版，
零依赖零成本，且中文零错字——多数「大字 + 目录 / 大字 + 副标题」封面本来就该走那条路。
EOF
exit 1
