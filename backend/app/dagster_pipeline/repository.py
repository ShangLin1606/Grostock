"""
Dagster Repository：整合所有 asset、job、schedule、sensor。
"""
from dagster import Definitions
from app.dagster_pipeline.assets.data_assets import update_stock_prices, generate_features, train_model, predict_market
from app.dagster_pipeline.jobs.daily_job import daily_job
from app.dagster_pipeline.schedules.daily_schedule import trading_day_schedule
from app.dagster_pipeline.sensors.retrain_sensor import retrain_sensor

defs = Definitions(
    assets=[update_stock_prices, generate_features, train_model, predict_market],
    jobs=[daily_job],
    schedules=[trading_day_schedule],
    sensors=[retrain_sensor],
)
