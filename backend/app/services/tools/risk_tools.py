import numpy as np

def calc_sharpe(returns):
    return np.mean(returns) / np.std(returns) * np.sqrt(252)

def calc_sortino(returns):
    downside = returns[returns < 0]
    return np.mean(returns) / np.std(downside) * np.sqrt(252)

def calc_max_drawdown(equity_curve):
    roll_max = np.maximum.accumulate(equity_curve)
    drawdown = (equity_curve - roll_max) / roll_max
    return drawdown.min()

def calc_var(returns, confidence=0.95):
    return np.percentile(returns, (1-confidence)*100)
