import { useState, useEffect } from 'react';
import HeatmapChart from '../../components/charts/HeatmapChart';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import { getHeatmapData } from '../../utils/api';

function Home() {
  const [stocks, setStocks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchData() {
      try {
        console.log('開始獲取熱力圖數據');
        const data = await getHeatmapData();
        console.log('熱力圖 API 回應:', data);
        if (data.length === 0) {
          setError('無熱力圖數據，請確認後端 API 或 stock_prices 表是否有最新數據。');
        }
        setStocks(data);
        setLoading(false);
        console.log('熱力圖數據獲取成功');
      } catch (error) {
        console.error(`獲取熱力圖數據失敗: ${error.message}`);
        setError('無法連接到後端 API，請檢查 http://localhost:8000/stocks/heatmap 或後端服務是否正常運行。');
        setStocks([]);
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  const hotStocks = stocks
    .sort((a, b) => (b.popularity_score || 0) - (a.popularity_score || 0))
    .slice(0, 3);

  if (loading) return <LoadingSpinner message="載入市場數據..." />;

  return (
    <div className="card">
      <h1 className="text-3xl font-bold mb-6 text-text">歡迎來到 Grostock</h1>
      <section className="mb-8">
        <h2 className="text-2xl font-semibold mb-4 text-text">股市熱力圖</h2>
        {error ? (
          <p className="text-neutral">{error}</p>
        ) : stocks.length === 0 ? (
          <p className="text-neutral">無熱力圖數據，請檢查後端服務或資料庫。</p>
        ) : (
          <HeatmapChart data={stocks} />
        )}
      </section>
      <section>
        <h2 className="text-2xl font-semibold mb-4 text-text">熱門股票</h2>
        {hotStocks.length === 0 ? (
          <p className="text-neutral">無熱門股票數據，請確認資料庫 popularity_score 欄位或後端 API。</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {hotStocks.map(stock => (
              <div key={stock.stock_id} className="bg-gray-700 p-4 rounded-lg shadow">
                <h3 className="text-lg font-medium text-text">{stock.stock_id} - {stock.stock_name}</h3>
                <p className={stock.change >= 0 ? 'text-up' : 'text-down'}>
                  漲跌幅: {(stock.change * 100).toFixed(2)}%
                </p>
                <p className="text-neutral">關注度分數: {(stock.popularity_score || 0).toFixed(2)}</p>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

export default Home;