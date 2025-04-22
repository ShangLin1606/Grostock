from app.dagster_pipeline.utils.database import db
from app.models.stock import Stock, StockPrice, TechnicalIndicator
from loguru import logger
from typing import List
import traceback

class StockController:
    def __init__(self):
        try:
            self.conn = db.connect_postgres()
            logger.info("StockController 初始化成功，已連接到 PostgreSQL")
        except Exception as e:
            logger.error(f"StockController 初始化失敗: {str(e)}\n{traceback.format_exc()}")
            raise

    def get_stock_list(self) -> List[Stock]:
        """獲取股票列表"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT stock_id, stock_name FROM stock_list;")
            rows = cursor.fetchall()
            stocks = [Stock(stock_id=row[0], stock_name=row[1]) for row in rows] if rows else []
            cursor.close()
            return stocks
        except Exception as e:
            logger.error(f"獲取股票列表失敗: {str(e)}\n{traceback.format_exc()}")
            raise

    def get_stock_prices(self, stock_id: str) -> List[StockPrice]:
        """獲取股票價格"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT stock_id, date, open_price, high_price, low_price, close_price, volume 
                FROM stock_prices WHERE stock_id = %s ORDER BY date;
            """, (stock_id,))
            rows = cursor.fetchall()
            prices = [StockPrice(
                stock_id=row[0], 
                date=row[1],  # Pydantic 會自動處理 datetime.date
                open_price=float(row[2]), 
                high_price=float(row[3]),
                low_price=float(row[4]), 
                close_price=float(row[5]), 
                volume=int(row[6])
            ) for row in rows] if rows else []
            cursor.close()
            return prices
        except Exception as e:
            logger.error(f"獲取股票 {stock_id} 價格失敗: {str(e)}\n{traceback.format_exc()}")
            raise

    def get_technical_indicators(self, stock_id: str) -> List[TechnicalIndicator]:
        """獲取技術指標"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT stock_id, date, sma_20, ema_20, rsi_14, macd, macd_signal, macd_hist,
                       bb_upper, bb_mid, bb_lower, atr_14, stochastic_k, stochastic_d, cci_20, adx_14, obv
                FROM technical_indicators WHERE stock_id = %s ORDER BY date;
            """, (stock_id,))
            rows = cursor.fetchall()
            indicators = [TechnicalIndicator(
                stock_id=row[0], 
                date=row[1],  # Pydantic 會自動處理 datetime.date
                sma_20=row[2], 
                ema_20=row[3], 
                rsi_14=row[4], 
                macd=row[5],
                macd_signal=row[6], 
                macd_hist=row[7], 
                bb_upper=row[8], 
                bb_mid=row[9], 
                bb_lower=row[10],
                atr_14=row[11], 
                stochastic_k=row[12], 
                stochastic_d=row[13], 
                cci_20=row[14], 
                adx_14=row[15], 
                obv=row[16]
            ) for row in rows] if rows else []
            cursor.close()
            return indicators
        except Exception as e:
            logger.error(f"獲取股票 {stock_id} 技術指標失敗: {str(e)}\n{traceback.format_exc()}")
            raise

stock_controller = StockController()