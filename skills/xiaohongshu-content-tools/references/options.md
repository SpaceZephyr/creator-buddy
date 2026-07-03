# 技能完整选项说明

## 1. 小红书关键词搜索

```bash
# 基础语法
node src/xiaohongshu/search-cli.js <关键词> [选项]

# 完整选项说明
--keyword -k <关键词>: 搜索关键词（必填，2-50个汉字，避免特殊符号）
--type -t <0/1/2>: 内容类型，0-全部（默认），1-视频，2-图文
--sort -s <0-4>: 排序规则，0-综合（默认），1-最新，2-最多点赞，3-最多评论，4-最多收藏
--time -i <0-3>: 发布时间，0-全部（默认），1-一天内，2-一周内，3-半年内
--limit -l <1-10000>: 搜索数量，1-100000（默认20）
--output -o <json/markdown>: 输出格式（默认json）
--help -h: 显示帮助信息

# 示例
node src/xiaohongshu/search-cli.js "露营装备" --sort 2 --limit 20
node src/xiaohongshu/search-cli.js --keyword "早春穿搭" --type 2 --output markdown
```

## 2. 小红书笔记详情查询

```bash
# 基础语法
node src/xiaohongshu/detail-cli.js <小红书笔记链接> [选项]

# 选项说明
--url -u <小红书笔记链接>: 小红书笔记链接（支持https://www.xiaohongshu.com/explore/xxx 或 http://xhslink.com/m/xxx）
--limit -l <1-10000>: 评论数量限制，1-10000（默认6）
--help -h: 显示帮助信息

# 链接格式要求
1. 完整链接：必须包含 xsec_token 参数（如 https://www.xiaohongshu.com/explore/xxx?xsec_token=yyy）
2. 短链接：https://xhslink.com/m/xxx（自动兼容，无需手动解析）
❌ 错误：链接含空格、无xsec_token的完整链接会直接报错

# 示例
node src/xiaohongshu/detail-cli.js "https://www.xiaohongshu.com/explore/xxx?xsec_token=yyy"
node src/xiaohongshu/detail-cli.js --url "http://xhslink.com/m/xxx"
```

## 3. 小红书博主已发布作品查询

```bash
# 基础语法
node src/xiaohongshu/post-cli.js <小红书博主链接> [选项]

# 选项说明
--url -u <小红书博主链接>: 小红书博主主页链接（支持https://www.xiaohongshu.com/user/profile/xxx?xsec_token=yyy 或 http://xhslink.com/m/xxx）
--limit -l <1-10000>: 主页笔记数量（默认 0, 最大 10000）
--help -h: 显示帮助信息

```
