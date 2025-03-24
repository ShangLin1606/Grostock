from loguru import logger
import os
from dotenv import load_dotenv

load_dotenv()

# 配置 Loguru
logger.add(
    "logs/grostock_{time}.log",
    rotation="500 MB",  # 每個檔案最大 500 MB
    retention="10 days",  # 保留 10 天
    level=os.getenv("LOG_LEVEL", "INFO")  # 從 .env 讀取日誌級別
)

class Logger:
    @staticmethod
    def info(message):
        logger.info(message)

    @staticmethod
    def warning(message):
        logger.warning(message)

    @staticmethod
    def error(message):
        logger.error(message)

# 測試日誌
if __name__ == "__main__":
    Logger.info("Grostock 開發環境初始化完成")
    Logger.warning("測試警告訊息")
    Logger.error("測試錯誤訊息")