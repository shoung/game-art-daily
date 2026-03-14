#!/usr/bin/env python3
"""
生成每日報告 HTML
"""

import os
import json
import datetime
from pathlib import Path

def load_data():
    """載入所有收集的數據"""
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    data_dir = Path('data')
    
    all_data = {
        'reddit': [],
        '2ch': [],
        'date': today
    }
    
    # 讀取 Reddit 數據
    reddit_file = data_dir / f'reddit_{today}.json'
    if reddit_file.exists():
        with open(reddit_file, 'r', encoding='utf-8') as f:
            all_data['reddit'] = json.load(f)
    
    # 讀取 2ch 數據
    2ch_file = data_dir / f'2ch_{today}.json'
    if 2ch_file.exists():
        with open(2ch_file, 'r', encoding='utf-8') as f:
            all_data['2ch'] = json.load(f)
    
    return all_data

def generate_html(data):
    """生成 HTML 報告"""
    today = datetime.datetime.now()
    date_str = today.strftime('%Y年%m月%d日')
    weekday = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日'][today.weekday()]
    
    html = f'''<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>遊戲美術外包 Daily Report - {date_str}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Noto Sans TC", sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            padding: 20px;
            color: #e4e4e7;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        header {{
            text-align: center;
            padding: 40px 0;
            border-bottom: 2px solid #4f46e5;
            margin-bottom: 40px;
        }}
        h1 {{
            font-size: 2.5rem;
            color: #fff;
            margin-bottom: 10px;
        }}
        .date {{
            color: #9ca3af;
            font-size: 1.1rem;
        }}
        .stats {{
            display: flex;
            justify-content: center;
            gap: 40px;
            margin: 30px 0;
        }}
        .stat {{
            text-align: center;
            background: rgba(255,255,255,0.05);
            padding: 20px 30px;
            border-radius: 12px;
        }}
        .stat-num {{
            font-size: 2rem;
            font-weight: bold;
            color: #4f46e5;
        }}
        .stat-label {{
            color: #9ca3af;
            font-size: 0.9rem;
        }}
        .section {{
            background: rgba(255,255,255,0.03);
            border-radius: 16px;
            padding: 30px;
            margin-bottom: 30px;
        }}
        .section h2 {{
            color: #4f46e5;
            font-size: 1.5rem;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }}
        .news-item {{
            background: rgba(255,255,255,0.05);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 15px;
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        .news-item:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.3);
        }}
        .news-title {{
            font-size: 1.1rem;
            color: #fff;
            margin-bottom: 10px;
        }}
        .news-title a {{
            color: inherit;
            text-decoration: none;
        }}
        .news-title a:hover {{
            color: #4f46e5;
        }}
        .news-meta {{
            display: flex;
            gap: 15px;
            font-size: 0.85rem;
            color: #9ca3af;
        }}
        .tag {{
            display: inline-block;
            background: rgba(79, 70, 229, 0.2);
            color: #a5b4fc;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 0.75rem;
        }}
        .category {{
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            margin-bottom: 20px;
        }}
        .category-tag {{
            padding: 8px 16px;
            border-radius: 20px;
            background: rgba(255,255,255,0.1);
            cursor: pointer;
            transition: background 0.2s;
        }}
        .category-tag:hover, .category-tag.active {{
            background: #4f46e5;
        }}
        .no-data {{
            text-align: center;
            padding: 40px;
            color: #9ca3af;
        }}
        footer {{
            text-align: center;
            padding: 40px 0;
            color: #6b7280;
            font-size: 0.9rem;
        }}
        @media (max-width: 768px) {{
            .stats {{ flex-direction: column; gap: 20px; }}
            h1 {{ font-size: 1.8rem; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🎮 遊戲美術外包 Daily Report</h1>
            <p class="date">{date_str} {weekday}</p>
            <div class="stats">
                <div class="stat">
                    <div class="stat-num">{len(data['reddit'])}</div>
                    <div class="stat-label">Reddit 熱門</div>
                </div>
                <div class="stat">
                    <div class="stat-num">{len(data['2ch'])}</div>
                    <div class="stat-label">日本資訊</div>
                </div>
            </div>
        </header>
'''

    # Reddit 熱門討論
    html += '<section class="section"><h2>🔥 Reddit 熱門討論</h2>'
    if data['reddit']:
        for item in data['reddit'][:15]:
            score = item.get('score', 0)
            comments = item.get('num_comments', 0)
            subreddit = item.get('subreddit', '')
            html += f'''
            <div class="news-item">
                <div class="news-title">
                    <a href="{item['url']}" target="_blank">{item['title']}</a>
                </div>
                <div class="news-meta">
                    <span class="tag">r/{subreddit}</span>
                    <span>⬆️ {score}</span>
                    <span>💬 {comments}</span>
                </div>
            </div>'''
    else:
        html += '<div class="no-data">今日無熱門討論</div>'
    html += '</section>'

    # 2ch/日本資訊
    html += '<section class="section"><h2>📺 日本遊戲資訊</h2>'
    if data['2ch']:
        for item in data['2ch'][:15]:
            board = item.get('board_name', item.get('source', ''))
            html += f'''
            <div class="news-item">
                <div class="news-title">
                    <a href="{item['url']}" target="_blank">{item['title']}</a>
                </div>
                <div class="news-meta">
                    <span class="tag">{board}</span>
                </div>
            </div>'''
    else:
        html += '<div class="no-data">今日無日本資訊</div>'
    html += '</section>'

    html += f'''
        <footer>
            <p>報告自動生成於 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>由 GitHub Actions 驅動</p>
        </footer>
    </div>
</body>
</html>'''
    
    return html

def main():
    print("Generating daily report...")
    data = load_data()
    html = generate_html(data)
    
    # 確保輸出目錄存在
    os.makedirs('output', exist_ok=True)
    
    # 寫入 index.html
    with open('output/index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    # 寫入當天日期的檔案
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    with open(f'output/{today}.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"Report generated: output/index.html")
    print(f"Reddit posts: {len(data['reddit'])}")
    print(f"2ch posts: {len(data['2ch'])}")

if __name__ == '__main__':
    main()
