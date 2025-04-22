from dagster import asset
import yfinance as yf
import datetime as dt
from app.dagster_pipeline.utils.database import db
from loguru import logger
import asyncio

@asset(deps=["stock_list"])
async def stock_prices(stock_list):
    conn = db.connect_postgres()
    cursor = conn.cursor()
    today = dt.datetime.today().date()

    async def fetch_price(stock_id):
        ticker = f"{stock_id}.TW"
        try:
            df = yf.download(ticker, start=today, end=today + dt.timedelta(days=1), progress=False)
            for date, row in df.iterrows():
                cursor.execute("""
                    INSERT INTO stock_prices (stock_id, date, open_price, high_price, low_price, close_price, volume)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (stock_id, date) DO NOTHING;
                """, (stock_id, date.date(), row["Open"], row["High"], row["Low"], row["Close"], int(row["Volume"])))
        except Exception as e:
            logger.error(f"Failed to fetch daily price for {stock_id}: {e}")

    # 分片處理
    chunk_size = 50
    for i in range(0, len(stock_list), chunk_size):
        chunk = stock_list[i:i + chunk_size]
        tasks = [fetch_price(stock["Code"]) for stock in chunk]
        await asyncio.gather(*tasks)
        logger.info(f"Processed daily price chunk {i // chunk_size + 1}/{len(stock_list) // chunk_size + 1}")

    conn.commit()
    cursor.close()
    conn.close()
    logger.info("Daily stock prices updated")