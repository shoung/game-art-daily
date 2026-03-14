#!/usr/bin/env python3
"""
2ch (5ch) 新聞收集腳本
收集日本遊戲相關討論
"""

import os
import json
import datetime
import requests
from bs4 import BeautifulSoup

# 2ch/5ch 遊戲相關板
BOARDS = [
    ('game', 'ゲーム'),
    ('gamedev', 'ゲーム製作技術'),
    ('cg', 'コンピュータグラフィックス'),
    ('prog', 'プログラミング'),
    ('biz', 'ビジネス・業界'),
]

# 關鍵字
KEYWORDS = [
    'ゲーム', '美術', 'アート', '外包', '採用', '求人',
    'AI', 'Midjourney', 'Stable Diffusion', 'Blender',
    '会社', 'スタジオ', 'リリース', '新作', '人事',
    'Unity', 'Unreal', '3D', '2D', 'イラスト'
]

def collect_2ch():
    """收集 2ch/5ch 討論"""
    results = []
    
    # 使用 5ch 的 RSS  feeds
    base_url = 'https://www.5ch.net'
    
    for board_id, board_name in BOARDS:
        try:
            # 嘗試獲取熱門文章
            url = f'https://{board_id}.5ch.net/subback.html'
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.encoding = 'shift_jis'
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 找到熱門主題（通常在列表中）
            threads = soup.find_all('a', href=True)
            
            for thread in threads[:50]:  # 檢查前50個
                title = thread.get_text(strip=True)
                href = thread.get('href', '')
                
                # 檢查是否包含關鍵字
                if any(kw in title for kw in KEYWORDS):
                    # 獲取主題鏈接
                    if not href.startswith('http'):
                        href = f'https://{board_id}.5ch.net{href}'
                    
                    results.append({
                        'source': '5ch',
                        'board': board_id,
                        'board_name': board_name,
                        'title': title,
                        'url': href,
                        'collected_at': datetime.datetime.now().isoformat()
                    })
                    
        except Exception as e:
            print(f"Error collecting from {board_id}: {e}")
    
    # 如果無法獲取，嘗試備用來源
    if not results:
        results = collect_game_news_japan_fallback()
    
    return results

def collect_game_news_japan_fallback():
    """備用：日本遊戲新聞收集"""
    results = []
    
    # 日本遊戲新聞網站
    news_sites = [
        ('https://gamebiz.jp/rss.xml', 'gamebiz'),
        ('https://www.4gamer.net/rss.xml', '4gamer'),
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    for url, name in news_sites:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.encoding = 'utf-8'
            
            soup = BeautifulSoup(response.text, 'xml')
            items = soup.find_all('item')[:10]
            
            for item in items:
                title = item.find('title')
                link = item.find('link')
                pub_date = item.find('pubDate')
                
                if title and link:
                    results.append({
                        'source': name,
                        'title': title.get_text(strip=True),
                        'url': link.get_text(strip=True),
                        'published': pub_date.get_text(strip=True) if pub_date else None,
                        'collected_at': datetime.datetime.now().isoformat()
                    })
                    
        except Exception as e:
            print(f"Error fetching {name}: {e}")
    
    return results

def save_results(results):
    """儲存結果到 JSON"""
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    filepath = f'data/2ch_{today}.json'
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"Saved {len(results)} 2ch posts to {filepath}")
    return filepath

if __name__ == '__main__':
    print("Starting 2ch collection...")
    results = collect_2ch()
    save_results(results)
    print(f"Collected {len(results)} posts from 2ch")
