from loguru import logger
import sys
import os

def init_logger(log_dir: str = "logs"):
    """初始化 Loguru 日誌系統"""
    os.makedirs(log_dir, exist_ok=True)
    logger.remove()
    logger.add(sys.stdout, colorize=True,
               format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>")
    logger.add(f"{log_dir}/grostock.log", rotation="500 MB", retention="7 days",
               level="INFO", encoding="utf-8",
               format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}")
    return logger
