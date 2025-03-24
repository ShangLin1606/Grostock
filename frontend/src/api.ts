import axios from 'axios';

const API_URL = 'http://localhost:8000';

export interface Stock {
  stock_id: string;
  stock_name: string;
}

export interface StockPrice {
  stock_id: string;
  date: string;
  open_price: number;
  high_price: number;
  low_price: number;
  close_price: number;
  volume: number;
}

export interface TechnicalIndicator {
  stock_id: string;
  date: string;
  sma_20?: number;
  ema_20?: number;
  rsi_14?: number;
  macd?: number;
  macd_signal?: number;
  macd_hist?: number;
  bb_upper?: number;
  bb_mid?: number;
  bb_lower?: number;
  atr_14?: number;
  stochastic_k?: number;
  stochastic_d?: number;
  cci_20?: number;
  adx_14?: number;
  obv?: number;
}

export interface AgentResponse {
  predictions: { [key: string]: number };
  strategies: { [key: string]: number };
  risks: { [key: string]: number };
}

export const fetchStocks = async (): Promise<Stock[]> => {
  const response = await axios.get(`${API_URL}/stocks`);
  return response.data;
};

export const fetchStockPrices = async (stockId: string): Promise<StockPrice[]> => {
  const response = await axios.get(`${API_URL}/stocks/${stockId}/prices`);
  return response.data;
};

export const fetchTechnicalIndicators = async (stockId: string): Promise<TechnicalIndicator[]> => {
  const response = await axios.get(`${API_URL}/features/${stockId}`);
  return response.data;
};

export const analyzeStock = async (query: string): Promise<AgentResponse> => {
  const response = await axios.get(`${API_URL}/agent/analyze`, { params: { query } });
  return response.data;
};

export const chatWithBot = async (query: string): Promise<string> => {
  const response = await axios.post(`${API_URL}/chatbot`, { query });
  return response.data.response;
};