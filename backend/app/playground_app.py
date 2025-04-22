from phi.playground import Playground, serve_playground_app
from app.controllers.agent_controller import agent_controller
from loguru import logger
import traceback
from fastapi import FastAPI

app = FastAPI()

try:
    logger.info("初始化 Playground")
    playground = Playground(
        agents=[
            agent_controller.price_agent,
            agent_controller.strategy_agent,
            agent_controller.risk_agent,
            agent_controller.market_agent,
            agent_controller.portfolio_agent,
            agent_controller.news_agent,
            agent_controller.investment_advisor
        ]
    )
    playground_app = playground.get_app()
    app.mount("/playground", playground_app)
    logger.info("Playground 初始化完成")
except Exception as e:
    logger.error(f"初始化 Playground 失敗: {str(e)}\n{traceback.format_exc()}")
    raise

# 添加根路徑測試
@app.get("/")
async def root():
    return {"message": "Playground is running. Try /playground or /chat"}

if __name__ == "__main__":
    serve_playground_app(
        app=app,
        host="0.0.0.0",
        port=8001,
    )