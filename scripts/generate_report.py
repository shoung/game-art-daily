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
    
    # 找到該週對應的日期
    jan1 = datetime.date(year, 1, 1)
    # 找到第一週的開始
    first_week = jan1.isocalendar()[1]
    week_start = jan1 + datetime.timedelta(weeks=week - first_week)
    
    all_data = {
        'reddit': [],
        'japan': [],
        'week': week,
        'year': year,
        'date_range': ''
    }
    
    # 掃描該週的所有數據
    for json_file in data_dir.glob('reddit_*.json'):
        try:
            date_str = json_file.stem.replace('reddit_', '')
            file_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
            
            # 檢查是否在該週
            week_num = file_date.isocalendar()[1]
            if week_num == week and file_date.year == year:
                with open(json_file, 'r', encoding='utf-8') as f:
                    all_data['reddit'].extend(json.load(f))
        except:
            pass
    
    for json_file in data_dir.glob('2ch_*.json'):
        try:
            date_str = json_file.stem.replace('2ch_', '')
            file_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
            
            week_num = file_date.isocalendar()[1]
            if week_num == week and file_date.year == year:
                with open(json_file, 'r', encoding='utf-8') as f:
                    all_data['japan'].extend(json.load(f))
        except:
            pass
    
    return all_data

def get_available_weeks():
    """獲取所有可用的週"""
    data_dir = Path('data')
    weeks = set()
    
    for json_file in data_dir.glob('*.json'):
        try:
            date_str = json_file.stem.split('_')[1]
            file_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
            week_num = file_date.isocalendar()[1]
            weeks.add((file_date.year, week_num))
        except:
            pass
    
    return sorted(weeks, reverse=True)

def group_by_tag(data):
    """按標籤分組"""
    tagged_items = defaultdict(list)
    
    for item in data['reddit'] + data['japan']:
        tags = item.get('tags', ['其他'])
        for tag in tags:
            tagged_items[tag].append(item)
    
    return dict(tagged_items)

def generate_html(weeks_data):
    """生成 HTML - 標籤頁切換"""
    
    # 獲取可用週
    available_weeks = get_available_weeks()
    current_week = datetime.datetime.now().isocalendar()[1]
    current_year = datetime.datetime.now().year
    
    today = datetime.datetime.now()
    date_str = today.strftime('%Y年%m月%d日')
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>游戏美术外包周报</title>
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
        
        /* Header */
        header {{
            padding: 60px 0 40px;
            border-bottom: 1px solid var(--light-gray);
            margin-bottom: 40px;
        }}
        
        .header-top {{
            display: flex;
            justify-content: space-between;
            align-items: center;
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
            font-size: clamp(32px, 5vw, 56px);
            font-weight: 700;
            color: var(--dark);
            margin-bottom: 12px;
        }}
        
        h1 span {{ color: var(--primary); }}
        
        .subtitle {{
            font-size: 18px;
            color: var(--gray);
            font-weight: 300;
        }}
        
        /* Week Tabs */
        .week-tabs {{
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
            margin-top: 30px;
        }}
        
        .week-tab {{
            padding: 10px 24px;
            background: var(--white);
            border: 2px solid var(--light-gray);
            border-radius: 30px;
            font-size: 14px;
            font-weight: 500;
            color: var(--gray);
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
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
        
        /* Bento Grid */
        .bento-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: 24px;
            padding: 40px 0;
        }}
        
        .bento-item {{
            background: var(--white);
            border-radius: 20px;
            overflow: hidden;
            box-shadow: var(--shadow);
            transition: all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
            opacity: 0;
            transform: translateY(30px);
        }}
        
        .bento-item:hover {{
            transform: translateY(-8px);
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
            height: 200px;
            object-fit: cover;
            background: var(--light-gray);
        }}
        
        .bento-content {{
            padding: 24px;
        }}
        
        .bento-meta {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }}
        
        .bento-source {{
            background: var(--primary);
            color: white;
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 500;
        }}
        
        .bento-title {{
            font-size: 16px;
            font-weight: 500;
            color: var(--dark);
            margin-bottom: 8px;
            line-height: 1.5;
        }}
        
        .bento-title a {{
            color: inherit;
            text-decoration: none;
        }}
        
        .bento-title a:hover {{ color: var(--primary); }}
        
        .bento-title-zh {{
            font-size: 14px;
            color: var(--gray);
            margin-bottom: 16px;
        }}
        
        .bento-footer {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-top: 16px;
            border-top: 1px solid var(--light-gray);
        }}
        
        .bento-stats {{
            display: flex;
            gap: 16px;
            font-size: 13px;
            color: var(--gray);
        }}
        
        .bento-stats span {{ display: flex; align-items: center; gap: 4px; }}
        
        .bento-tags {{
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }}
        
        .tag {{
            background: var(--light-gray);
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 11px;
            color: var(--gray);
        }}
        
        /* Footer */
        footer {{
            padding: 60px 0;
            border-top: 1px solid var(--light-gray);
            margin-top: 60px;
            text-align: center;
            color: var(--gray);
            font-size: 14px;
        }}
        
        .no-data {{
            text-align: center;
            padding: 100px 20px;
            color: var(--gray);
            font-size: 18px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="header-top">
                <div>
                    <div class="logo">Game Art Outsourcing</div>
                    <h1>游戏美术外包<span>周报</span></h1>
                    <p class="subtitle">日本与欧美论坛讨论精选</p>
                </div>
            </div>
            
            <!-- Week Tabs -->
            <div class="week-tabs">
'''

    # 添加週标签
    for year, week in available_weeks:
        is_active = (year == current_year and week == current_week)
        html += f'<a href="week{week}.html" class="week-tab {"active" if is_active else ""}">第{week}周 {year}</a>'

    html += '''
            </div>
        </header>
'''

    # 生成当前週的内容
    current_year, current_week = available_weeks[0] if available_weeks else (current_year, current_week)
    data = load_week_data(current_week, current_year)
    
    all_items = data['reddit'] + data['japan']
    tagged_data = group_by_tag(data)
    
    if all_items:
        html += f'''
        <div class="bento-grid">
'''
        
        # 合并所有标签的内容，按热度排序
        all_items.sort(key=lambda x: x.get('score', 0), reverse=True)
        
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
                    <div class="bento-meta">
                        <span class="bento-source">{source}</span>
                    </div>
                    <h3 class="bento-title">
                        <a href="{url}" target="_blank">{title}</a>
                    </h3>
                    <p class="bento-title-zh">{title_zh}</p>
                    <div class="bento-footer">
                        <div class="bento-stats">
                            <span>⬆️ {score}</span>
                            <span>💬 {comments}</span>
                        </div>
                        <div class="bento-tags">
                            {''.join(f'<span class="tag">{t}</span>' for t in tags[:2])}
                        </div>
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
            <p>📅 报告生成于 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        </footer>
    </div>
    
    <script>
        // GSAP Animations
        gsap.registerPlugin(ScrollTrigger);
        
        gsap.from('header', {{
            duration: 1,
            y: -30,
            opacity: 0,
            ease: 'power3.out'
        }});
        
        gsap.utils.toArray('.bento-item').forEach((item, i) => {{
            gsap.to(item, {{
                scrollTrigger: {{
                    trigger: item,
                    start: 'top 90%',
                }},
                duration: 0.5,
                y: 0,
                opacity: 1,
                delay: i * 0.05,
                ease: 'power2.out'
            }});
        }});
        
        document.querySelectorAll('.bento-item').forEach(item => {{
            item.addEventListener('mouseenter', () => {{
                gsap.to(item, {{ scale: 1.02, duration: 0.3 }});
            }});
            item.addEventListener('mouseleave', () => {{
                gsap.to(item, {{ scale: 1, duration: 0.3 }});
            }});
        }});
    </script>
</body>
</html>'''
    
    return html

def main():
    print("Generating weekly report...")
    
    # 生成主頁
    html = generate_html({})
    with open('output/index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    # 為每週生成獨立頁面
    available_weeks = get_available_weeks()
    for year, week in available_weeks:
        data = load_week_data(week, year)
        html = generate_html({f'week{week}': data})
        with open(f'output/week{week}.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"Generated week {week} {year}")
    
    print(f"Report generated: output/index.html")

if __name__ == '__main__':
    main()
