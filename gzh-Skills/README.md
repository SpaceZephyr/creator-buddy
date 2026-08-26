# gzh-Skills · 公众号创作 Skill 集合

面向微信公众号的 Skill 集合，按创作流程排列：**先定位，再找选题，然后写正文，起标题，最后配图排版。**

```
定位装修 ──→ 找选题 ──────→ 写正文 ─────────→ 起标题 ──→ 配图排版
gzh-        baokuan-       gzh-longform-      baokuan-   space-chart-image
positioning article-       writer（长文）      title-     space-text-logic-diagram
            analysis       gzh-short-post     generator  space-wechat-layout
            xhs-hotnotes  （≤1000 字短文）              space-gzh-cover（2.35:1 头图）
```

`references/my-voice.md` 是共享的个人文风档案，两个写作 Skill 都能读；说一句「用我的风格」即生效。

## 技能清单

### 定位 / 账号装修
| 技能 | 作用 |
|---|---|
| `gzh-positioning` | 公众号定位分析 + 三件套设计：账号简介 / 关注后回复 / 自定义菜单，全部带字数校验 |

### 写作
| 技能 | 作用 |
|---|---|
| `gzh-longform-writer` | 长文（1500–4000 字）。先诊断手上有什么，再路由到六种写法之一，带公众号专属质检 |
| `gzh-short-post` | 短文（≤1000 字，纯文字不配图）。一套风格规则 + 自检清单，也可把长文压成短文 |

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
| `space-gzh-cover` | **头图封面 2.35:1**，带分享安全区校验（分享时只保中央 42.6%） | 模型出图 PNG |
| `space-chart-image` | 10 类图表（流程/架构/思维导图/SWOT…）配图 | 模型出图 PNG |
| `space-text-logic-diagram` | 文本逻辑拆解 → 逻辑关系图配图 | HTML（可导 PNG） |
| `space-wechat-layout` | 整篇文章 → 公众号 HTML 排版（一键复制） | HTML |

## 配图 Skill 的出图方式

用户输入内容，两种出图路径：
- **HTML 出图**：生成自包含 HTML，可本地预览、可截图导出 PNG（逻辑图/排版类首选）。
- **模型出图**：调用当前环境内置出图模型直接生成 PNG——**Codex** 用内置 `image_gen`/`image2`，**workbuddy** 用其出图模型；都没有时回退各 Skill `scripts/` 下的 API 脚本（需自备 key）。

公众号常用尺寸：头图 2.35:1（1175×500）｜正文配图 16:9 或 3:2｜方图 1:1。

⚠️ **头图会被裁两次**：消息列表和文章顶部显示完整 2.35:1，但分享到朋友圈/聊天时**只抓取正中央的 1:1 方形**（仅占宽度 42.6%）。标题铺满全宽的封面，分享出去两头就没了。`space-gzh-cover` 自带 `check_cover.py`，可导出安全区标注图和分享裁切预览。

## 致谢

`space-wechat-layout` / `space-text-logic-diagram` / `space-chart-image` 三个配图 Skill 改编自 [SpaceZephyr/design-buddy](https://github.com/SpaceZephyr/design-buddy)，已适配为公众号配图形式并把出图后端切到 Codex/workbuddy 内置模型。
