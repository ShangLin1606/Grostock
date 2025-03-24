from dagster import asset
import requests
from bs4 import BeautifulSoup
import datetime as dt
from ..utils.database import db
from ..utils.huggingface import hf_processor
from ..utils.minio_client import minio_client
from ..utils.etcd_client import etcd_client
from loguru import logger
import os

@asset(deps=["stock_list"])
def stock_news(stock_list):
    mongo_db = db.connect_mongo()
    milvus_collection = db.connect_milvus()
    news_collection = mongo_db["news"]

    for stock in stock_list[:10]:  # 先測試前 10 檔
        stock_name = stock["Name"]
        url = f"https://ess.api.cnyes.com/ess/api/v1/news/keyword?q={stock_name}&limit=5&page=1"
        json_data = requests.get(url).json().get("data", {}).get("items", [])

        for item in json_data:
            news_id = item["newsId"]
            title = item["title"]
            publish_at = dt.datetime.utcfromtimestamp(item["publishAt"]).date()
            if (dt.datetime.today().date() - publish_at).days > 30:
                continue

            # 爬取內容並上傳到 MinIO
            content_url = f"https://news.cnyes.com/news/id/{news_id}"
            response = requests.get(content_url)
            soup = BeautifulSoup(response.content, "html.parser")
            content = " ".join(p.get_text() for p in soup.find_all("p")[4:])
            object_name = f"news/{stock['Code']}/{news_id}.txt"
            with open(f"/tmp/{news_id}.txt", "w") as f:
                f.write(content)
            minio_client.upload_file(f"/tmp/{news_id}.txt", object_name)
            os.remove(f"/tmp/{news_id}.txt")

            # Hugging Face 處理
            sentiment = hf_processor.get_sentiment(content)
            summary = hf_processor.get_summary(content)
            embedding = hf_processor.get_embedding(content)

            # 存入 MongoDB
            news_doc = {
                "stock_id": stock["Code"],
                "stock_name": stock_name,
                "date": publish_at.isoformat(),
                "title": title,
                "content_url": f"minio://{object_name}",  # 儲存 MinIO 路徑
                "sentiment": sentiment,
                "summary": summary
            }
            news_collection.insert_one(news_doc)

            # 存入 Milvus
            milvus_collection.insert([
                {
                    "embedding": embedding,
                    "stock_id": stock["Code"],
                    "date": publish_at.isoformat()
                }
            ])

            # 存入 etcd（元數據）
            etcd_key = f"/news/{stock['Code']}/{news_id}"
            etcd_client.put(etcd_key, f"title: {title}, date: {publish_at.isoformat()}")

    logger.info("新聞資料更新完成")