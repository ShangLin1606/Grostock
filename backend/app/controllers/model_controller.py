from fastapi import APIRouter
from app.services.model_service import (
    train_stacking_model,
    run_predictions,
    check_model_performance
)

router = APIRouter()

@router.post("/train")
def train_model():
    """
    手動觸發 Stacking 模型訓練。
    Base：LGBM、XGB、SVC、MLP
    Meta：Logistic
    """
    model_info = train_stacking_model()
    return {"status": "success", "model_info": model_info}

@router.post("/predict")
def predict_today():
    """
    使用最新模型對當前資料進行預測。
    """
    preds = run_predictions()
    return {"status": "success", "predictions": preds}

@router.get("/check")
def check_model():
    """
    檢查最近模型表現，若 F1 < 閾值 → 觸發 retrain。
    """
    status = check_model_performance()
    return {"status": status}
