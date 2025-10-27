import numpy as np
import pandas as pd
from loguru import logger

def calculate_risk_metrics(strategy_id: str):
    """計算策略風險指標（假設輸入為歷史報酬序列）"""
    # 模擬資料（真實情況會從 DB 撈取）
    returns = np.random.normal(0.001, 0.02, 200)
    avg_ret = np.mean(returns)
    std_ret = np.std(returns)
    sharpe = avg_ret / std_ret * np.sqrt(252)
    sortino = avg_ret / np.std([r for r in returns if r < 0]) * np.sqrt(252)
    mdd = np.max(np.maximum.accumulate(returns) - returns)
    calmar = avg_ret / (mdd + 1e-6)
    var_95 = np.percentile(returns, 5)

    metrics = {
        "Sharpe": round(sharpe, 3),
        "Sortino": round(sortino, 3),
        "Calmar": round(calmar, 3),
        "MaxDrawdown": round(mdd, 3),
        "VaR_95": round(var_95, 3),
    }
    logger.info(f"策略 {strategy_id} 風險指標: {metrics}")
    return metrics

def generate_risk_report(strategy_id: str):
    """AI 文字生成報告（可串接 LLM）"""
    metrics = calculate_risk_metrics(strategy_id)
    report = (
        f"策略 {strategy_id} 風險分析報告：\n"
        f"- Sharpe: {metrics['Sharpe']}\n"
        f"- Sortino: {metrics['Sortino']}\n"
        f"- Calmar: {metrics['Calmar']}\n"
        f"- 最大回撤: {metrics['MaxDrawdown']}\n"
        f"- 95% VaR: {metrics['VaR_95']}\n"
        f"綜合判斷：策略風險控制良好，建議觀察市場波動並持續追蹤。"
    )
    return report
