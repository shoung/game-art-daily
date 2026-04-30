import os
import json
import datetime
from pathlib import Path


def load_all_data():
    """載入所有數據並去重"""
    data_dir = Path('data')
    if not data_dir.exists():
        return []

    items = []
    for json_file in sorted(data_dir.glob('*.json')):
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                items.extend(data)
            else:
                items.append(data)

    # 去重
    seen = set()
    unique_items = []
    for item in items:
        title = item.get('title', '') or item.get('title_zh', '')
        if title not in seen:
            seen.add(title)
            unique_items.append(item)

    # 按分數排序
    unique_items.sort(key=lambda x: x.get('score', 0), reverse=True)
    return unique_items


CSS_TEMPLATE = """
<style>
    @font-face {
        font-family: 'Noto Sans SC';
        src: url('https://cdn.jsdelivr.net/npm/noto-sans-sc@1.0.0/fonts/NotoSansSC-Regular.woff2') format('woff2');
        font-weight: 400;
        font-style: normal;
        font-display: swap;
    }
    @font-face {
        font-family: 'Noto Sans SC';
        src: url('https://cdn.jsdelivr.net/npm/noto-sans-sc@1.0.0/fonts/NotoSansSC-Medium.woff2') format('woff2');
        font-weight: 500;
        font-style: normal;
        font-display: swap;
    }
    @font-face {
        font-family: 'Noto Sans SC';
        src: url('https://cdn.jsdelivr.net/npm/noto-sans-sc@1.0.0/fonts/NotoSansSC-Bold.woff2') format('woff2');
        font-weight: 700;
        font-style: normal;
        font-display: swap;
    }

    :root {
        --bg: #F1F5F9;
        --card-bg: #FFFFFF;
        --text: #0F172A;
        --text-secondary: #64748B;
        --text-muted: #94A3B8;
        --primary: #E63946;
        --accent: #3B82F6;
        --border: #E2E8F0;
        --card-hover-border: #E63946;
        --modal-bg: rgba(15, 23, 42, 0.75);
        --tag-bg: #F1F5F9;
        --tag-text: #475569;
        --shadow-sm: 0 1px 3px rgba(0,0,0,0.06);
        --shadow-md: 0 4px 16px rgba(0,0,0,0.08);
        --shadow-lg: 0 12px 32px rgba(0,0,0,0.12);
        --radius: 16px;
        --radius-sm: 8px;
        --radius-pill: 100px;
    }

    [data-theme="dark"] {
        --bg: #0B0F19;
        --card-bg: #151C2C;
        --text: #F1F5F9;
        --text-secondary: #94A3B8;
        --text-muted: #64748B;
        --border: #1E293B;
        --card-hover-border: #E63946;
        --tag-bg: #1E293B;
        --tag-text: #CBD5E1;
        --shadow-sm: 0 1px 3px rgba(0,0,0,0.3);
        --shadow-md: 0 4px 16px rgba(0,0,0,0.4);
        --shadow-lg: 0 12px 32px rgba(0,0,0,0.5);
    }

    *, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }
    html { scroll-behavior: smooth; }

    body {
        font-family: 'Noto Sans SC', -apple-system, BlinkMacSystemFont, sans-serif;
        background-color: var(--bg);
        color: var(--text);
        line-height: 1.6;
        min-height: 100vh;
        -webkit-font-smoothing: antialiased;
    }

    /* ── Container ── */
    .container { max-width: 1100px; margin: 0 auto; padding: 0 24px; }

    /* ── Header ── */
    header {
        padding: 64px 0 48px;
        display: flex;
        justify-content: space-between;
        align-items: flex-end;
        border-bottom: 1px solid var(--border);
        margin-bottom: 56px;
    }

    .brand h1 {
        font-size: clamp(1.8rem, 4vw, 2.6rem);
        font-weight: 800;
        letter-spacing: -0.03em;
        line-height: 1.1;
        color: var(--text);
    }

    .brand h1 span { color: var(--primary); }

    .brand-sub {
        margin-top: 10px;
        font-size: 0.9rem;
        color: var(--text-secondary);
        font-weight: 500;
        letter-spacing: 0.02em;
    }

    .controls { display: flex; gap: 12px; align-items: center; }

    .btn-icon {
        background: var(--card-bg);
        border: 1px solid var(--border);
        width: 44px;
        height: 44px;
        border-radius: 50%;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.1rem;
        box-shadow: var(--shadow-sm);
        transition: all 0.2s ease;
    }

    .btn-icon:hover { border-color: var(--primary); box-shadow: var(--shadow-md); }
    .btn-icon:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }

    /* ── Feed Layout — Bento Grid / Masonry ── */
    #feed {
        columns: 3 320px;
        column-gap: 20px;
        padding-bottom: 80px;
    }

    /* ── Article Card (Bento) ── */
    .article-card {
        background: var(--card-bg);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 0;
        display: inline-block;
        width: 100%;
        break-inside: avoid;
        margin-bottom: 20px;
        cursor: pointer;
        box-shadow: var(--shadow-sm);
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        opacity: 0;
        transform: translateY(12px);
        animation: cardEntrance 0.5s ease forwards;
        overflow: hidden;
    }

    @keyframes cardEntrance {
        to { opacity: 1; transform: translateY(0); }
    }

    .article-card:hover {
        border-color: var(--card-hover-border);
        box-shadow: 0 8px 32px rgba(230, 57, 70, 0.15), 0 2px 8px rgba(0,0,0,0.08);
        transform: translateY(-4px);
    }

    .article-card:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }

    /* Top accent bar — color-coded by region */
    .card-accent {
        height: 4px;
        width: 100%;
        background: var(--primary);
    }
    .card-accent.region-JP { background: #3B82F6; }
    .card-accent.region-CN { background: #F59E0B; }
    .card-accent.region-EN { background: #10B981; }

    .card-main { padding: 20px 22px 22px; }

    .card-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 14px;
        flex-wrap: wrap;
    }

    .card-source {
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: var(--primary);
        background: rgba(230, 57, 70, 0.08);
        padding: 3px 10px;
        border-radius: var(--radius-pill);
    }

    [data-theme="dark"] .card-source { background: rgba(230, 57, 70, 0.15); }

    .card-region {
        font-size: 0.7rem;
        font-weight: 600;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        color: var(--text-muted);
        padding: 3px 10px;
        border: 1px solid var(--border);
        border-radius: var(--radius-pill);
    }

    .card-date { font-size: 0.78rem; color: var(--text-muted); margin-left: auto; }

    .card-title {
        font-size: clamp(0.95rem, 2vw, 1.1rem);
        font-weight: 700;
        line-height: 1.4;
        color: var(--text);
        margin-bottom: 10px;
        letter-spacing: -0.01em;
    }

    .card-summary {
        font-size: 0.85rem;
        color: var(--text-secondary);
        line-height: 1.7;
        margin-bottom: 16px;
    }

    .card-footer {
        display: flex;
        align-items: center;
        gap: 20px;
        flex-wrap: wrap;
    }

    .card-stat {
        display: flex;
        align-items: center;
        gap: 5px;
        font-size: 0.8rem;
        color: var(--text-muted);
        font-weight: 500;
    }

    .card-stat svg { flex-shrink: 0; }

    .card-tags { display: flex; gap: 6px; flex-wrap: wrap; margin-left: auto; }

    .tag {
        font-size: 0.72rem;
        padding: 3px 10px;
        background: var(--tag-bg);
        color: var(--tag-text);
        border-radius: var(--radius-pill);
        font-weight: 500;
        letter-spacing: 0.01em;
    }

    /* ── Loading Sentinel ── */
    #loading-sentinel {
        height: 80px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: var(--text-muted);
        font-size: 0.875rem;
        font-weight: 500;
        letter-spacing: 0.02em;
    }

    .loading-dot {
        display: inline-block;
        width: 6px;
        height: 6px;
        background: var(--text-muted);
        border-radius: 50%;
        margin: 0 3px;
        animation: pulse 1.2s ease-in-out infinite;
    }

    .loading-dot:nth-child(2) { animation-delay: 0.2s; }
    .loading-dot:nth-child(3) { animation-delay: 0.4s; }

    @keyframes pulse {
        0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
        40% { transform: scale(1); opacity: 1; }
    }

    /* ── Modal ── */
    .modal-overlay {
        position: fixed;
        inset: 0;
        background: var(--modal-bg);
        z-index: 1000;
        display: none;
        align-items: center;
        justify-content: center;
        padding: 24px;
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
    }

    .modal {
        background: var(--card-bg);
        max-width: 720px;
        width: 100%;
        border-radius: 24px;
        max-height: 88vh;
        overflow-y: auto;
        position: relative;
        box-shadow: var(--shadow-lg);
        transform: scale(0.96) translateY(16px);
        opacity: 0;
        transition: all 0.35s cubic-bezier(0.34, 1.2, 0.64, 1);
        pointer-events: none;
    }

    .modal-overlay.active { display: flex; }
    .modal-overlay.active .modal { transform: scale(1) translateY(0); opacity: 1; pointer-events: auto; }

    .modal-header {
        padding: 40px 48px 0;
        display: flex;
        flex-direction: column;
        gap: 12px;
        border-bottom: none;
    }

    .modal-meta { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }

    .modal-close {
        position: absolute;
        top: 20px;
        right: 20px;
        width: 40px;
        height: 40px;
        background: var(--tag-bg);
        border: 1px solid var(--border);
        color: var(--text-secondary);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        font-size: 1.1rem;
        line-height: 1;
        transition: all 0.2s;
    }

    .modal-close:hover { background: var(--primary); color: #fff; border-color: var(--primary); }

    .modal-title {
        font-size: clamp(1.3rem, 3vw, 1.9rem);
        font-weight: 800;
        line-height: 1.3;
        letter-spacing: -0.02em;
        color: var(--text);
        padding-right: 48px;
    }

    .modal-body { padding: 28px 48px 40px; }

    .modal-text {
        font-size: 1rem;
        line-height: 1.85;
        color: var(--text-secondary);
        white-space: pre-wrap;
        margin-bottom: 32px;
    }

    .modal-footer {
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 16px;
        padding-top: 24px;
        border-top: 1px solid var(--border);
    }

    .modal-stats { display: flex; gap: 20px; }

    .modal-stat { font-size: 0.85rem; color: var(--text-muted); font-weight: 500; }

    .btn {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 12px 28px;
        background: var(--primary);
        color: #fff;
        text-decoration: none;
        border-radius: var(--radius-pill);
        font-weight: 700;
        font-size: 0.875rem;
        letter-spacing: 0.02em;
        box-shadow: 0 4px 12px rgba(230, 57, 70, 0.3);
        transition: all 0.2s ease;
    }

    .btn:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(230, 57, 70, 0.4); }
    .btn:active { transform: translateY(0); }

    /* ── Footer ── */
    footer {
        padding: 60px 0;
        border-top: 1px solid var(--border);
        text-align: center;
        color: var(--text-muted);
        font-size: 0.8rem;
    }

    /* ── Responsive ── */
    @media (max-width: 1024px) {
        #feed { columns: 2 280px; column-gap: 16px; }
    }

    @media (max-width: 768px) {
        header {
            flex-direction: column;
            align-items: flex-start;
            gap: 24px;
            padding: 48px 0 32px;
        }
        #feed { columns: 1; column-gap: 0; }
        .article-card { margin-bottom: 12px; }
        .card-main { padding: 16px 18px 18px; }
        .card-date { display: none; }
        .card-tags { display: none; }
        .modal-header { padding: 28px 24px 0; }
        .modal-body { padding: 20px 24px 32px; }
        .modal-title { font-size: 1.3rem; padding-right: 40px; }
        .modal-footer { flex-direction: column; align-items: flex-start; }
    }

    /* ── Reduced motion ── */
    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            animation-duration: 0.01ms !important;
            transition-duration: 0.01ms !important;
        }
    }
</style>
"""


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
    <link href="https://cdn.jsdelivr.net/npm/noto-sans-sc@1.0.0/fonts/NotoSansSC-Regular.woff2" rel="preload" as="font" type="font/woff2" crossorigin>
    <link href="https://cdn.jsdelivr.net/npm/noto-sans-sc@1.0.0/fonts/NotoSansSC-Medium.woff2" rel="preload" as="font" type="font/woff2" crossorigin>
    <link href="https://cdn.jsdelivr.net/npm/noto-sans-sc@1.0.0/fonts/NotoSansSC-Bold.woff2" rel="preload" as="font" type="font/woff2" crossorigin>
    {CSS_TEMPLATE}
</head>
<body>
    <div class="container">
        <header>
            <div class="brand">
                <h1>Game Art <span>Daily</span></h1>
                <p class="brand-sub">{date_str} · 精選全球遊戲美術資訊</p>
            </div>
            <div class="controls">
                <button class="btn-icon" onclick="toggleTheme()" id="themeBtn" aria-label="切換深色模式">☾</button>
            </div>
        </header>

        <div id="feed"></div>
        <div id="loading-sentinel">
            <span class="loading-dot"></span>
            <span class="loading-dot"></span>
            <span class="loading-dot"></span>
        </div>

        <footer>
            <p>© {today.year} Game Art Daily</p>
        </footer>
    </div>

    <!-- Modal -->
    <div class="modal-overlay" id="modalOverlay" onclick="closeModal(event)">
        <div class="modal" role="dialog" aria-modal="true">
            <button class="modal-close" onclick="hideModal()" aria-label="關閉">✕</button>
            <div class="modal-header">
                <div class="modal-meta">
                    <span class="card-source" id="modalSource">SOURCE</span>
                    <span class="card-region" id="modalRegion">REGION</span>
                </div>
                <h2 class="modal-title" id="modalTitle">Title</h2>
            </div>
            <div class="modal-body">
                <div class="modal-text" id="modalText">Content</div>
                <div class="modal-footer">
                    <div class="modal-stats">
                        <span class="modal-stat" id="modalScore">🔥 0</span>
                        <span class="modal-stat" id="modalComments">💬 0</span>
                    </div>
                    <a href="#" class="btn" id="modalLink" target="_blank" rel="noopener">
                        進入原始討論
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>
                    </a>
                </div>
            </div>
        </div>
    </div>

    <script>
        const allData = {cards_json};
        let currentIndex = 0;
        const BATCH_SIZE = 20;

        const feed = document.getElementById('feed');
        const sentinel = document.getElementById('loading-sentinel');

        function createCard(item, index) {{
            const source = (item.subreddit || item.source || 'NEWS').toUpperCase();
            const region = (item.region || 'JP').toUpperCase();
            const score = item.score || 0;
            const comments = item.num_comments || 0;
            const title_zh = item.title_zh || item.title || '無標題';
            const summary = item.summary || '';
            const tags = Array.isArray(item.tags) ? item.tags.slice(0, 3) : [];
            const collectedAt = item.collected_at ? new Date(item.collected_at).toLocaleDateString('zh-TW', {{month:'short', day:'numeric'}}) : '';

            const card = document.createElement('article');
            card.className = 'article-card';
            card.setAttribute('tabindex', '0');
            card.setAttribute('role', 'button');
            card.setAttribute('aria-label', title_zh);
            card.onclick = () => showModal(index);
            card.onkeydown = (e) => {{ if (e.key === 'Enter' || e.key === ' ') {{ e.preventDefault(); showModal(index); }} }};

            const tagsHtml = tags.length > 0
                ? `<div class="card-tags">${{tags.map(t => `<span class="tag">${{t}}</span>`).join('')}}</div>`
                : '';

            card.innerHTML = `
                <div class="card-accent region-${{item.region || 'JP'}}"></div>
                <div class="card-main">
                    <div class="card-header">
                        <span class="card-source">${{source}}</span>
                        <span class="card-region">${{region}}</span>
                        ${{collectedAt ? `<span class="card-date">${{collectedAt}}</span>` : ''}}
                    </div>
                    <h3 class="card-title">${{title_zh}}</h3>
                    ${{summary ? `<p class="card-summary">${{summary}}</p>` : ''}}
                    <div class="card-footer">
                        <span class="card-stat">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>
                            ${{score.toLocaleString()}}
                        </span>
                        <span class="card-stat">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
                            ${{comments.toLocaleString()}}
                        </span>
                        ${{tagsHtml}}
                    </div>
                </div>
            `;
            return card;
        }}

        function loadMore() {{
            if (currentIndex >= allData.length) {{
                sentinel.innerHTML = '已顯示全部 ${{allData.length}} 則';
                return;
            }}

            const fragment = document.createDocumentFragment();
            const end = Math.min(currentIndex + BATCH_SIZE, allData.length);

            for (let i = currentIndex; i < end; i++) {{
                fragment.appendChild(createCard(allData[i], i));
            }}

            feed.appendChild(fragment);
            currentIndex = end;

            if (currentIndex >= allData.length) {{
                sentinel.innerHTML = '已顯示全部 ${{allData.length}} 則';
            }}
        }}

        const observer = new IntersectionObserver((entries) => {{
            if (entries[0].isIntersecting) {{
                loadMore();
            }}
        }}, {{ rootMargin: '300px' }});

        observer.observe(sentinel);

        function toggleTheme() {{
            const current = document.body.getAttribute('data-theme');
            const next = current === 'dark' ? 'light' : 'dark';
            document.body.setAttribute('data-theme', next);
            localStorage.setItem('theme', next);
            document.getElementById('themeBtn').textContent = next === 'dark' ? '☀' : '☾';
        }}

        if (localStorage.getItem('theme') === 'dark' ||
            (!localStorage.getItem('theme') && window.matchMedia('(prefers-color-scheme: dark)').matches)) {{
            document.body.setAttribute('data-theme', 'dark');
            document.getElementById('themeBtn').textContent = '☀';
        }}

        function showModal(index) {{
            const item = allData[index];
            const title_zh = item.title_zh || item.title || '無標題';
            const source = (item.subreddit || item.source || 'NEWS').toUpperCase();
            const region = (item.region || 'JP').toUpperCase();
            const score = item.score || 0;
            const comments = item.num_comments || 0;

            document.getElementById('modalSource').textContent = source;
            document.getElementById('modalRegion').textContent = region;
            document.getElementById('modalTitle').textContent = title_zh;
            document.getElementById('modalText').textContent = item.content || item.summary || '';
            document.getElementById('modalScore').textContent = '🔥 ' + score.toLocaleString();
            document.getElementById('modalComments').textContent = '💬 ' + comments.toLocaleString();
            document.getElementById('modalLink').href = item.url || '#';

            document.getElementById('modalOverlay').classList.add('active');
            document.body.style.overflow = 'hidden';
            document.querySelector('.modal-close').focus();
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
