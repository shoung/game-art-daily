#!/usr/bin/env python3
"""
生成每週報告 HTML - 首頁直接顯示消息
"""

import os
import json
import datetime
from pathlib import Path
from collections import defaultdict

def load_week_data(week, year):
    """載入指定週的數據"""
    data_dir = Path('data')
    all_reddit = []
    all_japan = []
    
    # 掃描該週的所有數據
    for json_file in data_dir.glob('reddit_*.json'):
        try:
            date_str = json_file.stem.replace('reddit_', '')
            file_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
            week_num = file_date.isocalendar()[1]
            if week_num == week and file_date.year == year:
                with open(json_file, 'r', encoding='utf-8') as f:
                    all_reddit.extend(json.load(f))
        except:
            pass
    
    for json_file in data_dir.glob('2ch_*.json'):
        try:
            date_str = json_file.stem.replace('2ch_', '')
            file_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
            week_num = file_date.isocalendar()[1]
            if week_num == week and file_date.year == year:
                with open(json_file, 'r', encoding='utf-8') as f:
                    all_japan.extend(json.load(f))
        except:
            pass
    
    return {'reddit': all_reddit, 'japan': all_japan}

def get_available_weeks():
    """獲取所有可用的週"""
    data_dir = Path('data')
    weeks = set()
    
    for json_file in data_dir.glob('*.json'):
        try:
            parts = json_file.stem.split('_')
            if len(parts) >= 2:
                date_str = parts[1]
                file_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
                week_num = file_date.isocalendar()[1]
                weeks.add((file_date.year, week_num))
        except:
            pass
    
    return sorted(weeks, reverse=True)

def generate_html():
    """生成 HTML"""
    
    # 獲取可用週
    available_weeks = get_available_weeks()
    current_year = datetime.datetime.now().year
    current_week = datetime.datetime.now().isocalendar()[1]
    
    today = datetime.datetime.now()
    date_str = today.strftime('%Y年%m月%d日')
    
    # 默認加載當前週
    default_week = available_weeks[0] if available_weeks else (current_year, current_week)
    year, week = default_week
    data = load_week_data(week, year)
    all_items = data['reddit'] + data['japan']
    all_items.sort(key=lambda x: x.get('score', 0), reverse=True)
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>游戏美术外包周报 - 第{week}周</title>
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.12.5/dist/gsap.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.12.5/dist/ScrollTrigger.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --primary: #e20001;
            --dark: #1a1a1a;
            --gray: #666666;
            --light-gray: #f5f5f5;
            --white: #ffffff;
            --shadow: 0 4px 20px rgba(0,0,0,0.08);
            --shadow-hover: 0 8px 30px rgba(0,0,0,0.15);
        }}
        
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: 'Noto Sans SC', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--white);
            color: var(--dark);
            line-height: 1.6;
        }}
        
        .container {{ max-width: 1400px; margin: 0 auto; padding: 0 24px; }}
        
        header {{
            padding: 40px 0 30px;
            border-bottom: 1px solid var(--light-gray);
            margin-bottom: 30px;
        }}
        
        .logo {{
            font-size: 14px;
            font-weight: 500;
            color: var(--gray);
            letter-spacing: 2px;
            text-transform: uppercase;
        }}
        
        h1 {{
            font-size: clamp(28px, 4vw, 48px);
            font-weight: 700;
            color: var(--dark);
            margin: 12px 0;
        }}
        
        h1 span {{ color: var(--primary); }}
        
        .subtitle {{
            font-size: 16px;
            color: var(--gray);
            font-weight: 300;
        }}
        
        .week-tabs {{
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            margin-top: 20px;
        }}
        
        .week-tab {{
            padding: 8px 20px;
            background: var(--white);
            border: 2px solid var(--light-gray);
            border-radius: 25px;
            font-size: 13px;
            font-weight: 500;
            color: var(--gray);
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
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
        
        .bento-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            padding: 30px 0;
        }}
        
        .bento-item {{
            background: var(--white);
            border-radius: 16px;
            overflow: hidden;
            box-shadow: var(--shadow);
            transition: all 0.3s ease;
        }}
        
        .bento-item:hover {{
            transform: translateY(-4px);
            box-shadow: var(--shadow-hover);
        }}
        
        .bento-item.large {{ 
            grid-column: span 2; 
        }}
        
        @media (max-width: 768px) {{
            .bento-item.large {{ grid-column: span 1; }}
        }}
        
        .bento-image {{
            width: 100%;
            height: 180px;
            object-fit: cover;
            background: var(--light-gray);
        }}
        
        .bento-content {{
            padding: 20px;
        }}
        
        .bento-source {{
            display: inline-block;
            background: var(--primary);
            color: white;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 500;
            margin-bottom: 10px;
        }}
        
        .bento-title {{
            font-size: 15px;
            font-weight: 500;
            color: var(--dark);
            margin-bottom: 8px;
            line-height: 1.4;
        }}
        
        .bento-title a {{
            color: inherit;
            text-decoration: none;
        }}
        
        .bento-title a:hover {{ color: var(--primary); }}
        
        .bento-title-zh {{
            font-size: 13px;
            color: var(--gray);
            margin-bottom: 12px;
        }}
        
        .bento-footer {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-top: 12px;
            border-top: 1px solid var(--light-gray);
        }}
        
        .bento-stats {{
            font-size: 12px;
            color: var(--gray);
        }}
        
        .tag {{
            display: inline-block;
            background: var(--light-gray);
            padding: 3px 8px;
            border-radius: 3px;
            font-size: 10px;
            color: var(--gray);
        }}
        
        footer {{
            padding: 40px 0;
            border-top: 1px solid var(--light-gray);
            margin-top: 40px;
            text-align: center;
            color: var(--gray);
            font-size: 13px;
        }}
        
        .no-data {{
            text-align: center;
            padding: 60px 20px;
            color: var(--gray);
            font-size: 16px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="logo">Game Art Outsourcing</div>
            <h1>游戏美术外包<span>周报</span></h1>
            <p class="subtitle">日本与欧美论坛讨论精选</p>
            
            <div class="week-tabs">
'''

    # 添加週标签
    for y, w in available_weeks:
        is_active = (y == year and w == week)
        html += f'<a href="week{w}.html" class="week-tab {"active" if is_active else ""}">第{w}周 {y}</a>'

    html += f'''
            </div>
        </header>
'''

    if all_items:
        html += f'''
        <div class="bento-grid">
'''
        
        for i, item in enumerate(all_items[:30]):
            is_large = i == 0 and len(all_items) >= 3
            image = item.get('image', 'https://images.unsplash.com/photo-1614680376593-902f74cf0d41?w=600&h=400&fit=crop')
            title = item.get('title', '')
            title_zh = item.get('title_zh', title)
            url = item.get('url', '#')
            source = item.get('subreddit', item.get('source', ''))
            score = item.get('score', 0)
            comments = item.get('num_comments', 0)
            tags = item.get('tags', [])
            
            html += f'''
            <div class="bento-item {'large' if is_large else ''}">
                <img src="{image}" alt="" class="bento-image" loading="lazy">
                <div class="bento-content">
                    <span class="bento-source">{source}</span>
                    <h3 class="bento-title">
                        <a href="{url}" target="_blank">{title}</a>
                    </h3>
                    <p class="bento-title-zh">{title_zh}</p>
                    <div class="bento-footer">
                        <span class="bento-stats">⬆️ {score} · 💬 {comments}</span>
                        <span class="tag">{tags[0] if tags else ''}</span>
                    </div>
                </div>
            </div>
'''
        
        html += '''
        </div>
'''
    else:
        html += '''
        <div class="no-data">暂无数据</div>
'''

    html += f'''
        <footer>
            <p>📅 更新于 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        </footer>
    </div>
    
    <script>
        // GSAP Animations
        gsap.registerPlugin(ScrollTrigger);
        
        gsap.from('header', {{
            duration: 0.6,
            y: -20,
            opacity: 0,
            ease: 'power2.out'
        }});
        
        gsap.utils.toArray('.bento-item').forEach((item, i) => {{
            gsap.from(item, {{
                scrollTrigger: {{
                    trigger: item,
                    start: 'top 95%',
                }},
                duration: 0.4,
                y: 20,
                opacity: 0,
                delay: i * 0.03,
                ease: 'power2.out'
            }});
        }});
    </script>
</body>
</html>'''
    
    return html

def main():
    print("Generating weekly report...")
    
    # 生成主頁
    html = generate_html()
    with open('output/index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    # 為每週生成獨立頁面
    available_weeks = get_available_weeks()
    for year, week in available_weeks:
        data = load_week_data(week, year)
        all_items = data['reddit'] + data['japan']
        
        # 为这一周生成HTML
        html = generate_html()
        with open(f'output/week{week}.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"Generated week {week}")
    
    print(f"Done! Total weeks: {len(available_weeks)}")

if __name__ == '__main__':
    main()
