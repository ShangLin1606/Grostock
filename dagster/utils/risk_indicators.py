import numpy as np
import pandas as pd
from loguru import logger

class RiskIndicators:
    def __init__(self, returns):
        self.returns = returns  # 日報酬率序列

    def sharpe_ratio(self, risk_free_rate=0.01):
        """夏普比率"""
        return (self.returns.mean() - risk_free_rate) / self.returns.std()

    def sortino_ratio(self, risk_free_rate=0.01):
        """索提諾比率"""
        downside_risk = self.returns[self.returns < 0].std()
        return (self.returns.mean() - risk_free_rate) / downside_risk

    def max_drawdown(self):
        """最大回撤"""
        cum_returns = (1 + self.returns).cumprod()
        peak = cum_returns.cummax()
        drawdown = (cum_returns - peak) / peak
        return drawdown.min()

    def var(self, confidence_level=0.95):
        """價值-at-風險 (VaR)"""
        return np.percentile(self.returns, (1 - confidence_level) * 100)

    def cvar(self, confidence_level=0.95):
        """條件價值-at-風險 (CVaR)"""
        var = self.var(confidence_level)
        return self.returns[self.returns <= var].mean()

    def volatility(self):
        """波動率"""
        return self.returns.std()

    def downside_deviation(self):
        """下行偏差"""
        return self.returns[self.returns < 0].std()

    def upside_potential(self):
        """上行潛力"""
        return self.returns[self.returns > 0].mean()

    def omega_ratio(self, threshold=0):
        """歐米伽比率"""
        excess = self.returns - threshold
        return excess[excess > 0].sum() / -excess[excess < 0].sum()

    def treynor_ratio(self, beta, risk_free_rate=0.01):
        """特雷諾比率"""
        return (self.returns.mean() - risk_free_rate) / beta

    def information_ratio(self, benchmark_returns):
        """資訊比率"""
        excess_returns = self.returns - benchmark_returns
        return excess_returns.mean() / excess_returns.std()

    def beta(self, benchmark_returns):
        """貝塔係數"""
        covariance = np.cov(self.returns, benchmark_returns)[0, 1]
        return covariance / benchmark_returns.var()

    def alpha(self, benchmark_returns, risk_free_rate=0.01):
        """阿爾法係數"""
        beta = self.beta(benchmark_returns)
        return self.returns.mean() - (risk_free_rate + beta * (benchmark_returns.mean() - risk_free_rate))

    def tracking_error(self, benchmark_returns):
        """追蹤誤差"""
        return (self.returns - benchmark_returns).std()

    def sterling_ratio(self, avg_drawdown):
        """斯特林比率"""
        return self.returns.mean() / abs(avg_drawdown)

    def calmar_ratio(self):
        """卡爾馬比率"""
        return self.returns.mean() / abs(self.max_drawdown())

    def ulcer_index(self):
        """潰瘍指數"""
        cum_returns = (1 + self.returns).cumprod()
        peak = cum_returns.cummax()
        drawdown = (cum_returns - peak) / peak
        return np.sqrt(np.mean(drawdown**2))

    def pain_index(self):
        """痛苦指數"""
        cum_returns = (1 + self.returns).cumprod()
        peak = cum_returns.cummax()
        drawdown = (cum_returns - peak) / peak
        return drawdown.mean()

    def recovery_time(self):
        """恢復時間"""
        cum_returns = (1 + self.returns).cumprod()
        peak = cum_returns.cummax()
        drawdown = (cum_returns - peak) / peak
        return (drawdown < 0).sum()

    def compute_all(self, benchmark_returns=None):
        """計算所有風險指標"""
        benchmark = benchmark_returns if benchmark_returns is not None else pd.Series(np.zeros(len(self.returns)))
        beta = self.beta(benchmark)
        indicators = {
            "Sharpe_Ratio": self.sharpe_ratio(),
            "Sortino_Ratio": self.sortino_ratio(),
            "Max_Drawdown": self.max_drawdown(),
            "VaR_95": self.var(0.95),
            "CVaR_95": self.cvar(0.95),
            "Volatility": self.volatility(),
            "Downside_Deviation": self.downside_deviation(),
            "Upside_Potential": self.upside_potential(),
            "Omega_Ratio": self.omega_ratio(),
            "Treynor_Ratio": self.treynor_ratio(beta),
            "Information_Ratio": self.information_ratio(benchmark),
            "Beta": beta,
            "Alpha": self.alpha(benchmark),
            "Tracking_Error": self.tracking_error(benchmark),
            "Sterling_Ratio": self.sterling_ratio(self.max_drawdown()),
            "Calmar_Ratio": self.calmar_ratio(),
            "Ulcer_Index": self.ulcer_index(),
            "Pain_Index": self.pain_index(),
            "Recovery_Time": self.recovery_time()
        }
        logger.info("風險指標計算完成")
        return indicators