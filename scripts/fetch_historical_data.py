import requests
import yfinance as yf
import datetime as dt
import pandas as pd
import psycopg2
import asyncio
import aiohttp
from dotenv import load_dotenv
import os
from loguru import logger

# 配置 loguru 日誌
logger.remove()  # 移除預設處理器
logger.add("fetch_historical_data.log", rotation="500 MB", retention="10 days", level="INFO")  # 檔案輸出
logger.add(lambda msg: print(msg, end=""), format="{time} | {level} | {message}", level="INFO")  # 控制台輸出

# 載入環境變數
load_dotenv()

# 資料庫配置字典
DB_CONFIG = {
    "host":"localhost",
    "port": os.getenv("DB_PORT", "5432"),
    "dbname": os.getenv("DB_NAME", "grostock"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "postgres")
}

async def fetch_stock_list():
    """從證交所 API 爬取股票代碼和名稱"""
    url = "https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
    return data

async def fetch_stock_price(stock_id, start_date, end_date):
    """非同步抓取單一股票的歷史股價"""
    ticker = f"{stock_id}.TW" if stock_id != "大盤" else "^TWII"
    try:
        df = yf.download(ticker, start=start_date, end=end_date, auto_adjust=False, progress=False)
        if df.empty:
            logger.warning(f"找不到 {ticker} 的資料")
            return None
        df['stock_id'] = stock_id
        df = df.reset_index()
        df.columns = ['date', 'open', 'high', 'low', 'close', 'volume', 'stock_id'] if 'Adj Close' not in df.columns else ['date', 'open', 'high', 'low', 'close', 'adj_close', 'volume', 'stock_id']
        return df[['stock_id', 'date', 'open', 'high', 'low', 'close', 'volume']]
    except Exception as e:
        logger.error(f"抓取 {ticker} 資料時發生錯誤: {str(e)}")
        return None

def create_tables():
    """創建 stock_list 和 stock_prices 表格"""
    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS stock_list (
                        stock_id VARCHAR(10) PRIMARY KEY,
                        stock_name TEXT NOT NULL,
                        is_active BOOLEAN DEFAULT TRUE,
                        listing_status VARCHAR(20) DEFAULT 'active'
                    );
                """)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS stock_prices (
                        stock_id VARCHAR(10),
                        date DATE,
                        open_price FLOAT,
                        high_price FLOAT,
                        low_price FLOAT,
                        close_price FLOAT,
                        volume BIGINT,
                        PRIMARY KEY (stock_id, date)
                    );
                """)
            conn.commit()
        logger.info("stock_list 和 stock_prices 表格已建立或已存在")
    except Exception as e:
        logger.error(f"建立表格時發生錯誤: {str(e)}")

async def fetch_and_store_historical(stock_list, start_date="2000-01-01"):
    """
    分片與非同步抓取股票歷史股價並存入 PostgreSQL
    :param stock_list: 股票列表（包含 stock_id 和 stock_name）
    :param start_date: 開始日期（預設 2000-01-01）
    """
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # 儲存股票列表
    for item in stock_list:
        cursor.execute("""
            INSERT INTO stock_list (stock_id, stock_name, is_active, listing_status)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (stock_id) DO UPDATE SET 
                stock_name = EXCLUDED.stock_name,
                is_active = TRUE,
                listing_status = 'active';
        """, (item["Code"], item["Name"], True, 'active'))
    logger.info(f"Stock list stored: {len(stock_list)} stocks")

    # 分片與非同步抓取歷史股價
    chunk_size = 50
    end_date = dt.datetime.now()
    
    async def process_chunk(chunk):
        tasks = [fetch_stock_price(stock["Code"], start_date, end_date) for stock in chunk]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"分片處理中發生錯誤: {str(result)}")
                continue
            if result is not None and not result.empty:
                data = [(
                    row['stock_id'], 
                    row['date'].date(), 
                    row['open'], 
                    row['high'], 
                    row['low'], 
                    row['close'], 
                    int(row['volume'])
                ) for _, row in result.iterrows()]
                try:
                    cursor.executemany("""
                        INSERT INTO stock_prices (stock_id, date, open_price, high_price, low_price, close_price, volume)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (stock_id, date) DO NOTHING;
                    """, data)
                except Exception as e:
                    logger.error(f"儲存分片資料時發生錯誤: {str(e)}")

    for i in range(0, len(stock_list), chunk_size):
        chunk = stock_list[i:i + chunk_size]
        await process_chunk(chunk)
        logger.info(f"Processed historical chunk {i // chunk_size + 1}/{len(stock_list) // chunk_size + 1}")

    conn.commit()
    cursor.close()
    conn.close()
    logger.info("Historical data fetch and store completed")

async def main():
    # 建立表格
    create_tables()

    # 爬取股票列表並抓取歷史數據
    stock_list = await fetch_stock_list()
    if stock_list:
        await fetch_and_store_historical(stock_list)
    else:
        logger.error("無法獲取股票列表，無法繼續抓取歷史資料")

if __name__ == "__main__":
    asyncio.run(main())