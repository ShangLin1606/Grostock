import numpy as np
from loguru import logger
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv

class TradingStrategies:
    def __init__(self, prices, indicators):
        self.prices = prices
        self.indicators = indicators

    # 傳統策略
    def momentum_breakout(self, window=20):
        """動量突破策略"""
        sma = self.indicators["SMA_20"]
        weights = np.ones(len(self.prices))  # 動態調整權重可進一步優化
        signals = np.where(self.prices > sma.shift(1), 1, -1)
        return signals * weights

    def mean_reversion(self, window=20):
        """均值回歸策略"""
        sma = self.indicators["SMA_20"]
        weights = np.ones(len(self.prices))
        signals = np.where(self.prices < sma.shift(1), 1, -1)
        return signals * weights

    def volatility_arbitrage(self, window=20):
        """波動性套利"""
        atr = self.indicators["ATR_14"]
        weights = atr / atr.mean()  # 動態調整權重
        signals = np.where(self.prices.pct_change() > atr.shift(1), 1, -1)
        return signals * weights

    # 機器學習策略
    def lstm_strategy(self, predictions):
        """LSTM 價格預測策略"""
        signals = np.where(predictions > self.prices.shift(1), 1, -1)
        return signals

    def transformer_strategy(self, predictions):
        """Transformer 時間序列策略"""
        signals = np.where(predictions > self.prices.shift(1), 1, -1)
        return signals

    def gan_strategy(self, generated_prices):
        """GAN 價格生成策略"""
        signals = np.where(generated_prices > self.prices.shift(1), 1, -1)
        return signals

    def rlhf_optimize(self, signals, returns):
        """使用 RLHF 動態調整交易參數"""
        env = DummyVecEnv([lambda: TradingEnv(returns, signals)])
        model = PPO("MlpPolicy", env, verbose=0)
        model.learn(total_timesteps=10000)
        optimized_signals = model.predict(returns)[0]
        logger.info("RLHF 優化完成")
        return optimized_signals

class TradingEnv:
    def __init__(self, returns, signals):
        self.returns = returns
        self.signals = signals
        self.current_step = 0

    def reset(self):
        self.current_step = 0
        return self.returns.iloc[0]

    def step(self, action):
        reward = self.returns.iloc[self.current_step] * action
        self.current_step += 1
        done = self.current_step >= len(self.returns)
        return self.returns.iloc[self.current_step] if not done else 0, reward, done, {}