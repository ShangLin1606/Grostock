from dagster import asset
import requests
from bs4 import BeautifulSoup
import datetime as dt
from app.dagster_pipeline.utils.database import db
from app.dagster_pipeline.utils.huggingface import hf_processor
from app.dagster_pipeline.utils.minio_client import minio_client
from app.dagster_pipeline.utils.etcd_client import etcd_client
from loguru import logger
import os
import time
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline

# 配置 Hugging Face 情感分析模型
tokenizer = AutoTokenizer.from_pretrained("distilbert-base-multilingual-cased")
model = AutoModelForSequenceClassification.from_pretrained("distilbert-base-multilingual-cased")
sentiment_analyzer = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer, truncation=True, max_length=512)

@asset(deps=["stock_list"])
def stock_news():
    mongo_db = db.connect_mongo()
    milvus_collection = db.connect_milvus()
    news_collection = mongo_db["market_news"]

    logger.info("開始更新當天市場與產業新聞資料")
    today = dt.datetime.now().date()
    thirty_one_days_ago = today - dt.timedelta(days=31)
    start_ts = int(dt.datetime.combine(today, dt.datetime.min.time()).timestamp())
    end_ts = int(dt.datetime.combine(today, dt.datetime.max.time()).timestamp())

    # 刪除 31 天前的新聞
    news_collection.delete_many({"date": {"$lt": thirty_one_days_ago.isoformat()}})
    milvus_collection.delete(expr=f"date < '{thirty_one_days_ago.isoformat()}'")
    logger.info(f"已刪除 {thirty_one_days_ago.isoformat()} 前的舊新聞資料")

    # 刪除當天的舊資料
    news_collection.delete_many({"date": today.isoformat()})
    milvus_collection.delete(expr=f"date == '{today.isoformat()}'")
    logger.info(f"已刪除 {today.isoformat()} 的舊新聞資料")

    keywords = [
        "台股市場", "半導體產業", "科技產業", "金融市場", "能源產業",
        "全球經濟", "聯準會", "通膨", "利率決策", "國際股市"
    ]

    for keyword in keywords:
        url = f"https://ess.api.cnyes.com/ess/api/v1/news/keyword?q={keyword}&limit=50&start={start_ts}&end={end_ts}&page=1"
        retries = 3
        for attempt in range(retries):
            try:
                response = requests.get(url, timeout=30)
                if response.status_code != 200:
                    logger.warning(f"無法獲取 {keyword} 的新聞: HTTP {response.status_code}")
                    break
                json_data = response.json().get("data", {}).get("items", [])
                logger.info(f"為 {keyword} 獲取到 {len(json_data)} 篇當天新聞")
                break
            except Exception as e:
                logger.error(f"無法獲取 {keyword} 的新聞 (嘗試 {attempt + 1}/{retries}): {e}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    json_data = []

        for item in json_data:
            news_id = item["newsId"]
            title = item["title"]
            publish_at = dt.datetime.utcfromtimestamp(item["publishAt"]).date()
            if publish_at != today:
                logger.info(f"跳過非當天新聞 {news_id}")
                continue

            content_url = f"https://news.cnyes.com/news/id/{news_id}"
            retries = 3
            content = ""
            for attempt in range(retries):
                try:
                    response = requests.get(content_url, timeout=30)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, "html.parser")
                        content = " ".join(p.get_text() for p in soup.find_all("p")[4:])
                        break
                    else:
                        logger.warning(f"獲取新聞 {news_id} 內容失敗: HTTP {response.status_code}")
                except Exception as e:
                    logger.error(f"獲取新聞 {news_id} 內容失敗 (嘗試 {attempt + 1}/{retries}): {e}")
                    if attempt < retries - 1:
                        time.sleep(2 ** attempt)
                    else:
                        content = ""

            object_name = f"market_news/{news_id}.txt"
            with open(f"/tmp/{news_id}.txt", "w") as f:
                f.write(content)
            minio_client.upload_file(f"/tmp/{news_id}.txt", object_name)
            os.remove(f"/tmp/{news_id}.txt")
            logger.info(f"已將新聞 {news_id} 的內容上傳至 MinIO")

            try:
                sentiment_result = sentiment_analyzer(content or title)
                sentiment = {"label": sentiment_result[0]["label"], "score": sentiment_result[0]["score"]}
                summary = hf_processor.get_summary(content) if content else title
                embedding = hf_processor.get_embedding(content) if content else None
                logger.info(f"已為新聞 {news_id} 處理情感分析、摘要和嵌入向量")
            except Exception as e:
                logger.error(f"無法為新聞 {news_id} 執行 Hugging Face 處理: {e}")
                sentiment = {"label": "NEUTRAL", "score": 0.5}
                summary = title
                embedding = None

            news_doc = {
                "category": keyword,
                "date": publish_at.isoformat(),
                "title": title,
                "content": content,
                "content_url": f"minio://{object_name}",
                "sentiment": sentiment,
                "summary": summary,
                "news_id": news_id,
                "source": "cnyes"
            }
            if not news_collection.find_one({"news_id": news_id}):
                news_collection.insert_one(news_doc)
                logger.info(f"已將新聞 {news_id} 插入 MongoDB")
            else:
                logger.debug(f"新聞 {news_id} 已存在於 MongoDB，跳過插入")

            if embedding is not None:
                milvus_collection.insert([
                    {
                        "embedding": embedding,
                        "category": keyword,
                        "date": publish_at.isoformat()
                    }
                ])
                logger.info(f"已將新聞 {news_id} 插入 Milvus")

            etcd_key = f"/market_news/{news_id}"
            etcd_client.put(etcd_key, f"title: {title}, date: {publish_at.isoformat()}")
            logger.info(f"已將新聞 {news_id} 插入 etcd")

    logger.info("當天市場與產業新聞資料更新完成")