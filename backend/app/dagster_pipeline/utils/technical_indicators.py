import pandas as pd
import numpy as np
from loguru import logger

class TechnicalIndicators:
    def __init__(self, df):
        self.df = df.copy()
        self.close = df["close_price"]
        self.high = df["high_price"]
        self.low = df["low_price"]
        self.volume = df["volume"]
        self.volatility = self.close.pct_change().std() * np.sqrt(252)

    def sma(self, period=None):
        period = int(20 * (1 + self.volatility)) if period is None else period  # 動態調整窗口
        return self.close.rolling(window=period).mean()

    def ema(self, period=None):
        period = int(20 * (1 + self.volatility)) if period is None else period
        return self.close.ewm(span=period, adjust=False).mean()

    def rsi(self, period=14):
        delta = self.close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def macd(self, fast=12, slow=26, signal=9):
        ema_fast = self.ema(fast)
        ema_slow = self.ema(slow)
        macd = ema_fast - ema_slow
        signal_line = macd.ewm(span=signal, adjust=False).mean()
        hist = macd - signal_line
        return macd, signal_line, hist

    def bollinger_bands(self, period=None, std_dev=2):
        period = int(20 * (1 + self.volatility)) if period is None else period
        sma = self.sma(period)
        std = self.close.rolling(window=period).std()
        upper = sma + (std * std_dev)
        lower = sma - (std * std_dev)
        return upper, sma, lower

    def atr(self, period=14):
        tr = pd.concat([
            self.high - self.low,
            (self.high - self.close.shift()).abs(),
            (self.low - self.close.shift()).abs()
        ], axis=1).max(axis=1)
        return tr.rolling(window=period).mean()

    def stochastic_oscillator(self, k_period=14, d_period=3):
        lowest_low = self.low.rolling(window=k_period).min()
        highest_high = self.high.rolling(window=k_period).max()
        k = 100 * (self.close - lowest_low) / (highest_high - lowest_low)
        d = k.rolling(window=d_period).mean()
        return k, d

    def cci(self, period=20):
        typical_price = (self.high + self.low + self.close) / 3
        sma_tp = typical_price.rolling(window=period).mean()
        mean_dev = typical_price.rolling(window=period).apply(lambda x: np.mean(np.abs(x - np.mean(x))))
        return (typical_price - sma_tp) / (0.015 * mean_dev)

    def adx(self, period=14):
        plus_dm = self.high.diff().where(lambda x: x > 0, 0)
        minus_dm = -self.low.diff().where(lambda x: x < 0, 0)
        tr = self.atr(period)
        plus_di = 100 * (plus_dm.ewm(span=period, adjust=False).mean() / tr)
        minus_di = 100 * (minus_dm.ewm(span=period, adjust=False).mean() / tr)
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        return dx.ewm(span=period, adjust=False).mean()

    def obv(self):
        direction = np.where(self.close.diff() > 0, 1, np.where(self.close.diff() < 0, -1, 0))
        return (direction * self.volume).cumsum()

    def compute_all(self):
        macd, macd_signal, macd_hist = self.macd()
        bb_upper, bb_mid, bb_lower = self.bollinger_bands()
        stochastic_k, stochastic_d = self.stochastic_oscillator()
        return {
            "SMA_20": self.sma(),
            "EMA_20": self.ema(),
            "RSI_14": self.rsi(14),
            "MACD": macd,
            "MACD_Signal": macd_signal,
            "MACD_Hist": macd_hist,
            "BB_Upper": bb_upper,
            "BB_Mid": bb_mid,
            "BB_Lower": bb_lower,
            "ATR_14": self.atr(14),
            "Stochastic_K": stochastic_k,
            "Stochastic_D": stochastic_d,
            "CCI_20": self.cci(20),
            "ADX_14": self.adx(14),
            "OBV": self.obv()
        }