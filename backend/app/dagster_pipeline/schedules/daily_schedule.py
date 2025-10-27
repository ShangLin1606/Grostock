"""
每日 09:00 觸發 Dagster 工作（僅在交易日執行）。
"""
from dagster import schedule, DefaultScheduleStatus
from datetime import datetime
from app.dagster_pipeline.jobs.daily_job import daily_job

def is_trading_day(date: datetime) -> bool:
    # 可改成連接交易日曆資料庫
    return date.weekday() < 5  # 週一到週五

@schedule(
    cron_schedule="0 9 * * *",
    job=daily_job,
    execution_timezone="Asia/Taipei",
    default_status=DefaultScheduleStatus.RUNNING,
)
def trading_day_schedule(context):
    today = datetime.now().date()
    if is_trading_day(today):
        context.log.info(f"✅ {today} 是交易日，執行 daily_job")
        return {}
    else:
        context.log.info(f"⛔ {today} 非交易日，跳過執行")
        return None
