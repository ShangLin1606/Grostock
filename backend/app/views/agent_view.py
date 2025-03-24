from fastapi.responses import JSONResponse
from backend.app.models.agent import AgentResponse

def agent_analysis_view(response: AgentResponse) -> JSONResponse:
    return JSONResponse(content=response.dict())