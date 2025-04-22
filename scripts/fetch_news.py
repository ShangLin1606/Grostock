import requests
import datetime as dt
import asyncio
import aiohttp
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from loguru import logger
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

# 配置 loguru 日誌
logger.remove()
logger.add("fetch_news.log", rotation="500 MB", retention="10 days", level="INFO")
logger.add(lambda msg: print(msg, end=""), format="{time} | {level} | {message}", level="INFO")

load_dotenv()

MONGO_URI = "mongodb://localhost:27017/"
MONGO_DB = "grostock"
MONGO_COLLECTION = "market_news"

tokenizer = AutoTokenizer.from_pretrained("distilbert-base-multilingual-cased")
model = AutoModelForSequenceClassification.from_pretrained("distilbert-base-multilingual-cased")
sentiment_analyzer = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer, truncation=True, max_length=512)

async def fetch_market_news(session, keyword, start_ts, end_ts):
    """非同步抓取市場與產業新聞"""
    news_list = []
    page = 1
    retries = 3

    while True:
        url = f"https://ess.api.cnyes.com/ess/api/v1/news/keyword?q={keyword}&limit=50&start={start_ts}&end={end_ts}&page={page}"
        for attempt in range(retries):
            try:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status != 200:
                        logger.warning(f"無法獲取 {keyword} 的新聞 (頁 {page}): HTTP {response.status}")
                        return news_list
                    data = await response.json()
                    items = data.get("data", {}).get("items", [])
                    if not items:
                        logger.info(f"已完成 {keyword} 的新聞抓取，總計 {len(news_list)} 篇")
                        return news_list
                    page_news = [
                        {
                            "date": dt.datetime.utcfromtimestamp(item["publishAt"]).date().isoformat(),
                            "title": item["title"],
                            "news_id": item["newsId"],
                            "source": "cnyes"
                        }
                        for item in items
                    ]
                    news_list.extend(page_news)
                    logger.info(f"為 {keyword} 獲取第 {page} 頁，新增 {len(page_news)} 篇新聞，總計 {len(news_list)} 篇")
                    break
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                logger.error(f"獲取 {keyword} 新聞失敗 (頁 {page}, 嘗試 {attempt + 1}/{retries}): {str(e)}")
                if attempt < retries - 1:
                    await asyncio.sleep(2 ** attempt)
                else:
                    return news_list
        page += 1

async def fetch_news_content(session, news_id):
    """非同步抓取新聞內容"""
    content_url = f"https://news.cnyes.com/news/id/{news_id}"
    retries = 3
    for attempt in range(retries):
        try:
            async with session.get(content_url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status == 200:
                    soup = BeautifulSoup(await response.text(), "html.parser")
                    content = " ".join(p.get_text() for p in soup.find_all("p")[4:])
                    return content
                else:
                    logger.warning(f"無法獲取新聞 {news_id} 內容: HTTP {response.status}")
                    return ""
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            logger.error(f"獲取新聞 {news_id} 內容失敗 (嘗試 {attempt + 1}/{retries}): {str(e)}")
            if attempt < retries - 1:
                await asyncio.sleep(2 ** attempt)
            else:
                return ""

async def fetch_and_store_market_news():
    """抓取市場與產業新聞並存入 MongoDB"""
    mongo_client = MongoClient(MONGO_URI)
    db = mongo_client[MONGO_DB]
    collection = db[MONGO_COLLECTION]

    # 設置時間範圍
    thirty_days_ago = dt.datetime.now().date() - dt.timedelta(days=30)
    start_ts = int(dt.datetime.combine(thirty_days_ago, dt.datetime.min.time()).timestamp())
    end_ts = int(dt.datetime.now().timestamp())

    # 市場與產業關鍵字
    keywords = [
        "台股市場", "半導體產業", "科技產業", "金融市場", "能源產業",
        "全球經濟", "聯準會", "通膨", "利率決策", "國際股市"
    ]

    async def process_keyword(session, keyword):
        news_list = await fetch_market_news(session, keyword, start_ts, end_ts)
        for news_item in news_list:
            news_id = news_item["news_id"]
            title = news_item["title"]
            publish_at = dt.datetime.strptime(news_item["date"], "%Y-%m-%d").date()

            if collection.find_one({"news_id": news_id}):
                logger.debug(f"新聞 {news_id} 已存在，跳過")
                continue

            content = await fetch_news_content(session, news_id)
            try:
                sentiment_result = sentiment_analyzer(content or title)
                sentiment = {"label": sentiment_result[0]["label"], "score": sentiment_result[0]["score"]}
            except Exception as e:
                logger.error(f"無法生成 {news_id} 的情緒標籤: {e}")
                sentiment = {"label": "NEUTRAL", "score": 0.5}

            summary = content[:100] if content else title
            news_doc = {
                "category": keyword,
                "date": publish_at.isoformat(),
                "title": title,
                "content": content,
                "content_url": f"minio://market_news/{news_id}.txt",
                "sentiment": sentiment,
                "summary": summary,
                "news_id": news_id,
                "source": "cnyes"
            }
            try:
                collection.insert_one(news_doc)
                logger.info(f"已儲存市場新聞 {news_id} 到 MongoDB")
            except Exception as e:
                logger.error(f"儲存新聞 {news_id} 失敗: {e}")

    async with aiohttp.ClientSession() as session:
        tasks = [process_keyword(session, keyword) for keyword in keywords]
        await asyncio.gather(*tasks)

    mongo_client.close()
    logger.info("市場與產業新聞抓取與儲存完成")

async def main():
    await fetch_and_store_market_news()

if __name__ == "__main__":
    asyncio.run(main())