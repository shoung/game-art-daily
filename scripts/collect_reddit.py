#!/usr/bin/env python3
"""
Reddit 論壇討論收集腳本
只收集日本與歐美的遊戲美術外包相關討論
"""

import os
import json
import datetime
import requests

# 關鍵字 - 論壇風格 + 遊戲美術外包
KEYWORDS = [
    # 遊戲美術
    'game art', 'game artist', 'game美术', 'ゲームアート',
    '3D modeling', '3D artist', 'character art', 'environment art',
    'concept art', 'illustration', 'game UI', 'vfx', 'animation',
    # 外包
    'game outsourcing', 'art外包', 'art outsourcing', 'contract work',
    'freelance', 'freelancer', 'hourly rate', 'project quote',
    # AI 美術
    'AI art', 'Midjourney', 'Stable Diffusion', 'Generative AI',
    'AI game art', 'AI illustration',
    # 工具
    'Blender', 'Maya', 'ZBrush', 'Substance', 'Houdini',
    'Unreal Engine', 'Unity', 'Unreal', 'Unity3D',
    # 工作室/公司
    'game studio', 'indie dev', 'indie game', 'small studio',
    'AAA studio', 'game company', 'ゲーム会社', 'ゲームスタジオ',
    # 求職/裁員
    'hiring', 'job opening', 'job interview', 'salary', 'layoff',
    'fired', 'contractor', 'recruit', '採用', '求人',
    # 歐美論壇關鍵詞
    'portfolio', 'demo reel', 'showcase', 'critique',
    'salary discussion', 'pay', 'rate per hour'
]

# 只訂閱日本與歐美論壇 - 無台灣
SUBREDDITS = [
    # 美國/英語論壇
    'gamedev', 'GameArt', '3Dmodeling', 'cgjobs', 'IndieGaming',
    'gamedesign', 'GameUI', 'gaming', 'Games', 'lowpoly',
    'blender3d', 'ZBrush', 'substancepainter', 'Maya3D',
    'Unity3D', 'UnrealEngine', 'gamedevscreens',
    'pixelart', 'ImaginaryLandscapes', 'conceptart',
    'VFX', 'animation', 'digitalart', 'ArtStation',
    # 英國/加拿大
    'GameDevUK', 'gamedevcanada',
    # 歐洲
    'gamedevDE', 'gamedevFR',
    # 日本相關（英文）
    'japan_gaming', 'Tokyo',
    # 裁員/求職專板
    'GameJobs', 'layoff', 'career',
    # 自由職業
    'freelance', 'freelancegamedev', 'Upwork', 'GameArtJobs'
]

def get_image_for_keyword(title):
    """根據關鍵詞返回相關圖片URL"""
    title_lower = title.lower()
    
    image_keywords = {
        '3d': 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=600&h=400&fit=crop',
        'blender': 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=600&h=400&fit=crop',
        'maya': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=600&h=400&fit=crop',
        'zbrush': 'https://images.unsplash.com/photo-1561214115-f2f134cc4912?w=600&h=400&fit=crop',
        'game': 'https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=600&h=400&fit=crop',
        'art': 'https://images.unsplash.com/photo-1513364776144-60967b0f800f?w=600&h=400&fit=crop',
        'design': 'https://images.unsplash.com/photo-1561070791-2526d30994b5?w=600&h=400&fit=crop',
        'AI': 'https://images.unsplash.com/photo-1677442136019-21780ecad995?w=600&h=400&fit=crop',
        'midjourney': 'https://images.unsplash.com/photo-1677442136019-21780ecad995?w=600&h=400&fit=crop',
        'unreal': 'https://images.unsplash.com/photo-1542751371-adc38448a05e?w=600&h=400&fit=crop',
        'unity': 'https://images.unsplash.com/photo-1538481199705-c710c4e965fc?w=600&h=400&fit=crop',
        'pixel': 'https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=600&h=400&fit=crop',
        'hiring': 'https://images.unsplash.com/photo-1521737604893-d14cc237f11d?w=600&h=400&fit=crop',
        'job': 'https://images.unsplash.com/photo-1521737604893-d14cc237f11d?w=600&h=400&fit=crop',
        'layoff': 'https://images.unsplash.com/photo-1486312338219-ce68d2c6f44d?w=600&h=400&fit=crop',
        'freelance': 'https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=600&h=400&fit=crop',
        'portfolio': 'https://images.unsplash.com/photo-1561070791-2526d30994b5?w=600&h=400&fit=crop',
        'vfx': 'https://images.unsplash.com/photo-1557672172-298e090bd0f1?w=600&h=400&fit=crop',
        'animation': 'https://images.unsplash.com/photo-1557672172-298e090bd0f1?w=600&h=400&fit=crop',
        'concept': 'https://images.unsplash.com/photo-1561070791-2526d30994b5?w=600&h=400&fit=crop',
        'illustration': 'https://images.unsplash.com/photo-1513364776144-60967b0f800f?w=600&h=400&fit=crop',
    }
    
    for keyword, img_url in image_keywords.items():
        if keyword in title_lower:
            return img_url
    
    return 'https://images.unsplash.com/photo-1614680376593-902f74cf0d41?w=600&h=400&fit=crop'

def translate_to_simplified(text):
    """翻譯成簡體中文"""
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
        'AI': 'AI',
        'layoff': '裁员',
        'hire': '雇佣',
        'salary': '薪资',
        'freelance': '自由职业',
        'contract': '外包',
        'rate': '时薪',
        'portfolio': '作品集',
        'outsourcing': '外包',
        'artist': '美术师',
        'designer': '设计师',
        'animator': '动画师',
        'vfx': '特效',
        '3D': '3D',
        '2D': '2D',
        'indie': '独立游戏',
        'AAA': '3A',
        'unreal': '虚幻引擎',
        'unity': 'Unity',
        'Blender': 'Blender',
        'Maya': 'Maya',
        'ZBrush': 'ZBrush',
        'Substance': 'Substance',
        'showcase': '作品展示',
        'demo reel': 'Demo reel',
        'critique': '点评',
        'project': '项目',
        'quote': '报价',
        'hourly': '时薪',
        'remote': '远程',
        'remote work': '远程工作',
        'junior': '初级',
        'senior': '高级',
        'lead': '负责人',
        'manager': '经理',
        'team': '团队',
        'recruiting': '招聘中',
    }
    
    result = text
    for eng, chi in translations.items():
        result = result.replace(eng, chi)
    
    return result

def collect_reddit():
    """收集 Reddit 論壇討論 - 只日本與歐美"""
    results = []
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    for sub in SUBREDDITS:
        try:
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
                        'region': 'US/EU',  # 標記區域
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
    
    if any(k in title_lower for k in ['hire', 'job', 'salary', 'interview', 'layoff', 'recruit', 'hiring', 'opening']):
        tags.append('招聘')
    if any(k in title_lower for k in ['outsourcing', 'freelance', 'contract', 'rate', 'quote', 'hourly', 'project', 'bid']):
        tags.append('外包')
    if any(k in title_lower for k in ['AI', 'midjourney', 'stable', 'diffusion', 'generative', 'AI art']):
        tags.append('AI美术')
    if any(k in title_lower for k in ['unreal', 'unity', 'blender', 'maya', 'zbrush', '3d', 'substance', 'houdini']):
        tags.append('工具技术')
    if any(k in title_lower for k in ['studio', 'company', 'indie', 'small', 'AAA', 'team', 'studio']):
        tags.append('工作室')
    if any(k in title_lower for k in ['showcase', 'portfolio', 'demo', 'art', 'illustration', 'concept', 'design']):
        tags.append('作品展示')
    if any(k in title_lower for k in ['vfx', 'animation', 'animate', 'motion']):
        tags.append('动画特效')
        
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
    print('Starting Reddit forum collection (Japan & US/EU only)...')
    results = collect_reddit()
    save_results(results)
    print(f'Collected {len(results)} forum discussions')
