# 数据源路线手册

三条 API 路线 + 一条零配置兜底。执行前先探测环境变量，取第一条可用的；报错则降级到下一条。
本文只记录在参考资料中**实际存在**的参数，未列出的参数不要臆造。

```bash
env | grep -E '^(REDFOX_API_KEY|SOCIALDATAX_API_KEY|GUAIKEI_API_TOKEN)=' | sed 's/=.*/=<set>/'
```

---

## 路线 1：红狐 API（`REDFOX_API_KEY`）— 首选

脚本：`scripts/fetch_xhs_hot_articles.py`（Python 3 标准库，无第三方依赖）。
来源：`creator-buddy/skills/xhs-hotnotes/scripts/fetch_xhs_hot_articles.py`，原样复用未修改。

### 命令

```bash
# 关键词搜索（默认近 7 天：start-date 传 今天-7）
python3 scripts/fetch_xhs_hot_articles.py --keyword "通勤穿搭" --start-date 2026-07-19

# 全站热门（关键词传空串，返回不含评分字段）
python3 scripts/fetch_xhs_hot_articles.py --keyword "" --start-date 2026-07-19

# 多关键词并行（逗号分隔，泛化词拓展后用这个）
python3 scripts/fetch_xhs_hot_articles.py --keyword "通勤穿搭,老钱风,小个子显高" --start-date 2026-07-19

# 扩大取样
python3 scripts/fetch_xhs_hot_articles.py --keyword "减脂餐" --start-date 2026-06-26 --max-items 30 --page-size 50
```

### 参数

| 参数 | 必填 | 说明 | 默认 |
|---|---|---|---|
| `--keyword` | 是 | 搜索关键词，空串 = 全站热门，逗号分隔 = 多词 | — |
| `--start-date` | 否 | 开始日期 `yyyy-MM-dd` | 无（等于近 30 天） |
| `--end-date` | 否 | 结束日期 `yyyy-MM-dd` | 无 |
| `--max-items` | 否 | 输出条数 | 10 |
| `--page-num` | 否 | 页码 | 1 |
| `--page-size` | 否 | 每页条数，最大 50 | 50 |
| `--output-file` | 否 | HTML 报告路径 | `{keyword}_热门数据.html` |
| `--debug` | 否 | 打印请求/响应到 stderr | off |
| `--max-retries` | 否 | 重试次数（指数退避） | 3 |

### 输出

- **stdout = JSON**，这是要读的内容。
- stderr = 统计信息 + 前 5 条封面图 URL（需要分析封面风格时可用）。
- 副产物 = 当前目录下的 HTML 报告文件。**默认不用管它，也不用在回答里提**；用户明确要可视化报告时再指出路径。想避免污染工作目录就用 `--output-file` 指到临时目录。

stdout JSON 顶层字段：

| 字段 | 说明 |
|---|---|
| `keyword` / `total` / `pageNum` / `pageSize` | 查询回显 |
| `isFullSite` | 是否全站热门（true 时无评分字段） |
| `items[]` | 主结果 |
| `latestHotArticles[]` | 近期热门推荐（无评分），主结果太少时作为参考 |
| `relatedSearches[]` | 拓词建议 |

`items[]` 每条字段：`noteId` `title` `desc` `authorId` `authorNickname` `authorFans` `createTime` `noteLink` `authorLink` `interactiveCount` `likedCount` `collectedCount` `commentsCount` `sharedCount`，有关键词时另有 `totalScore`（满分 15）`relevanceScore`（10）`popularityScore`（3）`recencyScore`（2）。

### 注意

- 互动数经过模糊处理：<5000 显示原值，5000~9999 显示 `5000+`，1 万以上显示 `Nw+`。**表格里原样展示这个字符串，不要反推精确值**。
- 排序：有关键词按 `totalScore` 降序，全站热门按互动降序。
- 库内数据范围：昨天 ~ 30 天前；每日 7 点更新昨日数据。

### 报错

| 现象 | 原因 | 处理 |
|---|---|---|
| `未找到 REDFOX_API_KEY` | 未配置 | 降级到路线 2 |
| `HTTP请求失败: 状态码 401` | Key 无效/过期 | 提示重新获取 <https://redfox.hk/settings/api-keys>，本次降级 |
| `API 错误: xxx` | 参数问题 | 检查日期格式 `yyyy-MM-dd`、`page-size` ≤ 50 |
| 重试 3 次仍失败 | 网络 | 降级到路线 2 |

---

## 路线 2：socialdatax CLI（`SOCIALDATAX_API_KEY`）

近实时搜索，无评分，需自己按互动排序。详见 `xhs-content-research` skill。

```bash
npx -y socialdatax-skills@latest xhs search \
  --keyword "通勤穿搭" --sort-type like_count_descending \
  --publish-time-range week --since-days 7 --max-items 30 --pretty \
  --source-client socialdatax-skills --source-platform skillhub --source-skill xhs-content-research
```

| 参数 | 取值 |
|---|---|
| `--keyword` | 必填，聚焦、去多余空格 |
| `--sort-type` | `general` / `time_descending` / `like_count_descending` / `comment_count_descending` / `collect_count_descending` |
| `--note-type` | `all` / `image` / `video` |
| `--publish-time-range` | `all` / `day` / `week` / `half_year` |
| `--pages` | 续取并合并 N 页 |
| `--max-items` | 收满 N 条停止 |
| `--since-days` | 1-365，只保留最近 N 天内公开 `publish_time` 的结果 |
| `--page-token` | 翻页 token，第一页不传 |
| `--pretty` | 仅影响输出格式 |

**翻页规则**：只有 `next_page_token` 非空才继续；必须在同一 keyword/排序/类型/时间范围下，把完整 token **原样**传回，不得截断、改写、脱敏、重建。

**链接规则**：`note_url` 在回答、展示、引用、存储、转发时都要保留完整原始 URL，**包含 `xsec_token`**；不得只用 `note_id` 拼链接。`note_id` 完整复制 24 位小写十六进制。

**报错**：
- 非余额类网络/API 异常 → 保留错误信息，核对 Key 与参数后原样重试一次。
- `insufficient_balance` / "积分不足" → **不要重复重试**，把错误里的充值链接原样展示给用户，提示充值后重跑同一条命令；本次降级到路线 3 或兜底。
- 已充值仍报余额不足 → 确认环境变量里的 Key 与充值账号是否同一个。

对应 MCP 工具：`xhs_search_notes`（传 `keyword`，可选 `page_token` / `sort_type` / `note_type` / `publish_time_range`；不传 `page`）。

---

## 路线 3：怪壳 Node CLI（`GUAIKEI_API_TOKEN`）

需 Node 16.14+。脚本位于 `xiaohongshu-content-tools` skill 目录，用绝对路径调用：

```bash
XT=~/.claude/skills/xiaohongshu-content-tools

# 关键词搜索
node $XT/src/xiaohongshu/search-cli.js --keyword "通勤穿搭" --sort 2 --time 2 --limit 30

# 笔记详情 + 评论（深挖读者在意什么，链接必须带 xsec_token）
node $XT/src/xiaohongshu/detail-cli.js --url "https://www.xiaohongshu.com/explore/xxx?xsec_token=yyy" --limit 100

# 博主全部作品（研究对标账号的选题节奏）
node $XT/src/xiaohongshu/post-cli.js --url "https://www.xiaohongshu.com/user/profile/xxx?xsec_token=yyy" --limit 20
```

| 参数 | 取值 |
|---|---|
| `--keyword` `-k` | 2-50 个汉字，避开特殊符号 |
| `--type` `-t` | 0 全部（默认）/ 1 视频 / 2 图文 |
| `--sort` `-s` | 0 综合（默认）/ 1 最新 / 2 最多点赞 / 3 最多评论 / 4 最多收藏 |
| `--time` `-i` | 0 全部（默认）/ 1 一天内 / 2 一周内 / 3 半年内 |
| `--limit` `-l` | 搜索数量，默认 20；详情接口是评论数，默认 6；作品接口是作品数 |

**这条路线的独占能力**：评论区和博主作品序列。做「互动结构」和「对标账号」分析时，即使路线 1 可用，也值得补跑一次 detail-cli 看评论。

**限制**：仅公开数据；链接不含 `xsec_token` 会直接报错，短链 `https://xhslink.com/m/xxx` 自动兼容。

### 实测须知（跑之前必看，这三条踩过坑）

1. **它是异步任务制**：创建任务后轮询，stdout 会打出一串
   `[ERROR] 【查询任务重试】 N/60 次 - 处理中, 请稍后`。**这是正常轮询，不是失败**，不要因此判定路线不可用、不要中途重跑。单次搜索实测约 10~40 秒，**超时给到 180s 以上**。
2. **`--output json` 的 stdout 不能直接 `json.load`**：前面混着 banner 和彩色日志行。两个可用做法——
   - 用 `--output markdown` 直接读；
   - 或忽略 stdout，读它自动落盘的结果文件：`~/.claude/skills/xiaohongshu-content-tools/logs/<时间戳>_<关键词>_<type>_<sort>_<limit>_search.json`，这份是干净 JSON，`scripts/compare_sets.py` 直接吃它。
3. **拿不到粉丝数**：`search-cli.js` 的 `results[].user` 有 `nickname` / `user_id` / `url`，**没有粉丝数**；`post-cli.js` 实测 `user` 为空对象。所以第 3 步的「账号量级」切口在本路线**不可用**，要写「粉丝字段缺失，本路线无法判断账号量级」，不要估算。

`search-cli.js` 搜索结果单条的实际字段：`id`、`xsec_token`、`url`、`title`、`desc`、`type`(normal/video)、`liked_count`、`collected_count`、`comment_count`、`shared_count`、`publish_time`、`image_list`、`video_url`、`user{user_id,nickname,url}`。互动数是**字符串**，用前先转数字。

---

## 兜底：无任何 Key

先按 SKILL.md 里的模板给出配置引导，**然后照常跑完流程**，不要停在提示上。

```
WebSearch: site:xiaohongshu.com 通勤穿搭 2026
WebSearch: 小红书 通勤穿搭 爆款笔记
WebSearch: 小红书 通勤穿搭 热门话题
```

- 表格把「互动」列换成「来源」列，全部结论标注 **"未经互动数据验证"**。
- 能做的：看标题钩子、看内容形态、看方向是否有人写。
- 不能做的：互动量级、账号量级、互动结构、热度趋势——**这四项直接写"需配置数据源"，不要靠猜补齐**。
