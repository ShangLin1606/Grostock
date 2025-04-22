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
        backgroundColor: '#1E40AF',
      },
    ],
  };

  const options = {
    scales: {
      y: {
        title: {
          display: true,
          text: '情緒分數',
        },
        min: -1,
        max: 1,
      },
    },
    plugins: {
      legend: {
        position: 'top',
      },
    },
  };

  return <Bar data={chartData} options={options} />;
}

export default SentimentChart;