#!/usr/bin/env python3
"""
Reddit 論壇討論收集腳本
收集遊戲美術外包相關的小道消息和論壇討論
"""

import os
import json
import datetime
import requests

# 關鍵字 - 更多論壇風格的關鍵詞
KEYWORDS = [
    'game art', 'game artist', 'game美术', 'ゲームアート',
    'game outsourcing', 'art外包', '3D modeling', 'game design',
    'AI art', 'Midjourney', 'Stable Diffusion', 'game studio',
    '游戏公司', 'ゲーム会社', 'hiring', 'art job', 'art外包',
    'indie dev', 'indie game', 'small studio',
    'Blender', 'Maya', 'ZBrush', 'Substance', 'Unreal', 'Unity',
    'layoff', 'fired', 'hiring', 'interview', 'salary',
    'contract work', 'freelance', 'rate', 'quote',
    'portfolio', 'demo reel', 'showcase'
]

# Subreddits - 更多論壇風格的看板
SUBREDDITS = [
    'gamedev', 'GameArt', '3Dmodeling', 'cgjobs',
    'IndieGaming', 'gamedesign', 'gaming', 'Games',
    'GameUI', '像素艺术', 'houdini', 'Maya',
    'blender3d', 'ZBrush', 'substancepainter',
    'Unity3D', 'UnrealEngine', 'gamedevscreens',
    'lowpoly', 'indiegaming', ' roguelikedev'
]

def get_image_for_keyword(title):
    """根據關鍵詞返回相關圖片URL"""
    title_lower = title.lower()
    
    # 圖片關鍵詞映射
    image_keywords = {
        '3d': 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=400',
        'blender': 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=400',
        'maya': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400',
        'zbrush': 'https://images.unsplash.com/photo-1561214115-f2f134cc4912?w=400',
        'game': 'https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=400',
        'art': 'https://images.unsplash.com/photo-1513364776144-60967b0f800f?w=400',
        'design': 'https://images.unsplash.com/photo-1561070791-2526d30994b5?w=400',
        'ai': 'https://images.unsplash.com/photo-1677442136019-21780ecad995?w=400',
        'midjourney': 'https://images.unsplash.com/photo-1677442136019-21780ecad995?w=400',
        'stable': 'https://images.unsplash.com/photo-1620712943543-bcc4688e7485?w=400',
        'unreal': 'https://images.unsplash.com/photo-1542751371-adc38448a05e?w=400',
        'unity': 'https://images.unsplash.com/photo-1538481199705-c710c4e965fc?w=400',
        'pixel': 'https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=400',
        'hiring': 'https://images.unsplash.com/photo-1521737604893-d14cc237f11d?w=400',
        'job': 'https://images.unsplash.com/photo-1521737604893-d14cc237f11d?w=400',
        'layoff': 'https://images.unsplash.com/photo-1486312338219-ce68d2c6f44d?w=400',
        'freelance': 'https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=400',
    }
    
    for keyword, img_url in image_keywords.items():
        if keyword in title_lower:
            return img_url
    
    return 'https://images.unsplash.com/photo-1614680376593-902f74cf0d41?w=400'

def translate_to_simplified(text):
    """簡單的翻譯映射 - 實際項目應該使用 API"""
    translations = {
        'game art': '游戏美术',
        'game artist': '游戏美术师',
        'game dev': '游戏开发',
        'hiring': '招聘',
        'job': '工作',
        'news': '新闻',
        'discussion': '讨论',
        'update': '更新',
        'release': '发布',
        'report': '报告',
        ' earnings': '财报',
        'revenue': '营收',
        'studio': '工作室',
        'company': '公司',
        'AI': '人工智能',
        'layoff': '裁员',
        'hire': '雇佣',
        'salary': '薪资',
        'freelance': '自由职业',
        'contract': '合同',
        'rate': '费率',
        'portfolio': '作品集',
        'outsourcing': '外包',
    }
    
    result = text
    for eng, chi in translations.items():
        result = result.replace(eng, chi)
    
    return result

def collect_reddit():
    """收集 Reddit 論壇討論"""
    results = []
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    for sub in SUBREDDITS:
        try:
            # 使用舊式 Reddit API
            url = f'https://old.reddit.com/r/{sub}/hot/.json?limit=50'
            response = requests.get(url, headers=headers, timeout=15)
            data = response.json()
            
            for post in data['data']['children']:
                post_data = post['data']
                title_lower = post_data['title'].lower()
                
                # 檢查關鍵字
                if any(kw.lower() in title_lower for kw in KEYWORDS):
                    permalink = post_data.get('permalink', '')
                    
                    # 翻譯標題
                    translated_title = translate_to_simplified(post_data['title'])
                    
                    # 獲取相關圖片
                    thumbnail = post_data.get('thumbnail', '')
                    if thumbnail.startswith('http'):
                        image_url = thumbnail
                    else:
                        image_url = get_image_for_keyword(post_data['title'])
                    
                    results.append({
                        'source': 'reddit',
                        'subreddit': sub,
                        'title': post_data['title'],
                        'title_zh': translated_title,
                        'url': 'https://reddit.com' + permalink,
                        'score': post_data.get('score', 0),
                        'num_comments': post_data.get('num_comments', 0),
                        'image': image_url,
                        'created_utc': datetime.datetime.fromtimestamp(
                            post_data.get('created_utc', 0)
                        ).isoformat(),
                        'flair': post_data.get('link_flair_text'),
                        'tags': get_tags(post_data['title'])
                    })
                    
        except Exception as e:
            print(f'Error fetching r/{sub}: {e}')
    
    return results

def get_tags(title):
    """根據標題獲取標籤"""
    title_lower = title.lower()
    tags = []
    
    if any(k in title_lower for k in ['hire', 'job', 'salary', 'interview', 'layoff']):
        tags.append('招聘/裁员')
    if any(k in title_lower for k in ['outsourcing', 'freelance', 'contract', 'rate', 'quote']):
        tags.append('外包/自由职业')
    if any(k in title_lower for k in ['AI', 'midjourney', 'stable', 'diffusion']):
        tags.append('AI美术')
    if any(k in title_lower for k in ['unreal', 'unity', 'blender', 'maya', 'zbrush', '3d']):
        tags.append('工具/技术')
    if any(k in title_lower for k in ['studio', 'company', 'indie', 'small']):
        tags.append('工作室动态')
    if any(k in title_lower for k in ['showcase', 'portfolio', 'demo', 'art']):
        tags.append('作品展示')
        
    if not tags:
        tags.append('综合讨论')
        
    return tags

def save_results(results):
    """儲存結果到 JSON"""
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    filepath = f'data/reddit_{today}.json'
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f'Saved {len(results)} posts to {filepath}')
    return filepath

if __name__ == '__main__':
    print('Starting Reddit forum collection...')
    results = collect_reddit()
    save_results(results)
    print(f'Collected {len(results)} forum discussions')
