"""
每日工作：資料更新 → 特徵生成 → 模型訓練 → 預測。
"""
from dagster import define_asset_job
from app.dagster_pipeline.assets.data_assets import update_stock_prices, generate_features, train_model, predict_market

daily_job = define_asset_job(
    name="daily_update_job",
    selection=[update_stock_prices, generate_features, train_model, predict_market],
)
