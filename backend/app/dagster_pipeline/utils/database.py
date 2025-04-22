import os
import psycopg2
import pymongo
from loguru import logger
import time

class Database:
    def __init__(self):
        self.postgres_conn = None
        self.mongo_client = None
        self.mongo_db = None
        self.connect_postgres()
        self.connect_mongo()

    def connect_postgres(self, max_retries=5, retry_delay=5):
        attempt = 0
        while attempt < max_retries:
            try:
                self.postgres_conn = psycopg2.connect(
                    dbname=os.getenv("DB_NAME"),
                    user=os.getenv("DB_USER"),
                    password=os.getenv("DB_PASSWORD"),
                    host=os.getenv("DB_HOST"),
                    port=os.getenv("DB_PORT")
                )
                logger.info("Successfully connected to PostgreSQL")
                return self.postgres_conn
            except psycopg2.Error as e:
                attempt += 1
                logger.error(f"PostgreSQL connection failed (attempt {attempt}/{max_retries}): {e}")
                logger.error(f"Connection params: dbname={os.getenv('DB_NAME')}, user={os.getenv('DB_USER')}, host={os.getenv('DB_HOST')}, port={os.getenv('DB_PORT')}")
                if attempt < max_retries:
                    time.sleep(retry_delay)
        logger.error("Max retries reached, failed to connect to PostgreSQL")
        self.postgres_conn = None
        raise ValueError("PostgreSQL connection failed after max retries")

    def connect_mongo(self, max_retries=5, retry_delay=5):
        attempt = 0
        while attempt < max_retries:
            try:
                self.mongo_client = pymongo.MongoClient("mongodb://mongodb:27017/")
                self.mongo_db = self.mongo_client["grostock"]
                logger.info("Successfully connected to MongoDB")
                return self.mongo_db
            except Exception as e:
                attempt += 1
                logger.error(f"MongoDB connection failed (attempt {attempt}/{max_retries}): {e}")
                if attempt < max_retries:
                    time.sleep(retry_delay)
        logger.error("Max retries reached, failed to connect to MongoDB")
        self.mongo_db = None
        raise ValueError("MongoDB connection failed after max retries")

    def close(self):
        if self.postgres_conn:
            self.postgres_conn.close()
            logger.info("PostgreSQL connection closed")
        if self.mongo_client:
            self.mongo_client.close()
            logger.info("MongoDB connection closed")

db = Database()