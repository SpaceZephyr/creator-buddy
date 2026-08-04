# 全域内容搜索选项说明

## 1. 跨平台关键词搜索

```bash
node src/xiaohongshu/search-cli.js <关键词> [选项]
```

| 选项 | 说明 |
| --- | --- |
| `--platform -p` | 平台：`xiaohongshu` / `bilibili` / `douyin`，默认 `xiaohongshu` |
| `--keyword -k` | 搜索关键词 |
| `--limit -l` | 搜索数量，默认 20 |
| `--output -o` | 输出格式：`json` / `raw`，默认 `json` |
| `--type -t` | 兼容旧参数，部分平台忽略 |
| `--sort -s` | 兼容旧参数，部分平台忽略 |
| `--time -i` | 兼容旧参数，部分平台忽略 |

示例：

```bash
node src/xiaohongshu/search-cli.js --platform xiaohongshu --keyword "露营装备" --limit 20
node src/xiaohongshu/search-cli.js --platform bilibili --keyword "AI编程" --limit 10
node src/xiaohongshu/search-cli.js --platform douyin --keyword "AI工具"
```

## 2. 详情与评论

```bash
node src/xiaohongshu/detail-cli.js <链接或ID> [选项]
```

| 选项 | 说明 |
| --- | --- |
| `--platform -p` | 平台：`xiaohongshu` / `bilibili` / `douyin`，默认 `xiaohongshu` |
| `--url -u` | 笔记/视频链接或 ID |
| `--limit -l` | 评论数量，部分后端支持，默认 0 |
| `--output -o` | 输出格式：`json` / `raw`，默认 `json` |

示例：

```bash
node src/xiaohongshu/detail-cli.js \
  --platform xiaohongshu \
  --url "https://www.xiaohongshu.com/explore/xxx?xsec_token=yyy" \
  --limit 100

node src/xiaohongshu/detail-cli.js --platform bilibili --url "BVxxxx"
```

## 3. 创作者作品

```bash
node src/xiaohongshu/post-cli.js <主页链接或ID> [选项]
```

| 选项 | 说明 |
| --- | --- |
| `--platform -p` | 平台：`xiaohongshu` / `bilibili` / `douyin`，默认 `xiaohongshu` |
| `--url -u` | 创作者主页链接或 ID |
| `--limit -l` | 作品数量，默认 20 |
| `--output -o` | 输出格式：`json` / `raw`，默认 `json` |

示例：

```bash
node src/xiaohongshu/post-cli.js \
  --platform xiaohongshu \
  --url "https://www.xiaohongshu.com/user/profile/xxx?xsec_token=yyy" \
  --limit 20

node src/xiaohongshu/post-cli.js \
  --platform bilibili \
  --url "https://space.bilibili.com/123456" \
  --limit 20
```

## 4. 后端说明

### 小红书

按 `agent-reach doctor --json` 的 `xiaohongshu.active_backend` 自动选择：

- `OpenCLI`：`opencli xiaohongshu ...`
- `xiaohongshu-mcp`：`mcporter call 'xiaohongshu....'`
- `xhs-cli`：`xhs ...`
- 兜底：如果以上后端不可用，且配置了 `GUAIKEI_API_TOKEN`，自动使用 Guaikei API。

```bash
export GUAIKEI_API_TOKEN="your_api_token_here"
```

Guaikei API 兜底支持小红书关键词搜索、笔记详情/评论、博主作品。

### B站

优先级：

1. `bili-cli`
2. `opencli bilibili`
3. B站公开搜索/详情 API

### 抖音

Agent Reach 当前没有抖音后端。可设置：

```bash
export DOUYIN_COMMAND="/path/to/douyin-readonly-cli"
```

自定义 CLI 需支持：

```bash
$DOUYIN_COMMAND search <keyword> --limit <n>
$DOUYIN_COMMAND detail <url-or-id>
$DOUYIN_COMMAND user <user-url-or-id> --limit <n>
```
