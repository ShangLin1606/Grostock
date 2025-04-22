import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import PriceChart from '../../components/charts/PriceChart';
import SentimentChart from '../../components/charts/SentimentChart';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import { getStockPrices, getTechnicalIndicators, analyzeStock } from '../../utils/api';

function StockDetail() {
  const { stockId } = useParams();
  const [prices, setPrices] = useState([]);
  const [indicators, setIndicators] = useState([]);
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const [priceData, indicatorData, analysisData] = await Promise.all([
          getStockPrices(stockId),
          getTechnicalIndicators(stockId),
          analyzeStock(stockId),
        ]);
        setPrices(priceData);
        setIndicators(indicatorData);
        setAnalysis(analysisData);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching stock data:', error);
        setLoading(false);
      }
    }
    fetchData();
  }, [stockId]);

  if (loading) return <LoadingSpinner message="載入股票數據..." />;

  const priceChartData = {
    actual: prices.map(p => ({ date: p.date, price: p.close_price })),
    predicted: analysis ? analysis.predictions.map(p => ({ date: p.date, price: p.lstm_pred })) : [],
  };

  const sentimentChartData = {
    dates: analysis ? analysis.news_analysis.map(n => n.date) : [],
    scores: analysis ? analysis.news_analysis.map(n => n.sentiment === 'POSITIVE' ? 1 : n.sentiment === 'NEGATIVE' ? -1 : 0) : [],
  };

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">股票詳情: {stockId}</h1>
      <section className="mb-8">
        <h2 className="text-2xl font-semibold mb-4">價格走勢與預測</h2>
        <PriceChart data={priceChartData} />
      </section>
      <section className="mb-8">
        <h2 className="text-2xl font-semibold mb-4">技術指標</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {indicators.slice(-1).map(ind => (
            <div key={ind.date} className="bg-white p-4 rounded-lg shadow">
              <p>SMA 20: {ind.sma_20?.toFixed(2)}</p>
              <p>EMA 20: {ind.ema_20?.toFixed(2)}</p>
              <p>RSI 14: {ind.rsi_14?.toFixed(2)}</p>
            </div>
          ))}
        </div>
      </section>
      <section>
        <h2 className="text-2xl font-semibold mb-4">新聞與聲量</h2>
        <SentimentChart sentiments={sentimentChartData} />
        <div className="mt-4">
          {analysis?.news_analysis?.map(n => (
            <div key={n.date} className="bg-white p-4 rounded-lg shadow mb-4">
              <p className="font-medium">{n.title}</p>
              <p className="text-gray-600">日期: {n.date} | 情緒: {n.sentiment}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

export default StockDetail;