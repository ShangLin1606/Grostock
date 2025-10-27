from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.settings import settings
from app.config.logger import init_logger
from app.controllers import agent_controller, risk_controller, strategy_controller, model_controller

# 初始化 FastAPI
app = FastAPI(
    title="Grostock AI Backend",
    description="AI 投顧 + 量化策略 + 風險管理 後端系統",
    version="3.0.0"
)

# 初始化 Loguru
logger = init_logger()

# 設定 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 若部署時可改為具體網域
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 載入路由模組
app.include_router(agent_controller.router, prefix="/api/agent", tags=["AI Agent"])
app.include_router(risk_controller.router, prefix="/api/risk", tags=["風險管理"])
app.include_router(strategy_controller.router, prefix="/api/strategy", tags=["量化策略"])
app.include_router(model_controller.router, prefix="/api/model", tags=["模型管理"])

@app.get("/api/health")
def health_check():
    """健康檢查"""
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.API_HOST, port=settings.API_PORT, reload=True)
