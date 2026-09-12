import React from 'react';
import { Target, Eye, Clock, AlertTriangle } from 'lucide-react';

export default function MetricsCards({ metrics }) {
  const defaultMetrics = {
    detection_rate: 0,
    interception_rate: 0,
    average_intercept_time: 0,
    false_alarm_rate: 0
  };

  const data = metrics || defaultMetrics;

  const cards = [
    {
      title: 'Detection Rate',
      value: `${(data.detection_rate * 100).toFixed(1)}%`,
      icon: <Target className="w-6 h-6 text-accent-green" />,
      borderClass: 'border-l-accent-green',
      valueClass: 'text-accent-green'
    },
    {
      title: 'Interception Rate',
      value: `${(data.interception_rate * 100).toFixed(1)}%`,
      icon: <Eye className="w-6 h-6 text-accent-blue" />,
      borderClass: 'border-l-accent-blue',
      valueClass: 'text-white'
    },
    {
      title: 'Avg Intercept Time',
      value: `${data.average_intercept_time.toFixed(3)}s`,
      icon: <Clock className="w-6 h-6 text-accent-amber" />,
      borderClass: 'border-l-accent-amber',
      valueClass: 'text-white'
    },
    {
      title: 'False Alarm Rate',
      value: `${(data.false_alarm_rate * 100).toFixed(1)}%`,
      icon: <AlertTriangle className="w-6 h-6 text-accent-red" />,
      borderClass: 'border-l-accent-red',
      valueClass: 'text-accent-red'
    }
  ];

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      {cards.map((card, i) => (
        <div key={i} className={`bg-panel rounded-lg border border-gray-800 border-l-4 ${card.borderClass} p-4 shadow-lg flex items-center justify-between`}>
          <div>
            <div className="text-xs text-gray-500 uppercase font-bold tracking-wider mb-1">{card.title}</div>
            <div className={`text-2xl font-mono font-bold ${card.valueClass}`}>{card.value}</div>
          </div>
          <div className="bg-dark-surface p-2 rounded-full border border-gray-800">
            {card.icon}
          </div>
        </div>
      ))}
    </div>
  );
}
