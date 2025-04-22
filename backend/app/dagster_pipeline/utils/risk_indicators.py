import pandas as pd
import numpy as np
from loguru import logger

class RiskIndicators:
    def __init__(self, returns, benchmark_returns):
        self.returns = returns
        self.benchmark_returns = benchmark_returns

    def sharpe_ratio(self, rf_rate=0.01):
        excess_returns = self.returns - rf_rate / 252
        return np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252)

    def sortino_ratio(self, rf_rate=0.01):
        downside_returns = self.returns[self.returns < 0]
        return (np.mean(self.returns) - rf_rate / 252) / np.std(downside_returns) * np.sqrt(252)

    def max_drawdown(self):
        cumulative = (1 + self.returns).cumprod()
        peak = cumulative.cummax()
        drawdown = (cumulative - peak) / peak
        return drawdown.min()

    def var(self, confidence=0.95):
        return np.percentile(self.returns, (1 - confidence) * 100)

    def cvar(self, confidence=0.95):
        var = self.var(confidence)
        return self.returns[self.returns <= var].mean()

    def volatility(self):
        return self.returns.std() * np.sqrt(252)

    def beta(self):
        covariance = np.cov(self.returns, self.benchmark_returns)[0, 1]
        benchmark_variance = self.benchmark_returns.var()
        return covariance / benchmark_variance

    def alpha(self, rf_rate=0.01):
        sharpe = self.sharpe_ratio(rf_rate)
        benchmark_sharpe = np.mean(self.benchmark_returns - rf_rate / 252) / np.std(self.benchmark_returns) * np.sqrt(252)
        return sharpe - self.beta() * benchmark_sharpe

    def compute_all(self):
        return {
            "Sharpe_Ratio": self.sharpe_ratio(),
            "Sortino_Ratio": self.sortino_ratio(),
            "Max_Drawdown": self.max_drawdown(),
            "VaR_95": self.var(0.95),
            "CVaR_95": self.cvar(0.95),
            "Volatility": self.volatility(),
            "Beta": self.beta(),
            "Alpha": self.alpha(),
            "Downside_Deviation": self.returns[self.returns < 0].std() * np.sqrt(252)
        }