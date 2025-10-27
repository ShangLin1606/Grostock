import yfinance as yf
import psycopg2
import pandas as pd
from app.config.settings import settings
from loguru import logger

def get_stock_history(symbol: str, start="2023-01-01"):
    """抓取 Yahoo Finance 股價資料"""
    data = yf.download(symbol, start=start)
    data.reset_index(inplace=True)
    logger.info(f"下載 {symbol} 共 {len(data)} 筆資料")
    return data

def get_db_conn():
    """PostgreSQL 連線"""
    return psycopg2.connect(
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        dbname=settings.DB_NAME,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
    )

def load_table(table: str, limit=1000):
    """從資料庫載入表格"""
    conn = get_db_conn()
    df = pd.read_sql(f"SELECT * FROM {table} LIMIT {limit};", conn)
    conn.close()
    logger.info(f"載入資料表 {table} 共 {len(df)} 筆")
    return df
