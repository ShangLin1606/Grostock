from transformers import AutoTokenizer, AutoModel
from pymilvus import Collection, connections
from ...dagster.utils.database import db
import pandas as pd
import torch
from loguru import logger
import numpy as np
from typing import List, Dict

class RAG:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
        self.model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
        self.milvus_collection = self._connect_milvus()
        self.mongo_db = db.connect_mongo()

    def _connect_milvus(self):
        connections.connect(host="localhost", port="19530")
        return Collection("news_vectors")

    def chunk_text(self, text: str, max_length: int = 512) -> List[str]:
        """將文本切割成 chunks"""
        tokens = self.tokenizer.encode(text, add_special_tokens=False)
        chunks = []
        for i in range(0, len(tokens), max_length):
            chunk_tokens = tokens[i:i + max_length]
            chunks.append(self.tokenizer.decode(chunk_tokens))
        return chunks

    def embed_text(self, text: str) -> np.ndarray:
        """生成文本嵌入"""
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
        with torch.no_grad():
            outputs = self.model(**inputs)
        return outputs.last_hidden_state.mean(dim=1).squeeze().numpy()

    def retrieve(self, query: str, top_k: int = 5) -> List[Dict]:
        """檢索相關新聞"""
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
                # 混合評分：距離（50%）+ 情緒分數（30%）+ 時間近度（20%）
                distance_score = 1 - hit.distance / 100
                sentiment_score = doc["sentiment"]["score"] if doc["sentiment"]["label"] == "POSITIVE" else 1 - doc["sentiment"]["score"]
                time_score = 1 - (pd.Timestamp.now() - pd.Timestamp(date)).days / 30
                hybrid_score = 0.5 * distance_score + 0.3 * sentiment_score + 0.2 * time_score
                retrieved_docs.append({"doc": doc, "score": hybrid_score})
        
        # 按混合評分排序
        retrieved_docs.sort(key=lambda x: x["score"], reverse=True)
        return [doc["doc"] for doc in retrieved_docs[:top_k]]

    def augment(self, query: str, docs: List[Dict]) -> str:
        """增強生成提示"""
        context = "\n".join([f"新聞標題: {doc['title']}\n摘要: {doc['summary']}" for doc in docs])
        return f"問題: {query}\n相關資訊:\n{context}\n請根據以上資訊回答問題。"

rag = RAG()