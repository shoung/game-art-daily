import os
import json
import datetime
from pathlib import Path

def load_all_data():
    """載入所有數據並去重"""
    data_dir = Path('data')
    all_items = []
    
    # 遍歷所有 json 檔案
    if not data_dir.exists():
        data_dir.mkdir(exist_ok=True)
        
    for json_file in data_dir.glob('*.json'):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                items = data if isinstance(data, list) else data.get('entries', [])
                for item in items:
                    if not isinstance(item, dict): continue
                    if 'title_zh' not in item and 'title' not in item: continue
                    all_items.append(item)
        except Exception as e:
            print(f"Error loading {json_file}: {e}")
    
    # 去重 (依標題)
    unique_items = []
    seen = set()
    for item in all_items:
        title = item.get('title') or item.get('title_zh')
        if title not in seen:
            seen.add(title)
            unique_items.append(item)
    
    # 按分數排序
    unique_items.sort(key=lambda x: x.get('score', 0), reverse=True)
    return unique_items

def generate_html(items):
    """生成具有無限捲動功能的 HTML 報告"""
    today = datetime.datetime.now()
    date_str = today.strftime('%Y年%m月%d日')
    update_time = today.strftime('%H:%M')
    
    cards_json = json.dumps(items, ensure_ascii=False)
    
    html = f'''<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Game Art Daily - 遊戲美術外包日報</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&family=Noto+Sans+TC:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg: #f8f9fa;
            --card-bg: #ffffff;
            --text: #1a1a1a;
            --text-secondary: #6c757d;
            --primary: #e63946;
            --accent: #457b9d;
            --border: #e9ecef;
            --shadow: 0 4px 20px rgba(0,0,0,0.08);
            --modal-bg: rgba(0,0,0,0.85);
        }}

        [data-theme="dark"] {{
            --bg: #121212;
            --card-bg: #1e1e1e;
            --text: #f8f9fa;
            --text-secondary: #adb5bd;
            --border: #2d2d2d;
            --shadow: 0 4px 25px rgba(0,0,0,0.3);
        }}

        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: 'Inter', 'Noto Sans TC', sans-serif;
            background-color: var(--bg);
            color: var(--text);
            transition: background-color 0.3s, color 0.3s;
            line-height: 1.6;
        }}

        .container {{ max-width: 1400px; margin: 0 auto; padding: 0 24px; }}

        /* Header */
        header {{
            padding: 80px 0 40px;
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
            border-bottom: 1px solid var(--border);
            margin-bottom: 40px;
        }}

        .brand h1 {{ font-size: 2.8rem; font-weight: 800; letter-spacing: -1.5px; margin-bottom: 10px; }}
        .brand p {{ color: var(--text-secondary); font-size: 1.2rem; }}
        
        .controls {{ display: flex; gap: 15px; align-items: center; }}
        
        .theme-toggle {{
            background: var(--card-bg);
            border: 1px solid var(--border);
            padding: 10px;
            border-radius: 50%;
            cursor: pointer;
            width: 44px;
            height: 44px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.2rem;
            box-shadow: var(--shadow);
        }}

        /* Grid Layout */
        #grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: 30px;
            padding-bottom: 40px;
        }}

        #loading-sentinel {{ 
            height: 100px; 
            display: flex; 
            align-items: center; 
            justify-content: center; 
            color: var(--text-secondary); 
            font-weight: 500;
        }}

        /* Card Style */
        .card {{
            background: var(--card-bg);
            border-radius: 24px;
            overflow: hidden;
            border: 1px solid var(--border);
            transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
            cursor: pointer;
            animation: fadeIn 0.6s ease forwards;
        }}

        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        .card:hover {{
            transform: translateY(-8px);
            box-shadow: 0 12px 30px rgba(0,0,0,0.15);
            border-color: var(--primary);
        }}

        .card-img-wrapper {{ position: relative; height: 220px; overflow: hidden; }}
        .card-img {{ width: 100%; height: 100%; object-fit: cover; transition: transform 0.6s; }}
        .card:hover .card-img {{ transform: scale(1.05); }}

        .card-badge {{
            position: absolute;
            top: 15px; left: 15px;
            background: var(--primary);
            color: white;
            padding: 4px 14px;
            border-radius: 30px;
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            z-index: 2;
        }}

        .card-body {{ padding: 24px; }}
        .card-title {{ font-size: 1.2rem; font-weight: 700; margin-bottom: 12px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; height: 3.4em; }}
        .card-summary {{ font-size: 0.95rem; color: var(--text-secondary); margin-bottom: 20px; height: 4.8em; overflow: hidden; }}
        
        .card-meta {{
            display: flex;
            justify-content: space-between;
            font-size: 0.85rem;
            color: var(--text-secondary);
            padding-top: 15px;
            border-top: 1px solid var(--border);
        }}

        /* Modal */
        .modal-overlay {{
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: var(--modal-bg);
            z-index: 1000;
            display: none;
            align-items: center;
            justify-content: center;
            padding: 24px;
            backdrop-filter: blur(12px);
            transition: background 0.5s ease;
        }}

        .modal {{
            background: var(--card-bg);
            max-width: 850px;
            width: 100%;
            border-radius: 32px;
            max-height: 90vh;
            overflow-y: auto;
            position: relative;
            transform: scale(0.85) rotate(-4deg) translateY(60px);
            opacity: 0;
            transition: all 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
            pointer-events: none;
        }}

        .modal-overlay.active {{ display: flex; }}
        .modal-overlay.active .modal {{ 
            transform: scale(1) rotate(0deg) translateY(0); 
            opacity: 1; 
            pointer-events: auto;
        }}

        .modal-close {{
            position: absolute;
            top: 24px; right: 24px;
            width: 44px; height: 44px;
            background: rgba(0,0,0,0.5);
            color: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            z-index: 10;
        }}

        .modal-hero {{ width: 100%; height: 380px; object-fit: cover; }}
        .modal-content {{ padding: 48px; }}
        .modal-source {{ color: var(--primary); font-weight: 700; margin-bottom: 12px; display: block; letter-spacing: 1px; }}
        .modal-title {{ font-size: 2.2rem; font-weight: 800; margin-bottom: 24px; line-height: 1.25; }}
        .modal-text {{ font-size: 1.15rem; margin-bottom: 36px; white-space: pre-wrap; color: var(--text); opacity: 0.9; }}
        
        .btn {{
            display: inline-block;
            padding: 14px 36px;
            background: var(--primary);
            color: white;
            text-decoration: none;
            border-radius: 16px;
            font-weight: 700;
            transition: all 0.2s;
            box-shadow: 0 4px 15px rgba(230, 57, 70, 0.3);
        }}
        .btn:hover {{ transform: translateY(-2px); box-shadow: 0 6px 20px rgba(230, 57, 70, 0.4); }}

        footer {{ padding: 80px 0; border-top: 1px solid var(--border); text-align: center; color: var(--text-secondary); }}

        @media (max-width: 768px) {{
            header {{ flex-direction: column; padding: 60px 0 30px; align-items: flex-start; gap: 20px; }}
            .brand h1 {{ font-size: 2.2rem; }}
            .modal-content {{ padding: 30px; }}
            .modal-title {{ font-size: 1.6rem; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="brand">
                <h1>Game Art Daily</h1>
                <p>📈 {date_str} 更新 · 精選全球資訊</p>
            </div>
            <div class="controls">
                <button class="theme-toggle" onclick="toggleTheme()" id="themeBtn">🌙</button>
            </div>
        </header>

        <div id="grid"></div>
        <div id="loading-sentinel">載入中...</div>

        <footer>
            <p>© {today.year} Game Art Daily · 提供高品質行業洞察</p>
            <p style="margin-top: 8px; font-size: 0.8rem; opacity: 0.6;">手動匯入 JSON 驅動版</p>
        </footer>
    </div>

    <!-- Modal Container -->
    <div class="modal-overlay" id="modalOverlay" onclick="closeModal(event)">
        <div class="modal" id="modal">
            <div class="modal-close" onclick="hideModal()">✕</div>
            <img class="modal-hero" id="modalHero" src="" alt="">
            <div class="modal-content">
                <span class="modal-source" id="modalSource">SOURCE</span>
                <h2 class="modal-title" id="modalTitle">Title</h2>
                <div class="modal-text" id="modalText">Content</div>
                <a href="#" class="btn" id="modalLink" target="_blank">進入原始討論 →</a>
            </div>
        </div>
    </div>

    <script>
        const allData = {cards_json};
        let currentIndex = 0;
        const BATCH_SIZE = 20;

        const grid = document.getElementById('grid');
        const sentinel = document.getElementById('loading-sentinel');

        function createCard(item, index) {{
            const source = (item.subreddit || item.source || 'NEWS').toUpperCase();
            const score = item.score || 0;
            const comments = item.num_comments || 0;
            const image = item.image || 'https://images.unsplash.com/photo-1614680376593-902f74cf0d41?w=600&h=400&fit=crop';
            const title_zh = item.title_zh || item.title || '無標題';
            
            const card = document.createElement('div');
            card.className = 'card';
            card.onclick = () => showModal(index);
            card.innerHTML = `
                <div class="card-badge">${{source}}</div>
                <div class="card-img-wrapper">
                    <img class="card-img" src="${{image}}" alt="" loading="lazy">
                </div>
                <div class="card-body">
                    <h3 class="card-title">${{title_zh}}</h3>
                    <p class="card-summary">${{item.summary || ''}}</p>
                    <div class="card-meta">
                        <span>🔥 ${{score}}</span>
                        <span>💬 ${{comments}}</span>
                    </div>
                </div>
            `;
            return card;
        }}

        function loadMore() {{
            if (currentIndex >= allData.length) {{
                sentinel.textContent = '已顯示所有內容';
                return;
            }}

            const fragment = document.createDocumentFragment();
            const end = Math.min(currentIndex + BATCH_SIZE, allData.length);
            
            for (let i = currentIndex; i < end; i++) {{
                fragment.appendChild(createCard(allData[i], i));
            }}
            
            grid.appendChild(fragment);
            currentIndex = end;

            if (currentIndex >= allData.length) {{
                sentinel.textContent = '已顯示所有內容';
                observer.unobserve(sentinel);
            }}
        }}

        // Intersection Observer for Infinite Scroll
        const observer = new IntersectionObserver((entries) => {{
            if (entries[0].isIntersecting) {{
                loadMore();
            }}
        }}, {{ rootMargin: '200px' }});

        observer.observe(sentinel);

        // Theme Toggle
        function toggleTheme() {{
            const body = document.body;
            const current = body.getAttribute('data-theme');
            const next = current === 'dark' ? 'light' : 'dark';
            body.setAttribute('data-theme', next);
            localStorage.setItem('theme', next);
            document.getElementById('themeBtn').textContent = next === 'dark' ? '☀️' : '🌙';
        }}

        if (localStorage.getItem('theme') === 'dark' || 
            (!localStorage.getItem('theme') && window.matchMedia('(prefers-color-scheme: dark)').matches)) {{
            document.body.setAttribute('data-theme', 'dark');
            document.getElementById('themeBtn').textContent = '☀️';
        }}

        // Modal Logic
        function showModal(index) {{
            const item = allData[index];
            const title_zh = item.title_zh || item.title || '無標題';
            document.getElementById('modalHero').src = item.image || 'https://images.unsplash.com/photo-1614680376593-902f74cf0d41?w=800&h=500&fit=crop';
            document.getElementById('modalSource').textContent = (item.subreddit || item.source || 'NEWS').toUpperCase();
            document.getElementById('modalTitle').textContent = title_zh;
            document.getElementById('modalText').textContent = item.content || item.summary || '';
            document.getElementById('modalLink').href = item.url || '#';
            
            document.getElementById('modalOverlay').classList.add('active');
            document.body.style.overflow = 'hidden';
        }}

        function hideModal() {{
            document.getElementById('modalOverlay').classList.remove('active');
            document.body.style.overflow = '';
        }}

        function closeModal(e) {{
            if (e.target === document.getElementById('modalOverlay')) hideModal();
        }}

        document.addEventListener('keydown', (e) => {{
            if (e.key === 'Escape') hideModal();
        }});
    </script>
</body>
</html>'''
    return html

def main():
    print("🚀 Generating report...")
    items = load_all_data()
    if not items:
        print("⚠️ No items found in data/ directory!")
        html = generate_html([])
    else:
        html = generate_html(items)
        
    output_dir = Path('output')
    output_dir.mkdir(exist_ok=True)
    
    with open(output_dir / 'index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✨ Done! Generated report with {len(items)} items available for infinite scroll.")

if __name__ == '__main__':
    main()
