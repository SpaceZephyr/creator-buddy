#!/usr/bin/env python3
"""
公众号爆款数据查询脚本（支持 HTML 卡片布局输出）
支持跨分类统一排序、数据评分、分类多样性保证
榜单类型：低粉高阅读榜、阅读靠前榜、原创靠前榜、数据增长榜
"""

import sys
import re
import argparse
import html
import json
import socket
import ssl
import gzip
from urllib.parse import quote, urlparse


def sanitize_http_url(url) -> str:
    """返回可信的 http(s) URL 字符串；非法 scheme 或过长则返回空字符串。"""
    if url is None:
        return ""
    if not isinstance(url, str):
        url = str(url)
    url = url.strip()
    if not url or len(url) > 4096:
        return ""
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return ""
    return url


def safe_href_url(url) -> str:
    """HTML 属性用 href：在 sanitize 后再转义，防止 javascript:/data: 与属性注入。"""
    u = sanitize_http_url(url)
    if not u:
        return "#"
    return html.escape(u, quote=True)


def safe_wechat_account_id(account_id) -> str:
    """公众号原始 ID/username，用于二维码链接查询参数；非法字符直接丢弃。"""
    if account_id is None:
        return ""
    s = str(account_id).strip()
    if not s or len(s) > 64:
        return ""
    if not re.fullmatch(r"[A-Za-z0-9._-]+", s):
        return ""
    return s


def safe_filename_from_keyword(keyword: str, max_len: int = 120) -> str:
    """默认输出文件名由关键词推导时，去掉路径分隔符与穿越片段，降低路径遍历风险。"""
    base = keyword.strip() if keyword else ""
    if not base:
        return ""
    base = base.replace("\\", "_").replace("/", "_").replace("\x00", "")
    base = re.sub(r"\.+", "_", base)
    if base in (".", "..") or ".." in base:
        base = "keyword"
    return base[:max_len] if len(base) > max_len else base


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
        except Exception:
            return 0
    
    try:
        return int(float(value_str))
    except Exception:
        return 0


def decode_chunked(data):
    """解码 chunked 传输编码"""
    chunks = []
    idx = 0
    
    while idx < len(data):
        line_end = data.find(b'\r\n', idx)
        if line_end == -1:
            break
        
        chunk_size_line = data[idx:line_end]
        try:
            chunk_size = int(chunk_size_line, 16)
        except Exception:
            break
        
        if chunk_size == 0:
            break
        
        chunk_start = line_end + 2
        chunk_end = chunk_start + chunk_size
        
        if chunk_end > len(data):
            break
        
        chunk = data[chunk_start:chunk_end]
        chunks.append(chunk)
        idx = chunk_end + 2
    
    return b''.join(chunks)


def fetch_via_no_sni(base_url: str, params: dict, headers: dict, timeout: int = 60):
    """使用原生 socket 实现 HTTPS 请求（不发送 SNI）"""
    if "://" in base_url:
        base_url = base_url.split("://", 1)[1]
    host, path = base_url.split("/", 1)
    
    if params:
        query = "&".join(f"{quote(str(k))}={quote(str(v))}" for k, v in params.items())
        path = f"{path}?{query}"
    
    sock = socket.create_connection((host, 443), timeout=timeout)
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    ssl_sock = context.wrap_socket(sock, server_hostname=None)
    
    request_lines = [
        f"GET /{path} HTTP/1.1",
        f"Host: {host}",
    ]
    for k, v in headers.items():
        request_lines.append(f"{k}: {v}")
    request_lines.append("")
    request_lines.append("")
    
    request = "\r\n".join(request_lines)
    ssl_sock.send(request.encode())
    
    response_data = b""
    while True:
        try:
            chunk = ssl_sock.recv(8192)
            if not chunk:
                break
            response_data += chunk
        except Exception:
            break
    
    ssl_sock.close()
    
    response_str = response_data.decode('utf-8', errors='ignore')
    lines = response_str.split('\r\n')
    status_code = int(lines[0].split()[1])
    
    headers_dict = {}
    for i, line in enumerate(lines[1:]):
        if line == '':
            break
        if ':' in line:
            key, value = line.split(':', 1)
            headers_dict[key.strip().lower()] = value.strip()
    
    header_end = response_data.find(b'\r\n\r\n')
    body_bytes = response_data[header_end + 4:] if header_end != -1 else b""
    
    if headers_dict.get('transfer-encoding', '').lower() == 'chunked':
        body_bytes = decode_chunked(body_bytes)
    
    if headers_dict.get('content-encoding', '').lower() == 'gzip':
        try:
            body_bytes = gzip.decompress(body_bytes)
        except Exception:
            pass
    
    return status_code, body_bytes.decode('utf-8', errors='ignore')


def fetch_gzh_trends(keyword: str, debug: bool = False, max_retries: int = 3, start_date: str = None):
    """调用接口获取公众号爆款数据"""
    base_url = "https://onetotenvip.com/skill/cozeSkill/getWxCozeSkillData"
    params = {"keyword": keyword, "source": "公众号爆款文章洞察-SkillHub"}
    
    if start_date:
        params["startDate"] = start_date
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "close",
    }
    
    last_error = None
    for attempt in range(max_retries):
        try:
            if debug:
                print(f"\n=== DEBUG: 第 {attempt + 1} 次尝试 ===", file=sys.stderr)
            
            status_code, body = fetch_via_no_sni(base_url, params, headers)
            
            if debug:
                print(f"状态码: {status_code}", file=sys.stderr)
                print(f"响应长度: {len(body)} 字节", file=sys.stderr)
            
            if status_code >= 400:
                raise Exception(f"HTTP请求失败: 状态码 {status_code}")
            
            data = json.loads(body)
            
            if "data" not in data:
                raise Exception(f"API 错误: {data.get('msg', '未知错误')}")
            
            result_data = data.get("data", {})
            
            if debug:
                print("=== DEBUG: API 返回的 data 字段键 ===", file=sys.stderr)
                print(json.dumps(list(result_data.keys()), ensure_ascii=False, indent=2), file=sys.stderr)
            
            return {
                "keyword": keyword,
                "low_fan_explosive": result_data.get("lowPowderExplosiveArticle", []),
                "ten_w_reading": result_data.get("tenWReadingRank", []),
                "original_rank": result_data.get("originalRank", []),
                "one_w_reading": result_data.get("oneWReadingRank", [])
            }
            
        except Exception as e:
            last_error = str(e)
            if debug:
                print(f"  错误: {type(e).__name__}: {str(e)[:100]}", file=sys.stderr)
            import time
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            continue
    
    raise Exception(f"{last_error}（已尝试 {max_retries} 次）")


def get_cover_urls(data, max_per_category=5):
    """提取所有封面图URL"""
    urls = []
    categories = [
        ('low_fan_explosive', '低粉高阅读'),
        ('ten_w_reading', '阅读靠前'),
        ('original_rank', '原创靠前'),
        ('one_w_reading', '数据增长中')
    ]
    for key, name in categories:
        items = data.get(key, [])[:max_per_category]
        for item in items:
            cover_url = item.get('coverUrl', '')
            photo_id = item.get('photoId', '')
            title = (item.get('summary', '') or item.get('title', ''))[:20]
            if cover_url and photo_id:
                link = sanitize_http_url(f"https://mp.weixin.qq.com/s/{photo_id}") or ""
                urls.append({
                    'category': name,
                    'title': title,
                    'photo_id': photo_id,
                    'cover_url': cover_url,
                    'link': link,
                })
    return urls


def calculate_data_score(item, cat_key):
    """
    计算数据表现分数（0-100分）
    
    评分维度：
    - 点赞权重 30%（传播广度）
    - 收藏权重 30%（实用价值）- 公众号无收藏，改为分享权重
    - 评论权重 25%（互动深度）
    - 分享权重 15%（传播力）
    - 阅读数权重（新增，公众号特有）
    """
    like_num = parse_count(item.get('likeCount', 0))
    comment_num = parse_count(item.get('useCommentCount', 0) or item.get('commentCount', 0))
    share_num = parse_count(item.get('shareCount', 0))
    clicks_num = parse_count(item.get('clicksCount', 0))
    interactive_num = parse_count(item.get('interactiveCount', 0))
    
    # 计算加权分数
    total_inter = like_num + comment_num + share_num + interactive_num
    if total_inter == 0:
        return 0
    
    # 归一化到 0-100 分
    # 使用对数缩放，避免极值影响
    import math
    
    score = (
        math.log10(like_num + 1) * 15 +      # 点赞
        math.log10(share_num + 1) * 20 +     # 分享（权重最高，公众号核心指标）
        math.log10(comment_num + 1) * 18 +   # 评论
        math.log10(interactive_num + 1) * 12 # 互动总数
    )
    
    # 阅读数额外加分（公众号核心指标）
    if clicks_num > 0:
        score += min(15, math.log10(clicks_num + 1) * 3)  # 最高15分
    
    # 低粉高阅读额外加分（小号爆款更有参考价值）
    if cat_key == 'low_fan_explosive':
        fans = parse_count(item.get('fans', 0))
        if fans > 0 and fans < 10000:
            score += 8  # 万粉以下爆款加分
        elif fans > 0 and fans < 50000:
            score += 5  # 五万粉以下爆款加分
    
    # 阅读靠前额外加分
    if cat_key == 'ten_w_reading' and clicks_num >= 100000:
        score += 10
    
    return min(100, score)


def merge_and_sort_all(data, max_items=10):
    """
    跨分类合并数据并排序
    
    核心逻辑：
    1. 合并所有分类数据到一个候选池
    2. 去重
    3. 计算每条内容的数据分数
    4. 按分数全局排序
    5. 保证分类多样性
    """
    categories = [
        ('low_fan_explosive', '低粉高阅读'),
        ('ten_w_reading', '阅读靠前'),
        ('original_rank', '原创靠前'),
        ('one_w_reading', '数据增长中')
    ]
    
    # 1. 合并所有分类数据
    all_items = []
    for cat_key, cat_name in categories:
        items = data.get(cat_key, [])
        for item in items:
            all_items.append((cat_key, cat_name, item))
    
    # 2. 去重（按 photoId）
    seen = set()
    deduped_items = []
    for cat_key, cat_name, item in all_items:
        photo_id = item.get('photoId', '')
        if photo_id and photo_id not in seen:
            seen.add(photo_id)
            deduped_items.append((cat_key, cat_name, item))
    
    # 3. 计算分数并排序
    scored_items = []
    for cat_key, cat_name, item in deduped_items:
        score = calculate_data_score(item, cat_key)
        scored_items.append({
            'cat_key': cat_key,
            'cat_name': cat_name,
            'item': item,
            'score': score
        })
    
    # 4. 按分数降序排序
    scored_items.sort(key=lambda x: x['score'], reverse=True)
    
    # 5. 保证分类多样性（至少2个分类有数据）
    result = ensure_category_diversity(scored_items, max_items)
    
    return result


def ensure_category_diversity(scored_items, max_items=10):
    """
    保证分类多样性
    
    规则：
    - 必须覆盖 ≥3 个分类
    - 如果只有1个分类，从其他分类补充
    - 优先选择分数高的内容
    """
    if not scored_items:
        return []
    
    # 统计各分类数量
    cat_counts = {}
    for item in scored_items:
        cat_key = item['cat_key']
        cat_counts[cat_key] = cat_counts.get(cat_key, 0) + 1
    
    # 如果只有1个分类
    if len(cat_counts) == 1:
        only_cat = list(cat_counts.keys())[0]
        # 检查是否有其他分类的数据
        other_cat_items = [item for item in scored_items if item['cat_key'] != only_cat]
        if not other_cat_items:
            # 确实只有一个分类的数据，直接返回
            return scored_items[:max_items]
    
    # 多分类选择策略
    # 按分类分组
    cat_items = {}
    for item in scored_items:
        cat_key = item['cat_key']
        if cat_key not in cat_items:
            cat_items[cat_key] = []
        cat_items[cat_key].append(item)
    
    # 轮流从各分类选取，保证多样性
    result = []
    used_indices = {cat_key: 0 for cat_key in cat_items}
    
    # 按分数排序分类（该分类最高分内容排序）
    sorted_cats = sorted(cat_items.keys(), 
                        key=lambda k: cat_items[k][0]['score'] if cat_items[k] else 0, 
                        reverse=True)
    
    while len(result) < max_items:
        added = False
        for cat_key in sorted_cats:
            if used_indices[cat_key] < len(cat_items[cat_key]):
                result.append(cat_items[cat_key][used_indices[cat_key]])
                used_indices[cat_key] += 1
                added = True
                if len(result) >= max_items:
                    break
        if not added:
            break
    
    # 按分数重新排序最终结果
    result.sort(key=lambda x: x['score'], reverse=True)
    
    return result


def format_as_html(data: dict, max_items: int = 10, start_date: str = None):
    """
    格式化输出爆款数据（HTML 卡片布局）
    使用跨分类统一排序
    """
    from datetime import datetime
    
    def get_time_range(start_date):
        if start_date:
            try:
                start = datetime.strptime(start_date, '%Y-%m-%d')
                end = datetime.now()
                days = (end - start).days
                return f"近{days}天" if days > 1 else "近1天"
            except Exception:
                return "近30天"
        return "近30天"
    
    time_range = get_time_range(start_date)
    
    def process_title(item):
        """处理标题 - 从 summary 提取"""
        title = item.get('title', '')
        if not title or title.strip() == '':
            summary = item.get('summary', '')
            if summary:
                title = summary.replace('\n', ' ').replace('\r', ' ').strip()[:30]
                if len(summary) > 30:
                    title = title + '...'
        if not title or title.strip() == '':
            title = '无标题'
        return html.escape(str(title), quote=False)
    
    def format_time(item):
        """格式化发布时间"""
        pub_time = item.get('publicTime', '')
        if pub_time:
            try:
                month = int(pub_time[5:7])
                day = int(pub_time[8:10])
                return html.escape(f"{month}月{day}日", quote=False)
            except Exception:
                pass
        return html.escape('--', quote=False)
    
    def get_category_label(cat_key):
        labels = {
            'low_fan_explosive': '低粉高阅读',
            'ten_w_reading': '阅读靠前',
            'original_rank': '原创靠前',
            'one_w_reading': '数据增长中'
        }
        return labels.get(cat_key, '爆款')
    
    def generate_card(item_data, idx):
        """生成单个卡片 HTML"""
        cat_key = item_data['cat_key']
        cat_name = item_data['cat_name']
        item = item_data['item']
        score = item_data['score']
        
        photo_id = item.get('photoId', '')
        account_id = item.get('accountId', '')
        fans = item.get('fans', 0)
        title = process_title(item)
        pub_time = format_time(item)
        clicks_display = html.escape(str(item.get('clicksCount', '0')), quote=False)
        
        # 作品链接：仅允许 http/https，防止 javascript:/data: 注入
        note_link = safe_href_url(item.get('oriUrl', ''))
        acc_safe = safe_wechat_account_id(account_id)
        if acc_safe:
            author_link = safe_href_url(
                f"https://open.weixin.qq.com/qr/code?username={quote(acc_safe, safe='')}"
            )
        else:
            author_link = "#"
        raw_name = item.get('userName', '') or item.get('accountId', '未知账号')
        account_name = html.escape(str(raw_name), quote=False)
        cat_name_esc = html.escape(str(cat_name), quote=False)
        
        card_html = f'''
        <div class="card">
            <div class="card-title-row">
                <span class="card-index">{idx + 1}.</span>
                <a href="{note_link}" class="card-title" target="_blank" rel="noopener noreferrer">{title}</a>
            </div>
            <div class="card-meta">
                <a href="{author_link}" class="author-link" target="_blank" rel="noopener noreferrer">{account_name}</a>
                <span class="meta-divider">·</span>
                <span class="pub-time">发布日期：{pub_time}</span>
            </div>
            <div class="card-stats">
                <span class="read-count">📖 {clicks_display}阅读</span>
                <span class="category-tag">{cat_name_esc}</span>
                <a href="{note_link}" class="view-note-btn" target="_blank" rel="noopener noreferrer">查看作品 ↗</a>
            </div>
        </div>
        '''
        return card_html
    
    # 使用跨分类统一排序
    sorted_items = merge_and_sort_all(data, max_items)
    
    if not sorted_items:
        return f'''
        <div class="container">
            <h2>暂无相关爆款数据</h2>
            <p>很抱歉，当前关键词暂无足够的爆款文章数据。</p>
            <p>建议更换为更热门的关键词，如"职场干货"、"育儿经验"、"情感故事"等。</p>
        </div>
        '''
    
    cards_html = ''.join([generate_card(item_data, idx) for idx, item_data in enumerate(sorted_items)])
    
    keyword = html.escape(str(data.get("keyword", "全站热门")), quote=False)
    time_range_esc = html.escape(str(time_range), quote=False)
    
    html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>公众号爆款数据分析报告</title>
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
            background: linear-gradient(135deg, #07c160 0%, #1aad19 100%);
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
            color: #07c160;
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
            color: #07c160;
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
            color: #07c160;
        }}
        .meta-divider {{
            margin: 0 6px;
        }}
        .pub-time {{
            color: #999;
        }}
        .card-stats {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 16px;
            margin: 0 -16px;
            background: linear-gradient(135deg, #f0f9f4, #fff);
            flex-wrap: wrap;
            gap: 8px;
        }}
        .interaction-count {{
            font-size: 14px;
            font-weight: 600;
            color: #07c160;
        }}
        .read-count {{
            font-size: 12px;
            color: #666;
        }}
        .category-tag {{
            font-size: 12px;
            color: #1aad19;
            background: #e8f8ed;
            padding: 2px 8px;
            border-radius: 4px;
        }}
        .view-note-btn {{
            color: #07c160;
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
    </style>
</head>
<body>
    <div class="container">
        <div class="report-header">
            <h1>公众号爆款数据分析报告</h1>
            <div class="keyword">关键词：{keyword} | 时间范围：{time_range_esc}</div>
        </div>
        
        <div class="card-grid">
            {cards_html}
        </div>
        
        <div class="data-note">
            数据来源：公众号爆款文章查询，每日19点更新昨日热门内容<br>
            备注：互动数据为入库快照，实时数据可能持续增长
        </div>
    </div>
</body>
</html>'''
    
    return html_content


def format_as_json(data: dict, max_items: int = 10):
    """
    格式化输出 JSON 格式（供智能体分析生成推荐理由）
    使用跨分类统一排序
    """
    def get_interactive_count_json(item, cat_key):
        """获取互动数（JSON输出）"""
        count = item.get('interactiveCount')
        if count is not None:
            return parse_count(count)
        
        like = parse_count(item.get('likeCount', 0))
        comment = parse_count(item.get('commentCount', 0))
        share = parse_count(item.get('shareCount', 0))
        return like + comment + share
    
    # 使用跨分类统一排序
    sorted_items = merge_and_sort_all(data, max_items)
    
    result = []
    for item_data in sorted_items:
        cat_key = item_data['cat_key']
        cat_name = item_data['cat_name']
        item = item_data['item']
        score = item_data['score']
        
        photo_id = item.get('photoId', '')
        account_id = item.get('accountId', '')
        acc_safe = safe_wechat_account_id(account_id)
        
        result.append({
            'category': cat_name,
            'photoId': photo_id,
            'title': item.get('title', '') or item.get('summary', '')[:50],
            'summary': item.get('summary', ''),
            'accountId': account_id,
            'accountName': item.get('userName', '') or account_id,  # 优先使用 userName
            'fans': item.get('fans', 0),
            'publicTime': item.get('publicTime', ''),
            'noteLink': sanitize_http_url(item.get('oriUrl', '')),
            'authorLink': (
                f"https://open.weixin.qq.com/qr/code?username={quote(acc_safe, safe='')}"
                if acc_safe else ''
            ),
            'interactiveCount': get_interactive_count_json(item, cat_key),
            'likeCount': parse_count(item.get('likeCount', 0)),
            'commentCount': parse_count(item.get('commentCount', 0)),
            'shareCount': parse_count(item.get('shareCount', 0)),
            'clicksCount': item.get('clicksCount', '0'),
            'watchCount': item.get('watchCount', '0'),  # 在看数
            'dataScore': round(score, 2),  # 数据表现分数
        })
    
    return {
        'keyword': data.get('keyword', ''),
        'total': len(result),
        'items': result
    }


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='公众号爆款数据查询工具')
    parser.add_argument('--keyword', required=True, help='搜索关键词')
    parser.add_argument('--max-items', type=int, default=10, 
                       help='最多展示数量（默认10条）')
    parser.add_argument('--output-format', choices=['text', 'json', 'html'], 
                       default='html', help='输出格式：text（文本）、json（JSON）或 html（卡片布局，默认）')
    parser.add_argument('--output-file', type=str, default=None, 
                       help='输出文件路径（默认：关键词_爆款数据.html/json）')
    parser.add_argument('--start-date', type=str, default=None,
                       help='开始日期，格式 yyyy-MM-dd（默认：最近30天）')
    parser.add_argument('--debug', action='store_true',
                       help='调试模式，打印原始API响应')
    
    args = parser.parse_args()
    
    try:
        if args.output_file and "\x00" in args.output_file:
            raise ValueError("输出路径包含非法字符")

        # 查询数据
        data = fetch_gzh_trends(args.keyword, debug=args.debug, start_date=args.start_date)
        
        safe_kw = safe_filename_from_keyword(args.keyword)
        # 格式化输出
        if args.output_format == 'json':
            output = json.dumps(format_as_json(data, args.max_items), ensure_ascii=False, indent=2)
            default_filename = f"{safe_kw}_爆款数据.json" if safe_kw else "爆款数据.json"
        else:  # html
            output = format_as_html(data, args.max_items, args.start_date)
            default_filename = f"{safe_kw}_爆款数据.html" if safe_kw else "爆款数据.html"
        
        # 写入文件或打印到标准输出
        output_file = args.output_file or default_filename
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(output)
        
        print(f"✅ 数据已保存到: {output_file}")
        print(f"📊 查询关键词: {args.keyword}")
        print(f"📈 总数据量: {sum(len(data.get(k, [])) for k in ['low_fan_explosive', 'ten_w_reading', 'original_rank', 'one_w_reading'])} 条")
        
    except Exception as e:
        print(f"❌ 错误: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
