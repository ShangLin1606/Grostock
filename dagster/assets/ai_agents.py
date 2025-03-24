from dagster import asset
from phidata.agent import Agent, Tool
from ..utils.agent_tools import agent_tools
from ..utils.database import db
from loguru import logger
import os
from dotenv import load_dotenv
import pandas as pd
import asyncio

load_dotenv()

# 工具定義
price_tool = Tool(name="predict_price", description="預測股票價格", func=agent_tools.predict_price)
strategy_tool = Tool(name="generate_strategy", description="生成交易策略", func=agent_tools.generate_strategy)
risk_tool = Tool(name="assess_risk", description="評估風險", func=agent_tools.assess_risk)
market_tool = Tool(name="analyze_market", description="分析當天市場趨勢與新聞", func=agent_tools.analyze_market)

# 子 Agent
price_agent = Agent(
    name="PricePredictor",
    description="負責預測股價",
    llm="xai",
    api_key=os.getenv("XAI_API_KEY"),
    tools=[price_tool]
)

strategy_agent = Agent(
    name="StrategyGenerator",
    description="負責生成交易策略",
    llm="xai",
    api_key=os.getenv("XAI_API_KEY"),
    tools=[strategy_tool]
)

risk_agent = Agent(
    name="RiskAssessor",
    description="負責評估風險",
    llm="xai",
    api_key=os.getenv("XAI_API_KEY"),
    tools=[risk_tool]
)

market_agent = Agent(
    name="MarketAnalysisAgent",
    description="負責分析當天市場趨勢與新聞",
    llm="xai",
    api_key=os.getenv("XAI_API_KEY"),
    tools=[market_tool]
)

# 主 Agent 系統提示（Prompt Engineering）
system_prompt = """
你是一位專業的 AI 股票投資顧問，只能回答與股票、股市或市場相關的問題。
如果用戶問非相關問題，請回應：「抱歉，我只能回答與股票或市場相關的問題，請問您有什麼關於股票的疑問嗎？」
當用戶要求當天市場消息懶人包時，請調用 MarketAnalysisAgent 並整合結果。
回答時請保持專業、簡潔，並提供數據支持。
"""

investment_advisor = Agent(
    name="InvestmentAdvisor",
    description="AI 股票投資顧問",
    llm="xai",
    api_key=os.getenv("XAI_API_KEY"),
    system_prompt=system_prompt,
    tools=[price_tool, strategy_tool, risk_tool, market_tool],
    sub_agents=[price_agent, strategy_agent, risk_agent, market_agent]
)

@asset(deps=["technical_features"])
async def ai_agents(technical_features):
    conn = db.connect_postgres()
    cursor = conn.cursor()

    # 創建表格
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            stock_id VARCHAR(10),
            date DATE,
            lstm_pred FLOAT,
            transformer_pred FLOAT,
            gan_pred FLOAT,
            PRIMARY KEY (stock_id, date)
        );
        CREATE TABLE IF NOT EXISTS strategies (
            stock_id VARCHAR(10),
            date DATE,
            momentum_signal INT,
            mean_reversion_signal INT,
            volatility_signal INT,
            lstm_signal INT,
            transformer_signal INT,
            gan_signal INT,
            PRIMARY KEY (stock_id, date)
        );
        CREATE TABLE IF NOT EXISTS risks (
            stock_id VARCHAR(10),
            date DATE,
            sharpe_ratio FLOAT, sortino_ratio FLOAT, max_drawdown FLOAT,
            var_95 FLOAT, cvar_95 FLOAT, volatility FLOAT,
            downside_deviation FLOAT, upside_potential FLOAT, omega_ratio FLOAT,
            treynor_ratio FLOAT, information_ratio FLOAT, beta FLOAT,
            alpha FLOAT, tracking_error FLOAT, sterling_ratio FLOAT,
            calmar_ratio FLOAT, ulcer_index FLOAT, pain_index FLOAT,
            recovery_time INT,
            PRIMARY KEY (stock_id, date)
        );
    """)

    cursor.execute("SELECT DISTINCT stock_id FROM technical_indicators;")
    stock_ids = [row[0] for row in cursor.fetchall()]
    latest_date = pd.Timestamp.now().date()

    # 非同步處理
    async def process_stock(stock_id):
        price_result = await asyncio.to_thread(price_agent.run, f"請預測股票 {stock_id} 的未來價格")
        strategy_result = await asyncio.to_thread(strategy_agent.run, f"請生成股票 {stock_id} 的交易策略")
        risk_result = await asyncio.to_thread(risk_agent.run, f"請評估股票 {stock_id} 的風險")

        price_data = eval(price_result) if isinstance(price_result, str) else price_result
        strategy_data = eval(strategy_result) if isinstance(strategy_result, str) else strategy_result
        risk_data = eval(risk_result) if isinstance(risk_result, str) else risk_result

        cursor.execute("""
            INSERT INTO predictions (stock_id, date, lstm_pred, transformer_pred, gan_pred)
            VALUES (%s, %s, %s, %s, %s) ON CONFLICT (stock_id, date) DO NOTHING;
        """, (stock_id, latest_date, price_data["LSTM"], price_data["Transformer"], price_data["GAN"]))

        cursor.execute("""
            INSERT INTO strategies (stock_id, date, momentum_signal, mean_reversion_signal, volatility_signal,
                                   lstm_signal, transformer_signal, gan_signal)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (stock_id, date) DO NOTHING;
        """, (stock_id, latest_date, strategy_data["Momentum"], strategy_data["Mean_Reversion"], strategy_data["Volatility"],
              strategy_data["LSTM"], strategy_data["Transformer"], strategy_data["GAN"]))

        cursor.execute("""
            INSERT INTO risks (stock_id, date, sharpe_ratio, sortino_ratio, max_drawdown,
                              var_95, cvar_95, volatility, downside_deviation, upside_potential, omega_ratio,
                              treynor_ratio, information_ratio, beta, alpha, tracking_error, sterling_ratio,
                              calmar_ratio, ulcer_index, pain_index, recovery_time)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (stock_id, date) DO NOTHING;
        """, (stock_id, latest_date, risk_data["Sharpe_Ratio"], risk_data["Sortino_Ratio"], risk_data["Max_Drawdown"],
              risk_data["VaR_95"], risk_data["CVaR_95"], risk_data["Volatility"], risk_data["Downside_Deviation"],
              risk_data["Upside_Potential"], risk_data["Omega_Ratio"], risk_data["Treynor_Ratio"], risk_data["Information_Ratio"],
              risk_data["Beta"], risk_data["Alpha"], risk_data["Tracking_Error"], risk_data["Sterling_Ratio"],
              risk_data["Calmar_Ratio"], risk_data["Ulcer_Index"], risk_data["Pain_Index"], risk_data["Recovery_Time"]))

    tasks = [process_stock(stock_id) for stock_id in stock_ids[:10]]  # 先處理前 10 檔
    await asyncio.gather(*tasks)

    conn.commit()
    cursor.close()
    conn.close()
    logger.info("AI Agent 每日更新完成")