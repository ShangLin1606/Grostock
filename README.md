# Grostock

Grostock 是一個基於 AI 的股票分析平台，旨在提供歷史股價分析、每日更新、股價預測、交易策略生成和風險評估功能。

## 功能
- **歷史資料**：股票列表和股價從 2000 年至今，每日更新；新聞保留前 30 天。
- **每日更新**：從證交所 API 爬取股票列表，yfinance 獲取股價，新聞使用 Hugging Face 模型生成情緒標籤與摘要。
- **AI Agent**：股價預測、策略生成和風險評估。
- **智能問答機器人**：支援股票分析查詢，使用 RAG 和 GraphRAG。
- **技術棧**：AWS、Docker Compose、Minikube、FastAPI、React、PostgreSQL、MongoDB、Milvus。

## 安裝與運行
1. 安裝 Docker 和 Minikube。
2. 複製專案：
   ```bash
   git clone git@github.com:username/Grostock.git
   cd Grostock
   
## 開發進度
- [x] 步驟 1：設置開發環境
- [x] 步驟 2：資料爬取與更新
- [ ] 步驟 3：特徵工程
- [ ] 後續步驟待開發

## 運行 Dagster
1. 啟動服務：
   ```bash
   docker-compose up -d