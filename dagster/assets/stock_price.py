from dagster import asset
import yfinance as yf
import datetime as dt
from ..utils.database import db
from stock_list import stock_list
from loguru import logger
import asyncio
import aiohttp

@asset(deps=[stock_list])
async def stock_prices(stock_list):
    start_date = dt.datetime(2000, 1, 1)
    end_date = dt.datetime.today()
    conn = db.connect_postgres()
    cursor = conn.cursor()

    async def fetch_price(stock_id):
        ticker = f"{stock_id}.TW"
        try:
            df = yf.download(ticker, start=start_date, end=end_date, progress=False)
            for date, row in df.iterrows():
                cursor.execute("""
                    INSERT INTO stock_prices (stock_id, date, open_price, high_price, low_price, close_price, volume)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (stock_id, date) DO NOTHING;
                """, (stock_id, date.date(), row["Open"], row["High"], row["Low"], row["Close"], int(row["Volume"])))
        except Exception as e:
            logger.error(f"股票 {stock_id} 股價獲取失敗：{str(e)}")

    # 非同步處理分片
    tasks = [fetch_price(stock["Code"]) for stock in stock_list[:50]]  # 先測試前 50 檔，避免過載
    await asyncio.gather(*tasks)

    conn.commit()
    cursor.close()
    conn.close()
    logger.info("股價資料更新完成")