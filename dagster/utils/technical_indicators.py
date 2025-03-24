import pandas as pd
import numpy as np
from loguru import logger

class TechnicalIndicators:
    def __init__(self, df):
        self.df = df  # 包含日期與收盤價的 DataFrame

    def sma(self, period=20):
        """簡單移動平均線 (Simple Moving Average)"""
        return self.df['close_price'].rolling(window=period).mean()

    def ema(self, period=20):
        """指數移動平均線 (Exponential Moving Average)"""
        return self.df['close_price'].ewm(span=period, adjust=False).mean()

    def rsi(self, period=14):
        """相對強弱指數 (Relative Strength Index)"""
        delta = self.df['close_price'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def macd(self, fast=12, slow=26, signal=9):
        """移動平均收斂發散 (MACD)"""
        ema_fast = self.ema(fast)
        ema_slow = self.ema(slow)
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line
        return macd_line, signal_line, histogram

    def bollinger_bands(self, period=20, std_dev=2):
        """布林通道 (Bollinger Bands)"""
        sma = self.sma(period)
        rolling_std = self.df['close_price'].rolling(window=period).std()
        upper_band = sma + (rolling_std * std_dev)
        lower_band = sma - (rolling_std * std_dev)
        return upper_band, sma, lower_band

    def atr(self, period=14):
        """平均真實範圍 (Average True Range)"""
        high_low = self.df['high_price'] - self.df['low_price']
        high_close = np.abs(self.df['high_price'] - self.df['close_price'].shift())
        low_close = np.abs(self.df['low_price'] - self.df['close_price'].shift())
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        return true_range.rolling(window=period).mean()

    def stochastic_oscillator(self, period=14):
        """隨機震盪指標 (Stochastic Oscillator)"""
        lowest_low = self.df['low_price'].rolling(window=period).min()
        highest_high = self.df['high_price'].rolling(window=period).max()
        k = 100 * (self.df['close_price'] - lowest_low) / (highest_high - lowest_low)
        d = k.rolling(window=3).mean()
        return k, d

    def cci(self, period=20):
        """商品通道指數 (Commodity Channel Index)"""
        tp = (self.df['high_price'] + self.df['low_price'] + self.df['close_price']) / 3
        sma_tp = tp.rolling(window=period).mean()
        mad = tp.rolling(window=period).apply(lambda x: np.mean(np.abs(x - np.mean(x))))
        return (tp - sma_tp) / (0.015 * mad)

    def adx(self, period=14):
        """平均趨向指數 (Average Directional Index)"""
        dm_plus = (self.df['high_price'] - self.df['high_price'].shift()).where(lambda x: x > 0, 0)
        dm_minus = (self.df['low_price'].shift() - self.df['low_price']).where(lambda x: x > 0, 0)
        tr = self.atr(period)
        di_plus = 100 * (dm_plus.rolling(window=period).mean() / tr)
        di_minus = 100 * (dm_minus.rolling(window=period).mean() / tr)
        dx = 100 * np.abs(di_plus - di_minus) / (di_plus + di_minus)
        return dx.rolling(window=period).mean()

    def obv(self):
        """成交量淨額 (On-Balance Volume)"""
        direction = np.where(self.df['close_price'] > self.df['close_price'].shift(), 1, 
                            np.where(self.df['close_price'] < self.df['close_price'].shift(), -1, 0))
        return (direction * self.df['volume']).cumsum()

    def compute_all(self):
        """計算所有技術指標"""
        sma_20 = self.sma(20)
        ema_20 = self.ema(20)
        rsi_14 = self.rsi(14)
        macd_line, signal_line, histogram = self.macd()
        bb_upper, bb_mid, bb_lower = self.bollinger_bands()
        atr_14 = self.atr(14)
        sto_k, sto_d = self.stochastic_oscillator()
        cci_20 = self.cci(20)
        adx_14 = self.adx(14)
        obv = self.obv()

        indicators = {
            "SMA_20": sma_20,
            "EMA_20": ema_20,
            "RSI_14": rsi_14,
            "MACD": macd_line,
            "MACD_Signal": signal_line,
            "MACD_Hist": histogram,
            "BB_Upper": bb_upper,
            "BB_Mid": bb_mid,
            "BB_Lower": bb_lower,
            "ATR_14": atr_14,
            "Stochastic_K": sto_k,
            "Stochastic_D": sto_d,
            "CCI_20": cci_20,
            "ADX_14": adx_14,
            "OBV": obv
        }
        logger.info("技術指標計算完成")
        return indicators