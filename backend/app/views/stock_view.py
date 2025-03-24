from fastapi.responses import JSONResponse
from backend.app.models.stock import Stock, StockPrice, TechnicalIndicator
from typing import List

def stock_list_view(stocks: List[Stock]) -> JSONResponse:
    return JSONResponse(content=[stock.dict() for stock in stocks])

def stock_price_view(prices: List[StockPrice]) -> JSONResponse:
    return JSONResponse(content=[price.dict() for price in prices])

def technical_indicator_view(indicators: List[TechnicalIndicator]) -> JSONResponse:
    return JSONResponse(content=[indicator.dict() for indicator in indicators])