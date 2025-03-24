from ai_models import ai_models
from risk_indicators import RiskIndicators
from trading_strategies import TradingStrategies
from database import db
import pandas as pd
import torch
from loguru import logger
import requests
from bs4 import BeautifulSoup
import datetime as dt
import numpy as np

class AgentTools:
    def __init__(self):
        self.conn = db.connect_postgres()
        self.mongo_db = db.connect_mongo()

    def get_stock_data(self, stock_id):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT date, close_price, sma_20, ema_20, rsi_14, macd, macd_signal, macd_hist,
                   bb_upper, bb_mid, bb_lower, atr_14, stochastic_k, stochastic_d, cci_20, adx_14, obv
            FROM technical_indicators WHERE stock_id = %s ORDER BY date;
        """, (stock_id,))
        rows = cursor.fetchall()
        df = pd.DataFrame(rows, columns=["date", "close_price", "sma_20", "ema_20", "rsi_14", "macd", "macd_signal", "macd_hist",
                                         "bb_upper", "bb_mid", "bb_lower", "atr_14", "stochastic_k", "stochastic_d", "cci_20", "adx_14", "obv"])
        df.set_index("date", inplace=True)
        cursor.close()
        return df

    def predict_price(self, stock_id):
        df = self.get_stock_data(stock_id)
        features = df[["sma_20", "ema_20", "rsi_14", "macd", "macd_signal", "macd_hist",
                       "bb_upper", "bb_mid", "bb_lower", "atr_14", "stochastic_k", "stochastic_d", "cci_20", "adx_14", "obv"]]
        data = torch.tensor(features.values, dtype=torch.float32).unsqueeze(0)
        ai_models.train_lstm(data)
        lstm_pred = ai_models.predict(data, "lstm")[0]
        transformer_pred = ai_models.predict(data, "transformer")[0]
        gan_pred = ai_models.predict(data, "gan")[0]
        return {"LSTM": float(lstm_pred), "Transformer": float(transformer_pred), "GAN": float(gan_pred)}

    def generate_strategy(self, stock_id):
        df = self.get_stock_data(stock_id)
        strategies = TradingStrategies(df["close_price"], df)
        momentum = strategies.momentum_breakout()[-1]
        mean_reversion = strategies.mean_reversion()[-1]
        volatility = strategies.volatility_arbitrage()[-1]
        returns = df["close_price"].pct_change().dropna()
        lstm_pred = self.predict_price(stock_id)["LSTM"]
        transformer_pred = self.predict_price(stock_id)["Transformer"]
        gan_pred = self.predict_price(stock_id)["GAN"]
        lstm_signal = strategies.lstm_strategy(lstm_pred)[-1]
        transformer_signal = strategies.transformer_strategy(transformer_pred)[-1]
        gan_signal = strategies.gan_strategy(gan_pred)[-1]
        optimized_signals = strategies.rlhf_optimize(np.array([lstm_signal, transformer_signal, gan_signal]), returns)
        return {
            "Momentum": int(momentum),
            "Mean_Reversion": int(mean_reversion),
            "Volatility": int(volatility),
            "LSTM": int(optimized_signals[0]),
            "Transformer": int(optimized_signals[1]),
            "GAN": int(optimized_signals[2])
        }

    def assess_risk(self, stock_id):
        df = self.get_stock_data(stock_id)
        returns = df["close_price"].pct_change().dropna()
        risk_calc = RiskIndicators(returns)
        return risk_calc.compute_all()

    def analyze_market(self):
        """獲取當天市場新聞懶人包"""
        today = dt.datetime.now().date().isoformat()
        news = self.mongo_db["news"].find({"date": today}).limit(5)
        market_summary = []
        for item in news:
            market_summary.append(f"標題: {item['title']}\n摘要: {item['summary']}\n情緒: {item['sentiment']['label']}")
        
        # 爬取即時市場指數（例如台股大盤）
        url = "https://tw.stock.yahoo.com/quote/^TWII"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        index_value = soup.find("span", class_="Fz(32px)")  # 假設這是大盤指數的標籤
        market_index = f"台股大盤指數: {index_value.text if index_value else '無法獲取'}" if response.status_code == 200 else "無法獲取大盤指數"
        
        return {
            "market_index": market_index,
            "news_summary": "\n\n".join(market_summary)
        }

agent_tools = AgentTools()