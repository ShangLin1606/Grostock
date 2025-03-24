from ....dagster.utils.database import db
from backend.app.models.stock import Stock, StockPrice, TechnicalIndicator
from ..utils.logger import app_logger as logger
from typing import List

class StockController:
    def __init__(self):
        self.conn = db.connect_postgres()

    def get_stock_list(self) -> List[Stock]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT stock_id, stock_name FROM stock_list;")
        stocks = [Stock(stock_id=row[0], stock_name=row[1]) for row in cursor.fetchall()]
        cursor.close()
        logger.info(f"獲取股票列表，總數: {len(stocks)}")
        return stocks

    def get_stock_prices(self, stock_id: str) -> List[StockPrice]:
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT stock_id, date, open_price, high_price, low_price, close_price, volume
            FROM stock_prices WHERE stock_id = %s ORDER BY date;
        """, (stock_id,))
        prices = [StockPrice(stock_id=row[0], date=row[1], open_price=row[2], high_price=row[3],
                             low_price=row[4], close_price=row[5], volume=row[6]) for row in cursor.fetchall()]
        cursor.close()
        logger.info(f"獲取股票 {stock_id} 的價格資料，總數: {len(prices)}")
        return prices

    def get_technical_indicators(self, stock_id: str) -> List[TechnicalIndicator]:
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT stock_id, date, sma_20, ema_20, rsi_14, macd, macd_signal, macd_hist,
                   bb_upper, bb_mid, bb_lower, atr_14, stochastic_k, stochastic_d, cci_20, adx_14, obv
            FROM technical_indicators WHERE stock_id = %s ORDER BY date;
        """, (stock_id,))
        indicators = [TechnicalIndicator(stock_id=row[0], date=row[1], sma_20=row[2], ema_20=row[3], rsi_14=row[4],
                                        macd=row[5], macd_signal=row[6], macd_hist=row[7], bb_upper=row[8],
                                        bb_mid=row[9], bb_lower=row[10], atr_14=row[11], stochastic_k=row[12],
                                        stochastic_d=row[13], cci_20=row[14], adx_14=row[15], obv=row[16])
                      for row in cursor.fetchall()]
        cursor.close()
        logger.info(f"獲取股票 {stock_id} 的技術指標，總數: {len(indicators)}")
        return indicators

stock_controller = StockController()