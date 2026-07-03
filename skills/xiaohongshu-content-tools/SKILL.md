---
name: xiaohongshu-content-tools
description: 小红书运营数据工具｜当提到小红书关键词搜索,小红书笔记详情及评论,小红书博主作品时使用，可实现爆款挖掘/竞品分析/KOL筛选/趋势洞察，用数据驱动小红书流量增长，告别盲目创作
license: MIT
metadata:
  type: command
  runtime: "nodejs@16.14.0+"
  version: "1.0.5"
  requires:
    bins:
      - "node"
    env:
      - "GUAIKEI_API_TOKEN"
  env_desc:
    GUAIKEI_API_TOKEN: "小红书数据API访问令牌（必填），可通过 www.guaikei.com 开通获取"
  category:
    - "Data&APIs"
    - "内容创作"
  tags:
    - "小红书"
    - "小红书数据工具"
    - "小红书关键词搜索"
    - "小红书笔记详情查询"
    - "小红书评论分析"
    - "小红书爆款挖掘"
    - "小红书竞品监控"
    - "小红书趋势洞察"
    - "小红书KOL筛选"
    - "小红书运营"
    - "小红书内容创作"
    - "小红书营销"
    - "小红书数据爬虫"
    - "小红书互动数据统计"
    - "小红书热点监控"
  examples:
    - "搜索'露营装备'的热门小红书笔记: node src/xiaohongshu/search-cli.js --keyword '露营装备' --type 1 --sort 2 --limit 10"
    - "分析这篇小红书笔记的评论区情绪: node src/xiaohongshu/detail-cli.js --url 'https://www.xiaohongshu.com/explore/xxx?xsec_token=yyy' --limit 100"
    - "监控小红书博主的最新作品: node src/xiaohongshu/post-cli.js --url 'https://www.xiaohongshu.com/user/profile/xxx?xsec_token=yyy' --limit 20"
    - "监控小红书'夏季穿搭'关键词(最新排序+图文类型): node src/xiaohongshu/search-cli.js --keyword '夏季穿搭' --type 2 --sort 1"
---

# 📊 小红书洞察与竞品分析助手

> **一句话价值主张**：一款专业的小红书数据分析工具，通过挖掘爆款笔记、监控竞品动态、筛选高价值KOL，帮助你实现小红书账号的快速增长与精准营销。

## 1. 技能概述

这是一款专注于**小红书数据挖掘**的工具。它能够穿透小红书的公开数据层，为你提供深度的**竞品监控**、**趋势预测**和**KOL 筛选**服务。无论你是内容创作者、品牌营销人员还是市场分析师，都能通过此工具获取决策支持。

**🔥核心优势**

> - 轻量: 无需部署服务，Node.js 一键运行
> - 安全: 无需登录你的小红书账号，不担心风控风险 / 封号问题
> - 灵活: 支持多维度筛选、批量操作、多格式导出
> - 实用: 日志自动归档，适配营销报告 / 内容策划场景

**🎯 核心能力**

| 使用场景        | 具体价值                                                      |
| --------------- | ------------------------------------------------------------- |
| 🔍 内容创作选题 | 输入关键词，筛选「最多点赞」笔记，快速找到爆款选题方向        |
| 🕵️ 品牌竞品监控 | 输入竞品账号链接，分析其互动数据、内容风格，制定差异化策略    |
| 👥 KOL筛选      | 解析KOL笔记的真实互动率（点赞/评论/收藏），避免数据造假的博主 |
| 📈 市场趋势分析 | 定时监控关键词「最新排序」，捕捉小红书热点风向，提前布局内容  |

**✨ 适用人群**

✅ 小红书内容创作者/运营 | ✅ 品牌营销/市场人员 | ✅ 数据分析师 | ✅ MCN机构/博主经纪人

## 2. 🚀 快速使用

### 2.1 小红书关键词搜索

```bash
node src/xiaohongshu/search-cli.js --keyword "夏季穿搭"
```

### 2.2 小红书笔记详情及评论分析

```bash
node src/xiaohongshu/detail-cli.js --url "https://www.xiaohongshu.com/explore/xxx?xsec_token=yyy" --limit 100
```

### 2.3 小红书博主作品监控

```bash
node src/xiaohongshu/post-cli.js --url "https://www.xiaohongshu.com/user/profile/xxx?xsec_token=yyy" --limit 20
```

**💡 详细选项说明**， 可参阅 [完整选项说明](references/options.md)

## 3. 📌 使用场景

- 需要做内容选题 → 关键词搜索 + 点赞排序
- 需要模仿爆款文案 → 查看高赞图文笔记详情
- 需要监控竞品账号 → 批量抓取对方作品
- 需要分析评论区情绪 → 查看笔记的评论内容及互动数据
- 需要快速追热点 → 实时获取小红书热门笔记

## 4. ⚠️ 重要限制

- 仅抓取小红书公开数据，不支持私密 / 隐藏内容
- 需要配置 GUAIKEI_API_TOKEN 才能正常运行
- 数据仅限个人 / 团队内部使用，禁止违规分发
- 本工具无需登录小红书账号，不涉及用户隐私数据的获取

## 5. ❓ 技术说明

### 5.1 运行环境兼容说明

- 系统兼容：Windows/Linux/MacOS（无需额外依赖，仅需Node.js）
- Node.js版本：推荐16.14.0+
- 网络要求：需能正常访问网络，国内服务器无需代理
- 权限要求：无需管理员权限，普通用户即可运行

### 5.2 日志说明

- 启动时会打印工具Banner，方便确认是否正确执行；
- 过程中会输出彩色日志，用于反馈技能执行情况，过程中无需用户交互；
- 所有任务结果会自动保存到 `logs/` 目录（按时间+关键词/链接命名）。

> 版本更新日志，请参阅 [changelog.md](references/changelog.md)
