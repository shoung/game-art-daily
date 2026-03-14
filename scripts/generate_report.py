#!/usr/bin/env python3
"""
生成每日報告 HTML - 瀑布流 + 浮動卡片
"""

import os
import json
import datetime
from pathlib import Path

def load_latest_data():
    """載入最新數據"""
    data_dir = Path('data')
    all_items = []
    
    for json_file in sorted(data_dir.glob('*.json')):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                items = json.load(f)
                if isinstance(items, list):
                    for item in items:
                        # 確保有足夠的內容
                        if 'summary' not in item:
                            item['summary'] = item.get('title_zh', '')[:50]
                        if 'content' not in item:
                            item['content'] = item.get('title_zh', '')
                        all_items.append(item)
        except:
            pass
    
    all_items.sort(key=lambda x: x.get('score', 0), reverse=True)
    return all_items[:20]

def generate_html():
    """生成 HTML"""
    
    today = datetime.datetime.now()
    date_str = today.strftime('%Y年%m月%d日')
    
    items = load_latest_data()
    
    # 構建卡片數據
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
            margin-top: 20px;
            font-size: 14px;
            color: var(--gray);
        }}
        
        .week-tabs {{
            display: flex;
            gap: 10px;
            margin-top: 20px;
            flex-wrap: wrap;
        }}
        
        .week-tab {{
            padding: 8px 16px;
            background: var(--white);
            border: 2px solid var(--light-gray);
            border-radius: 20px;
            font-size: 13px;
            color: var(--gray);
            text-decoration: none;
            transition: all 0.3s ease;
        }}
        
        .week-tab:hover {{
            border-color: var(--primary);
            color: var(--primary);
        }}
        
        .week-tab.active {{
            background: var(--primary);
            border-color: var(--primary);
            color: white;
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
        
        .card-title {{
            font-size: 14px;
            font-weight: 500;
            margin-bottom: 6px;
        }}
        
        .card-title a {{
            color: var(--dark);
            text-decoration: none;
        }}
        
        .card-title a:hover {{ color: var(--primary); }}
        
        .card-preview {{
            font-size: 13px;
            color: var(--gray);
            margin-bottom: 10px;
            line-height: 1.5;
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
        
        .tag.source-tag {{
            background: var(--dark);
            color: white;
        }}
        
        /* Modal */
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
            max-height: 80vh;
            overflow-y: auto;
            position: relative;
            opacity: 0;
            transform: scale(0.8) translateY(20px);
            transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
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
            height: 250px;
            object-fit: cover;
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
        
        .modal-title-zh {{
            font-size: 16px;
            color: var(--gray);
            margin-bottom: 20px;
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
            <p class="stats">📊 {len(items)} 条讨论</p>
            
            <!-- Week Tabs -->
            <div class="week-tabs">
                <a href="index.html" class="week-tab active">本周</a>
                <a href="week10.html" class="week-tab">第10周</a>
                <a href="week09.html" class="week-tab">第9周</a>
            </div>
        </header>
'''

    # Add CSS for tabs and better animation
    # ... but first let me find where to add the CSS

    if items:
        html += '<div class="waterfall">'
        
        for i, item in enumerate(items):
            image = item.get('image', 'https://images.unsplash.com/photo-1614680376593-902f74cf0d41?w=600&h=400&fit=crop')
            title = item.get('title', '')
            title_zh = item.get('title_zh', title)
            url = item.get('url', '#')
            source = item.get('subreddit', item.get('source', ''))
            score = item.get('score', 0)
            comments = item.get('num_comments', 0)
            tags = item.get('tags', [])
            preview = item.get('summary', title_zh[:50])
            content = item.get('content', title_zh)
            
            html += f'''
        <div class="card" onclick="showModal({i})">
            <img src="{image}" alt="" class="card-image">
            <div class="card-content">
                <span class="card-source">{source}</span>
                <h3 class="card-title">{title_zh}</h3>
                <p class="card-preview">{preview}</p>
                <div class="card-footer">
                    <span>⬆️ {score} · 💬 {comments}</span>
                    <div>
                        <span class="tag">{tags[0] if tags else ''}</span>
                        <span class="tag source-tag">{item.get('source_name', source)}</span>
                    </div>
                </div>
            </div>
        </div>'''
        
        html += '</div>'
        
        # 添加 Modal HTML
        html += f'''
        <div class="modal-overlay" id="modal" onclick="closeModal(event)">
            <div class="modal" onclick="event.stopPropagation()">
                <span class="modal-close" onclick="hideModal()">✕</span>
                <img src="" alt="" class="modal-image" id="modalImage">
                <div class="modal-content">
                    <span class="modal-source" id="modalSource"></span>
                    <h2 class="modal-title" id="modalTitle"></h2>
                    <p class="modal-original-title" id="modalOriginalTitle"></p>
                    <div class="modal-body" id="modalBody"></div>
                    <p class="modal-original-title" id="modalOriginalTitle"></p>
                    <a href="#" target="_blank" class="modal-link" id="modalLink">查看原文 →</a>
                </div>
            </div>
        </div>
'''
        
        # 添加 JavaScript
        html += f'''
        <script>
        const cardsData = {cards_json};
        
        function showModal(index) {{
            const item = cardsData[index];
            document.getElementById('modalImage').src = item.image || 'https://images.unsplash.com/photo-1614680376593-902f74cf0d41?w=600&h=400&fit=crop';
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
    else:
        html += '<p style="padding:40px;text-align:center;color:#666;">暂无数据</p>'

    html += f'''
        <footer>
            <p>📅 更新于 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
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
    
    print(f"Done! Generated index.html with {len(load_latest_data())} items")

if __name__ == '__main__':
    main()
