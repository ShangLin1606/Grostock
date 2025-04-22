from dagster import asset
from phi.agent import Agent
from phi.model.xai import xAI
from app.dagster_pipeline.utils.agent_tools import agent_tools
from app.dagster_pipeline.utils.database import db
from app.dagster_pipeline.utils.agent_tools import AIModels
from loguru import logger
import os
from dotenv import load_dotenv
import torch
import pandas as pd
import asyncio

load_dotenv()

xai_model = xAI(id="grok-beta", api_key=os.getenv("XAI_API_KEY"))

price_agent = Agent(name="PricePredictor", model=xai_model, description="提供股票價格預測與漲跌信號")
strategy_agent = Agent(name="StrategyGenerator", model=xai_model, description="提供交易策略與報酬率分析")
risk_agent = Agent(name="RiskAssessor", model=xai_model, description="提供風險管理分析")
market_agent = Agent(name="MarketAnalysisAgent", model=xai_model, description="提供市場趨勢與新聞分析")

system_prompt = """
你是一位專業的 AI 股票投資顧問，只能回答與股票、股市或市場相關的問題。
若問題超出範圍，回應：「抱歉，我只能回答與股票或市場相關的問題，請問您有什麼關於股票的疑問嗎？」
根據用戶查詢，從資料庫提取預計算結果，整合子代理回應並提供建議。
若檢測到需要更新模型或策略，觸發重新訓練。
"""
investment_advisor = Agent(
    name="InvestmentAdvisor",
    model=xai_model,
    system_prompt=system_prompt,
    sub_agents=[price_agent, strategy_agent, risk_agent, market_agent],
    description="AI 股票投資顧問，整合結果並管理模型與策略更新"
)

@asset(deps=["technical_features"])
async def ai_agents(technical_features):
    conn = db.connect_postgres()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            stock_id VARCHAR(10),
            date DATE,
            prediction FLOAT,
            signal INT,
            PRIMARY KEY (stock_id, date)
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS strategies (
            stock_id VARCHAR(10),
            date DATE,
            momentum_signal INT,
            mean_reversion_signal INT,
            volatility_signal INT,
            multi_factor_signal INT,
            hedging_signal FLOAT,
            ml_signal INT,
            momentum_returns FLOAT,
            benchmark_returns FLOAT,
            PRIMARY KEY (stock_id, date)
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS risks (
            stock_id VARCHAR(10),
            date DATE,
            sharpe_ratio FLOAT, sortino_ratio FLOAT, max_drawdown FLOAT,
            var_95 FLOAT, cvar_95 FLOAT, volatility FLOAT,
            downside_deviation FLOAT, beta FLOAT, alpha FLOAT,
            PRIMARY KEY (stock_id, date)
        );
    """)

    cursor.execute("SELECT DISTINCT stock_id FROM technical_indicators;")
    stock_ids = [row[0] for row in cursor.fetchall()]
    latest_date = pd.Timestamp.now().date()

    async def process_stock(stock_id):
        df = agent_tools.get_stock_data(stock_id)
        if AIModels.should_retrain(df):
            data = torch.tensor(df[["sma_20", "ema_20", "rsi_14", "macd", "macd_signal", "macd_hist",
                                    "bb_upper", "bb_mid", "bb_lower", "atr_14", "stochastic_k", "stochastic_d", 
                                    "cci_20", "adx_14", "obv"]].values, dtype=torch.float32).unsqueeze(0)
            await asyncio.to_thread(AIModels.train_initial, data)
            logger.info(f"已為 {stock_id} 更新模型")

        price_result = agent_tools.predict_price(stock_id)
        strategy_result = agent_tools.generate_strategy(stock_id)
        risk_result = agent_tools.assess_risk(stock_id)

        cursor.execute("""
            INSERT INTO predictions (stock_id, date, prediction, signal)
            VALUES (%s, %s, %s, %s) ON CONFLICT (stock_id, date) DO NOTHING;
        """, (stock_id, latest_date, price_result["Prediction"], price_result["Signal"]))

        cursor.execute("""
            INSERT INTO strategies (stock_id, date, momentum_signal, mean_reversion_signal, volatility_signal,
                                   multi_factor_signal, hedging_signal, ml_signal, momentum_returns, benchmark_returns)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (stock_id, date) DO NOTHING;
        """, (stock_id, latest_date, strategy_result["Momentum"], strategy_result["Mean_Reversion"], strategy_result["Volatility"],
              strategy_result["Multi_Factor"], strategy_result["Hedging"], strategy_result["ML_Signal"],
              strategy_result["Momentum_Returns"], strategy_result["Benchmark_Returns"]))

        cursor.execute("""
            INSERT INTO risks (stock_id, date, sharpe_ratio, sortino_ratio, max_drawdown,
                              var_95, cvar_95, volatility, downside_deviation, beta, alpha)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (stock_id, date) DO NOTHING;
        """, (stock_id, latest_date, risk_result["Sharpe_Ratio"], risk_result["Sortino_Ratio"], risk_result["Max_Drawdown"],
              risk_result["VaR_95"], risk_result["CVaR_95"], risk_result["Volatility"], risk_result["Downside_Deviation"],
              risk_result["Beta"], risk_result["Alpha"]))

    tasks = [process_stock(stock_id) for stock_id in stock_ids[:10]]
    await asyncio.gather(*tasks)

    conn.commit()
    cursor.close()
    conn.close()
    logger.info("AI Agent 每日更新完成")