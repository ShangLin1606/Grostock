from app.services.agents.base_agent import BaseAgent
from pymongo import MongoClient
from app.config.settings import settings
import numpy as np

class SentimentAgent(BaseAgent):
    name = "SentimentAgent"
    description = "新聞與社群情緒分析 Agent"

    def __init__(self):
        super().__init__()
        self.mongo = MongoClient(settings.MONGO_URI)["grostock"]["sentiments"]

    def get_sentiment_summary(self, keyword: str):
        docs = list(self.mongo.find({"symbol": {"$regex": keyword}}, {"score": 1}).limit(50))
        if not docs:
            return "無相關情緒資料"
        scores = [d["score"] for d in docs]
        avg = np.mean(scores)
        trend = "偏多" if avg > 0 else "偏空" if avg < 0 else "中性"
        return f"平均情緒分數：{avg:.2f}（{trend}）"

    async def run(self, query: str):
        summary = self.get_sentiment_summary(query)
        prompt = f"請根據以下情緒統計提供投資建議：\n{summary}"
        answer = await self.ask_llm("你是情緒分析專家。", prompt)
        return {"agent": self.name, "content": answer}
