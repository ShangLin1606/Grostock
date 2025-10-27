import { useState, useEffect } from 'react';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import { createPortfolio } from '../../utils/api';

function Portfolio() {
  const [portfolio, setPortfolio] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedStocks, setSelectedStocks] = useState([]);
  const [riskLevel, setRiskLevel] = useState('medium');

  const handleSelectStock = (stockId) => {
    setSelectedStocks(prev => 
      prev.includes(stockId) ? prev.filter(id => id !== stockId) : [...prev, stockId]
    );
  };

  const handleCreatePortfolio = async () => {
    if (selectedStocks.length === 0) {
      setError('請至少選擇一支股票');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      console.log('創建投資組合:', { stocks: selectedStocks, riskLevel });
      const portfolioData = await createPortfolio({
        stocks: selectedStocks.map(stockId => ({ stock_id: stockId })),
        risk_level: riskLevel,
      });
      if (!portfolioData || !portfolioData.stocks) {
        throw new Error('投資組合數據無效');
      }
      setPortfolio(portfolioData);
      console.log('投資組合創建成功:', portfolioData);
    } catch (err) {
      console.error('創建投資組合失敗:', err.message);
      setError(`無法創建投資組合，請稍後再試。錯誤: ${err.message}`);
      setPortfolio(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h1 className="text-3xl font-bold mb-6 text-text">投資組合</h1>
      <div className="mb-4">
        <label className="text-text mr-2">選擇風險等級:</label>
        <select
          value={riskLevel}
          onChange={e => setRiskLevel(e.target.value)}
          className="p-2 border rounded-md bg-gray-600 text-text border-gray-500"
        >
          <option value="low">低風險</option>
          <option value="medium">中風險</option>
          <option value="high">高風險</option>
        </select>
      </div>
      <div className="mb-4">
        <h2 className="text-xl font-semibold mb-2 text-text">選擇股票</h2>
        {/* 假設有一個簡單的股票選擇清單 */}
        <div className="grid grid-cols-3 gap-2">
          {['0050', '0051', '2330'].map(stockId => (
            <label key={stockId} className="flex items-center text-text">
              <input
                type="checkbox"
                checked={selectedStocks.includes(stockId)}
                onChange={() => handleSelectStock(stockId)}
                className="mr-2"
              />
              {stockId}
            </label>
          ))}
        </div>
      </div>
      <button
        onClick={handleCreatePortfolio}
        className="btn mb-4"
        disabled={loading}
      >
        創建投資組合
      </button>
      {loading && <LoadingSpinner message="創建投資組合中..." />}
      {error && <p className="text-neutral mb-4">{error}</p>}
      {portfolio && (
        <div className="bg-gray-700 rounded-lg shadow p-4">
          <h2 className="text-xl font-semibold mb-4 text-text">投資組合建議</h2>
          <p className="text-text mb-2">風險等級: {portfolio.risk_level}</p>
          <div className="overflow-x-auto">
            <table className="min-w-full">
              <thead className="bg-gray-600">
                <tr>
                  <th className="px-4 py-2 text-left text-text">股票 ID</th>
                  <th className="px-4 py-2 text-left text-text">權重</th>
                  <th className="px-4 py-2 text-left text-text">預測回報</th>
                </tr>
              </thead>
              <tbody>
                {portfolio.stocks && portfolio.stocks.length > 0 ? (
                  portfolio.stocks.map((stock, index) => (
                    <tr key={index} className="border-t border-gray-600">
                      <td className="px-4 py-2">{stock.stock_id}</td>
                      <td className="px-4 py-2">{(stock.weight * 100).toFixed(2)}%</td>
                      <td className="px-4 py-2">{stock.predicted_return?.toFixed(2) || 'N/A'}</td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="3" className="px-4 py-2 text-neutral">無股票數據</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

export default Portfolio;