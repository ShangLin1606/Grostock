from loguru import logger
import os
from dotenv import load_dotenv

load_dotenv()

class Logger:
    def __init__(self):
        # 配置 Loguru
        log_file = "logs/grostock_{time}.log"
        logger.add(
            log_file,
            rotation="500 MB",  # 每個檔案最大 500 MB
            retention="10 days",  # 保留 10 天
            level=os.getenv("LOG_LEVEL", "INFO"),  # 從 .env 讀取日誌級別
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
        )
        self.logger = logger

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

# 單例實例
app_logger = Logger()

if __name__ == "__main__":
    app_logger.info("Loguru 配置測試：資訊訊息")
    app_logger.warning("Loguru 配置測試：警告訊息")
    app_logger.error("Loguru 配置測試：錯誤訊息")