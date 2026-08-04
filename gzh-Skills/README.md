# gzh-Skills · 公众号创作 Skill 集合

面向微信公众号内容创作的 Skill 集合：从找选题、起标题，到出配图、整篇排版。

## 技能清单

### 内容搜索 / 分析
| 技能 | 作用 |
|---|---|
| `baokuan-article-analysis` | 按赛道/关键词抓公众号爆款文章，做数据洞察 |
| `gzh-explosive-content-detector` | 每日爆款收录（低粉高阅读、数据增长中等） |
| `global-content-search` | 全域内容搜索（小红书/B站/抖音关键词、详情、评论） |
| `xhs-hotnotes` | 小红书热门笔记搜索，找选题灵感 |

### 标题
| 技能 | 作用 |
|---|---|
| `baokuan-title-generator` | 科技/AI 领域 10万+ 爆款标题生成、评分、A/B |

### 配图（用户给内容 → 出 HTML 或用 codex/workbuddy 内置模型出图）
| 技能 | 作用 | 主输出 |
|---|---|---|
| `space-chart-image` | 10 类图表（流程/架构/思维导图/SWOT…）配图 | 模型出图 PNG |
| `space-text-logic-diagram` | 文本逻辑拆解 → 逻辑关系图配图 | HTML（可导 PNG） |
| `space-wechat-layout` | 整篇文章 → 公众号 HTML 排版（一键复制） | HTML |

## 配图 Skill 的出图方式

用户输入内容，两种出图路径：
- **HTML 出图**：生成自包含 HTML，可本地预览、可截图导出 PNG（逻辑图/排版类首选）。
- **模型出图**：调用当前环境内置出图模型直接生成 PNG——**Codex** 用内置 `image_gen`/`image2`，**workbuddy** 用其出图模型；都没有时回退各 Skill `scripts/` 下的 API 脚本（需自备 key）。

公众号常用尺寸：头图 2.35:1（1175×500）｜正文配图 16:9 或 3:2｜方图 1:1。

## 致谢

`space-wechat-layout` / `space-text-logic-diagram` / `space-chart-image` 三个配图 Skill 改编自 [SpaceZephyr/design-buddy](https://github.com/SpaceZephyr/design-buddy)，已适配为公众号配图形式并把出图后端切到 Codex/workbuddy 内置模型。
