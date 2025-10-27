#  Grostock AI 投顧平台 (AI Investment Advisor Platform)

Grostock 是一個結合 **AI、RAG、GraphRAG、Dagster、自動化排程、與多智能體 (Multi-Agent) LLM 系統** 的智能投資分析平台。  
本系統能整合各種金融資料、量化模型與語言模型，提供投資分析、風險報告與策略建議。  
This project integrates **AI Agents, Quantitative Models, RAG, Graph Databases, and Workflow Automation** for intelligent investment insights.

---

##  功能總覽 (Key Features)

| 模組 | 功能摘要 |
|------|-----------|
|  **LLM Multi-Agent System** | 自動判斷並調用 RAG、Finance、Risk、Quant、Graph、Sentiment Agents。 |
|  **Quant Engine** | 提供回測、策略模擬與資金配置建議。 |
|  **Stacking ML Model** | LGBM + XGB + SVC + MLP 集成預測，Meta 模型 Logistic Regression。 |
|  **Dagster Pipeline** | 自動每日資料更新、特徵生成、訓練、預測與 retrain。 |
|  **Risk Management** | 計算 Sharpe、Sortino、Calmar、MDD、VaR 並自動生成報告。 |
|  **GraphRAG** | 基於 Neo4j 查詢公司供應鏈與產業鏈。 |
|  **RAG** | 使用 Milvus + MongoDB 建立向量檢索知識庫。 |
|  **Tools Framework** | Agents 可調用真實工具（行情、DB、回測、報表、RAG 檢索等）。 |
|  **FastAPI + React** | RESTful API 與前端分析視覺化介面。 |

---

## AI Agent 架構 (LLM Multi-Agent System)

Grostock 採用 **LLM 驅動代理人選擇架構**：
- LLMRouter 會理解使用者問題，並由 LLM 決定要啟動哪些 Agent（0~多個）。
- 每個 Agent 擁有專屬 LLM + 工具鏈 (Tools)。
- 所有 Agent 並行運行並整合為最終 AI 投顧回答。

```
使用者問題
   ↓
FastAPI /api/agent/query
   ↓
LLMRouter (由 LLM 決定使用哪些 Agent)
   ↓
多 Agent 並行執行 (RAG / Quant / Risk ...)
   ↓
整合結果 → LLM 總結 → 最終回答
```

---

## 六大 Agent 說明

| Agent | 功能 | 工具鏈 (Tools) |
|--------|------|----------------|
|  **RAGAgent** | 文件檢索與公告分析 | Milvus / MongoDB / LLM Summarizer |
|  **GraphAgent** | 產業鏈與公司關聯查詢 | Neo4j |
|  **FinanceAgent** | 模型預測與估值 | PostgreSQL / Stacking Model |
|  **SentimentAgent** | 新聞與社群情緒分析 | MongoDB / LLM Summarizer |
|  **QuantAgent** | 回測與策略模擬 | PostgreSQL / QuantTools |
|  **RiskAgent** | 風險評估與報告生成 | RiskTools / LLM Report Generator |

---

##  Dagster Pipeline 自動化流程

**每日自動任務：**
1. 更新資料庫股價
2. 執行特徵工程
3. 訓練 stacking 模型
4. 預測市場走勢
5. 當 F1 低於閾值自動 retrain

---

#  SYSTEM ARCHITECTURE (系統架構文件)

## Overview
Grostock is a modular, multi-agent AI system that integrates data pipelines, quantitative models, and language intelligence into a single backend ecosystem.

---

## Architecture Layers

| Layer | Description |
|--------|--------------|
| **Frontend (React)** | User interface for dashboards and analytics |
| **API Layer (FastAPI)** | Exposes RESTful endpoints for agent queries, models, strategies, and risks |
| **AI Layer (LLMRouter + Agents)** | LLMRouter decides which agents to activate based on the user query |
| **Agents Layer** | Each agent handles a domain-specific task (Finance, Risk, Quant, etc.) |
| **Tools Layer** | Agents invoke real data or analytical functions (DB, Quant, Risk) |
| **Data Layer** | Multi-database architecture supporting SQL + NoSQL + Vector + Graph |
| **Pipeline Layer (Dagster)** | Automates training, updates, and retraining cycles |

---

## Data Flow

```
User Query
  ↓
FastAPI (/api/agent/query)
  ↓
LLMRouter → LLM decides Agent combination
  ↓
Agents (Finance, Risk, Quant, RAG...)
  ↓
Tools (DB, Quant, Milvus, Risk)
  ↓
LLM Summarizer → Final Output
```

---

## Data Sources
- **PostgreSQL**: Market data, features, predictions
- **MongoDB**: News, sentiments, agent memory
- **Neo4j**: Corporate relationships & graph queries
- **Milvus**: Vector embeddings for RAG search
- **MinIO**: Model files & generated reports storage

---

## Author
 **ShangLin Xie (謝尚霖)**  
Data & AI Scientist / AI Engineer  
Project: **Grostock AI 投顧平台**  
GitHub: [ShangLin1606](https://github.com/ShangLin1606/Grostock)
