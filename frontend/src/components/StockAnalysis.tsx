import React, { useState } from 'react';
import { analyzeStock, fetchTechnicalIndicators, TechnicalIndicator, AgentResponse } from '../api';

const StockAnalysis: React.FC = () => {
  const [stockId, setStockId] = useState('');
  const [analysis, setAnalysis] = useState<AgentResponse | null>(null);
  const [indicators, setIndicators] = useState<TechnicalIndicator[]>([]);
  const [loading, setLoading] = useState(false);

  const handleAnalyze = async () => {
    setLoading(true);
    try {
      const analysisData = await analyzeStock(`請分析股票 ${stockId}`);
      const indicatorData = await fetchTechnicalIndicators(stockId);
      setAnalysis(analysisData);
      setIndicators(indicatorData.slice(-1)); // 只顯示最新一天的技術指標
    } catch (error) {
      console.error('Error analyzing stock:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2>股票分析</h2>
      <input
        type="text"
        value={stockId}
        onChange={e => setStockId(e.target.value)}
        placeholder="輸入股票代碼（例如 2330）"
      />
      <button onClick={handleAnalyze} disabled={loading}>
        {loading ? '分析中...' : '分析'}
      </button>

      {analysis && (
        <div>
          <h3>價格預測</h3>
          <ul>
            {Object.entries(analysis.predictions).map(([key, value]) => (
              <li key={key}>{key}: {value.toFixed(2)}</li>
            ))}
          </ul>
          <h3>交易策略</h3>
          <ul>
            {Object.entries(analysis.strategies).map(([key, value]) => (
              <li key={key}>{key}: {value > 0 ? '買入' : '賣出'}</li>
            ))}
          </ul>
          <h3>風險評估</h3>
          <ul>
            {Object.entries(analysis.risks).map(([key, value]) => (
              <li key={key}>{key}: {value.toFixed(4)}</li>
            ))}
          </ul>
        </div>
      )}

      {indicators.length > 0 && (
        <div>
          <h3>最新技術指標</h3>
          <table>
            <thead>
              <tr>
                <th>指標</th>
                <th>數值</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(indicators[0]).map(([key, value]) => 
                key !== 'stock_id' && key !== 'date' && value !== null ? (
                  <tr key={key}>
                    <td>{key}</td>
                    <td>{typeof value === 'number' ? value.toFixed(2) : value}</td>
                  </tr>
                ) : null
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default StockAnalysis;