#!/usr/bin/env python3
"""
Reddit 新聞收集腳本
收集遊戲美術外包相關的熱門討論
"""

import os
import json
import datetime
import requests
from praw import Reddit

# Reddit API 設定
CLIENT_ID = os.getenv('REDDIT_CLIENT_ID', '')
CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET', '')
USER_AGENT = os.getenv('REDDIT_USER_AGENT', 'GameArtNewsBot/1.0')

# 關鍵字列表
KEYWORDS = [
    'game art', 'game artist', 'game美术', 'ゲームアート',
    'game outsourcing', 'art外包', '3D modeling', 'game design',
    'AI art', 'Midjourney', 'Stable Diffusion', 'game studio',
    '游戏公司', 'ゲーム会社', 'hiring', 'art job',
    'Blender', 'Maya', 'ZBrush', 'Substance', 'Unreal', 'Unity',
    'hiring', 'artist', 'game dev'
]

# Subreddits to monitor
SUBREDDITS = [
    'gamedev', 'GameArt', '3Dmodeling', 'cgnews',
    'design', 'gaming', 'gamedesign', 'indiegaming',
    'roguelike', 'Games', 'gamingnews'
]

def collect_reddit():
    """收集 Reddit 討論"""
    results = []
    
    # 嘗試使用 Reddit API
    if CLIENT_ID and CLIENT_SECRET:
        try:
            reddit = Reddit(
                client_id=CLIENT_ID,
                client_secret=CLIENT_SECRET,
                user_agent=USER_AGENT
            )
            
            for subreddit_name in SUBREDDITS:
                try:
                    subreddit = reddit.subreddit(subreddit_name)
                    for post in subreddit.hot(limit=30):
                        title_lower = post.title.lower()
                        if any(kw.lower() in title_lower for kw in KEYWORDS):
                            results.append({
                                'source': 'reddit',
                                'subreddit': subreddit_name,
                                'title': post.title,
                                'url': f'https://reddit.com{post.permalink}',
                                'score': post.score,
                                'num_comments': post.num_comments,
                                'created_utc': datetime.datetime.fromtimestamp(
                                    post.created_utc
                                ).isoformat(),
                                'flair': str(post.link_flair_text) if post.link_flair_text else None
                            })
                except Exception as e:
                    print(f"Error fetching r/{subreddit_name}: {e}")
                    
        except Exception as e:
            print(f"Reddit API error: {e}")
    
    # 如果沒有結果，使用備用方式
    if not results:
        results = collect_reddit_fallback()
    
    return results

def collect_reddit_fallback():
    """使用 RSS 備用收集"""
    results = []
    subreddits = ['gamedev', 'GameArt', '3Dmodeling', 'gaming']
    
    for sub in subreddits:
        try:
            # 使用舊式 Reddit URL
            url = f'https://old.reddit.com/r/{sub}/hot/.json?limit=30'
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            data = response.json()
            
            for post in data['data']['children']:
                post_data = post['data']
                title_lower = post_data['title'].lower()
                
                if any(kw.lower() in title_lower for kw in KEYWORDS):
                    results.append({
                        'source': 'reddit',
                        'subreddit': sub,
                        'title': post_data['title'],
                        'url': f'https://reddit.com{post_data['permalink']}",
                        'score': post_data['score'],
                        'num_comments': post_data['num_comments'],
                        'created_utc': datetime.datetime.fromtimestamp(
                            post_data['created_utc']
                        ).isoformat(),
                        'flair': post_data.get('link_flair_text')
                    })
                    
        except Exception as e:
            print(f"Error fetching r/{sub}: {e}")
    
    return results

def save_results(results):
    """儲存結果到 JSON"""
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    filepath = f'data/reddit_{today}.json'
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"Saved {len(results)} Reddit posts to {filepath}")
    return filepath

if __name__ == '__main__':
    print("Starting Reddit collection...")
    results = collect_reddit()
    save_results(results)
    print(f"Collected {len(results)} posts from Reddit")
