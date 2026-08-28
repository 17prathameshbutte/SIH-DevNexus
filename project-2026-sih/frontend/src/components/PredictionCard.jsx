import React from 'react';
import { Brain } from 'lucide-react';

export default function PredictionCard({ decision }) {
  if (!decision) return null;

  const getRecommendationBadge = (prob) => {
    if (prob > 0.8) return <span className="bg-accent-green/20 text-accent-green border border-accent-green px-2 py-0.5 rounded text-xs">HIGH PRIORITY</span>;
    if (prob > 0.4) return <span className="bg-accent-amber/20 text-accent-amber border border-accent-amber px-2 py-0.5 rounded text-xs">MEDIUM</span>;
    return <span className="bg-gray-700 text-gray-300 border border-gray-600 px-2 py-0.5 rounded text-xs">LOW</span>;
  };

  return (
    <div className="bg-panel rounded-lg border border-gray-800 shadow-lg p-4">
      <div className="flex justify-between items-center border-b border-gray-800 pb-2 mb-4">
        <h3 className="text-xs font-bold text-gray-400 uppercase tracking-widest flex items-center">
          <Brain className="w-4 h-4 mr-2" /> Decision Analysis
        </h3>
        {getRecommendationBadge(decision.probability)}
      </div>

      <div className="flex items-center justify-between mb-4">
        <span className="text-sm text-gray-400">Selected Band</span>
        <span className="font-mono text-xl text-accent-cyan">{decision.selected_band}</span>
      </div>

      <div className="space-y-3">
        {decision.ranking && decision.ranking[0] && decision.ranking[0].components && 
          Object.entries(decision.ranking[0].components).map(([key, val]) => (
            <div key={key}>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-gray-400 capitalize">{key.replace('_', ' ')}</span>
                <span className="font-mono">{(val*100).toFixed(1)}%</span>
              </div>
              <div className="w-full bg-gray-800 rounded-full h-1.5">
                <div className="bg-accent-purple h-1.5 rounded-full" style={{ width: `${Math.min(100, Math.max(0, val*100))}%` }}></div>
              </div>
            </div>
          ))
        }
      </div>

      <div className="mt-4 pt-3 border-t border-gray-800 flex justify-between items-center">
        <span className="text-xs text-gray-500 uppercase">Final Priority Score</span>
        <span className="font-mono text-lg text-accent-green">
          {decision.ranking && decision.ranking[0] ? decision.ranking[0].priority_score.toFixed(3) : 'N/A'}
        </span>
      </div>
    </div>
  );
}
