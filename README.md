# 🎮 遊戲美術外包 Daily Report

每日自動收集遊戲美術外包行業新聞資訊。

## 功能

- 🤖 每日自動執行（早上 8:00 UTC）
- 📱 收集 Reddit 遊戲開發、美術相關熱門討論
- 📺 收集日本 2ch/5ch 遊戲相關資訊
- 🌐 自動生成 HTML 報告
- 🚀 部署到 GitHub Pages

## 數據來源

- Reddit: gamedev, GameArt, 3Dmodeling, cgnews, design, jappan_gaming
- 日本: 5ch ゲーム板、ビジネス・業界板

## 本地開發

```bash
# 複製專案
git clone https://github.com/shoung/game-art-daily.git
cd game-art-daily

# 安裝依賴
pip install -r requirements.txt

# 測試收集腳本
python scripts/collect_reddit.py
python scripts/collect_2ch.py

# 生成報告
python scripts/generate_report.py
```

## GitHub Secrets 設定

如需 Reddit API 存取權限，請設定：
- `REDDIT_CLIENT_ID`
- `REDDIT_CLIENT_SECRET`
- `REDDIT_USER_AGENT`

## 部署

專案使用 GitHub Actions 自動部署到 GitHub Pages。

訪問: https://shoung.github.io/game-art-daily
