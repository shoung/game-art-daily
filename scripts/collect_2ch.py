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

def collect_game_news_japan():
    """收集日本遊戲新聞"""
    results = []
    
    # 日本遊戲新聞網站 (更可靠的來源)
    news_sites = [
        # 4gamer.net
        ('https://www.4gamer.net/atom.xml', '4gamer.net'),
        # gamebiz.jp
        ('https://gamebiz.jp/feed', 'gamebiz.jp'),
        # AUTOMATON
        ('https://automaton-media.com/feed/', 'AUTOMATON'),
        # Game*Spark
        ('https://www.gamespark.jp/rss', 'Game*Spark'),
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    for url, name in news_sites:
        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.encoding = 'utf-8'
            
            soup = BeautifulSoup(response.text, 'xml')
            items = soup.find_all('item')[:10]
            
            for item in items:
                title = item.find('title')
                link = item.find('link')
                pub_date = item.find('pubDate')
                description = item.find('description')
                
                if title and link:
                    results.append({
                        'source': name,
                        'title': title.get_text(strip=True),
                        'url': link.get_text(strip=True) if link else url,
                        'published': pub_date.get_text(strip=True) if pub_date else None,
                        'description': description.get_text(strip=True)[:200] if description else None,
                        'collected_at': datetime.datetime.now().isoformat()
                    })
                    
        except Exception as e:
            print(f"Error fetching {name}: {e}")
            # 嘗試 HTML 解析
            try:
                response = requests.get(url.replace('/atom.xml', '').replace('/feed', ''), headers=headers, timeout=15)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 找標題和連結
                for link in soup.find_all('a', href=True)[:20]:
                    title = link.get_text(strip=True)
                    href = link.get('href', '')
                    if title and len(title) > 10 and ('ゲーム' in title or 'ゲーム' in href or 'Game' in title):
                        results.append({
                            'source': name,
                            'title': title,
                            'url': href if href.startswith('http') else url,
                            'collected_at': datetime.datetime.now().isoformat()
                        })
            except Exception as e2:
                print(f"Fallback also failed for {name}: {e2}")
    
    return results

def save_results(results):
    """儲存結果到 JSON"""
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    filepath = f'data/2ch_{today}.json'
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"Saved {len(results)} posts to {filepath}")
    return filepath

if __name__ == '__main__':
    print("Starting Japan game news collection...")
    results = collect_game_news_japan()
    save_results(results)
    print(f"Collected {len(results)} posts from Japan")
