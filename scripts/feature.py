import psycopg2
import pandas as pd
import numpy as np
import os
from dotenv import load_dotenv
from loguru import logger

# === 初始化設定 ===
logger.remove()
logger.add("feature_v2.log", rotation="500 MB", retention="10 days",
           level="INFO", format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}")

load_dotenv()
DB_CONFIG = {
    "host": "localhost",
    "port": os.getenv("DB_PORT"),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}

def run_feature_engineering():
    """計算特徵工程，加入漲跌幅與Y標籤（是否上漲）"""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stock_features (
            stock_id VARCHAR(10),
            date DATE,
            sma_20 FLOAT,
            ema_20 FLOAT,
            rsi_14 FLOAT,
            macd FLOAT,
            macd_signal FLOAT,
            return_1d FLOAT,
            y_updown INTEGER,
            PRIMARY KEY (stock_id, date)
        );
    ''')

    cursor.execute("SELECT stock_id FROM stock_list WHERE is_active = TRUE;")
    stock_ids = [r[0] for r in cursor.fetchall()]

    for sid in stock_ids:
        cursor.execute("SELECT date, close_price FROM stock_prices WHERE stock_id = %s ORDER BY date;", (sid,))
        data = pd.DataFrame(cursor.fetchall(), columns=["date", "close_price"])
        if len(data) < 30:
            continue

        data["return_1d"] = data["close_price"].pct_change()
        data["y_updown"] = np.where(data["return_1d"] > 0, 1, 0)

        data["sma_20"] = data["close_price"].rolling(20).mean()
        data["ema_20"] = data["close_price"].ewm(span=20).mean()

        delta = data["close_price"].diff()
        gain = delta.clip(lower=0).rolling(14).mean()
        loss = -delta.clip(upper=0).rolling(14).mean()
        rs = gain / loss.replace(0, np.nan)
        data["rsi_14"] = 100 - (100 / (1 + rs))

        ema12 = data["close_price"].ewm(span=12).mean()
        ema26 = data["close_price"].ewm(span=26).mean()
        data["macd"] = ema12 - ema26
        data["macd_signal"] = data["macd"].ewm(span=9).mean()

        for _, r in data.iterrows():
            if pd.notna(r["sma_20"]):
                cursor.execute(
                    '''INSERT INTO stock_features 
                    (stock_id, date, sma_20, ema_20, rsi_14, macd, macd_signal, return_1d, y_updown)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    ON CONFLICT (stock_id, date) DO UPDATE SET
                        sma_20=EXCLUDED.sma_20,
                        ema_20=EXCLUDED.ema_20,
                        rsi_14=EXCLUDED.rsi_14,
                        macd=EXCLUDED.macd,
                        macd_signal=EXCLUDED.macd_signal,
                        return_1d=EXCLUDED.return_1d,
                        y_updown=EXCLUDED.y_updown;
                    ''',
                    (sid, r["date"], r["sma_20"], r["ema_20"], r["rsi_14"], r["macd"],
                     r["macd_signal"], r["return_1d"], int(r["y_updown"])),
                )

    conn.commit()
    cursor.close()
    conn.close()
    logger.info("✅ 特徵工程完成，含漲跌幅與Y標籤")

if __name__ == "__main__":
    run_feature_engineering()
