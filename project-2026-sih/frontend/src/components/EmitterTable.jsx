import React from 'react';

export default function EmitterTable({ emitters }) {
  if (!emitters || emitters.length === 0) {
    return <div className="p-4 bg-panel rounded border border-gray-800 text-gray-500 text-sm">No emitters found.</div>;
  }

  const getTypeColor = (type) => {
    switch (type.toLowerCase()) {
      case 'periodic': return 'text-accent-blue bg-accent-blue/10 border-accent-blue/20';
      case 'frequency_agile': return 'text-accent-amber bg-accent-amber/10 border-accent-amber/20';
      case 'intermittent': return 'text-accent-purple bg-accent-purple/10 border-accent-purple/20';
      default: return 'text-gray-400 bg-gray-800 border-gray-700';
    }
  };

  return (
    <div className="bg-panel rounded-lg border border-gray-800 shadow-lg overflow-hidden">
      <div className="p-4 border-b border-gray-800">
        <h3 className="text-xs font-bold text-gray-400 uppercase tracking-widest">Known Emitters</h3>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead className="bg-dark-surface text-gray-400 text-xs uppercase font-bold border-b border-gray-800">
            <tr>
              <th className="px-4 py-3">ID</th>
              <th className="px-4 py-3">Freq (MHz)</th>
              <th className="px-4 py-3">PRI (μs)</th>
              <th className="px-4 py-3">PW (μs)</th>
              <th className="px-4 py-3">Power (dBm)</th>
              <th className="px-4 py-3">Type</th>
              <th className="px-4 py-3">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-800">
            {emitters.map(e => (
              <tr key={e.id} className="hover:bg-gray-800/50 transition-colors">
                <td className="px-4 py-3 font-mono text-gray-300">{e.id}</td>
                <td className="px-4 py-3 font-mono text-accent-cyan">{e.frequency_mhz?.toFixed(1)}</td>
                <td className="px-4 py-3 font-mono text-gray-400">{e.pri_us?.toFixed(1)}</td>
                <td className="px-4 py-3 font-mono text-gray-400">{e.pulse_width_us?.toFixed(1)}</td>
                <td className="px-4 py-3 font-mono text-gray-400">{e.power_dbm?.toFixed(1)}</td>
                <td className="px-4 py-3">
                  <span className={`px-2 py-0.5 rounded text-xs border ${getTypeColor(e.emitter_type)}`}>
                    {e.emitter_type}
                  </span>
                </td>
                <td className="px-4 py-3">
                  {e.active ? (
                    <span className="flex items-center text-accent-green text-xs"><div className="w-2 h-2 rounded-full bg-accent-green mr-1.5 animate-pulse"></div> Active</span>
                  ) : (
                    <span className="flex items-center text-gray-500 text-xs"><div className="w-2 h-2 rounded-full bg-gray-600 mr-1.5"></div> Inactive</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
