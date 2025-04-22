import { useState, useEffect } from 'react';
import HeatmapChart from '../../components/charts/HeatmapChart';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import { getStocks } from '../../utils/api';

function Heatmap() {
  const [stocks, setStocks] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const data = await getStocks();
        const heatmapData = data.map(stock => ({
          stock_id: stock.stock_id,
          change: (Math.random() - 0.5) * 0.2, // 模擬漲跌幅
        }));
        setStocks(heatmapData);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching heatmap data:', error);
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  if (loading) return <LoadingSpinner message="載入熱力圖數據..." />;

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">股市熱力圖</h1>
      <HeatmapChart data={stocks} />
    </div>
  );
}

export default Heatmap;