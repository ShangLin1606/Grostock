import { Line } from 'react-chartjs-2';
import { Chart as ChartJS, LineElement, PointElement, LinearScale, CategoryScale, Title, Tooltip, Legend } from 'chart.js';

ChartJS.register(LineElement, PointElement, LinearScale, CategoryScale, Title, Tooltip, Legend);

function SignalChart({ signals }) {
  const chartData = {
    labels: signals.dates,
    datasets: [
      {
        label: '動量信號',
        data: signals.momentum,
        borderColor: '#F43F5E', // 紅色（漲）
        fill: false,
      },
      {
        label: '均值回歸信號',
        data: signals.meanReversion,
        borderColor: '#10B981', // 綠色（跌）
        fill: false,
      },
    ],
  };

  const options = {
    scales: {
      y: {
        title: {
          display: true,
          text: '信號值',
          color: '#F3F4F6', // 文字使用 text 色
        },
        ticks: {
          color: '#F3F4F6',
        },
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

  return <Line data={chartData} options={options} />;
}

export default SignalChart;