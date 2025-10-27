"""
Dagster Asset：負責資料更新與特徵生成。
"""
from dagster import asset
from app.services.model_service import train_stacking_model, run_predictions
from loguru import logger
import psycopg2
from app.config.settings import settings
import pandas as pd

def get_conn():
    return psycopg2.connect(
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        dbname=settings.DB_NAME,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
    )

@asset
def update_stock_prices():
    """更新股票價格資料"""
    logger.info("🧾 更新股價資料")
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("UPDATE stock_prices SET close_price = close_price;")  # placeholder
    conn.commit()
    cursor.close()
    conn.close()
    logger.info("✅ 股價資料更新完成")

@asset
def generate_features():
    """執行特徵工程"""
    from app.scripts.feature_v2 import run_feature_engineering
    run_feature_engineering()
    logger.info("✅ 特徵工程完成")

@asset
def train_model():
    """訓練 Stacking 模型"""
    result = train_stacking_model()
    logger.info(f"✅ 模型訓練完成 F1={result['f1']}")
    return result

@asset
def predict_market():
    """使用最新模型生成預測"""
    preds = run_predictions()
    logger.info("✅ 預測完成")
    return preds
