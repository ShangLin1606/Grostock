from dagster import asset
import requests
from ..utils.database import db
from loguru import logger

@asset
def stock_list():
    url = "https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL"
    response = requests.get(url)
    data = response.json()

    conn = db.connect_postgres()
    cursor = conn.cursor()
    for item in data:
        cursor.execute("""
            INSERT INTO stock_list (stock_id, stock_name)
            VALUES (%s, %s)
            ON CONFLICT (stock_id) DO UPDATE SET stock_name = EXCLUDED.stock_name;
        """, (item["Code"], item["Name"]))
    conn.commit()
    cursor.close()
    conn.close()
    logger.info(f"股票列表更新完成，總數：{len(data)}")
    return data