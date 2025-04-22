from phi.agent import Agent
from phi.model.xai import xAI
from app.dagster_pipeline.utils.agent_tools import agent_tools
from app.models.agent import AgentResponse, PortfolioResponse
from app.rag import rag
from app.graph_rag import graph_rag
from loguru import logger
import os
from dotenv import load_dotenv
from cachetools import TTLCache
import asyncio
from typing import List, Dict
import traceback

load_dotenv()

cache = TTLCache(maxsize=1000, ttl=3600)

class AgentController:
    def __init__(self):
        self.xai_model = None
        try:
            logger.info("開始初始化 XAI 模型")
            self.xai_model = xAI(model_id="grok-beta", api_key=os.getenv("XAI_API_KEY"))
            logger.info("XAI 模型初始化成功")
        except Exception as e:
            logger.error(f"XAI 模型初始化失敗: {str(e)}\n{traceback.format_exc()}")

        self.price_tool = agent_tools.predict_price
        self.strategy_tool = agent_tools.generate_strategy
        self.risk_tool = agent_tools.assess_risk
        self.market_tool = agent_tools.analyze_market
        self.portfolio_tool = agent_tools.generate_portfolio
        self.news_tool = agent_tools.analyze_news

        self.price_agent = Agent(
            name="PricePredictor", model=self.xai_model, tools=[self.price_tool], 
            description="負責預測股價" if self.xai_model else "負責預測股價（XAI 不可用）"
        ) if self.xai_model else None
        self.strategy_agent = Agent(
            name="StrategyGenerator", model=self.xai_model, tools=[self.strategy_tool], 
            description="負責生成交易策略" if self.xai_model else "負責生成交易策略（XAI 不可用）"
        ) if self.xai_model else None
        self.risk_agent = Agent(
            name="RiskAssessor", model=self.xai_model, tools=[self.risk_tool], 
            description="負責評估風險" if self.xai_model else "負責評估風險（XAI 不可用）"
        ) if self.xai_model else None
        self.market_agent = Agent(
            name="MarketAnalysisAgent", model=self.xai_model, tools=[self.market_tool], 
            description="負責分析市場趨勢與新聞" if self.xai_model else "負責分析市場趨勢與新聞（XAI 不可用）"
        ) if self.xai_model else None
        self.portfolio_agent = Agent(
            name="PortfolioAdvisor", model=self.xai_model, tools=[self.portfolio_tool], 
            description="負責提供投組建議" if self.xai_model else "負責提供投組建議（XAI 不可用）"
        ) if self.xai_model else None
        self.news_agent = Agent(
            name="NewsAnalyzer", model=self.xai_model, tools=[self.news_tool], 
            description="負責分析新聞內容並提取關鍵資訊" if self.xai_model else "負責分析新聞內容並提取關鍵資訊（XAI 不可用）"
        ) if self.xai_model else None

        system_prompt = """
你是一位專業的 AI 股票投資顧問，只能回答與股票、股市或市場相關的問題。
如果問題超出範圍，回應：「抱歉，我只能回答與股票或市場相關的問題，請問您有什麼關於股票的疑問嗎？」
根據問題複雜性，選擇自行處理或調用子代理：
- 簡單問題（如價格查詢）：自行處理。
- 複雜問題（如投組建議、市場分析）：調用相關子代理。
整合 RAG 和 GraphRAG 的結果，提供詳細回應，包含價格預測、策略建議、風險評估、市場趨勢、投組建議和新聞分析。
若 XAI 不可用，回應：「抱歉，XAI 服務當前不可用，無法提供完整分析。」
"""
        self.investment_advisor = Agent(
            name="InvestmentAdvisor",
            model=self.xai_model,
            system_prompt=system_prompt,
            tools=[self.price_tool, self.strategy_tool, self.risk_tool, self.market_tool, self.portfolio_tool, self.news_tool],
            sub_agents=[self.price_agent, self.strategy_agent, self.risk_agent, self.market_agent, self.portfolio_agent, self.news_agent] if self.xai_model else [],
            description="AI 股票投資顧問，整合所有子代理" if self.xai_model else "AI 股票投資顧問（XAI 不可用）"
        ) if self.xai_model else None

    async def analyze_stock(self, query: str) -> AgentResponse:
        try:
            cache_key = f"analyze_{query}"
            if cache_key in cache:
                logger.info(f"Cache hit for {query}")
                return cache[cache_key]

            stock_id = query.split()[-1]
            if not self.investment_advisor:
                logger.warning("XAI 不可用，無法進行股票分析")
                return AgentResponse(predictions={}, strategies={}, risks={}, market_analysis={}, news_analysis="XAI 服務不可用")

            tasks = [
                asyncio.to_thread(self.price_agent.run, f"請預測股票 {stock_id} 的未來價格") if self.price_agent else asyncio.sleep(0, result="XAI 不可用"),
                asyncio.to_thread(self.strategy_agent.run, f"請生成股票 {stock_id} 的交易策略") if self.strategy_agent else asyncio.sleep(0, result="XAI 不可用"),
                asyncio.to_thread(self.risk_agent.run, f"請評估股票 {stock_id} 的風險") if self.risk_agent else asyncio.sleep(0, result="XAI 不可用"),
                asyncio.to_thread(self.market_agent.run) if self.market_agent else asyncio.sleep(0, result="XAI 不可用"),
                asyncio.to_thread(self.news_agent.run, stock_id) if self.news_agent else asyncio.sleep(0, result="XAI 不可用")
            ]
            price_result, strategy_result, risk_result, market_result, news_result = await asyncio.gather(*tasks)

            price_data = eval(price_result) if isinstance(price_result, str) and price_result != "XAI 不可用" else {}
            strategy_data = eval(strategy_result) if isinstance(strategy_result, str) and strategy_result != "XAI 不可用" else {}
            risk_data = eval(risk_result) if isinstance(risk_result, str) and risk_result != "XAI 不可用" else {}
            market_data = {"market_summary": market_result} if isinstance(market_result, str) and market_result != "XAI 不可用" else market_result if isinstance(market_result, dict) else {}
            news_data = news_result.get("news_analysis", "") if isinstance(news_result, dict) else news_result if news_result != "XAI 不可用" else ""

            response = AgentResponse(
                predictions=price_data,
                strategies=strategy_data,
                risks=risk_data,
                market_analysis=market_data,
                news_analysis=news_data
            )
            cache[cache_key] = response
            logger.info(f"分析股票 {stock_id} 完成")
            return response
        except Exception as e:
            logger.error(f"分析股票 {query} 失敗: {str(e)}\n{traceback.format_exc()}")
            raise

    async def chat(self, query: str) -> str:
        try:
            cache_key = f"chat_{query}"
            if cache_key in cache:
                logger.info(f"Cache hit for chat {query}")
                return cache[cache_key]

            if not self.investment_advisor:
                logger.warning("XAI 不可用，無法處理問答")
                return "抱歉，XAI 服務當前不可用，無法提供完整分析。"

            retrieved_docs = await asyncio.to_thread(rag.retrieve, query)
            augmented_prompt = await asyncio.to_thread(rag.augment, query, retrieved_docs)
            graph_response = await asyncio.to_thread(graph_rag.query_graph, query)
            full_prompt = f"{augmented_prompt}\n圖資料: {graph_response}\n請生成詳細回應，包含價格預測、策略建議、風險評估、市場趨勢、投組建議和新聞分析。"
            response = await asyncio.to_thread(self.investment_advisor.run, full_prompt)
            
            if isinstance(response, dict):
                response = str(response)
            cache[cache_key] = response
            logger.info(f"問答查詢: {query}, 回應生成完成")
            return response
        except Exception as e:
            logger.error(f"問答查詢 {query} 失敗: {str(e)}\n{traceback.format_exc()}")
            return f"抱歉，處理查詢時發生錯誤: {str(e)}"

    async def recommend_portfolio(self, request: PortfolioResponse) -> Dict:
        try:
            stock_ids = [stock.stock_id for stock in request.stocks]
            cache_key = f"portfolio_{request.risk_level}_{'_'.join(stock_ids)}"
            if cache_key in cache:
                logger.info(f"Cache hit for portfolio {cache_key}")
                return cache[cache_key]

            if not self.investment_advisor:
                logger.warning("XAI 不可用，無法生成投資組合建議")
                return {"stocks": [], "risk_level": request.risk_level, "message": "XAI 服務不可用"}

            tasks = [self.analyze_stock(f"請分析股票 {stock_id}") for stock_id in stock_ids]
            results = await asyncio.gather(*tasks)

            weights = self._allocate_weights(results, request.risk_level)
            portfolio = {
                "stocks": [
                    {"stock_id": stock_id, "weight": weight, "predicted_return": result.predictions.get("Prediction", 0.0)}
                    for stock_id, weight, result in zip(stock_ids, weights, results)
                ],
                "risk_level": request.risk_level
            }
            cache[cache_key] = portfolio
            logger.info(f"投資組合建議生成完成: {stock_ids}")
            return portfolio
        except Exception as e:
            logger.error(f"生成投資組合建議失敗: {str(e)}\n{traceback.format_exc()}")
            raise

    def _allocate_weights(self, results: List[AgentResponse], risk_level: str) -> List[float]:
        volatilities = [result.risks.get("Volatility", 0.0) for result in results]
        total_vol = sum(volatilities)
        if total_vol == 0:
            return [1.0 / len(results)] * len(results)

        if risk_level == "low":
            weights = [1 - (v / total_vol) for v in volatilities]
        elif risk_level == "high":
            weights = [v / total_vol for v in volatilities]
        else:  # medium
            weights = [1.0 / len(results)] * len(results)

        total_weight = sum(weights)
        return [w / total_weight for w in weights] if total_weight > 0 else weights

agent_controller = AgentController()