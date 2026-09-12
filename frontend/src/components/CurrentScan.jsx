import React from 'react';
import { Target, Zap, Clock, Activity } from 'lucide-react';

export default function CurrentScan({ step }) {
  if (!step) {
    return (
      <div className="bg-panel rounded-lg border border-gray-800 p-4 shadow-lg min-h-[150px] flex items-center justify-center">
        <span className="text-gray-500">Waiting for simulation to start...</span>
      </div>
    );
  }

  const isHit = step.result;

  return (
    <div className={`bg-panel rounded-lg border p-4 shadow-lg transition-colors duration-300 ${isHit ? 'border-accent-green shadow-[0_0_15px_rgba(0,255,136,0.1)]' : 'border-gray-800'}`}>
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-1">Current Scan</h3>
          <div className="flex items-baseline space-x-2">
            <span className="text-3xl font-mono font-bold text-white">Band {step.band_id}</span>
            <span className="text-lg text-gray-400 font-mono">{step.band_center_mhz?.toFixed(1)} MHz</span>
          </div>
        </div>
        <div className={`px-4 py-1 rounded font-bold tracking-widest text-sm ${isHit ? 'bg-accent-green text-midnight animate-pulse' : 'bg-accent-red/20 text-accent-red border border-accent-red/50'}`}>
          {isHit ? 'HIT' : 'MISS'}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 mt-4">
        <div className="bg-dark-surface p-3 rounded border border-gray-800">
          <div className="text-xs text-gray-500 mb-1 flex items-center"><Clock className="w-3 h-3 mr-1"/> Step / Time</div>
          <div className="font-mono text-white">{step.step} / {step.time?.toFixed(3)}s</div>
        </div>
        <div className="bg-dark-surface p-3 rounded border border-gray-800">
          <div className="text-xs text-gray-500 mb-1 flex items-center"><Activity className="w-3 h-3 mr-1"/> Pulses</div>
          <div className="font-mono text-accent-cyan">{step.num_pulses || 0} detected</div>
        </div>
      </div>
    </div>
  );
}
