from fastapi import FastAPI
from backend.app.controllers.stock_controller import stock_controller
from backend.app.controllers.agent_controller import agent_controller
from backend.app.views.stock_view import stock_list_view, stock_price_view, technical_indicator_view
from backend.app.views.agent_view import agent_analysis_view
from loguru import logger
from pydantic import BaseModel

app = FastAPI()

class ChatRequest(BaseModel):
    query: str

@app.on_event("startup")
async def startup_event():
    from backend.app.graph_rag import graph_rag
    graph_rag.initialize_graph()
    logger.info("後端服務啟動，Neo4j 圖初始化完成")

@app.get("/stocks")
async def get_stocks():
    stocks = stock_controller.get_stock_list()
    return stock_list_view(stocks)

@app.get("/stocks/{stock_id}/prices")
async def get_stock_prices(stock_id: str):
    prices = stock_controller.get_stock_prices(stock_id)
    return stock_price_view(prices)

@app.get("/features/{stock_id}")
async def get_technical_indicators(stock_id: str):
    indicators = stock_controller.get_technical_indicators(stock_id)
    return technical_indicator_view(indicators)

@app.get("/agent/analyze")
async def analyze_stock(query: str):
    response = agent_controller.analyze_stock(query)
    return agent_analysis_view(response)

@app.post("/chatbot")
async def chat(request: ChatRequest):
    response = agent_controller.chat(request.query)
    return {"response": response}