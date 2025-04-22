import { useState, useEffect } from 'react';
import SignalChart from '../../components/charts/SignalChart';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import { analyzeStock } from '../../utils/api';

function Strategy() {
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const data = await analyzeStock('2330'); // 示例股票
        setAnalysis(data);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching strategy data:', error);
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  if (loading) return <LoadingSpinner message="載入策略數據..." />;

  const signalChartData = {
    dates: analysis ? analysis.strategies.map(s => s.date) : [],
    momentum: analysis ? analysis.strategies.map(s => s.momentum_signal) : [],
    meanReversion: analysis ? analysis.strategies.map(s => s.mean_reversion_signal) : [],
  };

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">策略分析</h1>
      <section className="mb-8">
        <h2 className="text-2xl font-semibold mb-4">信號圖表</h2>
        <SignalChart signals={signalChartData} />
      </section>
      <section>
        <h2 className="text-2xl font-semibold mb-4">回測結果</h2>
        <div className="bg-white p-4 rounded-lg shadow">
          <p>動量策略報酬率: {analysis?.strategies[0]?.momentum_returns?.toFixed(2)}%</p>
          <p>基準報酬率: {analysis?.strategies[0]?.benchmark_returns?.toFixed(2)}%</p>
        </div>
      </section>
    </div>
  );
}

export default Strategy;