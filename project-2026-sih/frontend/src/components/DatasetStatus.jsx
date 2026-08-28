import React, { useEffect, useState } from 'react';
import { File, Activity, Maximize, Clock, Database, Layers } from 'lucide-react';
import * as api from '../services/api';

export default function DatasetStatus() {
  const [summary, setSummary] = useState(null);

  useEffect(() => {
    api.getDatasetSummary().then(setSummary).catch(console.error);
  }, []);

  if (!summary) return <div className="p-4 bg-gray-900/50 backdrop-blur-sm rounded-lg border border-gray-700/50 text-sm text-gray-500">Loading dataset...</div>;

  return (
    <div className="bg-gray-900/50 backdrop-blur-sm rounded-lg border border-gray-700/50 p-4 space-y-3 shadow-lg">
      <div className="flex items-center justify-between border-b border-gray-700/50 pb-2">
        <h3 className="text-xs font-bold text-gray-400 uppercase tracking-widest flex items-center">
          <Database className="w-4 h-4 mr-2 text-cyan-400" /> Dataset Status
        </h3>
        <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse"></div>
      </div>
      
      <div className="space-y-2">
        <div className="flex justify-between items-center text-sm">
          <span className="text-gray-400 flex items-center"><File className="w-3.5 h-3.5 mr-1.5"/> File</span>
          <span className="font-mono text-white truncate max-w-[140px]" title={summary.filename}>
            {summary.filename ? summary.filename.split('/').pop() : 'N/A'}
          </span>
        </div>
        <div className="flex justify-between items-center text-sm">
          <span className="text-gray-400 flex items-center"><Activity className="w-3.5 h-3.5 mr-1.5"/> Emitters</span>
          <span className="font-mono text-cyan-400 font-bold">{summary.num_transmitters || 0}</span>
        </div>
        <div className="flex justify-between items-center text-sm">
          <span className="text-gray-400 flex items-center"><Layers className="w-3.5 h-3.5 mr-1.5"/> Bands</span>
          <span className="font-mono text-gray-300">{summary.num_bands || 0}</span>
        </div>
        <div className="flex justify-between items-center text-sm">
          <span className="text-gray-400 flex items-center"><Maximize className="w-3.5 h-3.5 mr-1.5"/> Pulses</span>
          <span className="font-mono text-gray-300">{(summary.num_pulses || 0).toLocaleString()}</span>
        </div>
        {summary.frequency_range && (
          <div className="flex justify-between items-center text-sm">
            <span className="text-gray-400 flex items-center"><Clock className="w-3.5 h-3.5 mr-1.5"/> Freq Range</span>
            <span className="font-mono text-gray-300">
              {(summary.frequency_range.min / 1000).toFixed(1)}-{(summary.frequency_range.max / 1000).toFixed(1)} GHz
            </span>
          </div>
        )}
      </div>
    </div>
  );
}
