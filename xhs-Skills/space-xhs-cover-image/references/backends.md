# 生图后端：探测、调用、降级

**执行任何生图之前先跑一次探测**，不要假设某个后端存在。

```bash
bash ~/.claude/skills/space-xhs-cover-image/scripts/detect_backend.sh
```

退出码 0 = 有可用路线（脚本会打印走哪条）；1 = 全部不可用（脚本会打印配置引导）。

---

## 路线 1：codex CLI 的 imagen 能力（优先级最高）

**诚实说明：本机没有安装 codex，本 skill 的作者无法实测它的生图子命令和参数。
下面写的是探测流程，不是可以照抄的命令。任何"codex imagen --xxx"式的具体写法都是编造的，不要照抄。**

正确做法：

```bash
# 1. 在不在 PATH？
command -v codex || echo "未安装"

# 2. 在的话，先看它到底有什么子命令
codex --help

# 3. 帮助里如果出现 image / imagen / gen-image 之类的子命令，再看它的参数
codex <那个子命令> --help
```

判定规则：
- 帮助输出里**确实存在**生图子命令，且能看到"输出路径""比例/尺寸""prompt"这三类参数
  → 按它自己的参数名调用，比例取 3:4 或 1080×1440。
- 帮助里**没有**生图能力，或参数看不明白
  → **不要试探性乱传参数**，直接降级到路线 2，并告诉用户"检测到 codex 但没找到生图子命令，已改用 X"。

调完拿到图，一样要跑 `scripts/check_image.py` 验尺寸和白底——不同后端对比例参数的理解不一致，很可能给你一张 1:1。

---

## 路线 2：baoyu-image-gen（本机已装，命令来自它的 SKILL.md）

脚本位置：`~/.claude/skills/baoyu-image-gen/scripts/main.ts`

```bash
npx -y bun ~/.claude/skills/baoyu-image-gen/scripts/main.ts \
  --prompt "$(cat prompts/01-cover.md)" \
  --image out/01-cover.png \
  --provider google \
  --ar 3:4 \
  --quality 2k
```

**未实测**：本机三个 API Key 都没配，上面这条命令**没有在本机跑通过**，
参数名照抄自 `baoyu-image-gen/SKILL.md` 的 Options 表。第一次跑失败时先 `--help` 或读它的 SKILL.md 核对。

| 参数 | 本 skill 的取值 | 说明 |
|---|---|---|
| `--provider` | `google` / `openai` / `dashscope` | 见下表选型 |
| `--ar` | `3:4` | 该 skill 支持的比例里包含 3:4 |
| `--quality` | `2k` | 默认值，封面用足 |
| `--image` | 输出路径 | 必填 |
| `--ref <files...>` | 组图第 2 张起传第 1 张 | 仅 google 多模态 / openai GPT-Image edits 支持 |
| `--prompt` / `--promptfiles` | prompt 长时用 `--promptfiles` | 避免 shell 转义踩坑 |

**provider 选型**：

| provider | env | 拿 Key | 特点（据其文档，未实测） |
|---|---|---|---|
| `google` | `GOOGLE_API_KEY` | https://aistudio.google.com/apikey | 默认 provider；多模态，支持 `--ref`；线稿类风格通常最稳 |
| `openai` | `OPENAI_API_KEY` | https://platform.openai.com/api-keys | GPT-Image 系列，指令跟随强；`--ref` 需 GPT Image 模型 |
| `dashscope` | `DASHSCOPE_API_KEY` | https://bailian.console.aliyun.com/ | 通义万相，国内直连不需代理；中文语义理解较好 |

Key 也可以不写环境变量，放 `~/.baoyu-skills/.env`（它的加载优先级：CLI 参数 > EXTEND.md > env > `<cwd>/.baoyu-skills/.env` > `~/.baoyu-skills/.env`）。

**注意**：`--ar 3:4` 未必换来精确的 1080×1440。拿到图先 `check_image.py`，不对就用
`--size 1080x1440` 重试，仍不对就本地 resize（脚本会打印怎么裁）。

---

## 路线 3：都没有 → 配置引导 + 兜底

三个 Key 都没有且 codex 不在时，**不要静默失败**，按此模板回复：

```
没有检测到可用的生图后端（codex 未安装，GOOGLE / OPENAI / DASHSCOPE 三个 Key 都没配）。

配置任一即可（推荐第 1 个）：
  export GOOGLE_API_KEY=...      # https://aistudio.google.com/apikey
  export OPENAI_API_KEY=...      # https://platform.openai.com/api-keys
  export DASHSCOPE_API_KEY=...   # https://bailian.console.aliyun.com/
写进 ~/.zshrc 后重开终端。

在你配置之前，有两个选择：
A. 你这张封面主视觉其实是文字（大字 + 目录 / 大字 + 副标题）→ 直接走
   xhs-html，HTML/CSS 精确排版，不需要任何 Key，中文零错字，现在就能出图。
B. 确实需要插画感 → 我先把 prompt 全套写好存到 prompts/ 目录，你配好 Key 后
   一条命令批量出图。
```

**然后真的把 B 做完**——分析内容、选模板、写完整 prompt、存盘、给出待执行的命令清单。
不要因为没有后端就停在提示上，prompt 工程本身就是本 skill 一半的价值。

---

## 失败处理

| 现象 | 处理 |
|---|---|
| 401 / 403 | Key 无效或过期，报给用户，降级下一条路线 |
| 余额不足 / quota | 明确告知，换 provider 或降级 |
| 超时 / 网络失败 | 重试 1 次，仍失败换 provider |
| 出图比例不对 | 换 `--size 1080x1440` 重试；再不行本地裁（`check_image.py` 会给裁法） |
| 出图有乱码中文 | 不是重试能解决的，回 `references/text-strategy.md` 换路线 C |
| 批量中某张失败 | 记下来继续跑，最后统一汇报失败项，不要中断整批 |

**批量节奏**：顺序生成，每张之间隔 2–3 秒，避免限流。除非用户明确要求并行。
