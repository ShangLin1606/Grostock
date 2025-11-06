
# Grostock — AI Financial Intelligence System

An enterprise-grade backend system for quantitative forecasting, risk analysis, and multi-agent reasoning in the financial domain.

---

## Overview

Grostock is an AI-driven financial research system that integrates:
- Quantitative modeling for stock forecasting and backtesting
- Multi-agent architecture (RAG, Quant, Risk, LLM) with automatic routing
- Knowledge retrieval (RAG / GraphRAG)
- Automated MLOps pipeline (Dagster)
- Centralized logging, monitoring, and configuration management

The system demonstrates production-level AI engineering capabilities combining data infrastructure, financial analytics, and intelligent agent systems.

---

## System Architecture

```
                +-----------------------------+
                |     Frontend (Optional)     |
                |  React Dashboard / API UI   |
                +-------------+---------------+
                              |
+------------------------------+------------------------------+
|                             |                              |
|        Backend (FastAPI)    |     MLOps / Scheduler         |
|                             |         (Dagster)             |
| +-----------------------+   |   +-------------------------+  |
| |  API Routes (v2)      |-->|-->|  Assets: Crawlers       |  |
| |  /v2/data /v2/agent   |   |   |  ETL / Train / Risk     |  |
| +-----------------------+   |   +-------------------------+  |
| |  Services Layer       |   |                              |
| |  - Crawler Service    |   |                              |
| |  - Quant Service      |   |                              |
| |  - Risk Service       |   |                              |
| |  - LLM Service        |   |                              |
| |  - Agent Router       |   |                              |
| +-----------------------+   |                              |
+------------------------------+------------------------------+
                              |
                       +------+------ +
                       | PostgreSQL   |
                       | + MinIO      |
                       +--------------+
                              |
                       +------+------ +
                       | Monitoring   |
                       | (Grafana, ELK) |
                       +--------------+
```

---

## Tech Stack

| Category | Technology | Description |
|-----------|-------------|-------------|
| Backend Framework | FastAPI | High-performance asynchronous API framework |
| MLOps | Dagster | Data pipeline, ETL, model training & scheduling |
| Database | PostgreSQL | Stores stock, news, and model output data |
| Crawlers | requests, yfinance, feedparser | Collects stock prices and news |
| AI Models | scikit-learn, PyTorch | Quantitative forecasting models |
| LLM Agents | LangChain, OpenAI API | Intelligent multi-agent reasoning |
| Containerization | Docker, Docker Compose | Deployment and environment control |
| Monitoring | Grafana, Prometheus, ELK | System and log monitoring |

---

## Core Modules

| Module | Description |
|---------|-------------|
| Crawler Service | Automatically retrieves stock prices and financial news |
| Quant Service | Wraps model inference for market forecasting |
| Risk Service | Generates risk summaries using volatility and technical indicators |
| LLM Service | Answers general financial questions without exposing reasoning |
| Agent Router | Automatically selects the correct agent (RAG / Quant / Risk / LLM) |
| Dagster Pipelines | Automates daily ETL → training → evaluation → reporting |
| Config & Logging | Unified management with dotenv and Loguru |

---

## Multi-Agent Decision Flow

```
User Query → Agent Router →
  - "forecast" / "trend" / "strategy" → Quant Agent
  - "risk" / "volatility" / "VaR" → Risk Agent
  - "document" / "knowledge" → RAG Agent
  - Otherwise → LLM Agent (default)
```

Each agent returns only the final answer (no chain-of-thought).

---

## Main APIs (v2)

### Health Check
```
GET /health
Response: {"status":"ok","version":"v2"}
```

### Data Retrieval
```
GET /v2/data/stock?symbol=AAPL&start=2024-01-01&end=2024-06-30
GET /v2/data/news
```

### Agent Query
```
POST /v2/agent/ask
{
  "query": "Show me the prediction for AAPL"
}
Response:
{
  "agent": "quant",
  "output": "AAPL model signal: Buy"
}
```

---

## Deployment

```
git clone https://github.com/ShangLin1606/Grostock.git
cd Grostock-main

# Build and start all services
docker-compose up --build

# To use v2 backend:
# CMD ["uvicorn", "app.main_v2:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

---

## Automated Pipeline Example

| Time | Task |
|------|------|
| 00:00 | Fetch latest stock prices and news |
| 00:10 | Clean and transform data |
| 00:30 | Retrain quantitative models |
| 01:00 | Generate risk report |
| 08:00 | LLM Agent produces daily market summary |

---

## Project Highlights

- Complete end-to-end AI financial backend system  
- Modular and extensible architecture  
- Multi-Agent reasoning with contextual understanding  
- Daily automated retraining and reporting  
- Fully containerized and production-ready  

---

## Author

**Developer:** Shang-Lin Hsieh  
**Domain:** Data Science / AI Engineering / Quantitative Systems  
**Expertise:** FastAPI, Dagster, LLM Agents, Quant Models, MLOps

---

## License

MIT License © 2025 
