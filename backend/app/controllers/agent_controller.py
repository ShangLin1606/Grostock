from phidata.agent import Agent, Tool
from ....dagster.utils.agent_tools import agent_tools
from backend.app.models.agent import AgentResponse
from backend.app.rag import rag
from backend.app.graph_rag import graph_rag
from ..utils.logger import app_logger as logger
import os
from dotenv import load_dotenv

load_dotenv()

class AgentController:
    def __init__(self):
        self.price_tool = Tool(name="predict_price", description="預測股票價格", func=agent_tools.predict_price)
        self.strategy_tool = Tool(name="generate_strategy", description="生成交易策略", func=agent_tools.generate_strategy)
        self.risk_tool = Tool(name="assess_risk", description="評估風險", func=agent_tools.assess_risk)
        self.market_tool = Tool(name="analyze_market", description="分析當天市場趨勢與新聞", func=agent_tools.analyze_market)

        self.price_agent = Agent(name="PricePredictor", llm="xai", api_key=os.getenv("XAI_API_KEY"), tools=[self.price_tool])
        self.strategy_agent = Agent(name="StrategyGenerator", llm="xai", api_key=os.getenv("XAI_API_KEY"), tools=[self.strategy_tool])
        self.risk_agent = Agent(name="RiskAssessor", llm="xai", api_key=os.getenv("XAI_API_KEY"), tools=[self.risk_tool])
        self.market_agent = Agent(name="MarketAnalysisAgent", llm="xai", api_key=os.getenv("XAI_API_KEY"), tools=[self.market_tool])

        system_prompt = """
你是一位專業的 AI 股票投資顧問，只能回答與股票、股市或市場相關的問題。
如果用戶問非相關問題，請回應：「抱歉，我只能回答與股票或市場相關的問題，請問您有什麼關於股票的疑問嗎？」
當用戶要求當天市場消息懶人包時，請調用 MarketAnalysisAgent 並整合結果。
回答時請保持專業、簡潔，並提供數據支持。
"""
        self.chatbot = Agent(
            name="StockChatbot",
            description="智能問答機器人",
            llm="xai",
            api_key=os.getenv("XAI_API_KEY"),
            system_prompt=system_prompt,
            tools=[self.price_tool, self.strategy_tool, self.risk_tool, self.market_tool],
            sub_agents=[self.price_agent, self.strategy_agent, self.risk_agent, self.market_agent]
        )

    def analyze_stock(self, query: str) -> AgentResponse:
        price_result = self.price_agent.run(f"請預測股票 {query.split()[-1]} 的未來價格")
        strategy_result = self.strategy_agent.run(f"請生成股票 {query.split()[-1]} 的交易策略")
        risk_result = self.risk_agent.run(f"請評估股票 {query.split()[-1]} 的風險")

        price_data = eval(price_result) if isinstance(price_result, str) else price_result
        strategy_data = eval(strategy_result) if isinstance(strategy_result, str) else strategy_result
        risk_data = eval(risk_result) if isinstance(risk_result, str) else risk_result

        response = AgentResponse(
            predictions=price_data,
            strategies=strategy_data,
            risks=risk_data
        )
        logger.info(f"分析股票 {query.split()[-1]} 完成")
        return response

    def chat(self, query: str) -> str:
        retrieved_docs = rag.retrieve(query)
        augmented_prompt = rag.augment(query, retrieved_docs)
        graph_response = graph_rag.query_graph(query)
        full_prompt = f"{augmented_prompt}\n圖資料: {graph_response}\n請生成詳細回應，包含價格預測、策略建議、風險評估和新聞資訊。"
        response = self.chatbot.run(full_prompt)
        logger.info(f"問答查詢: {query}, 回應生成完成")
        return response

agent_controller = AgentController()