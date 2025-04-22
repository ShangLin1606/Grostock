import { Line } from 'react-chartjs-2';

function SignalChart({ signals }) {
  const chartData = {
    labels: signals.dates,
    datasets: [
      {
        label: '動量信號',
        data: signals.momentum,
        borderColor: '#1E40AF',
        fill: false,
      },
      {
        label: '均值回歸信號',
        data: signals.meanReversion,
        borderColor: '#F59E0B',
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

export default SignalChart;