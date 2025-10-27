from app.services.agents.base_agent import BaseAgent
from app.services.tools.risk_tools import calc_sharpe, calc_sortino, calc_max_drawdown, calc_var
import numpy as np

class RiskAgent(BaseAgent):
    name = "RiskAgent"
    description = "風險控管與報酬波動分析 Agent"

    async def run(self, query: str):
        returns = np.random.normal(0.001, 0.02, 200)
        sharpe = calc_sharpe(returns)
        sortino = calc_sortino(returns)
        mdd = calc_max_drawdown(np.cumprod(1 + returns))
        var = calc_var(returns)
        summary = f"Sharpe={sharpe:.2f}, Sortino={sortino:.2f}, MDD={mdd:.2%}, VaR95={var:.3f}"
        prompt = f"請解釋以下風險指標代表的意義並給出管理建議：\n{summary}"
        answer = await self.ask_llm("你是風險管理顧問。", prompt)
        return {"agent": self.name, "content": answer}
