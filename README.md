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







階段 3：測試後端功能  並且優化調整  

階段 4：測試前端功能  並且優化調整 且用得更美化更高級一點 然後要有主頁說明專案 還有股票列表顯示的與預測值 及新聞 與股票聲量等等的頁面 還有投資顧問的頁面 還有甚麼頁面你可以幫我想 還有我策略分析的頁面 加入一些圖表之類的幫我想 子加入Chart.js（圖表庫）和 Tailwind CSS（美化樣式）
所有策略都要有訊號的圖表等前端部分要放在前端 幫我設計更多頁面等等 且要有跑圈圈等待AI回答

階段 4 成功，加入 ELK + grafana + prometheus 並且把專案功能調整到好 你幫我想還要加入的功能或是未加入的功能加入且用好 還有哪些功能需要改的 改好

上架到AWS且用ngix反向代理+用K8S


回顧我整個專案，給我三樣東西:
1.我整體專案的架構圖。
2.我整個專案完整的README.md。
3.我整個專案的敘述與技術棧，寫履歷用，用寫履歷的高級原則來寫。

股市熱力圖參考https://tw.tradingview.com/heatmap/stock/#%7B%22dataSource%22%3A%22SPX500%22%2C%22blockColor%22%3A%22change%22%2C%22blockSize%22%3A%22market_cap_basic%22%2C%22grouping%22%3A%22sector%22%7D 並且幫我改變網頁整體設計風格 紅漲綠跌 給我完整程式碼

新增你覺得需要的網頁並且增加需要的後端或功能程式碼 符合需求 

後續我要訓練模型，模型部分要做更多特徵與每日是否漲跌等等的欄位來預測漲跌與語言模型部分優化與精進
