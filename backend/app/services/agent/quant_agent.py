from app.services.agents.base_agent import BaseAgent
from app.services.tools.quant_tools import simple_backtest
from app.services.tools.data_tools import get_db_conn
import pandas as pd

class QuantAgent(BaseAgent):
    name = "QuantAgent"
    description = "量化策略與回測分析 Agent"

    def get_price_series(self, stock_id="TSM"):
        conn = get_db_conn()
        df = pd.read_sql(f"SELECT date, close_price FROM stock_prices WHERE stock_id='{stock_id}' ORDER BY date;", conn)
        conn.close()
        return df["close_price"]

    async def run(self, query: str):
        prices = self.get_price_series("TSM")
        backtest = simple_backtest(prices)
        prompt = f"回測結果如下：{backtest}\n請解釋策略表現與可改進方向。"
        answer = await self.ask_llm("你是量化策略分析師。", prompt)
        return {"agent": self.name, "content": answer}
