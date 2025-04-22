from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.controllers.stock_controller import stock_controller
from app.controllers.agent_controller import agent_controller
from app.views.stock_view import stock_list_view, stock_price_view, technical_indicator_view
from app.views.agent_view import agent_analysis_view
from app.models.agent import AgentResponse, PortfolioResponse, ChatRequest
from loguru import logger
import asyncio
import traceback
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 檢查環境變數
required_env_vars = ["DB_USER", "DB_PASSWORD", "DB_NAME", "DB_HOST", "DB_PORT", "MONGODB_URI", "XAI_API_KEY"]
for var in required_env_vars:
    if not os.getenv(var):
        logger.error(f"缺少環境變數: {var}")
        raise ValueError(f"缺少環境變數: {var}")

try:
    logger.info("初始化 AgentController")
    agent_controller_instance = agent_controller  # 確保初始化完成
    logger.info("AgentController 初始化成功")
except Exception as e:
    logger.error(f"AgentController 初始化失敗: {str(e)}\n{traceback.format_exc()}")
    raise

@app.on_event("startup")
async def startup_event():
    from app.graph_rag import graph_rag
    try:
        logger.info("開始初始化 Neo4j 圖")
        await asyncio.to_thread(graph_rag.initialize_graph)
        logger.info("後端服務啟動，Neo4j 圖初始化完成")
    except Exception as e:
        logger.error(f"啟動失敗，Neo4j 圖初始化錯誤: {str(e)}\n{traceback.format_exc()}")
        raise
    finally:
        logger.info("startup_event 執行完成")

@app.get("/stocks")
async def get_stocks():
    """獲取股票列表"""
    try:
        logger.debug("處理 /stocks 請求")
        stocks = stock_controller.get_stock_list()
        if not stocks:
            logger.warning("股票列表為空")
            return stock_list_view([])
        logger.info(f"成功獲取 {len(stocks)} 個股票")
        return stock_list_view(stocks)
    except Exception as e:
        logger.error(f"獲取股票列表失敗: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"無法獲取股票列表: {str(e)}")

@app.get("/stocks/{stock_id}/prices")
async def get_stock_prices(stock_id: str):
    """獲取股票價格"""
    try:
        logger.debug(f"處理 /stocks/{stock_id}/prices 請求")
        prices = stock_controller.get_stock_prices(stock_id)
        if not prices:
            logger.warning(f"股票 {stock_id} 的價格資料不存在")
            raise HTTPException(status_code=404, detail=f"股票 {stock_id} 的價格資料不存在")
        logger.info(f"成功獲取股票 {stock_id} 的價格資料")
        return stock_price_view(prices)
    except Exception as e:
        logger.error(f"獲取股票 {stock_id} 價格失敗: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"無法獲取股票價格: {str(e)}")

@app.get("/features/{stock_id}")
async def get_technical_indicators(stock_id: str):
    """獲取技術指標"""
    try:
        logger.debug(f"處理 /features/{stock_id} 請求")
        indicators = stock_controller.get_technical_indicators(stock_id)
        if not indicators:
            logger.warning(f"股票 {stock_id} 的技術指標不存在")
            raise HTTPException(status_code=404, detail=f"股票 {stock_id} 的技術指標不存在")
        logger.info(f"成功獲取股票 {stock_id} 的技術指標")
        return technical_indicator_view(indicators)
    except Exception as e:
        logger.error(f"獲取股票 {stock_id} 技術指標失敗: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"無法獲取技術指標: {str(e)}")

@app.get("/agent/analyze", response_model=AgentResponse)
async def analyze_stock(query: str):
    """分析單一股票"""
    try:
        logger.debug(f"處理 /agent/analyze 請求: {query}")
        response = await agent_controller.analyze_stock(query)
        logger.info(f"成功分析股票: {query}")
        return response
    except Exception as e:
        logger.error(f"分析股票 {query} 失敗: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"分析股票失敗: {str(e)}")

@app.post("/chatbot")
async def chat(request: ChatRequest):
    """處理問答"""
    try:
        logger.debug(f"處理 /chatbot 請求: {request.query}")
        response = await agent_controller.chat(request.query)
        logger.info(f"成功處理問答查詢: {request.query}")
        return {"response": response}
    except Exception as e:
        logger.error(f"問答查詢 {request.query} 失敗: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"問答處理失敗: {str(e)}")

@app.post("/portfolio")
async def recommend_portfolio(request: PortfolioResponse):
    """生成投資組合建議"""
    try:
        logger.debug(f"處理 /portfolio 請求")
        portfolio = await agent_controller.recommend_portfolio(request)
        logger.info(f"成功生成投資組合建議")
        return portfolio
    except Exception as e:
        logger.error(f"生成投資組合建議失敗: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"生成投資組合建議失敗: {str(e)}")