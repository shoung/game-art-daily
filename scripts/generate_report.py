#!/usr/bin/env python3
"""
生成每日報告 HTML - 瀑布流布局
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
                    all_items.extend(items)
        except:
            pass
    
    all_items.sort(key=lambda x: x.get('score', 0), reverse=True)
    return all_items[:30]

def generate_html():
    """生成 HTML"""
    
    today = datetime.datetime.now()
    date_str = today.strftime('%Y年%m月%d日')
    
    items = load_latest_data()
    
    html = f'''<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>游戏美术外包 Daily Report</title>
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
        
        /* 瀑布流布局 */
        .waterfall {{
            column-count: 4;
            column-gap: 20px;
            padding: 20px 0 40px;
        }}
        
        @media (max-width: 1200px) {{
            .waterfall {{ column-count: 3; }}
        }}
        
        @media (max-width: 900px) {{
            .waterfall {{ column-count: 2; }}
        }}
        
        @media (max-width: 600px) {{
            .waterfall {{ column-count: 1; }}
        }}
        
        .card {{
            break-inside: avoid;
            background: var(--white);
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 2px 12px rgba(0,0,0,0.08);
            margin-bottom: 20px;
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
        
        .card-title-zh {{
            font-size: 13px;
            color: var(--gray);
            margin-bottom: 10px;
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
            <h1>游戏美术外包 Daily Report</h1>
            <p class="date">{date_str}</p>
            <p class="stats">📊 {len(items)} 条讨论</p>
        </header>
'''

    if items:
        html += '<div class="waterfall">'
        
        for item in items:
            image = item.get('image', 'https://images.unsplash.com/photo-1614680376593-902f74cf0d41?w=600&h=400&fit=crop')
            title = item.get('title', '')
            title_zh = item.get('title_zh', title)
            url = item.get('url', '#')
            source = item.get('subreddit', item.get('source', ''))
            score = item.get('score', 0)
            comments = item.get('num_comments', 0)
            tags = item.get('tags', [])
            
            html += f'''
        <div class="card">
            <img src="{image}" alt="" class="card-image">
            <div class="card-content">
                <span class="card-source">{source}</span>
                <h3 class="card-title">
                    <a href="{url}" target="_blank">{title}</a>
                </h3>
                <p class="card-title-zh">{title_zh}</p>
                <div class="card-footer">
                    <span>⬆️ {score} · 💬 {comments}</span>
                    <span class="tag">{tags[0] if tags else ''}</span>
                </div>
            </div>
        </div>'''
        
        html += '</div>'
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
