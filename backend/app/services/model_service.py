import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score
from sklearn.ensemble import StackingClassifier
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
import joblib
from loguru import logger
import psycopg2
from app.config.settings import settings

MODEL_PATH = "models/stacking_model.joblib"

def get_db_conn():
    return psycopg2.connect(
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        dbname=settings.DB_NAME,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
    )

def train_stacking_model():
    """訓練 Stacking 模型"""
    conn = get_db_conn()
    df = pd.read_sql("SELECT * FROM stock_features WHERE y_updown IS NOT NULL;", conn)
    conn.close()

    X = df[["sma_20", "ema_20", "rsi_14", "macd", "macd_signal"]].fillna(0)
    y = df["y_updown"].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=True)

    base_models = [
        ("lgbm", LGBMClassifier()),
        ("xgb", XGBClassifier(use_label_encoder=False, eval_metric="logloss")),
        ("svc", SVC(probability=True)),
        ("mlp", MLPClassifier(hidden_layer_sizes=(32, 16), max_iter=500))
    ]

    meta_model = LogisticRegression(max_iter=200)
    model = StackingClassifier(estimators=base_models, final_estimator=meta_model)
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    score = f1_score(y_test, preds)
    joblib.dump(model, MODEL_PATH)

    logger.info(f"Stacking 模型訓練完成，F1: {score:.4f}")
    return {"f1": score, "model_path": MODEL_PATH}

def run_predictions():
    """使用訓練好的模型進行預測"""
    conn = get_db_conn()
    df = pd.read_sql("SELECT * FROM stock_features ORDER BY date DESC LIMIT 1000;", conn)
    conn.close()

    model = joblib.load(MODEL_PATH)
    X = df[["sma_20", "ema_20", "rsi_14", "macd", "macd_signal"]].fillna(0)
    df["predicted"] = model.predict(X)
    logger.info(f"生成預測結果 {len(df)} 筆")
    return df[["stock_id", "date", "predicted"]].to_dict(orient="records")

def check_model_performance(threshold: float = 0.55):
    """檢查最近模型效能，若低於門檻觸發 retrain"""
    result = train_stacking_model()
    if result["f1"] < threshold:
        logger.warning("模型效能下降，觸發重新訓練")
        train_stacking_model()
        return "retrained"
    return "ok"
