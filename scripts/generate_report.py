#!/usr/bin/env python3
"""
生成每日報告 HTML - 便當盒設計 + GSAP動效
"""

import os
import json
import datetime
from pathlib import Path
from collections import defaultdict

def load_data():
    """載入所有收集的數據"""
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    week = datetime.datetime.now().isocalendar()[1]
    data_dir = Path('data')
    
    all_data = {
        'reddit': [],
        'japan': [],
        'date': today,
        'week': week,
        'year': datetime.datetime.now().year
    }
    
    # 讀取 Reddit 數據
    reddit_file = data_dir / f'reddit_{today}.json'
    if reddit_file.exists():
        with open(reddit_file, 'r', encoding='utf-8') as f:
            all_data['reddit'] = json.load(f)
    
    # 讀取日本論壇數據
    twoch_file = data_dir / f'2ch_{today}.json'
    if twoch_file.exists():
        with open(twoch_file, 'r', encoding='utf-8') as f:
            all_data['japan'] = json.load(f)
    
    return all_data

def group_by_tag(data):
    """按標籤分組"""
    tagged_items = defaultdict(list)
    
    for item in data['reddit'] + data['japan']:
        tags = item.get('tags', ['其他'])
        for tag in tags:
            tagged_items[tag].append(item)
    
    return dict(tagged_items)

def generate_html(data):
    """生成 HTML 報告 - 便當盒設計"""
    today = datetime.datetime.now()
    date_str = today.strftime('%Y年%m月%d日')
    week = today.isocalendar()[1]
    weekday = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'][today.weekday()]
    
    # 按標籤分組
    tagged_data = group_by_tag(data)
    
    # 計算總數
    total_reddit = len(data['reddit'])
    total_japan = len(data['japan'])
    total = total_reddit + total_japan
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>游戏美术外包周报 {week}期</title>
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
            overflow-x: hidden;
        }}
        
        .container {{ max-width: 1400px; margin: 0 auto; padding: 0 24px; }}
        
        /* Header */
        header {{
            padding: 60px 0 40px;
            border-bottom: 1px solid var(--light-gray);
            margin-bottom: 60px;
        }}
        
        .header-top {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 30px;
        }}
        
        .logo {{
            font-size: 14px;
            font-weight: 500;
            color: var(--gray);
            letter-spacing: 2px;
            text-transform: uppercase;
        }}
        
        .week-badge {{
            background: var(--primary);
            color: white;
            padding: 8px 20px;
            font-size: 14px;
            font-weight: 500;
            border-radius: 30px;
        }}
        
        h1 {{
            font-size: clamp(32px, 5vw, 56px);
            font-weight: 700;
            color: var(--dark);
            margin-bottom: 16px;
            letter-spacing: -1px;
        }}
        
        h1 span {{ color: var(--primary); }}
        
        .subtitle {{
            font-size: 18px;
            color: var(--gray);
            font-weight: 300;
        }}
        
        .date-info {{
            display: flex;
            gap: 20px;
            margin-top: 30px;
            font-size: 14px;
            color: var(--gray);
        }}
        
        .date-info span {{ display: flex; align-items: center; gap: 8px; }}
        
        /* Stats */
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 80px;
        }}
        
        .stat-card {{
            background: var(--white);
            border: 1px solid var(--light-gray);
            padding: 30px;
            border-radius: 16px;
            transition: all 0.3s ease;
        }}
        
        .stat-card:hover {{
            border-color: var(--primary);
            transform: translateY(-4px);
            box-shadow: var(--shadow);
        }}
        
        .stat-number {{
            font-size: 42px;
            font-weight: 700;
            color: var(--dark);
            margin-bottom: 8px;
        }}
        
        .stat-label {{
            font-size: 14px;
            color: var(--gray);
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        /* Tag Sections */
        .tag-section {{
            margin-bottom: 80px;
        }}
        
        .tag-header {{
            display: flex;
            align-items: center;
            gap: 16px;
            margin-bottom: 30px;
        }}
        
        .tag-title {{
            font-size: 24px;
            font-weight: 600;
            color: var(--dark);
        }}
        
        .tag-count {{
            background: var(--light-gray);
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 13px;
            color: var(--gray);
        }}
        
        /* Bento Grid */
        .bento-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 24px;
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
        
        .bento-item.large {{ grid-column: span 2; }}
        
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
            font-size: 12px;
            color: var(--gray);
        }}
        
        .bento-source {{
            background: var(--primary);
            color: white;
            padding: 4px 10px;
            border-radius: 4px;
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
        
        /* Responsive */
        @media (max-width: 768px) {{
            .bento-item.large {{ grid-column: span 1; }}
            .header-top {{ flex-direction: column; gap: 20px; }}
            h1 {{ font-size: 32px; }}
            .bento-grid {{ grid-template-columns: 1fr; }}
        }}
        
        /* Loading Animation */
        .loading {{
            text-align: center;
            padding: 60px;
            color: var(--gray);
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="header-top">
                <div>
                    <div class="logo">Game Art Outsourcing</div>
                    <h1>周报 <span>{week}</span></h1>
                    <p class="subtitle">游戏美术外包行业论坛讨论精选</p>
                </div>
                <div class="week-badge">第 {week} 期</div>
            </div>
            <div class="date-info">
                <span>📅 {date_str} {weekday}</span>
                <span>📊 {total} 条讨论</span>
            </div>
        </header>
        
        <!-- 统计卡片 -->
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{total_reddit}</div>
                <div class="stat-label">Reddit 讨论</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{total_japan}</div>
                <div class="stat-label">日本论坛</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(tagged_data)}</div>
                <div class="stat-label">话题分类</div>
            </div>
        </div>
'''

    # 生成每個標籤區塊
    tag_order = ['招聘/裁员', '外包/自由职业', 'AI美术', '工具/技术', '工作室动态', '作品展示', '综合讨论', '其他']
    
    for tag in tag_order:
        if tag in tagged_data and tagged_data[tag]:
            items = tagged_data[tag][:12]  # 每個標籤最多12條
            
            html += f'''
        <section class="tag-section">
            <div class="tag-header">
                <h2 class="tag-title">🏷️ {tag}</h2>
                <span class="tag-count">{len(items)} 条</span>
            </div>
            <div class="bento-grid">
'''
            
            for i, item in enumerate(items):
                is_large = i == 0 and len(items) >= 3
                image = item.get('image', 'https://images.unsplash.com/photo-1614680376593-902f74cf0d41?w=400')
                title = item.get('title', '')
                title_zh = item.get('title_zh', title)
                url = item.get('url', '#')
                source = item.get('subreddit', item.get('source', ''))
                score = item.get('score', 0)
                comments = item.get('num_comments', 0)
                tags = item.get('tags', [])
                
                html += f'''
                <div class="bento-item {'large' if is_large else ''}" data-tag="{tag}">
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
        </section>
'''

    html += f'''
        <footer>
            <p>📅 报告自动生成于 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
            <p>🔄 每周一自动更新 | 由 GitHub Actions 驱动</p>
        </footer>
    </div>
    
    <script>
        // GSAP Animations
        gsap.registerPlugin(ScrollTrigger);
        
        // Header animation
        gsap.from('header', {{
            duration: 1,
            y: -50,
            opacity: 0,
            ease: 'power3.out'
        }});
        
        // Stats animation
        gsap.from('.stat-card', {{
            duration: 0.8,
            y: 50,
            opacity: 0,
            stagger: 0.15,
            delay: 0.3,
            ease: 'power3.out'
        }});
        
        // Bento items animation
        gsap.utils.toArray('.bento-item').forEach((item, i) => {{
            gsap.to(item, {{
                scrollTrigger: {{
                    trigger: item,
                    start: 'top 85%',
                    toggleActions: 'play none none reverse'
                }},
                duration: 0.6,
                y: 0,
                opacity: 1,
                delay: i * 0.05,
                ease: 'power2.out'
            }});
        }});
        
        // Hover effects
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
    data = load_data()
    html = generate_html(data)
    
    # 確保輸出目錄存在
    os.makedirs('output', exist_ok=True)
    
    # 寫入 index.html
    with open('output/index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    # 寫入當天日期的檔案
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    week = datetime.datetime.now().isocalendar()[1]
    with open(f'output/week{week}.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"Weekly report generated: output/index.html")
    print(f"Reddit posts: {len(data['reddit'])}")
    print(f"Japan posts: {len(data['japan'])}")

if __name__ == '__main__':
    main()
