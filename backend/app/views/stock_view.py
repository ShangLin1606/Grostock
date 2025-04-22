from fastapi.responses import JSONResponse
from app.models.stock import Stock, StockPrice, TechnicalIndicator
from typing import List

def stock_list_view(stocks: List[Stock]) -> JSONResponse:
    return JSONResponse(content=[stock.dict() for stock in stocks])

def stock_price_view(prices: List[StockPrice]) -> JSONResponse:
    prices_dict = [price.dict() for price in prices]
    for price in prices_dict:
        price["date"] = price["date"].isoformat()  # 將 datetime.date 轉為 ISO 字串
    return JSONResponse(content=prices_dict)

def technical_indicator_view(indicators: List[TechnicalIndicator]) -> JSONResponse:
    indicators_dict = [indicator.dict() for indicator in indicators]
    for indicator in indicators_dict:
        indicator["date"] = indicator["date"].isoformat()  # 將 datetime.date 轉為 ISO 字串
    return JSONResponse(content=indicators_dict)