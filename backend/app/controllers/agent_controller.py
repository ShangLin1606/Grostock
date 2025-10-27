from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.llm_agent_router import LLMRouter

router = APIRouter()
router_llm = LLMRouter()

class AgentQuery(BaseModel):
    query: str

@router.post("/query")
async def query_agent(payload: AgentQuery):
    """
    AI Agent 問答系統：
    由 LLMRouter 自動判斷要使用哪個 Agent（可能是 0~多個），
    並整合最終回覆（不顯示思考鏈）。
    """
    try:
        result = await router_llm.route_query(payload.query)
        return {
            "status": "success",
            "mode": result["mode"],
            "agents": result["agents"],
            "output": result["output"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
