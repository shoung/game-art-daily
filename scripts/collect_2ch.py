#!/usr/bin/env python3
"""
日本論壇討論收集腳本
收集日本遊戲相關的小道消息和論壇討論
"""

import os
import json
import datetime
import requests
from bs4 import BeautifulSoup

def translate_to_simplified(text):
    """日文翻譯成簡體中文"""
    translations = {
        'ゲーム': '游戏',
        '美術': '美术',
        'アート': '美术',
        '採用': '招聘',
        '求人': '招聘',
        '外包': '外包',
        '仕事': '工作',
        '会社': '公司',
        'スタジオ': '工作室',
        '新作': '新作',
        'リリース': '发布',
        '開発': '开发',
        'AI': 'AI',
        'Midjourney': 'AI绘画',
        'Blender': 'Blender',
        'Unity': 'Unity',
        'Unreal': '虚幻引擎',
        '3D': '3D',
        '2D': '2D',
        'イラスト': '插画',
        '人事': '人事',
        '裁员': '裁员',
        'フリーランス': '自由职业',
        '単価': '单价',
        '案件': '项目',
        '退職': '辞职',
        '面接': '面试',
        '給与': '薪资',
        '報酬': '报酬',
        'ukumu': '受雇',
        '，不禁': '',
    }
    
    result = text
    for jp, chi in translations.items():
        result = result.replace(jp, chi)
    
    return result

def get_image_for_keyword(title):
    """根據關鍵詞返回相關圖片URL"""
    image_keywords = {
        'ゲーム': 'https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=600&h=400&fit=crop',
        '美術': 'https://images.unsplash.com/photo-1513364776144-60967b0f800f?w=600&h=400&fit=crop',
        'AI': 'https://images.unsplash.com/photo-1677442136019-21780ecad995?w=600&h=400&fit=crop',
        '3D': 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=600&h=400&fit=crop',
        '採用': 'https://images.unsplash.com/photo-1521737604893-d14cc237f11d?w=600&h=400&fit=crop',
        '外包': 'https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=600&h=400&fit=crop',
        'Unity': 'https://images.unsplash.com/photo-1538481199705-c710c4e965fc?w=600&h=400&fit=crop',
        'Blender': 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=600&h=400&fit=crop',
        'イラスト': 'https://images.unsplash.com/photo-1513364776144-60967b0f800f?w=600&h=400&fit=crop',
        '開発': 'https://images.unsplash.com/photo-1542751371-adc38448a05e?w=600&h=400&fit=crop',
    }
    
    for keyword, img_url in image_keywords.items():
        if keyword in title:
            return img_url
    
    return 'https://images.unsplash.com/photo-1614680376593-902f74cf0d41?w=600&h=400&fit=crop'

def get_tags(title):
    """根據標題獲取標籤"""
    tags = []
    
    if any(k in title for k in ['採用', '求人', '募集', '面接', '給与', '退職']):
        tags.append('招聘')
    if any(k in title for k in ['フリーランス', '単価', '案件', '外包', '報酬']):
        tags.append('外包')
    if any(k in title for k in ['AI', 'Midjourney', 'Stable Diffusion', '生成AI', '画像生成']):
        tags.append('AI美术')
    if any(k in title for k in ['Unity', 'Unreal', 'Blender', 'Maya', '3D', '開発']):
        tags.append('工具技术')
    if any(k in title for k in ['会社', 'スタジオ', '新作', '開発', '企業']):
        tags.append('工作室')
    if any(k in title for k in ['イラスト', '絵', 'アート', '美术', 'デザイン']):
        tags.append('美术')
        
    if not tags:
        tags.append('讨论')
        
    return tags

def collect_japan_forums():
    """收集日本論壇討論"""
    results = []
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    # 日本論壇來源 - 只選日本論壇，無台灣
    forums = [
        # 5ch 傳統論壇
        ('https://game.5ch.net/test/readacc.cgi?b=11&v=pc', '5ch_游戏开发', 'JP'),
        ('https://game.5ch.net/test/readacc.cgi?b=14&v=pc', '5ch_游戏业界', 'JP'),
        ('https://mevius.5ch.net/test/readacc.cgi?b=business&v=pc', '5ch_商业', 'JP'),
        # はてなブックマーク
        ('https://b.hatena.ne.jp/hotentry/game', 'はてな_游戏热门', 'JP'),
        ('https://b.hatena.ne.jp/hotentry/it', 'はてな_IT技术', 'JP'),
        # Yahoo Japan 知恵袋 - 游戏相关
        ('https://chiebukuro.yahoo.co.jp/category/2080401792/ recent', 'Yahoo知恵袋_游戏', 'JP'),
    ]
    
    for url, name, region in forums:
        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.encoding = 'utf-8'
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找链接和标题
            for link in soup.find_all(['a', 'title'], href=True)[:40]:
                title = link.get_text(strip=True)
                href = link.get('href', '')
                
                # 过滤标题
                if len(title) > 8 and len(title) < 200:
                    # 翻译
                    translated_title = translate_to_simplified(title)
                    
                    results.append({
                        'source': name,
                        'region': region,  # 日本
                        'title': title,
                        'title_zh': translated_title,
                        'url': href if href.startswith('http') else url,
                        'image': get_image_for_keyword(title),
                        'collected_at': datetime.datetime.now().isoformat(),
                        'tags': get_tags(title)
                    })
                    
        except Exception as e:
            print(f'Error fetching {name}: {e}')
    
    # 去重
    seen = set()
    unique_results = []
    for item in results:
        if item['title'] not in seen:
            seen.add(item['title'])
            unique_results.append(item)
    
    return unique_results

def save_results(results):
    """儲存結果到 JSON"""
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    filepath = f'data/2ch_{today}.json'
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f'Saved {len(results)} posts to {filepath}')
    return filepath

if __name__ == '__main__':
    print('Starting Japan forum collection...')
    results = collect_japan_forums()
    save_results(results)
    print(f'Collected {len(results)} forum discussions')
