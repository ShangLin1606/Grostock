from fastapi import APIRouter, Query
from app.services.agents.quant_agent import QuantAgent
from app.services.agents.finance_agent import FinanceAgent

router = APIRouter()
quant_agent = QuantAgent()
finance_agent = FinanceAgent()

@router.get("/backtest")
def run_backtest(strategy_id: str = Query(..., description="策略代碼")):
    """
    對指定策略進行回測分析。
    回傳年化報酬、Sharpe、MDD 等指標。
    """
    result = quant_agent.backtest_strategy(strategy_id)
    return {"strategy_id": strategy_id, "result": result}

@router.get("/simulate")
def simulate_portfolio(strategy_id: str = Query(...), capital: float = 1000000):
    """
    根據策略模擬投資組合結果。
    """
    sim_result = finance_agent.simulate_strategy(strategy_id, capital)
    return {"strategy_id": strategy_id, "capital": capital, "simulation": sim_result}
