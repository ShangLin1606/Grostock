from app.services.agents.base_agent import BaseAgent
from app.services.tools.rag_tools import search_vector_db
from pymongo import MongoClient
from app.config.settings import settings
from loguru import logger

class RAGAgent(BaseAgent):
    name = "RAGAgent"
    description = "文件檢索與公告分析 Agent"

    def __init__(self):
        super().__init__()
        self.mongo = MongoClient(settings.MONGO_URI)["grostock"]["news"]

    def load_recent_docs(self, keyword: str, limit=3):
        """從 MongoDB 抓取關鍵字相關的最新文件"""
        docs = self.mongo.find({"content": {"$regex": keyword}}, {"title": 1, "content": 1}).limit(limit)
        text = "\n".join([f"{d['title']}\n{d['content']}" for d in docs])
        return text

    async def run(self, query: str):
        mongo_context = self.load_recent_docs(query)
        rag_context = search_vector_db([0.5]*384)  # 假設用固定向量，可換 SentenceTransformer
        full_context = mongo_context + "\n" + rag_context
        prompt = f"以下是相關文件內容，請用摘要方式回答：\n{full_context}\n問題：{query}"
        answer = await self.ask_llm("你是研究助理，根據文件回答。", prompt)
        logger.info(f"[{self.name}] 完成文件檢索回答")
        return {"agent": self.name, "content": answer}
