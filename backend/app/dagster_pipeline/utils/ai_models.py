import torch
import torch.nn as nn
from transformers import TimeSeriesTransformerModel
from sklearn.ensemble import StackingRegressor
from sklearn.linear_model import LinearRegression
from loguru import logger
import numpy as np
import os
from dotenv import load_dotenv
import pandas as pd
from stable_baselines3 import PPO
from app.dagster_pipeline.utils.database import db

load_dotenv()

class LSTMPricePredictor(nn.Module):
    def __init__(self, input_size=15, hidden_size=64, num_layers=2):
        super(LSTMPricePredictor, self).__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, 1)

    def forward(self, x):
        out, _ = self.lstm(x)
        out = self.fc(out[:, -1, :])
        return out

class TransformerPricePredictor:
    def __init__(self):
        self.model = TimeSeriesTransformerModel.from_pretrained("huggingface/time-series-transformer-tourism-monthly")

    def predict(self, data):
        outputs = self.model(data)
        return outputs.last_hidden_state.mean(dim=1)

class GANPriceGenerator(nn.Module):
    def __init__(self, noise_dim=100, hidden_size=128, output_size=1):
        super(GANPriceGenerator, self).__init__()
        self.generator = nn.Sequential(
            nn.Linear(noise_dim, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, output_size)
        )

    def forward(self, noise):
        return self.generator(noise)

class AIModels:
    def __init__(self):
        self.input_size = 15  # 技術指標數量
        self.lstm = LSTMPricePredictor(input_size=self.input_size)
        self.transformer = TransformerPricePredictor()
        self.gan = GANPriceGenerator()
        self.model_dir = "models"
        os.makedirs(self.model_dir, exist_ok=True)
        self.stacking_model = None
        self.rl_model = PPO("MlpPolicy", "CartPole-v1", verbose=0)  # 替換為自定義環境
        self.conn = db.connect_postgres()
        self.load_models()

    def get_all_stock_data(self):
        """獲取資料庫中所有股票的技術指標資料"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT stock_id, date, close_price, sma_20, ema_20, rsi_14, macd, macd_signal, macd_hist,
                   bb_upper, bb_mid, bb_lower, atr_14, stochastic_k, stochastic_d, cci_20, adx_14, obv
            FROM technical_indicators ORDER BY stock_id, date;
        """)
        rows = cursor.fetchall()
        df = pd.DataFrame(rows, columns=["stock_id", "date", "close_price", "sma_20", "ema_20", "rsi_14", "macd", "macd_signal", "macd_hist",
                                         "bb_upper", "bb_mid", "bb_lower", "atr_14", "stochastic_k", "stochastic_d", "cci_20", "adx_14", "obv"])
        cursor.close()
        return df

    def prepare_training_data(self):
        """準備所有股票的訓練資料"""
        df = self.get_all_stock_data()
        grouped = df.groupby("stock_id")
        all_features = []
        all_targets = []
        
        for stock_id, group in grouped:
            features = group[["sma_20", "ema_20", "rsi_14", "macd", "macd_signal", "macd_hist",
                              "bb_upper", "bb_mid", "bb_lower", "atr_14", "stochastic_k", "stochastic_d", 
                              "cci_20", "adx_14", "obv"]].values
            target = group["close_price"].shift(-1).values[:-1]  # 下一天的收盤價作為目標
            features = features[:-1]  # 移除最後一行以匹配目標
            if len(features) > 0:
                all_features.append(features)
                all_targets.append(target)
        
        # 合併所有股票資料
        X = np.vstack(all_features)
        y = np.concatenate(all_targets)
        return torch.tensor(X, dtype=torch.float32), torch.tensor(y, dtype=torch.float32)

    def train_initial(self, epochs=50):
        """首次訓練並儲存模型，使用所有股票資料"""
        X, y = self.prepare_training_data()
        data = X.unsqueeze(0)  # 添加批次維度
        
        # 訓練 LSTM
        optimizer_lstm = torch.optim.Adam(self.lstm.parameters(), lr=0.001)
        criterion = nn.MSELoss()
        for epoch in range(epochs):
            optimizer_lstm.zero_grad()
            pred = self.lstm(data)
            loss = criterion(pred.squeeze(), y)
            loss.backward()
            optimizer_lstm.step()
            logger.info(f"LSTM Epoch {epoch}, Loss: {loss.item()}")

        torch.save(self.lstm.state_dict(), os.path.join(self.model_dir, "lstm.pth"))

        # 訓練 GAN
        optimizer_gan = torch.optim.Adam(self.gan.parameters(), lr=0.001)
        noise = torch.randn(data.shape[0], 100)
        for epoch in range(epochs):
            optimizer_gan.zero_grad()
            gen_price = self.gan(noise)
            loss = criterion(gen_price.squeeze(), y)
            loss.backward()
            optimizer_gan.step()
            logger.info(f"GAN Epoch {epoch}, Loss: {loss.item()}")

        torch.save(self.gan.state_dict(), os.path.join(self.model_dir, "gan.pth"))

        # Stacking 訓練
        lstm_preds = self.lstm(data).detach().numpy()
        transformer_preds = self.transformer.predict(data).detach().numpy()
        gan_preds = self.gan(noise).detach().numpy()
        X_stack = np.hstack([lstm_preds, transformer_preds, gan_preds])
        self.stacking_model = StackingRegressor(
            estimators=[("lstm", LinearRegression()), ("transformer", LinearRegression()), ("gan", LinearRegression())],
            final_estimator=LinearRegression()
        )
        self.stacking_model.fit(X_stack, y.numpy())
        logger.info("Stacking 模型訓練完成")

    def load_models(self):
        """載入預訓練模型"""
        lstm_path = os.path.join(self.model_dir, "lstm.pth")
        gan_path = os.path.join(self.model_dir, "gan.pth")
        if os.path.exists(lstm_path):
            self.lstm.load_state_dict(torch.load(lstm_path))
            logger.info("已載入預訓練 LSTM 模型")
        if os.path.exists(gan_path):
            self.gan.load_state_dict(torch.load(gan_path))
            logger.info("已載入預訓練 GAN 模型")

    def predict(self, data):
        """使用 Stacking 模型預測"""
        with torch.no_grad():
            lstm_pred = self.lstm(data).numpy()
            transformer_pred = self.transformer.predict(data).numpy()
            noise = torch.randn(data.shape[0], 100)
            gan_pred = self.gan(noise).numpy()
            X = np.hstack([lstm_pred, transformer_pred, gan_pred])
            return self.stacking_model.predict(X)

    def should_retrain(self, df):
        """檢查是否需要重新訓練模型"""
        rsi = df["rsi_14"].iloc[-1]
        volatility = df["close_price"].pct_change().std() * np.sqrt(252)
        news_count = self.mongo_db["market_news"].count_documents({"date": {"$gte": (dt.datetime.now() - dt.timedelta(days=7)).isoformat()}})
        if rsi > 70 or rsi < 30 or volatility > 0.2 or news_count > 50:
            logger.info(f"觸發模型更新: RSI={rsi}, Volatility={volatility}, News Count={news_count}")
            return True
        return False

ai_models = AIModels()

if __name__ == "__main__":
    lstm_path = os.path.join(ai_models.model_dir, "lstm.pth")
    gan_path = os.path.join(ai_models.model_dir, "gan.pth")
    if not os.path.exists(lstm_path) or not os.path.exists(gan_path):
        logger.info("未找到預訓練模型，開始首次訓練")
        ai_models.train_initial()
    else:
        logger.info("已載入現有模型，無需首次訓練")