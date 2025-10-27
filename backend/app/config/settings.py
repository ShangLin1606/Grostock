from pydantic import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    """統一系統設定管理"""
    # === 資料庫設定 ===
    DB_HOST: str = "postgres"
    DB_PORT: int = 5432
    DB_NAME: str = "stock_db"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"

    # === MongoDB ===
    MONGO_URI: str = "mongodb://mongo:mongo@mongodb:27017/grostock"

    # === 其他服務 ===
    MILVUS_HOST: str = "milvus"
    MILVUS_PORT: int = 19530
    NEO4J_URI: str = "bolt://neo4j:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "neo4j123"

    # === MinIO ===
    MINIO_ROOT_USER: str = "minioadmin"
    MINIO_ROOT_PASSWORD: str = "minioadmin"
    MINIO_ADDRESS: str = "minio:9000"

    # === FastAPI ===
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    LOG_LEVEL: str = "INFO"

    # === API Keys ===
    HF_API_KEY: str = "your_huggingface_key"
    XAI_API_KEY: str = "your_xai_key"
    PHIDATA_API_KEY: str = "your_phidata_key"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
