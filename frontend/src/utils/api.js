import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
});

const proxyApi = axios.create({
  baseURL: 'http://localhost:5001',
});

export async function getStocks() {
  try {
    const response = await proxyApi.get('/stocks');
    return response.data;
  } catch (error) {
    console.error('獲取股票列表失敗:', error.message);
    return [];
  }
}

export async function getStockHistory(stockId) {
  try {
    const response = await proxyApi.get(`/stocks/history?stock_id=${stockId}`);
    return response.data;
  } catch (error) {
    console.error(`獲取股票 ${stockId} 歷史股價失敗:`, error.message);
    return [];
  }
}

export async function getStockPredictions(stockId) {
  try {
    const response = await proxyApi.get(`/stocks/predictions?stock_id=${stockId}`);
    return response.data;
  } catch (error) {
    console.error(`獲取股票 ${stockId} 預測數據失敗:`, error.message);
    return null;
  }
}

export async function getStockPrices(stockId) {
  try {
    const response = await api.get(`/stocks/${stockId}/prices`);
    return response.data;
  } catch (error) {
    console.error(`獲取股票 ${stockId} 價格失敗:`, error.message);
    return [];
  }
}

export async function getTechnicalIndicators(stockId) {
  try {
    const response = await api.get(`/features/${stockId}`);
    return response.data;
  } catch (error) {
    console.error(`獲取股票 ${stockId} 技術指標失敗:`, error.message);
    return [];
  }
}

export async function analyzeStock(stockId) {
  try {
    const response = await api.get(`/agent/analyze?query=請分析股票 ${stockId}`);
    return response.data;
  } catch (error) {
    console.error(`分析股票 ${stockId} 失敗:`, error.message);
    return null;
  }
}

export async function chatWithAdvisor(query) {
  try {
    const response = await api.post('/chatbot', { query });
    return response.data.response;
  } catch (error) {
    console.error(`AI 投顧查詢失敗:`, error.message);
    throw error;
  }
}

export async function getPortfolio(stocks, riskLevel) {
  try {
    const response = await api.post('/portfolio', { stocks, risk_level: riskLevel });
    return response.data;
  } catch (error) {
    console.error(`獲取投資組合失敗:`, error.message);
    return null;
  }
}

export async function getHeatmapData() {
  try {
    const response = await api.get('/stocks/heatmap');
    return response.data;
  } catch (error) {
    console.error('獲取熱力圖數據失敗:', error.message);
    return [];
  }
}

export async function createPortfolio(portfolio) {
  try {
    const response = await api.post('/portfolio/create', portfolio);
    return response.data;
  } catch (error) {
    console.error('創建投資組合失敗:', error.message);
    return null;
  }
}

export async function getMarketOverview() {
  try {
    const response = await api.get('/market-overview');
    return response.data;
  } catch (error) {
    console.error('獲取市場概覽數據失敗:', error.message);
    return null;
  }
}