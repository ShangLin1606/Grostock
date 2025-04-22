import { useState, useEffect } from 'react';
import HeatmapChart from '../../components/charts/HeatmapChart';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import { getStocks } from '../../utils/api';

function Home() {
  const [stocks, setStocks] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const data = await getStocks();
        // 模擬熱力圖數據
        const heatmapData = data.map(stock => ({
          stock_id: stock.stock_id,
          change: (Math.random() - 0.5) * 0.2, // 模擬漲跌幅
        }));
        setStocks(heatmapData);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching stocks:', error);
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  if (loading) return <LoadingSpinner message="載入市場數據..." />;

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">歡迎來到 Grostock</h1>
      <section className="mb-8">
        <h2 className="text-2xl font-semibold mb-4">股市熱力圖</h2>
        <HeatmapChart data={stocks} />
      </section>
      <section>
        <h2 className="text-2xl font-semibold mb-4">熱門股票</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {stocks.slice(0, 3).map(stock => (
            <div key={stock.stock_id} className="bg-white p-4 rounded-lg shadow">
              <h3 className="text-lg font-medium">{stock.stock_id}</h3>
              <p>漲跌幅: {(stock.change * 100).toFixed(2)}%</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

export default Home;