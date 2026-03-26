#!/usr/bin/env python3
"""
日本論壇討論收集腳本
收集日本遊戲相關的小道消息和論壇討論
"""

import os
import json
import datetime
import requests
import random
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from utils_llm import translate_and_summarize

# Load environment variables
load_dotenv()

def get_image_for_keyword(title_zh):
    """根據中文譯文關鍵詞返回相關圖片URL"""
    image_keywords = {
        '游戏': 'https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=600&h=400&fit=crop',
        '美术': 'https://images.unsplash.com/photo-1513364776144-60967b0f800f?w=600&h=400&fit=crop',
        'AI': 'https://images.unsplash.com/photo-1677442136019-21780ecad995?w=600&h=400&fit=crop',
        '3D': 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=600&h=400&fit=crop',
        '招聘': 'https://images.unsplash.com/photo-1521737604893-d14cc237f11d?w=600&h=400&fit=crop',
        '外包': 'https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=600&h=400&fit=crop',
        'Unity': 'https://images.unsplash.com/photo-1538481199705-c710c4e965fc?w=600&h=400&fit=crop',
        'Blender': 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=600&h=400&fit=crop',
        '插画': 'https://images.unsplash.com/photo-1513364776144-60967b0f800f?w=600&h=400&fit=crop',
        '開發': 'https://images.unsplash.com/photo-1542751371-adc38448a05e?w=600&h=400&fit=crop',
    }
    
    for keyword, img_url in image_keywords.items():
        if keyword in title_zh:
            return img_url
    
    return 'https://images.unsplash.com/photo-1614680376593-902f74cf0d41?w=600&h=400&fit=crop'

def get_tags(title_zh):
    """根據中文譯文獲取標籤"""
    tags = []
    
    if any(k in title_zh for k in ['招聘', '薪資', '面試', '招聘', '入職']):
        tags.append('招聘')
    if any(k in title_zh for k in ['外包', '項目', '自由職業', '報價']):
        tags.append('外包')
    if any(k in title_zh for k in ['AI', '生成式', '繪畫']):
        tags.append('AI美术')
    if any(k in title_zh for k in ['Unity', '虛幻', 'Blender', '3D', '技術']):
        tags.append('工具技术')
    if any(k in title_zh for k in ['工作室', '公司', '廠商']):
        tags.append('工作室')
    if any(k in title_zh for k in ['美術', '插畫', '設計', '作品']):
        tags.append('美术')
        
    if not tags:
        tags.append('日本討論')
        
    return tags

def collect_japan_forums():
    """收集日本論壇討論"""
    results = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    forums = [
        ('https://game.5ch.net/test/readacc.cgi?b=11&v=pc', '5ch_游戏开发', 'JP'),
        ('https://game.5ch.net/test/readacc.cgi?b=14&v=pc', '5ch_游戏业界', 'JP'),
        ('https://b.hatena.ne.jp/hotentry/game', 'はてな_游戏热门', 'JP'),
        ('https://chiebukuro.yahoo.co.jp/category/2080401792/', 'Yahoo知恵袋_游戏', 'JP'),
    ]
    
    for url, name, region in forums:
        try:
            print(f"Fetching {name}...")
            response = requests.get(url, headers=headers, timeout=15)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')
            
            links = []
            if '5ch' in name:
                links = soup.select('a')
            elif 'hatena' in name:
                links = soup.select('.entry-link, .entry-contents-title a')
            elif 'yahoo' in name:
                links = soup.select('a[class*="Title"]')
            
            if not links:
                links = soup.find_all('a', href=True)

            count = 0
            for link in links:
                if count >= 30: break
                
                title_original = link.get_text(strip=True)
                href = link.get('href', '')
                
                if len(title_original) > 12 and not any(x in title_original for x in ['利用規約', 'ヘルプ', 'お問い合わせ']):
                    print(f"  Translating: {title_original[:40]}...")
                    title_zh, summary = translate_and_summarize(title_original)
                    
                    virtual_score = random.randint(30, 150)
                    
                    results.append({
                        'source': name,
                        'region': region,
                        'title': title_original,
                        'title_zh': title_zh,
                        'summary': summary,
                        'content': summary,
                        'url': href if href.startswith('http') else (url + href if href.startswith('/') else url),
                        'image': get_image_for_keyword(title_zh),
                        'score': virtual_score,
                        'num_comments': random.randint(10, 100),
                        'collected_at': datetime.datetime.now().isoformat(),
                        'tags': get_tags(title_zh)
                    })
                    count += 1
        except Exception as e:
            print(f'Error fetching {name}: {e}')
    
    unique_results = []
    seen = set()
    for item in results:
        if item['title'] not in seen:
            seen.add(item['title'])
            unique_results.append(item)
    
    return unique_results

def save_results(results):
    """儲存結果到 JSON"""
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    filepath = f'data/2ch_{today}.json'
    
    if not os.path.exists('data'):
        os.makedirs('data')

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f'Saved {len(results)} posts to {filepath}')
    return filepath

if __name__ == '__main__':
    print('Starting Japan forum collection with LLM enhancement...')
    results = collect_japan_forums()
    save_results(results)
    print(f'Collected {len(results)} forum discussions')
