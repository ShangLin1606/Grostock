import pandas as pd
import numpy as np
from loguru import logger
import backtrader as bt
from datetime import datetime, timedelta

class TradingStrategies:
    def __init__(self, prices, indicators, benchmark="0050"):
        self.prices = prices
        self.indicators = indicators
        self.benchmark = benchmark

    def momentum_breakout(self):
        sma_50 = self.indicators["SMA_20"].rolling(window=50).mean()
        signals = np.where(self.prices > sma_50, 1, 0)
        return signals

    def mean_reversion(self):
        rsi = self.indicators["RSI_14"]
        signals = np.where(rsi < 30, 1, np.where(rsi > 70, -1, 0))
        return signals

    def volatility_arbitrage(self):
        atr = self.indicators["ATR_14"]
        signals = np.where(atr > atr.mean() + atr.std(), 1, 0)
        return signals

    def multi_factor(self, size_factor, value_factor):
        momentum = self.momentum_breakout()
        size_score = size_factor / size_factor.max()
        value_score = value_factor / value_factor.max()
        combined_score = 0.4 * momentum + 0.3 * size_score + 0.3 * value_score
        signals = np.where(combined_score > 0.5, 1, 0)
        return signals

    def hedging_strategy(self, beta):
        signals = np.where(self.prices.pct_change() > 0, -beta, beta)
        return signals

    def dynamic_adjust(self, signals, volatility):
        adjustment = 1 if volatility < 0.1 else 0.5 if volatility < 0.2 else 0
        return signals * adjustment

    def backtest_strategy(self, strategy_signals, start_date, end_date):
        """使用 Backtrader 回測策略"""
        class Strategy(bt.Strategy):
            def __init__(self):
                self.signals = strategy_signals
                self.position_size = 100000

            def next(self):
                date = self.datas[0].datetime.date(0).isoformat()
                if date in self.signals.index:
                    signal = self.signals.loc[date]
                    if signal > 0 and not self.position:
                        self.buy(size=self.position_size // self.data.close[0])
                    elif signal < 0 and self.position:
                        self.sell(size=self.position.size)

        cerebro = bt.Cerebro()
        data = bt.feeds.PandasData(dataname=self.prices.to_frame(name="close"), fromdate=start_date, todate=end_date)
        cerebro.adddata(data)
        cerebro.addstrategy(Strategy)
        cerebro.broker.set_cash(100000)
        cerebro.run()

        final_value = cerebro.broker.getvalue()
        returns = (final_value - 100000) / 100000
        benchmark_returns = (self.prices.iloc[-1] - self.prices.iloc[0]) / self.prices.iloc[0]
        logger.info(f"策略報酬率: {returns:.2%}, 大盤報酬率: {benchmark_returns:.2%}")
        return returns, benchmark_returns

    def ml_strategy(self, prediction, volatility):
        base_signal = np.where(prediction > self.prices.iloc[-1], 1, -1)
        adjusted_signal = self.dynamic_adjust(base_signal, volatility)
        return adjusted_signal