from app.dagster_pipeline.utils.ai_models import AIModels
from app.dagster_pipeline.utils.risk_indicators import RiskIndicators
from app.dagster_pipeline.utils.trading_strategies import TradingStrategies
from app.dagster_pipeline.utils.technical_indicators import TechnicalIndicators
from app.dagster_pipeline.utils.database import db
from app.controllers.stock_controller import stock_controller
import pandas as pd
import torch
from loguru import logger
import datetime as dt
import numpy as np

class AgentTools:
    def __init__(self):
        self.conn = db.connect_postgres()
        self.mongo_db = db.connect_mongo()

    def get_stock_data(self, stock_id):
        """獲取單一股票的技術指標資料"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT date, close_price, sma_20, ema_20, rsi_14, macd, macd_signal, macd_hist,
                   bb_upper, bb_mid, bb_lower, atr_14, stochastic_k, stochastic_d, cci_20, adx_14, obv
            FROM technical_indicators WHERE stock_id = %s ORDER BY date;
        """, (stock_id,))
        rows = cursor.fetchall()
        if not rows:
            logger.warning(f"股票 {stock_id} 的技術指標資料不存在")
            return pd.DataFrame()
        df = pd.DataFrame(rows, columns=["date", "close_price", "sma_20", "ema_20", "rsi_14", "macd", "macd_signal", "macd_hist",
                                         "bb_upper", "bb_mid", "bb_lower", "atr_14", "stochastic_k", "stochastic_d", "cci_20", "adx_14", "obv"])
        df.set_index("date", inplace=True)
        cursor.close()
        return df

    def get_benchmark_data(self):
        """獲取 0050 大盤資料"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT date, close_price FROM stock_prices WHERE stock_id = '0050' ORDER BY date;
        """)
        rows = cursor.fetchall()
        if not rows:
            logger.warning("0050 大盤資料不存在")
            return pd.DataFrame()
        df = pd.DataFrame(rows, columns=["date", "close_price"])
        df.set_index("date", inplace=True)
        cursor.close()
        return df

    def predict_price(self, stock_id):
        """預測股票價格"""
        df = self.get_stock_data(stock_id)
        if df.empty:
            return {"Prediction": 0.0, "Signal": 0}
        features = df[["sma_20", "ema_20", "rsi_14", "macd", "macd_signal", "macd_hist",
                       "bb_upper", "bb_mid", "bb_lower", "atr_14", "stochastic_k", "stochastic_d", "cci_20", "adx_14", "obv"]]
        data = torch.tensor(features.values, dtype=torch.float32).unsqueeze(0)
        pred = AIModels.predict(data)[0]
        signal = 1 if pred > df["close_price"].iloc[-1] else -1
        return {"Prediction": float(pred), "Signal": int(signal)}

    def generate_strategy(self, stock_id):
        """生成交易策略"""
        df = self.get_stock_data(stock_id)
        if df.empty:
            return {
                "Momentum": 0, "Mean_Reversion": 0, "Volatility": 0, "Multi_Factor": 0, "Hedging": 0.0,
                "ML_Signal": 0, "Momentum_Returns": 0.0, "Benchmark_Returns": 0.0
            }
        benchmark_df = self.get_benchmark_data()
        prices = df["close_price"]
        indicators = TechnicalIndicators(df).compute_all()
        strategies = TradingStrategies(prices, indicators, benchmark="0050")
        
        momentum = strategies.momentum_breakout()[-1]
        mean_reversion = strategies.mean_reversion()[-1]
        volatility = strategies.volatility_arbitrage()[-1]
        multi_factor = strategies.multi_factor(df["close_price"].mean(), df["close_price"].mean() / df["close_price"].iloc[-1])
        hedging = strategies.hedging_strategy(RiskIndicators(prices.pct_change().dropna(), benchmark_df["close_price"].pct_change().dropna()).beta())
        
        returns = prices.pct_change().dropna()
        benchmark_returns = benchmark_df["close_price"].pct_change().dropna()
        volatility_val = returns.std() * np.sqrt(252)
        
        pred = self.predict_price(stock_id)["Prediction"]
        ml_signal = strategies.ml_strategy(pred, volatility_val)[-1]
        
        start_date = returns.index[0]
        end_date = returns.index[-1]
        momentum_returns, benchmark_returns_val = strategies.backtest_strategy(pd.Series(strategies.momentum_breakout(), index=returns.index), start_date, end_date)
        
        return {
            "Momentum": int(momentum),
            "Mean_Reversion": int(mean_reversion),
            "Volatility": int(volatility),
            "Multi_Factor": int(multi_factor[-1]),
            "Hedging": float(hedging[-1]),
            "ML_Signal": int(ml_signal),
            "Momentum_Returns": float(momentum_returns),
            "Benchmark_Returns": float(benchmark_returns_val)
        }

    def assess_risk(self, stock_id):
        """評估股票風險"""
        df = self.get_stock_data(stock_id)
        if df.empty:
            return {key: 0.0 for key in ["Sharpe_Ratio", "Sortino_Ratio", "Max_Drawdown", "VaR_95", "CVaR_95", "Volatility", "Downside_Deviation", "Beta", "Alpha"]}
        benchmark_df = self.get_benchmark_data()
        returns = df["close_price"].pct_change().dropna()
        benchmark_returns = benchmark_df["close_price"].pct_change().dropna()
        risk_calc = RiskIndicators(returns, benchmark_returns)
        return risk_calc.compute_all()

    def analyze_market(self):
        """分析市場趨勢與新聞，返回字串"""
        today = dt.datetime.now().date().isoformat()
        news = list(self.mongo_db["market_news"].find({"date": today}).limit(5))
        if not news:
            return "今日無市場新聞"
        market_summary = "\n\n".join([f"類別: {item['category']}\n標題: {item['title']}\n摘要: {item['summary']}\n情緒: {item['sentiment']['label']}" for item in news])
        return market_summary

    def generate_portfolio(self, stock_ids: list):
        """生成投組建議"""
        weights = {}
        for stock_id in stock_ids:
            df = self.get_stock_data(stock_id)
            if df.empty:
                weights[stock_id] = 0.0
                continue
            returns = df["close_price"].pct_change().dropna()
            risk = RiskIndicators(returns).compute_all()
            sharpe_ratio = risk["Sharpe_Ratio"]
            weights[stock_id] = sharpe_ratio if sharpe_ratio > 0 else 0
        
        total_weight = sum(weights.values())
        if total_weight > 0:
            normalized_weights = {k: v / total_weight for k, v in weights.items()}
        else:
            normalized_weights = {k: 1 / len(stock_ids) for k in stock_ids}
        
        return {"portfolio_weights": normalized_weights}

    def analyze_news(self, stock_id):
        """分析與股票相關的新聞"""
        news = list(self.mongo_db["market_news"].find({"stock_id": stock_id}).limit(5))
        analysis = "\n\n".join([f"日期: {item['date']}\n標題: {item['title']}\n摘要: {item['summary']}\n情緒: {item['sentiment']['label']}" for item in news])
        return {"news_analysis": analysis if analysis else "無相關新聞"}

agent_tools = AgentTools()