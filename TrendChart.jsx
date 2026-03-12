import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Filler,
  Legend,
} from 'chart.js';
import { Line } from 'react-chartjs-2';

// Registrera Chart.js moduler
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Filler,
  Legend
);

const TrendChart = ({ dataLogs }) => {
  // TRUE DARK TEMATING
  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false, // Vi håller det minimalistiskt
      },
      tooltip: {
        backgroundColor: '#1e1e1e',
        titleColor: '#d62828',
        bodyColor: '#fff',
        borderColor: '#333',
        borderWidth: 1,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 10,
        grid: { color: '#222' },
        ticks: { color: '#666' },
      },
      x: {
        grid: { display: false },
        ticks: { color: '#666' },
      },
    },
  };

  // Mappa data från lokala loggar (Dagsform 1-10)
  const chartData = {
    labels: dataLogs.map(log => log.date).slice(-7), // Senaste 7 dagarna
    datasets: [
      {
        fill: true,
        label: 'Dagsform',
        data: dataLogs.map(log => log.mood).slice(-7),
        borderColor: '#d62828', // Rova-Röd
        backgroundColor: 'rgba(214, 40, 40, 0.1)',
        tension: 0.4, // Gör linjen mjuk
        pointRadius: 4,
        pointBackgroundColor: '#d62828',
      },
    ],
  };

  return (
    <div style={{ height: '200px', width: '100%', marginTop: '20px' }}>
      <Line options={options} data={chartData} />
    </div>
  );
};

export default TrendChart;
