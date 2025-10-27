"""
LLMRouter v2
使用 LLM 判斷應該喚醒哪些 Agent（RAG、Graph、Finance、Sentiment、Quant、Risk），
並整合結果生成最終回答。
"""
import asyncio
from loguru import logger
from app.services.agents.rag_agent import RAGAgent
from app.services.agents.graph_agent import GraphAgent
from app.services.agents.finance_agent import FinanceAgent
from app.services.agents.sentiment_agent import SentimentAgent
from app.services.agents.quant_agent import QuantAgent
from app.services.agents.risk_agent import RiskAgent
from app.config.settings import settings
import openai

# 初始化 OpenAI API（或其他 LLM）
openai.api_key = settings.HF_API_KEY  # 這裡你也可改成 OpenAI / Ollama / Local LLM

class LLMRouter:
    def __init__(self):
        """初始化六大 Agent"""
        self.agents = {
            "RAG": RAGAgent(),
            "GraphRAG": GraphAgent(),
            "Finance": FinanceAgent(),
            "Sentiment": SentimentAgent(),
            "Quant": QuantAgent(),
            "Risk": RiskAgent()
        }

    async def ask_llm_to_route(self, query: str):
        """
        讓 LLM 分析輸入問題，決定要使用哪些 Agent。
        輸出範例：
        {
            "use_agents": ["RAG", "Finance"],
            "reason": "問題包含公司資訊與財務預測。"
        }
        """
        system_prompt = """
        你是一個 AI 系統的總管，負責決定要喚醒哪些專家代理人 (Agent) 來回答問題。
        可選的 Agent 包含：
        - RAG：基於文件檢索
        - GraphRAG：基於產業鏈與關聯圖譜
        - Finance：股價、預測、估值
        - Sentiment：新聞、社群輿論分析
        - Quant：量化策略、回測、配置
        - Risk：風險控管、報酬波動分析

        請根據使用者問題內容，輸出一個 JSON：
        {
            "use_agents": [...],
            "reason": "..."
        }
        僅能輸出 JSON，不要解釋。
        """

        prompt = f"{system_prompt}\n使用者問題：{query}"
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": system_prompt},
                          {"role": "user", "content": query}],
                temperature=0.3,
                max_tokens=300,
            )
            msg = response.choices[0].message["content"]
            logger.info(f"🔍 LLM Routing 判斷：{msg}")
            import json
            decision = json.loads(msg)
            return decision
        except Exception as e:
            logger.error(f"LLM Routing 失敗: {e}")
            # fallback: 預設使用 Finance
            return {"use_agents": ["Finance"], "reason": "LLM 判斷失敗，預設使用 Finance"}

    async def route_query(self, query: str):
        """主流程：由 LLM 決定要啟用哪些 Agent，再並行執行"""
        decision = await self.ask_llm_to_route(query)
        selected = decision.get("use_agents", [])
        reason = decision.get("reason", "")
        logger.info(f"📡 啟用 Agent：{selected}")

        if not selected:
            return {
                "mode": "LLM_ONLY",
                "agents": [],
                "output": f"這是一個一般金融問題：{query}\n建議請詢問具體個股、策略或市場事件。"
            }

        tasks = [self.agents[name].run(query) for name in selected if name in self.agents]
        results = await asyncio.gather(*tasks)
        merged_context = "\n".join([r["content"] for r in results])

        # 綜合回答
        summary_prompt = f"""
        以下是各代理人提供的分析結果，請用簡潔口語化中文整合成最終回答，
        限 300 字以內，不顯示推理過程。
        {merged_context}
        """
        try:
            final_response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": "你是一位投資顧問助理"},
                          {"role": "user", "content": summary_prompt}],
                temperature=0.4,
                max_tokens=400,
            )
            output_text = final_response.choices[0].message["content"]
        except Exception as e:
            output_text = f"整合分析失敗：{e}"

        return {
            "mode": "MULTI_AGENT",
            "agents": selected,
            "reason": reason,
            "output": output_text
        }
