# 公众号爆款数据格式说明

## 概览

本文档定义了公众号爆款数据查询脚本 `fetch_gzh_trends.py` 的输入输出格式规范。

## 重要说明

**爆款文章范围**：阅读数1w+以上的文章和部分阅读数远高于粉丝数的文章。

## 输入格式

### 脚本参数

```bash
python scripts/fetch_gzh_trends.py --keyword <关键词> [选项]
```

| 参数 | 必填 | 说明 | 默认值 |
|------|------|------|--------|
| `--keyword` | 是 | 搜索关键词（支持多个关键词，逗号分隔，最多5个，总长度不超过200字符） | - |
| `--start-date` | 否 | 开始日期，格式 yyyy-MM-dd | 最近30天 |
| `--max-items` | 否 | 每类内容最多展示数量 | 10 |
| `--output-format` | 否 | 输出格式：text、json 或 html | html |
| `--output-file` | 否 | 输出文件路径 | 关键词_爆款数据.html |
| `--debug` | 否 | 调试模式，打印原始API响应 | False |

## 输出格式


### 文章数据字段（完整）

每篇文章包含以下字段：

#### 文章基本信息

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `photoId` | string | 文章ID（唯一标识） |
| `title` | string | 文章标题（可能为空，需从summary提取） |
| `summary` | string | 文章摘要/正文片段 |
| `publicTime` | string | 发布时间（格式：YYYY-MM-DD HH:MM:SS） |

#### 作者信息

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `accountId` | string | 公众号ID（格式：gh_xxxx 或自定义ID） |
| `userName` | string | 公众号名称 |
| `userHeadUrl` | string | 作者头像地址（可能为NULL） |
| `fans` | string | 粉丝数（可能为"100w+"格式） |


**作者二维码链接拼接规则**：
```
https://open.weixin.qq.com/qr/code?username={accountId}
```
点击后会弹出公众号二维码，用户可扫码关注。

**作品链接**：
- 直接使用 `oriUrl` 字段（完整文章链接）
- 无备用方案

#### 互动数据

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `likeCount` | int/string | 点赞数 |
| `commentCount` | int/string | 评论数 |
| `shareCount` | int/string | 分享数 |
| `interactiveCount` | int/string | 互动总数 |
| `clicksCount` | string | 阅读数（如"10w+"） |
| `watchCount` | string | 在看数 |

#### 图片链接

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `coverUrl` | string | 封面图URL |

#### 其他字段

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `oriUrl` | string | 文章原始链接（完整URL） |
| `orderNum` | int | 排序序号（0=头条，1=次条） |
| `originalFlag` | int | 原创标识（1=原创） |
| `type` | string | 内容类型（如"文摘"） |
| `thumbnail` | string | 缩略图URL |

### JSON 输出示例

```json
{
  "keyword": "职场",
  "low_fan_explosive": [
    {
      "accountId": "gh_e6580d8dcccb",
      "clicksCount": "5w+",
      "commentCount": "9",
      "coverUrl": "https://mmbiz.qpic.cn/mmbiz_jpg/...",
      "fans": "100w+",
      "interactiveCount": "988",
      "likeCount": "124",
      "orderNum": 0,
      "originalFlag": 1,
      "photoId": "8CF6280D97686E92F91445054AF9AAF9",
      "publicTime": "2026-03-19 20:06:58",
      "shareCount": "834",
      "summary": "蓝箭航天的朱雀2..."
    }
  ],
  "ten_w_reading": [
    {
      "accountId": "YJwujian",
      "clicksCount": "10w+",
      "commentCount": "29",
      "coverUrl": "https://mmbiz.qpic.cn/mmbiz_jpg/...",
      "fans": "100w+",
      "interactiveCount": "4747",
      "likeCount": "706",
      "orderNum": 0,
      "originalFlag": 1,
      "photoId": "319359512EA49A0D6774CEBAEDA8E134",
      "publicTime": "2026-03-05 22:09:00",
      "shareCount": "3854",
      "summary": "这下再也不用担心我团战打..."
    }
  ],
  "original_rank": [
    {
      "accountId": "beitaishuoche",
      "clicksCount": "9w+",
      "commentCount": "27",
      "coverUrl": "https://mmbiz.qpic.cn/mmbiz_jpg/...",
      "fans": "100w+",
      "interactiveCount": "852",
      "likeCount": "352",
      "orderNum": 0,
      "originalFlag": 1,
      "photoId": "9D8E75E91E08C147BE9F3F9BF23A691C",
      "publicTime": "2026-03-05 17:30:05",
      "shareCount": "398",
      "summary": "遇到刹车失灵，撞墙会是最安..."
    }
  ]
}
```

### HTML 输出格式（卡片形式）

HTML 输出采用响应式卡片布局，结构清晰，便于阅读：

```html
<div class="card">
    <div class="card-title-row">
        <span class="card-index">1.</span>
        <a href="https://mp.weixin.qq.com/s/{photoId}" class="card-title" target="_blank">文章标题</a>
    </div>
    <div class="card-meta">
        <a href="https://open.weixin.qq.com/qr/code?username={accountId}" 
           class="author-link" target="_blank">公众号名称</a>
        <span class="meta-divider">·</span>
        <span class="pub-time">发布日期：3月15日</span>
    </div>
    <div class="card-stats">
        <span class="read-count">📖 10w+阅读</span>
        <span class="category-tag">低粉高阅读</span>
        <a href="https://mp.weixin.qq.com/s/{photoId}" class="view-note-btn" target="_blank">查看作品 ↗</a>
    </div>
</div>
```

### 卡片字段说明

| 字段 | 说明 |
|------|------|
| 序号 | 从1开始编号，格式为"1."、"2."等 |
| 标题 | 文章标题（可点击跳转文章详情） |
| 作者 | 公众号名称（可点击弹出二维码） |
| 发布日期 | 文章发布日期（月日格式） |
| 阅读数 | 文章阅读量 |
| 分类标签 | 低粉高阅读/阅读靠前/数据增长中/原创靠前 |
| 查看作品 | 跳转文章详情的链接 |

## 四大榜单说明

### 1. 低粉高阅读（lowPowderExplosiveArticle）
- **定位**：小号爆款文章，粉丝数较少但阅读数据优秀
- **价值**：小号也能出爆款，参考价值高
- **特点**：粉丝数通常在10万以下，阅读数据突出

### 2. 阅读靠前（tenWReadingRank）
- **定位**：阅读量排名靠前的高传播文章
- **价值**：高传播力内容，适合学习爆款逻辑
- **特点**：阅读量高，传播广度强

### 3. 数据增长中（onewReadingRank）
- **定位**：阅读量在1w~10w范围内，具有增长潜力的文章
- **价值**：发掘潜力内容，把握增长趋势
- **特点**：阅读量1w~10w，处于增长阶段

### 4. 原创靠前（originalRank）
- **定位**：原创优质内容排名靠前
- **价值**：原创保护，内容质量高
- **特点**：originalFlag=1，内容原创性强

## 使用注意事项

### 数据获取原则

1. **必须调用脚本查询**：不能使用其他方式查询或直接搜索网络资讯
2. **必须等待脚本执行完成**：获取返回结果后才能进行后续步骤
3. **必须展示完整数据列表**：不能跳过或询问用户

### 数据展示原则

1. **展示所有字段**：每篇文章展示完整信息，包括封面图、作者链接、互动数据等
2. **四类爆款内容全部展示**：低粉高阅读、阅读靠前、数据增长中、原创靠前

### 字段说明

1. **标题提取**：如果title字段为空，从summary字段提取前30个字符作为标题
2. **作者名称**：公众号没有userName字段，使用accountId代替
3. **粉丝数格式**：可能是"100w+"、"5.2万"等格式，直接展示原值
4. **阅读数格式**：可能是"10w+"、"5w+"等格式，直接展示原值
