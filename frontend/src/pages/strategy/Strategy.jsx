import { useState, useEffect } from 'react';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import axios from 'axios';
import * as d3 from 'd3';

function Strategy() {
  const [strategyData, setStrategyData] = useState([]);
  const [marketData, setMarketData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchData() {
      try {
        console.log('開始獲取策略和市場數據');
        const strategyResponse = await axios.get('http://localhost:8000/strategies');
        const marketResponse = await axios.get('http://localhost:8000/market-index');
        setStrategyData(strategyResponse.data);
        setMarketData(marketResponse.data);
        setLoading(false);
        console.log('策略和市場數據獲取成功');
        renderChart(strategyResponse.data, marketResponse.data);
      } catch (error) {
        console.error('獲取數據失敗:', error.message);
        setError('無法獲取策略或市場數據，請檢查後端服務。');
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  const renderChart = (strategyData, marketData) => {
    const svg = d3.select("#strategy-chart")
      .attr('width', 800)
      .attr('height', 400);

    svg.selectAll('*').remove();

    const margin = { top: 20, right: 30, bottom: 30, left: 50 };
    const width = 800 - margin.left - margin.right;
    const height = 400 - margin.top - margin.bottom;

    const g = svg.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    const x = d3.scaleTime()
      .domain(d3.extent(strategyData, d => new Date(d.date)))
      .range([0, width]);

    const y = d3.scaleLinear()
      .domain([0, d3.max([...strategyData.map(d => d.return), ...marketData.map(d => d.value)])])
      .range([height, 0]);

    const line = d3.line()
      .x(d => x(new Date(d.date)))
      .y(d => y(d.return || d.value));

    g.append('path')
      .datum(strategyData)
      .attr('fill', 'none')
      .attr('stroke', '#10B981')
      .attr('stroke-width', 2)
      .attr('d', line);

    g.append('path')
      .datum(marketData)
      .attr('fill', 'none')
      .attr('stroke', '#F43F5E')
      .attr('stroke-width', 2)
      .attr('d', line);

    g.append('g')
      .attr('transform', `translate(0,${height})`)
      .call(d3.axisBottom(x));

    g.append('g')
      .call(d3.axisLeft(y));
  };

  if (loading) return <LoadingSpinner message="載入策略數據..." />;

  return (
    <div className="card">
      <h1 className="text-3xl font-bold mb-6 text-text">策略分析</h1>
      {error ? (
        <p className="text-neutral">{error}</p>
      ) : (
        <div>
          <div className="bg-gray-700 rounded-lg shadow p-4 mb-4">
            <h2 className="text-2xl font-semibold mb-4 text-text">策略表現與大盤比較</h2>
            <svg id="strategy-chart"></svg>
            <div className="flex items-center mt-4">
              <div className="w-4 h-4 bg-up mr-2"></div>
              <span className="text-text">策略表現</span>
              <div className="w-4 h-4 bg-down ml-4 mr-2"></div>
              <span className="text-text">台股加權指數</span>
            </div>
          </div>
          <div className="bg-gray-700 rounded-lg shadow p-4">
            <h2 className="text-2xl font-semibold mb-4 text-text">策略詳情</h2>
            {strategyData.length > 0 ? (
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-text"><strong>總收益率:</strong> {(strategyData[strategyData.length - 1]?.return || 0).toFixed(2)}%</p>
                  <p className="text-text"><strong>年化收益率:</strong> {(strategyData[strategyData.length - 1]?.annualized_return || 0).toFixed(2)}%</p>
                </div>
                <div>
                  <p className="text-text"><strong>最大回撤:</strong> {(strategyData[strategyData.length - 1]?.max_drawdown || 0).toFixed(2)}%</p>
                  <p className="text-text"><strong>夏普比率:</strong> {(strategyData[strategyData.length - 1]?.sharpe_ratio || 0).toFixed(2)}</p>
                </div>
              </div>
            ) : (
              <p className="text-neutral">無策略數據</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default Strategy;