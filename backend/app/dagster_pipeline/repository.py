from dagster import repository, define_asset_job, ScheduleDefinition
from app.dagster_pipeline.assets.stock_list import stock_list
from app.dagster_pipeline.assets.stock_prices import stock_prices
from app.dagster_pipeline.assets.stock_news import stock_news
from app.dagster_pipeline.assets.feature_engineering import technical_features
from app.dagster_pipeline.assets.ai_agents import ai_agents

@repository
def grostock_repository():
    return [
        stock_list,
        stock_prices,
        stock_news,
        technical_features,
        ai_agents,
        define_asset_job("daily_update", selection=["stock_list", "stock_prices", "stock_news", "technical_features", "ai_agents"]),
        ScheduleDefinition(job_name="daily_update", cron_schedule="0 0 * * *")
    ]