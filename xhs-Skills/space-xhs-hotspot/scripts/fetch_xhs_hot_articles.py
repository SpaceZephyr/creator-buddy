#!/usr/bin/env python3
"""
小红书热门笔记搜索脚本（支持 HTML 卡片布局输出）
基于红狐数据API，支持关键词搜索、分页、时间筛选
"""

import sys
import argparse
import json
import os
import urllib.request
import urllib.error


def parse_count(value):
    """解析数量，支持 "17w+"、"1.5w" 格式"""
    if value is None:
        return 0
    if isinstance(value, int):
        return value
    value_str = str(value).replace('+', '').replace(',', '').strip()
    
    # 处理 "w" 或 "W"（万）
    if 'w' in value_str.lower():
        value_str = value_str.lower().replace('w', '')
        try:
            return int(float(value_str) * 10000)
        except:
            return 0
    
    try:
        return int(float(value_str))
    except:
        return 0


def fuzzy_count(value):
    """对5000+的互动数做模糊处理，5000以下保留原始数值"""
    if value is None:
        return '--'
    num = parse_count(value)
    if num <= 0:
        return '--'
    if num < 5000:
        return str(num)
    if num < 10000:
        return '5000+'
    # 1万以上：以万为单位，向下取整
    wan = num // 10000
    return f'{wan}w+'


def fetch_xhs_hot_notes(keyword: str, debug: bool = False, max_retries: int = 3, 
                        start_date: str = None, end_date: str = None, 
                        page_num: int = 1, page_size: int = 50):
    """调用接口获取小红书热门笔记数据"""
    # 从环境变量读取 API Key
    api_key = os.environ.get("REDFOX_API_KEY", "").strip()
    if not api_key:
        print("❌ 错误：未找到 REDFOX_API_KEY 环境变量。", file=sys.stderr)
        print("请在 Coze 平台的环境变量配置中添加 REDFOX_API_KEY，或在本地 shell 配置文件（如 ~/.zshrc / ~/.bashrc）中添加：", file=sys.stderr)
        print("  export REDFOX_API_KEY=your_api_key_here", file=sys.stderr)
        sys.exit(1)
    
    # 构建请求
    url = "https://redfox.hk/story/api/xhs/search/search"
    headers = {
        "Content-Type": "application/json",
        "X-API-KEY": api_key
    }
    payload = {
        "keyword": keyword,
        "pageNum": page_num,
        "pageSize": page_size,
        "startDate": start_date or "",
        "endDate": end_date or "",
        "source": "小红书爆款笔记洞察-SkillHub"
    }
    
    import time
    last_error = None
    for attempt in range(max_retries):
        try:
            if debug:
                print(f"\n=== DEBUG: 第 {attempt + 1} 次尝试 ===", file=sys.stderr)
                print(f"请求参数: {json.dumps(payload, ensure_ascii=False)}", file=sys.stderr)
            
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            req = urllib.request.Request(url, data=body, headers=headers, method="POST")
            
            with urllib.request.urlopen(req, timeout=30) as resp:
                status_code = resp.status
                raw = resp.read().decode("utf-8")
            
            if debug:
                print(f"状态码: {status_code}", file=sys.stderr)
                print(f"响应长度: {len(raw)} 字节", file=sys.stderr)
            
            data = json.loads(raw)
            
            # 检查返回码
            if data.get("code") != 2000:
                raise Exception(f"API 错误: {data.get('msg', '未知错误')}")
            
            result_data = data.get("data", {})
            
            if debug:
                print("=== DEBUG: API 返回的 data 字段键 ===", file=sys.stderr)
                print(json.dumps(list(result_data.keys()), ensure_ascii=False, indent=2), file=sys.stderr)
                print(f"总条数: {result_data.get('total', 0)}", file=sys.stderr)
            
            articles = result_data.get("articles", [])
            return {
                "keyword": result_data.get("keyword", keyword),
                "articles": articles,
                "total": len(articles),
                "pageNum": result_data.get("pageNum", page_num),
                "pageSize": result_data.get("pageSize", page_size),
                "hotTopics": result_data.get("hotTopics", []),
                "relatedSearches": result_data.get("relatedSearches", []),
                "latestHotArticles": result_data.get("latestHotArticles", [])
            }
            
        except urllib.error.HTTPError as e:
            last_error = f"HTTP请求失败: 状态码 {e.code}, {e.read().decode('utf-8', errors='ignore')[:200]}"
            if debug:
                print(f"  错误: {last_error[:100]}", file=sys.stderr)
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            continue
        except urllib.error.URLError as e:
            last_error = f"请求失败: {str(e.reason)}"
            if debug:
                print(f"  错误: {last_error[:100]}", file=sys.stderr)
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            continue
        except Exception as e:
            last_error = str(e)
            if debug:
                print(f"  错误: {str(e)[:100]}", file=sys.stderr)
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            continue
    
    raise Exception(f"{last_error}（已尝试 {max_retries} 次）")


def get_cover_urls(data, max_items=10):
    """提取所有封面图URL"""
    urls = []
    articles = data.get("articles", [])[:max_items]
    for item in articles:
        cover_url = item.get('cover', '')
        note_id = item.get('id', '')
        title = (item.get('title', '') or item.get('desc', ''))[:30]
        if cover_url and note_id:
            urls.append({
                'title': title,
                'note_id': note_id,
                'cover_url': cover_url,
                'link': item.get('shareInfoLink', f"https://www.xiaohongshu.com/explore/{note_id}")
            })
    return urls


def get_top_articles(data, max_items=10):
    """
    获取文章列表（按接口原始返回顺序，截取前 max_items 条）
    """
    articles = data.get("articles", [])[:max_items]
    return articles


def format_as_html(data: dict, max_items: int = 10, start_date: str = None):
    """
    格式化输出热门笔记数据（HTML 卡片布局）
    """
    from datetime import datetime
    
    keyword = data.get("keyword", "")
    total = data.get("total", 0)
    is_full_site = not keyword or keyword.strip() == ""
    
    def process_title(item):
        """处理标题"""
        title = item.get('title', '')
        if not title or title.strip() == '':
            desc = item.get('desc', '')
            if desc:
                title = desc.replace('\n', ' ').replace('\r', ' ').strip()[:30]
                if len(desc) > 30:
                    title = title + '...'
        if not title or title.strip() == '':
            title = '无标题'
        title = title.replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
        return title
    
    def format_time(item):
        """格式化发布时间"""
        create_time = item.get('createTime', '')
        if create_time:
            try:
                month = int(create_time[5:7])
                day = int(create_time[8:10])
                return f"{month}月{day}日"
            except:
                pass
        return '--'
    
    def generate_card(item, idx):
        """生成单个卡片 HTML"""
        
        note_id = item.get('id', '')
        author_id = item.get('authorId', '')
        author_name = item.get('authorNickname', '未知')
        fans = item.get('authorFans', 0)
        title = process_title(item)
        pub_time = format_time(item)
        interactive_count = fuzzy_count(item.get('interactiveCount', 0))
        like_count = fuzzy_count(item.get('likedCount', 0))
        collect_count = fuzzy_count(item.get('collectedCount', 0))
        
        # 作品链接
        note_link = item.get('shareInfoLink') or f"https://www.xiaohongshu.com/explore/{note_id}"
        # 作者主页链接
        author_link = f"https://www.xiaohongshu.com/user/profile/{author_id}" if author_id else "#"
        
        relevance_score = item.get('relevanceScore', 0)
        popularity_score = item.get('popularityScore', 0)
        recency_score = item.get('recencyScore', 0)
        total_score = item.get('totalScore', 0)

        # 评分标签（全站热门时不展示）
        scores_html = ''
        if not is_full_site:
            scores_html = f'''
            <div class="card-scores">
                <span class="score-tag relevance">相关性 {relevance_score}</span>
                <span class="score-tag popularity">热度 {popularity_score}</span>
                <span class="score-tag recency">时效 {recency_score}</span>
            </div>
            '''

        card_html = f'''
        <div class="card">
            <div class="card-title-row">
                <span class="card-index">{idx + 1}.</span>
                <a href="{note_link}" class="card-title" target="_blank">{title}</a>
            </div>
            <div class="card-meta">
                <a href="{author_link}" class="author-link" target="_blank">{author_name}（{fuzzy_count(fans)}粉）</a>
                <span class="meta-divider">·</span>
                <span class="pub-time">发布日期：{pub_time}</span>
            </div>
            {scores_html}
            <div class="card-stats">
                <span class="interaction-count">🔥 {interactive_count}互动</span>
                <span class="detail-stats">👍{like_count} ⭐{collect_count}</span>
                <a href="{note_link}" class="view-note-btn" target="_blank">查看作品 ↗</a>
            </div>
        </div>
        '''
        return card_html
    
    # 获取数据（接口原始顺序）
    top_items = get_top_articles(data, max_items)
    latest_hot_items = data.get("latestHotArticles", [])[:10]
    
    # 主列表为空时的提示
    no_articles_hint = ''
    if not top_items:
        no_articles_hint = '''
        <div class="no-data-hint">
            <p>未查询到相关热门笔记，建议更换关键词重试。</p>
        </div>
        '''
    
    cards_html = ''.join([generate_card(item, idx) for idx, item in enumerate(top_items)]) if top_items else ''
    
    # 推荐热门笔记区域（latestHotArticles，仅在有关键词文章时额外展示）
    latest_hot_html = ''
    if latest_hot_items:
        latest_cards = ''.join([generate_card(item, idx) for idx, item in enumerate(latest_hot_items)])
        latest_hot_html = f'''
        <div class="section-header">
            <h2>近期热门笔记推荐</h2>
        </div>
        <div class="card-grid">
            {latest_cards}
        </div>
        '''
    
    time_range = f"近30天" if not start_date else f"从{start_date}起"
    
    html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>小红书热门笔记数据分析报告</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background-color: #f5f5f5;
            padding: 16px;
            color: #333;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        .report-header {{
            background: linear-gradient(135deg, #ff2442 0%, #ff6b81 100%);
            color: white;
            padding: 20px 24px;
            border-radius: 12px;
            margin-bottom: 20px;
        }}
        .report-header h1 {{
            font-size: 20px;
            margin-bottom: 8px;
        }}
        .report-header .keyword {{
            font-size: 14px;
            opacity: 0.9;
        }}
        .report-header .total {{
            font-size: 12px;
            opacity: 0.8;
            margin-top: 4px;
        }}
        .card-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 16px;
        }}
        .card {{
            background: white;
            border-radius: 12px;
            padding: 16px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            transition: transform 0.2s, box-shadow 0.2s;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }}
        .card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 16px rgba(0,0,0,0.12);
        }}
        .card-title-row {{
            border-bottom: 1px solid #f0f0f0;
            padding-bottom: 10px;
            display: flex;
            align-items: flex-start;
            gap: 6px;
        }}
        .card-index {{
            font-size: 15px;
            font-weight: 700;
            color: #ff2442;
            min-width: 20px;
        }}
        .card-title {{
            font-size: 15px;
            font-weight: 700;
            color: #1a1a1a;
            text-decoration: none;
            line-height: 1.5;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
            transition: color 0.2s;
        }}
        .card-title:hover {{
            color: #ff2442;
        }}
        .card-meta {{
            font-size: 13px;
            color: #999;
            padding: 8px 0;
        }}
        .author-link {{
            color: #666;
            text-decoration: none;
            transition: color 0.2s;
        }}
        .author-link:hover {{
            color: #ff2442;
        }}
        .meta-divider {{
            margin: 0 6px;
        }}
        .pub-time {{
            color: #999;
        }}
        .card-scores {{
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }}
        .score-tag {{
            font-size: 12px;
            padding: 2px 8px;
            border-radius: 10px;
            font-weight: 500;
        }}
        .score-tag.relevance {{
            background: #e8f5e9;
            color: #2e7d32;
        }}
        .score-tag.popularity {{
            background: #fff3e0;
            color: #e65100;
        }}
        .score-tag.recency {{
            background: #e3f2fd;
            color: #1565c0;
        }}
        .card-stats {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 16px;
            margin: 0 -16px;
            background: linear-gradient(135deg, #fff5f5, #fff);
        }}
        .interaction-count {{
            font-size: 14px;
            font-weight: 600;
            color: #ff2442;
        }}
        .detail-stats {{
            font-size: 12px;
            color: #666;
        }}
        .view-note-btn {{
            color: #ff2442;
            text-decoration: none;
            font-size: 14px;
            font-weight: 500;
            transition: opacity 0.2s;
        }}
        .view-note-btn:hover {{
            opacity: 0.7;
            text-decoration: underline;
        }}
        .data-note {{
            text-align: center;
            color: #999;
            font-size: 12px;
            margin-top: 20px;
            padding: 12px;
            background: white;
            border-radius: 8px;
        }}
        .section-header {{
            margin-top: 24px;
            margin-bottom: 16px;
            padding: 12px 16px;
            background: linear-gradient(135deg, #ff6b81 0%, #ff2442 100%);
            border-radius: 8px;
        }}
        .section-header h2 {{
            color: white;
            font-size: 16px;
            font-weight: 600;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="report-header">
            <h1>小红书热门笔记数据分析报告</h1>
            <div class="keyword">关键词：{keyword} | 时间范围：{time_range}</div>
            <div class="total">共找到 {total} 条相关笔记</div>
        </div>
        
        {no_articles_hint}
        <div class="card-grid">
            {cards_html}
        </div>
        
        {latest_hot_html}
        
        <div class="data-note">
            数据来源：小红书热门笔记搜索，每日更新最新热门内容<br>
            备注：互动数据为入库快照，实时数据可能持续增长
        </div>
    </div>
</body>
</html>'''
    
    return html_content


def format_as_json(data: dict, max_items: int = 10):
    """
    格式化输出 JSON 格式（供智能体分析生成推荐理由）
    """
    top_items = get_top_articles(data, max_items)
    keyword = data.get('keyword', '')
    is_full_site = not keyword or keyword.strip() == ""
    latest_hot_items = data.get("latestHotArticles", [])[:10]
    
    result = []
    for item in top_items:
        note_id = item.get('id', '')
        item_data = {
            'noteId': note_id,
            'title': item.get('title', '') or item.get('desc', '')[:50],
            'desc': item.get('desc', ''),
            'authorId': item.get('authorId', ''),
            'authorNickname': item.get('authorNickname', ''),
            'authorFans': fuzzy_count(item.get('authorFans', 0)),
            'createTime': item.get('createTime', ''),
            'noteLink': item.get('shareInfoLink') or f"https://www.xiaohongshu.com/explore/{note_id}",
            'authorLink': f"https://www.xiaohongshu.com/user/profile/{item.get('authorId', '')}" if item.get('authorId') else '',
            'interactiveCount': fuzzy_count(item.get('interactiveCount', 0)),
            'likedCount': fuzzy_count(item.get('likedCount', 0)),
            'collectedCount': fuzzy_count(item.get('collectedCount', 0)),
            'commentsCount': fuzzy_count(item.get('commentsCount', 0)),
            'sharedCount': fuzzy_count(item.get('sharedCount', 0)),
        }
        # 有关键词时才输出评分字段
        if not is_full_site:
            item_data['totalScore'] = item.get('totalScore', 0)
            item_data['relevanceScore'] = item.get('relevanceScore', 0)
            item_data['popularityScore'] = item.get('popularityScore', 0)
            item_data['recencyScore'] = item.get('recencyScore', 0)
        result.append(item_data)
    
    # 格式化推荐热门笔记（latestHotArticles，无评分字段）
    latest_hot_result = []
    for item in latest_hot_items:
        note_id = item.get('id', '')
        latest_hot_result.append({
            'noteId': note_id,
            'title': item.get('title', '') or item.get('desc', '')[:50],
            'authorNickname': item.get('authorNickname', ''),
            'authorFans': fuzzy_count(item.get('authorFans', 0)),
            'createTime': item.get('createTime', ''),
            'noteLink': item.get('shareInfoLink') or f"https://www.xiaohongshu.com/explore/{note_id}",
            'authorLink': f"https://www.xiaohongshu.com/user/profile/{item.get('authorId', '')}" if item.get('authorId') else '',
            'interactiveCount': fuzzy_count(item.get('interactiveCount', 0)),
            'likedCount': fuzzy_count(item.get('likedCount', 0)),
            'collectedCount': fuzzy_count(item.get('collectedCount', 0)),
        })

    return {
        'keyword': data.get('keyword', ''),
        'total': data.get('total', 0),
        'pageNum': data.get('pageNum', 1),
        'pageSize': data.get('pageSize', 50),
        'isFullSite': is_full_site,
        'items': result,
        'latestHotArticles': latest_hot_result,
        'relatedSearches': data.get('relatedSearches', [])
    }


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='小红书热门笔记搜索工具')
    parser.add_argument('--keyword', required=True, help='搜索关键词')
    parser.add_argument('--max-items', type=int, default=10, 
                       help='最多展示数量（默认10条）')
    parser.add_argument('--output-format', choices=['json', 'html'], 
                       default='json', help='输出格式（默认json输出到stdout，html输出到文件）')
    parser.add_argument('--output-file', type=str, default=None, 
                       help='输出文件路径（默认：关键词_热门数据.html）')
    parser.add_argument('--start-date', type=str, default=None,
                       help='开始日期，格式 yyyy-MM-dd')
    parser.add_argument('--end-date', type=str, default=None,
                       help='结束日期，格式 yyyy-MM-dd')
    parser.add_argument('--page-num', type=int, default=1,
                       help='页码（默认1）')
    parser.add_argument('--page-size', type=int, default=50,
                       help='每页条数（默认50）')
    parser.add_argument('--debug', action='store_true', help='启用调试模式')
    parser.add_argument('--max-retries', type=int, default=3, 
                       help='最大重试次数（默认3次）')
    
    args = parser.parse_args()
    
    try:
        data = fetch_xhs_hot_notes(
            keyword=args.keyword, 
            debug=args.debug, 
            max_retries=args.max_retries, 
            start_date=args.start_date,
            end_date=args.end_date,
            page_num=args.page_num,
            page_size=args.page_size
        )
        
        # 生成 JSON 数据（始终输出到 stdout，供智能体读取）
        json_data = format_as_json(data, max_items=args.max_items)
        
        # 输出 JSON 到 stdout（智能体从此读取结构化数据）
        print(json.dumps(json_data, ensure_ascii=False, indent=2))
        
        # 同时生成 HTML 文件
        html_content = format_as_html(data, max_items=args.max_items, start_date=args.start_date)
        keyword_safe = args.keyword.replace('"', '').replace(' ', '_') or '全站热门'
        html_file = args.output_file or f"{keyword_safe}_热门数据.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # 统计信息输出到 stderr
        print(f"✓ HTML 结果已保存到: {html_file}", file=sys.stderr)
        print(f"✓ 关键词: {args.keyword}", file=sys.stderr)
        print(f"✓ 总条数: {json_data['total']} 条", file=sys.stderr)
        print(f"✓ 筛选结果: {len(json_data['items'])} 条", file=sys.stderr)
        print(f"✓ 推荐热门笔记: {len(json_data.get('latestHotArticles', []))} 条", file=sys.stderr)
        
        # 输出封面图URL供后续分析
        cover_urls = get_cover_urls(data, max_items=5)
        if cover_urls:
            print(f"\n=== 封面图URL（用于风格分析）===", file=sys.stderr)
            for i, item in enumerate(cover_urls, 1):
                print(f"{i}. {item['title']}: {item['cover_url']}", file=sys.stderr)
                
    except Exception as e:
        print(f"❌ 错误: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
