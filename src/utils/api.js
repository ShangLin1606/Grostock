import axios from 'axios';

// === 全域 API 設定 ===
// 自動讀取 .env 中的 VITE_API_BASE_URL，例如 http://localhost:8000/api
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

// === 統一錯誤處理 ===
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API 錯誤：', error);
    alert('伺服器連線錯誤或逾時');
    return Promise.reject(error);
  }
);

// === 各功能 API ===

// 股票列表
export const fetchStocks = async () => {
  const res = await api.get('/stocks');
  return res.data;
};

// 熱力圖資料
export const fetchHeatmap = async () => {
  const res = await api.get('/heatmap');
  return res.data;
};

// 市場概覽
export const fetchMarketOverview = async () => {
  const res = await api.get('/market-overview');
  return res.data;
};

// AI 問答（LLMRouter）
export const queryAgent = async (question) => {
  const res = await api.post('/agent/query', { query: question });
  return res.data;
};

export default api;
