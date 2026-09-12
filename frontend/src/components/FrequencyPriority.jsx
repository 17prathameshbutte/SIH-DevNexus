import React from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';

export default function FrequencyPriority({ rankings }) {
  if (!rankings || rankings.length === 0) {
    return (
      <div className="bg-panel rounded-lg border border-gray-800 shadow-lg p-4 h-full flex flex-col">
         <h3 className="text-xs font-bold text-gray-400 uppercase tracking-widest border-b border-gray-800 pb-2 mb-4">
          Frequency Priority
        </h3>
        <div className="flex-1 flex items-center justify-center text-gray-500 text-sm">
          No ranking data available
        </div>
      </div>
    );
  }

  const data = rankings.slice(0, 10).map(r => ({
    name: `Band ${r.band_id}`,
    prob: r.probability * 100,
    score: r.priority_score,
    center: r.center_mhz
  }));

  return (
    <div className="bg-panel rounded-lg border border-gray-800 shadow-lg p-4 h-full flex flex-col">
      <h3 className="text-xs font-bold text-gray-400 uppercase tracking-widest border-b border-gray-800 pb-2 mb-4">
        Frequency Priority (Top 10)
      </h3>
      <div className="flex-1 min-h-[250px]">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            layout="vertical"
            data={data}
            margin={{ top: 0, right: 30, left: 20, bottom: 0 }}
          >
            <XAxis type="number" domain={[0, 100]} hide />
            <YAxis dataKey="name" type="category" axisLine={false} tickLine={false} tick={{fill: '#9ca3af', fontSize: 12}} width={70} />
            <Tooltip 
              cursor={{fill: '#1f2937'}}
              contentStyle={{backgroundColor: '#111827', borderColor: '#374151', color: '#fff'}}
              formatter={(value, name) => [`${value.toFixed(1)}%`, 'Probability']}
            />
            <Bar dataKey="prob" radius={[0, 4, 4, 0]}>
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={index === 0 ? '#00ff88' : `rgba(0, 255, 136, ${Math.max(0.2, 1 - index*0.1)})`} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
