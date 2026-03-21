#!/usr/bin/env python3
"""
生成每日報告 HTML - 無限滾動瀑布流
按日期倒序展示（最新在前），滾動到底部時自動載入更多
"""

import os
import json
import datetime
import re
from pathlib import Path


def load_all_data():
    """載入所有數據，按日期排序（最新在前）"""
    data_dir = Path('data')
    all_items = []
    
    for json_file in sorted(data_dir.glob('*.json'), reverse=True):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, dict) and 'entries' in data:
                    items = data['entries']
                    file_date = data.get('date', json_file.stem)
                elif isinstance(data, list):
                    items = data
                    file_date = json_file.stem
                else:
                    continue
                    
                for item in items:
                    item['collected_date'] = file_date
                    
                    if 'summary' not in item:
                        item['summary'] = item.get('title_zh', '')[:50]
                    if 'content' not in item:
                        item['content'] = item.get('summary', item.get('title_zh', ''))
                    
                    url = item.get('url', '')
                    if 'www.reddit.com' in url:
                        item['url'] = url.replace('www.reddit.com', 'reddit.com')
                    
                    all_items.append(item)
        except Exception as e:
            print(f"Error loading {json_file}: {e}")
            continue
    
    all_items.sort(key=lambda x: (x.get('collected_date', ''), x.get('score', 0)), reverse=True)
    return all_items


def escape_js_str(s):
    """Escape string for JavaScript"""
    if s is None:
        return ''
    return str(s).replace('\\', '\\\\').replace('"', '\\"').replace("'", "\\'").replace('\n', '\\n').replace('\r', '')


def generate_card_html(item, index):
    """Generate HTML for a single card"""
    image = item.get('image', '')
    title = escape_js_str(item.get('title', ''))
    title_zh = escape_js_str(item.get('title_zh', title))
    url = escape_js_str(item.get('url', '#'))
    source = escape_js_str(item.get('subreddit', item.get('source', '')))
    score = item.get('score', 0)
    comments = item.get('num_comments', 0)
    tags = item.get('tags', [])
    collected_date = item.get('collected_date', '')
    preview = escape_js_str(item.get('summary', title_zh[:80]))
    
    date_badge = f'<span class="date-badge">{collected_date}</span>' if collected_date else ''
    img_tag = f'<img src="{image}" alt="" class="card-image" loading="lazy">' if image else '<div class="card-image-placeholder"></div>'
    tag_text = escape_js_str(tags[0] if tags else '')
    
    return f'''
        <div class="card" onclick="showModal({index})">
            {img_tag}
            <div class="card-content">
                {date_badge}
                <span class="card-source">{source}</span>
                <h3 class="card-title">{title_zh}</h3>
                <p class="card-preview">{preview}</p>
                <div class="card-footer">
                    <span>⬆️ {score} · 💬 {comments}</span>
                    <div>
                        <span class="tag">{tag_text}</span>
                    </div>
                </div>
            </div>
        </div>'''


def generate_html():
    """生成 HTML"""
    
    today = datetime.datetime.now()
    date_str = today.strftime('%Y年%m月%d日')
    
    items = load_all_data()
    
    page_size = 20
    first_page = items[:page_size]
    
    first_cards_html = ''
    for i, item in enumerate(first_page):
        first_cards_html += generate_card_html(item, i)
    
    cards_json = json.dumps(items, ensure_ascii=False)
    
    html = f'''<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>游戏美术外包日报</title>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --primary: #e20001;
            --dark: #1a1a1a;
            --gray: #666666;
            --light-gray: #f5f5f5;
            --white: #ffffff;
        }}
        
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: 'Noto Sans SC', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--white);
            color: var(--dark);
            line-height: 1.6;
        }}
        
        .container {{ max-width: 1400px; margin: 0 auto; padding: 0 20px; }}
        
        header {{
            padding: 40px 0 30px;
            border-bottom: 1px solid var(--light-gray);
            margin-bottom: 30px;
            text-align: center;
        }}
        
        .logo {{
            font-size: 13px;
            font-weight: 500;
            color: var(--gray);
            letter-spacing: 2px;
            text-transform: uppercase;
        }}
        
        h1 {{
            font-size: 32px;
            font-weight: 700;
            margin: 10px 0;
        }}
        
        .date {{
            color: var(--gray);
            font-size: 14px;
        }}
        
        .stats {{
            margin-top: 15px;
            font-size: 14px;
            color: var(--gray);
        }}
        
        .waterfall {{
            column-count: 4;
            column-gap: 20px;
            padding: 20px 0 40px;
        }}
        
        @media (max-width: 1200px) {{ .waterfall {{ column-count: 3; }} }}
        @media (max-width: 900px) {{ .waterfall {{ column-count: 2; }} }}
        @media (max-width: 600px) {{ .waterfall {{ column-count: 1; }} }}
        
        .card {{
            break-inside: avoid;
            background: var(--white);
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 2px 12px rgba(0,0,0,0.08);
            margin-bottom: 20px;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        
        .card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 6px 20px rgba(0,0,0,0.12);
        }}
        
        .card-image {{
            width: 100%;
            display: block;
            object-fit: cover;
        }}
        
        .card-image-placeholder {{
            width: 100%;
            height: 160px;
            background: linear-gradient(135deg, #f5f5f5 0%, #e0e0e0 100%);
        }}
        
        .card-content {{
            padding: 16px;
        }}
        
        .card-source {{
            display: inline-block;
            background: var(--primary);
            color: white;
            padding: 2px 8px;
            border-radius: 3px;
            font-size: 11px;
            margin-bottom: 8px;
        }}
        
        .date-badge {{
            display: inline-block;
            background: var(--dark);
            color: white;
            padding: 2px 8px;
            border-radius: 3px;
            font-size: 10px;
            margin-right: 6px;
        }}
        
        .card-title {{
            font-size: 14px;
            font-weight: 500;
            margin-bottom: 6px;
            line-height: 1.4;
        }}
        
        .card-preview {{
            font-size: 13px;
            color: var(--gray);
            margin-bottom: 10px;
            line-height: 1.5;
            display: -webkit-box;
            -webkit-line-clamp: 3;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }}
        
        .card-footer {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-top: 10px;
            border-top: 1px solid var(--light-gray);
            font-size: 12px;
            color: var(--gray);
        }}
        
        .tag {{
            background: var(--light-gray);
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 10px;
        }}
        
        .modal-overlay {{
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0);
            z-index: 1000;
            align-items: center;
            justify-content: center;
            padding: 20px;
            transition: background 0.3s ease;
        }}
        
        .modal-overlay.active {{
            display: flex;
            background: rgba(0,0,0,0.7);
        }}
        
        .modal {{
            background: var(--white);
            border-radius: 16px;
            max-width: 700px;
            width: 100%;
            max-height: 85vh;
            overflow-y: auto;
            position: relative;
            opacity: 0;
            transform: scale(0.7) translateY(30px);
            transition: all 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
        }}
        
        .modal-overlay.active .modal {{
            opacity: 1;
            transform: scale(1);
        }}
        
        .modal-close {{
            position: absolute;
            top: 16px;
            right: 16px;
            font-size: 24px;
            cursor: pointer;
            color: var(--gray);
            z-index: 10;
        }}
        
        .modal-image {{
            width: 100%;
            height: 300px;
            object-fit: cover;
            background: #f5f5f5;
        }}
        
        .modal-content {{
            padding: 24px;
        }}
        
        .modal-source {{
            display: inline-block;
            background: var(--primary);
            color: white;
            padding: 4px 12px;
            border-radius: 4px;
            font-size: 12px;
            margin-bottom: 12px;
        }}
        
        .modal-title {{
            font-size: 20px;
            font-weight: 600;
            margin-bottom: 8px;
        }}
        
        .modal-body {{
            font-size: 15px;
            line-height: 1.8;
            color: var(--dark);
            margin-bottom: 20px;
        }}
        
        .modal-original-title {{
            font-size: 13px;
            color: var(--gray);
            margin-bottom: 16px;
            font-style: italic;
        }}
        
        .modal-link {{
            color: var(--primary);
            text-decoration: underline;
            font-size: 14px;
        }}
        
        .modal-link:hover {{
            color: #cc0000;
        }}
        
        .loading {{
            text-align: center;
            padding: 30px;
            color: var(--gray);
            display: none;
        }}
        
        .loading.active {{
            display: block;
        }}
        
        .loading-spinner {{
            width: 30px;
            height: 30px;
            border: 3px solid var(--light-gray);
            border-top-color: var(--primary);
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 10px;
        }}
        
        @keyframes spin {{
            to {{ transform: rotate(360deg); }}
        }}
        
        footer {{
            padding: 30px 0;
            border-top: 1px solid var(--light-gray);
            text-align: center;
            color: var(--gray);
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="logo">Game Art Outsourcing</div>
            <h1>游戏美术外包日报</h1>
            <p class="date">{date_str}</p>
            <p class="stats">📊 {len(items)} 条讨论 · 滚动加载更多</p>
        </header>
'''

    if first_page:
        html += f'<div class="waterfall" id="cardContainer">{first_cards_html}</div>'
    else:
        html += '<p style="padding:40px;text-align:center;color:#666;">暂无数据</p><div class="waterfall" id="cardContainer"></div>'
    
    html += '''
        <div class="loading" id="loadingIndicator">
            <div class="loading-spinner"></div>
            <p>加载更多...</p>
        </div>
        
        <div class="modal-overlay" id="modal" onclick="closeModal(event)">
            <div class="modal" onclick="event.stopPropagation()">
                <span class="modal-close" onclick="hideModal()">✕</span>
                <img src="" alt="" class="modal-image" id="modalImage">
                <div class="modal-content">
                    <span class="modal-source" id="modalSource"></span>
                    <h2 class="modal-title" id="modalTitle"></h2>
                    <p class="modal-original-title" id="modalOriginalTitle"></p>
                    <div class="modal-body" id="modalBody"></div>
                    <a href="#" target="_blank" class="modal-link" id="modalLink">查看原文 →</a>
                </div>
            </div>
        </div>
    '''
    
    html += f'''
        <script>
        var allData = {cards_json};
        var currentIndex = {len(first_page)};
        var pageSize = {page_size};
        var totalItems = allData.length;
        
        var loadingIndicator = document.getElementById('loadingIndicator');
        var cardContainer = document.getElementById('cardContainer');
        
        function createCardHTML(item, index) {{
            var image = item.image || '';
            var title = item.title || '';
            var titleZh = item.title_zh || title;
            var source = item.subreddit || item.source || '';
            var score = item.score || 0;
            var comments = item.num_comments || 0;
            var tags = item.tags || [];
            var date = item.collected_date || '';
            var preview = item.summary || titleZh.substring(0, 80);
            var dateBadge = date ? '<span class="date-badge">' + date + '</span>' : '';
            var tagText = tags.length > 0 ? tags[0] : '';
            var imgTag = image ? '<img src="' + image + '" alt="" class="card-image" loading="lazy">' : '<div class="card-image-placeholder"></div>';
            
            return '<div class="card" onclick="showModal(' + index + ')">' +
                imgTag +
                '<div class="card-content">' +
                dateBadge +
                '<span class="card-source">' + source + '</span>' +
                '<h3 class="card-title">' + titleZh + '</h3>' +
                '<p class="card-preview">' + preview + '</p>' +
                '<div class="card-footer">' +
                '<span>⬆️ ' + score + ' · 💬 ' + comments + '</span>' +
                '<div><span class="tag">' + tagText + '</span></div>' +
                '</div></div></div>';
        }}
        
        function loadMoreCards() {{
            if (currentIndex >= totalItems) {{
                loadingIndicator.classList.remove('active');
                loadingIndicator.innerHTML = '<p>已加载全部 ' + totalItems + ' 条</p>';
                return;
            }}
            
            loadingIndicator.classList.add('active');
            
            setTimeout(function() {{
                var endIndex = Math.min(currentIndex + pageSize, totalItems);
                var newCardsHTML = '';
                
                for (var i = currentIndex; i < endIndex; i++) {{
                    newCardsHTML += createCardHTML(allData[i], i);
                }}
                
                cardContainer.insertAdjacentHTML('beforeend', newCardsHTML);
                currentIndex = endIndex;
                loadingIndicator.classList.remove('active');
                
                if (currentIndex >= totalItems) {{
                    loadingIndicator.innerHTML = '<p>已加载全部 ' + totalItems + ' 条</p>';
                }}
            }}, 300);
        }}
        
        var observer = new IntersectionObserver(function(entries) {{
            entries.forEach(function(entry) {{
                if (entry.isIntersecting && currentIndex < totalItems) {{
                    loadMoreCards();
                }}
            }});
        }}, {{ rootMargin: '200px' }});
        
        if (loadingIndicator) {{
            observer.observe(loadingIndicator);
        }}
        
        function showModal(index) {{
            var item = allData[index];
            var modalImg = document.getElementById('modalImage');
            modalImg.src = item.image || 'https://images.unsplash.com/photo-1614680376593-902f74cf0d41?w=600&h=400&fit=crop';
            document.getElementById('modalSource').textContent = item.subreddit || item.source || '';
            document.getElementById('modalTitle').textContent = item.title_zh || item.title || '';
            document.getElementById('modalOriginalTitle').textContent = '原文: ' + (item.title || '');
            document.getElementById('modalBody').textContent = item.content || item.summary || item.title_zh || '';
            document.getElementById('modalLink').href = item.url || '#';
            document.getElementById('modal').classList.add('active');
            document.body.style.overflow = 'hidden';
        }}
        
        function hideModal() {{
            document.getElementById('modal').classList.remove('active');
            document.body.style.overflow = '';
        }}
        
        function closeModal(e) {{
            if (e.target.classList.contains('modal-overlay')) {{
                hideModal();
            }}
        }}
        
        document.addEventListener('keydown', function(e) {{
            if (e.key === 'Escape') hideModal();
        }});
        </script>
    '''
    
    html += f'''
        <footer>
            <p>📅 更新于 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')} · 共 {len(items)} 条</p>
        </footer>
    </div>
</body>
</html>'''
    
    return html


def main():
    print("Generating daily report...")
    
    html = generate_html()
    with open('output/index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    items = load_all_data()
    print(f"Done! Generated index.html with {len(items)} items")


if __name__ == '__main__':
    main()
