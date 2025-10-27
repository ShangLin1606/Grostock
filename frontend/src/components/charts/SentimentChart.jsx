import { Bar } from 'react-chartjs-2';
import { Chart as ChartJS, BarElement, CategoryScale, LinearScale, Title, Tooltip, Legend } from 'chart.js';

ChartJS.register(BarElement, CategoryScale, LinearScale, Title, Tooltip, Legend);

function SentimentChart({ sentiments }) {
  const chartData = {
    labels: sentiments.dates,
    datasets: [
      {
        label: '情緒分數',
        data: sentiments.scores,
        backgroundColor: '#3B82F6', // 深藍（主色）
      },
    ],
  };

  const options = {
    scales: {
      y: {
        title: {
          display: true,
          text: '情緒分數',
          color: '#F3F4F6', // 文字使用 text 色
        },
        ticks: {
          color: '#F3F4F6',
        },
        min: -1,
        max: 1,
      },
      x: {
        title: {
          display: true,
          text: '日期',
          color: '#F3F4F6',
        },
        ticks: {
          color: '#F3F4F6',
        },
      },
    },
    plugins: {
      legend: {
        position: 'top',
        labels: {
          color: '#F3F4F6',
        },
      },
    },
  };

  return <Bar data={chartData} options={options} />;
}

export default SentimentChart;