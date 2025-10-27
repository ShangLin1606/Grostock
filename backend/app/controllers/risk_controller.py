from fastapi import APIRouter, Query
from app.services.risk_service import calculate_risk_metrics, generate_risk_report

router = APIRouter()

@router.get("/metrics")
def get_risk_metrics(strategy_id: str = Query(..., description="策略代碼")):
    """
    計算指定策略的風險指標。
    包含 Sharpe、Sortino、Calmar、MDD、VaR。
    """
    metrics = calculate_risk_metrics(strategy_id)
    return {"strategy_id": strategy_id, "metrics": metrics}

@router.get("/report")
def get_risk_report(strategy_id: str = Query(...)):
    """
    生成風險分析報告（AI 總結）。
    """
    report = generate_risk_report(strategy_id)
    return {"strategy_id": strategy_id, "report": report}
