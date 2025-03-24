import torch
import torch.nn as nn
from transformers import TimeSeriesTransformerModel
from loguru import logger
import numpy as np

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
        # 假設 data 是時間序列資料 (batch_size, seq_length, feature_dim)
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
        self.lstm = LSTMPricePredictor()
        self.transformer = TransformerPricePredictor()
        self.gan = GANPriceGenerator()

    def train_lstm(self, data, epochs=10):
        optimizer = torch.optim.Adam(self.lstm.parameters(), lr=0.001)
        criterion = nn.MSELoss()
        for epoch in range(epochs):
            optimizer.zero_grad()
            pred = self.lstm(data)
            loss = criterion(pred, data[:, -1, 0])  # 預測最後一天收盤價
            loss.backward()
            optimizer.step()
            logger.info(f"LSTM Epoch {epoch}, Loss: {loss.item()}")

    def predict(self, data, model_type="lstm"):
        if model_type == "lstm":
            with torch.no_grad():
                return self.lstm(data).numpy()
        elif model_type == "transformer":
            return self.transformer.predict(data).numpy()
        elif model_type == "gan":
            noise = torch.randn(data.shape[0], 100)
            return self.gan(noise).detach().numpy()

ai_models = AIModels()