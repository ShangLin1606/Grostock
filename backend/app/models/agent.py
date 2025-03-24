from pydantic import BaseModel
from typing import Dict

class Prediction(BaseModel):
    stock_id: str
    date: str
    lstm_pred: float
    transformer_pred: float
    gan_pred: float

class Strategy(BaseModel):
    stock_id: str
    date: str
    momentum_signal: int
    mean_reversion_signal: int
    volatility_signal: int
    lstm_signal: int
    transformer_signal: int
    gan_signal: int

class Risk(BaseModel):
    stock_id: str
    date: str
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    var_95: float
    cvar_95: float
    volatility: float
    downside_deviation: float
    upside_potential: float
    omega_ratio: float
    treynor_ratio: float
    information_ratio: float
    beta: float
    alpha: float
    tracking_error: float
    sterling_ratio: float
    calmar_ratio: float
    ulcer_index: float
    pain_index: float
    recovery_time: int

class AgentResponse(BaseModel):
    predictions: Dict[str, float]
    strategies: Dict[str, int]
    risks: Dict[str, float]