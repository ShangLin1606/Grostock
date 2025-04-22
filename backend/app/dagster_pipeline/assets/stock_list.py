from dagster import asset
import requests
import asyncio
import aiohttp
import psycopg2
from dotenv import load_dotenv
import os
from loguru import logger

# 配置 loguru 日誌
logger.remove()
logger.add("stock_list.log", rotation="500 MB", retention="10 days", level="INFO", format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}")
logger.add(lambda msg: print(msg, end=""), format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}", level="INFO", colorize=True)

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD")
}

@asset
async def stock_list():
    url = "https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()

    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # 確保表格包含新欄位
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stock_list (
            stock_id VARCHAR(10) PRIMARY KEY,
            stock_name TEXT NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            listing_status VARCHAR(20) DEFAULT 'active'
        );
    """)

    # 獲取資料庫中現有的股票代碼
    cursor.execute("SELECT stock_id FROM stock_list;")
    existing_stocks = {row[0] for row in cursor.fetchall()}
    current_stocks = {item["Code"] for item in data}

    # 更新股票列表
    for item in data:
        stock_id = item["Code"]
        stock_name = item["Name"]
        is_new = stock_id not in existing_stocks

        cursor.execute("""
            INSERT INTO stock_list (stock_id, stock_name, is_active, listing_status)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (stock_id) DO UPDATE SET 
                stock_name = EXCLUDED.stock_name,
                is_active = TRUE,
                listing_status = CASE 
                    WHEN stock_list.listing_status = 'delisted' THEN 'active'
                    ELSE EXCLUDED.listing_status
                END;
        """, (stock_id, stock_name, True, 'newly_listed' if is_new else 'active'))

    # 標記下市股票
    delisted_stocks = existing_stocks - current_stocks
    if delisted_stocks:
        cursor.execute("""
            UPDATE stock_list 
            SET is_active = FALSE, listing_status = 'delisted'
            WHERE stock_id = ANY(%s);
        """, (list(delisted_stocks),))
        logger.info(f"Marked {len(delisted_stocks)} stocks as delisted: {delisted_stocks}")

    conn.commit()
    cursor.close()
    conn.close()
    logger.info(f"Daily stock list updated: {len(data)} stocks, {len(delisted_stocks)} delisted, {len(current_stocks - existing_stocks)} newly listed")
    return data