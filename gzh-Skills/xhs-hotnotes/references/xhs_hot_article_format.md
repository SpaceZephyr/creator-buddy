# 小红书热门笔记数据格式说明

## 概览

本文档定义了小红书热门笔记搜索脚本 `fetch_xhs_hot_articles.py` 的输入输出格式规范。

## 输入格式

### 脚本参数

```bash
python scripts/fetch_xhs_hot_articles.py --keyword <关键词> [选项]
```

| 参数 | 必填 | 说明 | 默认值 |
|------|------|------|--------|
| `--keyword` | 是 | 搜索关键词 | - |
| `--max-items` | 否 | 最多展示数量 | 10 |
| `--output-format` | 否 | 输出格式：text、json 或 html | html |
| `--output-file` | 否 | 输出文件路径 | 关键词_热门数据.html |
| `--start-date` | 否 | 开始日期，格式 yyyy-MM-dd | - |
| `--end-date` | 否 | 结束日期，格式 yyyy-MM-dd | - |
| `--page-num` | 否 | 页码 | 1 |
| `--page-size` | 否 | 每页条数 | 50 |
| `--debug` | 否 | 调试模式，打印原始API响应 | False |

## API 接口

### 请求参数

```json
{
  "keyword": "女士护肤",
  "pageNum": 1,
  "pageSize": 10,
  "startDate": "",
  "endDate": "",
  "source": "小红书爆款笔记洞察-SkillHub"
}
```

| 参数 | 类型 | 说明 |
|------|------|------|
| `keyword` | string | 搜索关键词 |
| `pageNum` | int | 页码，从1开始 |
| `pageSize` | int | 每页条数，最大50 |
| `startDate` | string | 开始日期，格式 yyyy-MM-dd |
| `endDate` | string | 结束日期，格式 yyyy-MM-dd |
| `source` | string | 固定值："小红书爆款笔记洞察-GitHub" |

### 响应格式

```json
{
  "code": 2000,
  "data": {
    "articles": [...],
    "hotTopics": [],
    "keyword": "女士护肤",
    "latestHotArticles": [],
    "pageNum": 1,
    "pageSize": 50,
    "relatedSearches": [],
    "tips": null,
    "total": 23813
  },
  "msg": "成功"
}
```

## 输出格式

### 作品数据字段（完整）

每条文章包含以下字段：

#### 作品基本信息

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `id` | string | 作品ID（唯一标识） |
| `title` | string | 作品标题 |
| `desc` | string | 作品描述/正文 |
| `createTime` | string | 发布时间（格式：YYYY-MM-DD HH:MM:SS） |
| `cover` | string | 封面图URL |
| `shareInfoLink` | string | 作品链接 |

#### 作者信息

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `authorId` | string | 作者ID |
| `authorNickname` | string | 作者名称 |
| `authorFans` | int | 粉丝数 |

**作者主页链接拼接规则**：
```
https://www.xiaohongshu.com/user/profile/{authorId}
```

#### 互动数据

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `likedCount` | int | 点赞数 |
| `collectedCount` | int | 收藏数 |
| `commentsCount` | int | 评论数 |
| `sharedCount` | int | 分享数 |
| `interactiveCount` | int | 互动总数 |

#### 评分数据

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `popularityScore` | float | 热度分数 |
| `recencyScore` | float | 时效分数 |
| `relevanceScore` | float | 相关性分数 |
| `totalScore` | float | 总分 |

### JSON 输出示例

```json
{
  "keyword": "女士护肤",
  "total": 23813,
  "pageNum": 1,
  "pageSize": 50,
  "items": [
    {
      "noteId": "69dcbb56000000001d01ae3c",
      "title": "防晒换个思路，别再只看女士护肤品了！",
      "desc": "#防晒#油痘#高夫#高夫防晒#肤感#油皮#物理防晒#高夫小蓝盾",
      "authorId": "62bec245000000001902de0f",
      "authorNickname": "可口可粒",
      "authorFans": 196831,
      "createTime": "2026-04-13 18:30:55",
      "noteLink": "https://www.xiaohongshu.com/explore/69dcbb56000000001d01ae3c",
      "authorLink": "https://www.xiaohongshu.com/user/profile/62bec245000000001902de0f",
      "interactiveCount": 2560,
      "likedCount": 1753,
      "collectedCount": 719,
      "commentsCount": 88,
      "sharedCount": 44,
      "totalScore": 11.5,
      "relevanceScore": 10.0,
      "popularityScore": 1.0,
      "recencyScore": 0.5
    }
  ]
}
```

## 评分说明

数据评分由接口直接返回，无需计算：

| 字段名 | 说明 |
|--------|------|
| `totalScore` | 综合评分（主排序依据） |
| `popularityScore` | 热度分数 |
| `relevanceScore` | 相关性分数 |
| `recencyScore` | 时效性分数 |

排序规则：按 `totalScore` 降序排列。

## 常见错误处理

| 错误 | 原因 | 解决方案 |
|------|------|---------|
| `缺少 API Key 配置` | 未配置凭证 | 配置 COZE_REDFORX_XHS_API 环境变量 |
| `HTTP请求失败: 状态码 401` | API Key 无效 | 检查 API Key 是否正确 |
| `API 错误: xxx` | 接口返回错误 | 检查请求参数是否正确 |
