import psycopg2
import pymongo
from pymilvus import connections, Collection, utility, FieldSchema, CollectionSchema, DataType
from dotenv import load_dotenv
import os
from loguru import logger

load_dotenv()

class Database:
    def __init__(self):
        self.db_config = {
            "dbname": os.getenv("DB_NAME"),
            "user": os.getenv("DB_USER"),
            "password": os.getenv("DB_PASSWORD"),
            "host": os.getenv("DB_HOST"),
            "port": os.getenv("DB_PORT")
        }
        self.mongo_uri = os.getenv("MONGODB_URI")
        self.milvus_host = os.getenv("MILVUS_HOST")
        self.milvus_port = os.getenv("MILVUS_PORT")

    def connect_postgres(self):
        return psycopg2.connect(**self.db_config)

    def connect_mongo(self):
        return pymongo.MongoClient(self.mongo_uri)["grostock"]

    def connect_milvus(self):
        connections.connect(host=self.milvus_host, port=self.milvus_port)
        if not utility.has_collection("news_vectors"):
            fields = [
                FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
                FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=384),  # all-MiniLM-L6-v2 的維度
                FieldSchema(name="stock_id", dtype=DataType.VARCHAR, max_length=10),
                FieldSchema(name="date", dtype=DataType.VARCHAR, max_length=10)
            ]
            schema = CollectionSchema(fields=fields, description="新聞向量")
            collection = Collection("news_vectors", schema)
            collection.create_index(field_name="embedding", index_params={"index_type": "IVF_FLAT", "metric_type": "L2", "params": {"nlist": 1024}})
            collection.load()
        return Collection("news_vectors")

    def init_postgres_tables(self):
        conn = self.connect_postgres()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stock_list (
                stock_id VARCHAR(10) PRIMARY KEY,
                stock_name TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS stock_prices (
                stock_id VARCHAR(10),
                date DATE,
                open_price FLOAT,
                high_price FLOAT,
                low_price FLOAT,
                close_price FLOAT,
                volume BIGINT,
                PRIMARY KEY (stock_id, date)
            );
        """)
        conn.commit()
        cursor.close()
        conn.close()
        logger.info("PostgreSQL 表格初始化完成")

db = Database()