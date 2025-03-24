from pydantic import BaseModel
from typing import Optional, List, Dict
import datetime

class Stock(BaseModel):
    stock_id: str
    stock_name: str

class StockPrice(BaseModel):
    stock_id: str
    date: datetime.date
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: int

class TechnicalIndicator(BaseModel):
    stock_id: str
    date: datetime.date
    sma_20: Optional[float]
    ema_20: Optional[float]
    rsi_14: Optional[float]
    macd: Optional[float]
    macd_signal: Optional[float]
    macd_hist: Optional[float]
    bb_upper: Optional[float]
    bb_mid: Optional[float]
    bb_lower: Optional[float]
    atr_14: Optional[float]
    stochastic_k: Optional[float]
    stochastic_d: Optional[float]
    cci_20: Optional[float]
    adx_14: Optional[float]
    obv: Optional[int]