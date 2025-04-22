import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import { getStocks } from '../../utils/api';

function StockList() {
  const [stocks, setStocks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  useEffect(() => {
    async function fetchData() {
      try {
        const data = await getStocks();
        setStocks(data);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching stocks:', error);
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  const filteredStocks = stocks.filter(stock =>
    stock.stock_id.includes(search) || stock.stock_name.includes(search)
  );

  if (loading) return <LoadingSpinner message="載入股票列表..." />;

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">股票列表</h1>
      <input
        type="text"
        placeholder="搜尋股票 ID 或名稱..."
        value={search}
        onChange={e => setSearch(e.target.value)}
        className="w-full p-2 mb-4 border rounded-md"
      />
      <div className="bg-white rounded-lg shadow overflow-x-auto">
        <table className="min-w-full">
          <thead className="bg-gray-200">
            <tr>
              <th className="px-4 py-2 text-left">股票 ID</th>
              <th className="px-4 py-2 text-left">名稱</th>
              <th className="px-4 py-2 text-left">操作</th>
            </tr>
          </thead>
          <tbody>
            {filteredStocks.map(stock => (
              <tr key={stock.stock_id} className="border-t">
                <td className="px-4 py-2">{stock.stock_id}</td>
                <td className="px-4 py-2">{stock.stock_name}</td>
                <td className="px-4 py-2">
                  <Link to={`/stocks/${stock.stock_id}`} className="text-blue-600 hover:underline">查看詳情</Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default StockList;