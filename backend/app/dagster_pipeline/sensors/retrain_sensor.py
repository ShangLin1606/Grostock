"""
模型效能監控感測器：當模型 F1 < 閾值時觸發 retrain。
"""
from dagster import sensor, RunRequest
from app.services.model_service import check_model_performance
from loguru import logger

@sensor(job_name="daily_update_job")
def retrain_sensor(context):
    status = check_model_performance()
    if status == "retrained":
        logger.warning("⚠️ 模型已自動重新訓練")
        yield RunRequest(run_key=None, run_config={})
