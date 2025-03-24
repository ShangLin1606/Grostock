import React, { useEffect, useState } from 'react';
import { fetchStocks, Stock } from '../api';

const StockList: React.FC = () => {
  const [stocks, setStocks] = useState<Stock[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadStocks = async () => {
      try {
        const data = await fetchStocks();
        setStocks(data);
      } catch (error) {
        console.error('Error fetching stocks:', error);
      } finally {
        setLoading(false);
      }
    };
    loadStocks();
  }, []);

  if (loading) return <p>載入中...</p>;

  return (
    <div>
      <h2>股票列表</h2>
      <table>
        <thead>
          <tr>
            <th>股票代碼</th>
            <th>股票名稱</th>
          </tr>
        </thead>
        <tbody>
          {stocks.map(stock => (
            <tr key={stock.stock_id}>
              <td>{stock.stock_id}</td>
              <td>{stock.stock_name}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default StockList;