from dagster import asset
from ..utils.database import db
from ..utils.technical_indicators import TechnicalIndicators
from loguru import logger
import pandas as pd

@asset(deps=["stock_prices"])
def technical_features(stock_prices):
    conn = db.connect_postgres()
    cursor = conn.cursor()

    # 創建技術指標表格
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS technical_indicators (
            stock_id VARCHAR(10),
            date DATE,
            sma_20 FLOAT, ema_20 FLOAT, rsi_14 FLOAT,
            macd FLOAT, macd_signal FLOAT, macd_hist FLOAT,
            bb_upper FLOAT, bb_mid FLOAT, bb_lower FLOAT,
            atr_14 FLOAT, stochastic_k FLOAT, stochastic_d FLOAT,
            cci_20 FLOAT, adx_14 FLOAT, obv BIGINT,
            PRIMARY KEY (stock_id, date)
        );
    """)

    # 從 PostgreSQL 獲取股價資料
    cursor.execute("SELECT DISTINCT stock_id FROM stock_prices;")
    stock_ids = [row[0] for row in cursor.fetchall()]

    for stock_id in stock_ids[:50]:  # 先處理前 50 檔
        cursor.execute("""
            SELECT date, open_price, high_price, low_price, close_price, volume
            FROM stock_prices WHERE stock_id = %s ORDER BY date;
        """, (stock_id,))
        rows = cursor.fetchall()
        df = pd.DataFrame(rows, columns=["date", "open_price", "high_price", "low_price", "close_price", "volume"])
        df.set_index("date", inplace=True)

        # 計算技術指標
        ti = TechnicalIndicators(df)
        indicators = ti.compute_all()

        # 存入 PostgreSQL
        for date, row in df.iterrows():
            cursor.execute("""
                INSERT INTO technical_indicators (
                    stock_id, date, sma_20, ema_20, rsi_14,
                    macd, macd_signal, macd_hist,
                    bb_upper, bb_mid, bb_lower,
                    atr_14, stochastic_k, stochastic_d,
                    cci_20, adx_14, obv
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (stock_id, date) DO NOTHING;
            """, (
                stock_id, date,
                indicators["SMA_20"].loc[date] if date in indicators["SMA_20"].index else None,
                indicators["EMA_20"].loc[date] if date in indicators["EMA_20"].index else None,
                indicators["RSI_14"].loc[date] if date in indicators["RSI_14"].index else None,
                indicators["MACD"].loc[date] if date in indicators["MACD"].index else None,
                indicators["MACD_Signal"].loc[date] if date in indicators["MACD_Signal"].index else None,
                indicators["MACD_Hist"].loc[date] if date in indicators["MACD_Hist"].index else None,
                indicators["BB_Upper"].loc[date] if date in indicators["BB_Upper"].index else None,
                indicators["BB_Mid"].loc[date] if date in indicators["BB_Mid"].index else None,
                indicators["BB_Lower"].loc[date] if date in indicators["BB_Lower"].index else None,
                indicators["ATR_14"].loc[date] if date in indicators["ATR_14"].index else None,
                indicators["Stochastic_K"].loc[date] if date in indicators["Stochastic_K"].index else None,
                indicators["Stochastic_D"].loc[date] if date in indicators["Stochastic_D"].index else None,
                indicators["CCI_20"].loc[date] if date in indicators["CCI_20"].index else None,
                indicators["ADX_14"].loc[date] if date in indicators["ADX_14"].index else None,
                indicators["OBV"].loc[date] if date in indicators["OBV"].index else None
            ))

    conn.commit()
    cursor.close()
    conn.close()
    logger.info("技術指標特徵存入 PostgreSQL 完成")