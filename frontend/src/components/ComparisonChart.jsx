import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer, CartesianGrid } from 'recharts';
import * as api from '../services/api';

export default function ComparisonChart() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchComparison = async () => {
    setLoading(true);
    try {
      const res = await api.getComparison();
      if (res && res.smartscan) {
        setData([
          {
            metric: 'Detection Rate (%)',
            Sequential: res.sequential.detection_rate * 100,
            Random: res.random.detection_rate * 100,
            SmartScan: res.smartscan.detection_rate * 100,
          },
          {
            metric: 'Interception Rate (%)',
            Sequential: res.sequential.interception_rate * 100,
            Random: res.random.interception_rate * 100,
            SmartScan: res.smartscan.interception_rate * 100,
          }
        ]);
      }
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchComparison();
  }, []);

  return (
    <div className="bg-panel rounded-lg border border-gray-800 p-4 shadow-lg h-full flex flex-col">
      <div className="flex justify-between items-center mb-4 border-b border-gray-800 pb-2">
        <h3 className="text-xs font-bold text-gray-400 uppercase tracking-widest">
          Scheduler Performance Comparison
        </h3>
        <button 
          onClick={fetchComparison}
          disabled={loading}
          className="text-xs bg-gray-800 hover:bg-gray-700 text-white px-3 py-1 rounded transition-colors"
        >
          {loading ? 'Running...' : 'Run Comparison'}
        </button>
      </div>

      <div className="flex-1 min-h-[250px]">
        {data.length > 0 ? (
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" vertical={false} />
              <XAxis dataKey="metric" stroke="#9ca3af" tick={{fill: '#9ca3af'}} />
              <YAxis stroke="#9ca3af" tick={{fill: '#9ca3af'}} domain={[0, 100]} />
              <Tooltip cursor={{fill: '#1f2937'}} contentStyle={{backgroundColor: '#111827', borderColor: '#374151'}} />
              <Legend wrapperStyle={{paddingTop: '20px'}} />
              <Bar dataKey="Sequential" fill="#6b7280" radius={[4, 4, 0, 0]} />
              <Bar dataKey="Random" fill="#f59e0b" radius={[4, 4, 0, 0]} />
              <Bar dataKey="SmartScan" fill="#00ff88" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <div className="flex items-center justify-center h-full text-gray-500">
            Click 'Run Comparison' to simulate schedulers
          </div>
        )}
      </div>
    </div>
  );
}
