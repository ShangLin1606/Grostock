# backend/app/rag.py
from pymilvus import connections, Collection, utility, FieldSchema, CollectionSchema, DataType
from transformers import AutoTokenizer, AutoModel
import pandas as pd
import torch
from loguru import logger
import numpy as np
import time
from typing import List, Dict
from app.dagster_pipeline.utils.database import db

class RAG:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
        self.model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
        try:
            self.mongo_db = db.connect_mongo()
            if self.mongo_db is None:
                raise ValueError("MongoDB connection returned None")
            logger.info("MongoDB connection established")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            self.mongo_db = None  # 明確設置為 None，避免後續未定義
            raise
        self.milvus_collection = self._connect_milvus()
        if self.mongo_db is not None:  # 僅在 MongoDB 可用時初始化數據
            self._initialize_data_if_empty()

    def _connect_milvus(self):
        max_retries = 15
        retry_delay = 5
        for attempt in range(max_retries):
            try:
                connections.connect(host="milvus", port="19530")
                logger.info("Successfully connected to Milvus")
                if not utility.has_collection("news_vectors"):
                    logger.info("Creating news_vectors collection")
                    fields = [
                        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
                        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=384),
                        FieldSchema(name="stock_id", dtype=DataType.VARCHAR, max_length=10),
                        FieldSchema(name="date", dtype=DataType.VARCHAR, max_length=10)
                    ]
                    schema = CollectionSchema(fields=fields, description="新聞向量")
                    collection = Collection("news_vectors", schema)
                    collection.create_index(field_name="embedding", index_params={"index_type": "IVF_FLAT", "metric_type": "L2", "params": {"nlist": 1024}})
                    collection.load()
                    logger.info("Created and loaded news_vectors collection")
                else:
                    collection = Collection("news_vectors")
                    collection.load()
                    logger.info("Loaded existing news_vectors collection")
                return collection
            except Exception as e:
                logger.error(f"Failed to connect to Milvus (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    raise Exception("Max retries reached, failed to connect to Milvus")

    def _initialize_data_if_empty(self):
        if self.mongo_db is None:
            logger.warning("MongoDB not available, skipping data initialization")
            return
        try:
            if self.mongo_db["news"].count_documents({}) == 0:
                logger.warning("No news data found in MongoDB, inserting test data")
                test_news = [
                    {"stock_id": "AAPL", "date": "2025-03-29", "title": "Apple releases new product", "summary": "Apple announced a new iPhone today.", "sentiment": {"label": "POSITIVE", "score": 0.9}},
                    {"stock_id": "TSLA", "date": "2025-03-29", "title": "Tesla stock surges", "summary": "Tesla shares rose 5% after earnings report.", "sentiment": {"label": "POSITIVE", "score": 0.85}}
                ]
                self.mongo_db["news"].insert_many(test_news)
                for news in test_news:
                    embedding = self.embed_text(f"{news['title']} {news['summary']}")
                    self.milvus_collection.insert([[embedding], [news["stock_id"]], [news["date"]]])
                logger.info("Inserted test news data into MongoDB and Milvus")
        except Exception as e:
            logger.error(f"Failed to initialize test data: {e}")

    def chunk_text(self, text: str, max_length: int = 512) -> List[str]:
        tokens = self.tokenizer.encode(text, add_special_tokens=False)
        chunks = []
        for i in range(0, len(tokens), max_length):
            chunk_tokens = tokens[i:i + max_length]
            chunks.append(self.tokenizer.decode(chunk_tokens))
        return chunks

    def embed_text(self, text: str) -> np.ndarray:
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
        with torch.no_grad():
            outputs = self.model(**inputs)
        return outputs.last_hidden_state.mean(dim=1).squeeze().numpy()

    def retrieve(self, query: str, top_k: int = 5) -> List[Dict]:
        if self.mongo_db is None or self.milvus_collection is None:
            logger.error("Cannot retrieve data: MongoDB or Milvus not initialized")
            return []
        query_embedding = self.embed_text(query)
        search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
        results = self.milvus_collection.search(
            data=[query_embedding], anns_field="embedding", param=search_params, limit=top_k
        )
        retrieved_docs = []
        for hit in results[0]:
            stock_id = hit.entity.get("stock_id")
            date = hit.entity.get("date")
            doc = self.mongo_db["news"].find_one({"stock_id": stock_id, "date": date})
            if doc:
                distance_score = 1 - hit.distance / 100
                sentiment_score = doc["sentiment"]["score"] if doc["sentiment"]["label"] == "POSITIVE" else 1 - doc["sentiment"]["score"]
                time_score = 1 - (pd.Timestamp.now() - pd.Timestamp(date)).days / 30
                hybrid_score = 0.5 * distance_score + 0.3 * sentiment_score + 0.2 * time_score
                retrieved_docs.append({"doc": doc, "score": hybrid_score})
        retrieved_docs.sort(key=lambda x: x["score"], reverse=True)
        return [doc["doc"] for doc in retrieved_docs[:top_k]]

    def augment(self, query: str, docs: List[Dict]) -> str:
        context = "\n".join([f"新聞標題: {doc['title']}\n摘要: {doc['summary']}" for doc in docs])
        return f"問題: {query}\n相關資訊:\n{context}\n請根據以上資訊回答問題。"

rag = RAG()