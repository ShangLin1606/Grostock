import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
});

export async function getStocks() {
  const response = await api.get('/stocks');
  return response.data;
}

export async function getStockPrices(stockId) {
  const response = await api.get(`/stocks/${stockId}/prices`);
  return response.data;
}

export async function getTechnicalIndicators(stockId) {
  const response = await api.get(`/features/${stockId}`);
  return response.data;
}

export async function analyzeStock(stockId) {
  const response = await api.get(`/agent/analyze?query=請分析股票 ${stockId}`);
  return response.data;
}

export async function chatWithAdvisor(query) {
  const response = await api.post('/chatbot', { query });
  return response.data.response;
}

export async function getPortfolio(stocks, riskLevel) {
  const response = await api.post('/portfolio', { stocks, risk_level: riskLevel });
  return response.data;
}