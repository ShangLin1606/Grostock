import numpy as np
import pandas as pd

def simple_backtest(prices: pd.Series, window: int = 20):
    """簡單均線策略回測"""
    signal = prices.rolling(window).mean()
    position = (prices > signal).astype(int)
    daily_ret = prices.pct_change().fillna(0)
    strategy_ret = daily_ret * position.shift(1)
    cum_return = (1 + strategy_ret).cumprod() - 1
    sharpe = np.mean(strategy_ret) / np.std(strategy_ret) * np.sqrt(252)
    return {"CAGR": cum_return.iloc[-1], "Sharpe": sharpe}

def optimize_portfolio(returns: pd.DataFrame):
    """最簡化資產配置（平均分配）"""
    weights = np.ones(returns.shape[1]) / returns.shape[1]
    port_ret = np.dot(returns.mean(), weights) * 252
    port_vol = np.sqrt(np.dot(weights.T, np.dot(returns.cov() * 252, weights)))
    sharpe = port_ret / port_vol
    return {"annual_ret": port_ret, "volatility": port_vol, "Sharpe": sharpe, "weights": weights.tolist()}
