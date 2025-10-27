from app.services.agents.base_agent import BaseAgent
from app.services.model_service import run_predictions
from app.services.tools.data_tools import get_db_conn
import pandas as pd
from loguru import logger

class FinanceAgent(BaseAgent):
    name = "FinanceAgent"
    description = "財務預測與估值分析 Agent"

    def load_financials(self, stock_name: str):
        conn = get_db_conn()
        df = pd.read_sql(f"SELECT * FROM stock_prices WHERE stock_id='{stock_name}' ORDER BY date DESC LIMIT 30;", conn)
        conn.close()
        return df

    async def run(self, query: str):
        stock_id = query.strip().upper().replace("台積電", "TSM")
        df = self.load_financials(stock_id)
        preds = run_predictions()
        prompt = f"股票 {stock_id} 近期價格走勢如下：\n{df.tail(5)}\n模型預測結果：{preds[:3]}"
        answer = await self.ask_llm("你是財務顧問，請總結重點並給投資建議。", prompt)
        logger.info(f"[{self.name}] 完成財務分析回答")
        return {"agent": self.name, "content": answer}
