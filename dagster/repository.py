from dagster import repository, define_asset_job, ScheduleDefinition
from assets import stock_list, stock_prices, stock_news, technical_features, ai_agents

@repository
def grostock_repository():
    return [
        stock_list,
        stock_prices,
        stock_news,
        technical_features,
        ai_agents,
        define_asset_job("daily_update", selection=["stock_list", "stock_prices", "stock_news", "technical_features", "ai_agents"]),
        ScheduleDefinition(job_name="daily_update", cron_schedule="0 0 * * *")  # 每天凌晨執行
    ]