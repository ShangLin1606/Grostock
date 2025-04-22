import { Line } from 'react-chartjs-2';
import { Chart as ChartJS, LineElement, PointElement, LinearScale, TimeScale, Title, Tooltip, Legend } from 'chart.js';
import 'chartjs-adapter-date-fns';

ChartJS.register(LineElement, PointElement, LinearScale, TimeScale, Title, Tooltip, Legend);

function PriceChart({ data }) {
  const chartData = {
    datasets: [
      {
        label: '實際價格',
        data: data.actual.map((point) => ({ x: point.date, y: point.price })),
        borderColor: '#1E40AF',
        fill: false,
      },
      {
        label: '預測價格',
        data: data.predicted.map((point) => ({ x: point.date, y: point.price })),
        borderColor: '#F59E0B',
        borderDash: [5, 5],
        fill: false,
      },
    ],
  };

  const options = {
    scales: {
      x: {
        type: 'time',
        time: {
          unit: 'day',
        },
        title: {
          display: true,
          text: '日期',
        },
      },
      y: {
        title: {
          display: true,
          text: '價格 (TWD)',
        },
      },
    },
    plugins: {
      legend: {
        position: 'top',
      },
    },
  };

  return <Line data={chartData} options={options} />;
}

export default PriceChart;