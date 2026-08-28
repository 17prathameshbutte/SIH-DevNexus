import React, { useState, useEffect } from 'react';
import { X, Zap, CheckCircle2, ChevronRight } from 'lucide-react';
import * as api from '../services/api';

export default function DemoMode({ onClose }) {
  const [step, setStep] = useState(0);
  const [results, setResults] = useState(null);

  const steps = [
    "Loading Dataset...",
    "Running Sequential Scan (Baseline)...",
    "Running SmartScan (RL Agent)...",
    "Generating Comparison..."
  ];

  useEffect(() => {
    let current = 0;
    const interval = setInterval(async () => {
      current++;
      setStep(current);
      if (current === 3) {
        // At final step, fetch comparison
        try {
          const res = await api.getComparison();
          setResults(res);
        } catch(e) {
          console.error(e);
        }
        clearInterval(interval);
      }
    }, 2000); // 2s per fake step for dramatic effect

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="fixed inset-0 bg-midnight/90 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-panel border border-purple-500/50 rounded-xl max-w-3xl w-full shadow-[0_0_50px_rgba(168,85,247,0.15)] overflow-hidden">
        
        <div className="bg-gradient-to-r from-purple-900/50 to-panel p-4 border-b border-purple-500/30 flex justify-between items-center">
          <h2 className="text-xl font-bold text-white flex items-center">
            <Zap className="w-6 h-6 text-accent-purple mr-2" />
            SMARTSCAN DEMONSTRATION
          </h2>
          <button onClick={onClose} className="text-gray-400 hover:text-white">
            <X className="w-6 h-6" />
          </button>
        </div>

        <div className="p-8">
          {!results ? (
            <div className="space-y-6">
              {steps.map((text, i) => (
                <div key={i} className={`flex items-center ${i > step ? 'opacity-30' : 'opacity-100'} transition-opacity duration-500`}>
                  {i < step ? (
                    <CheckCircle2 className="w-6 h-6 text-accent-green mr-4" />
                  ) : i === step ? (
                    <div className="w-6 h-6 border-2 border-accent-cyan border-t-transparent rounded-full animate-spin mr-4"></div>
                  ) : (
                    <div className="w-6 h-6 border-2 border-gray-700 rounded-full mr-4"></div>
                  )}
                  <span className={`text-lg ${i === step ? 'text-white font-bold' : 'text-gray-400'}`}>{text}</span>
                </div>
              ))}
            </div>
          ) : (
            <div className="animate-in fade-in zoom-in duration-700">
              <h3 className="text-center text-gray-400 uppercase tracking-widest text-sm mb-8">Performance Improvement</h3>
              
              <div className="grid grid-cols-2 gap-8 mb-8">
                <div className="bg-dark-surface rounded-lg p-6 border border-gray-800 text-center relative overflow-hidden">
                  <div className="absolute top-0 left-0 w-full h-1 bg-gray-600"></div>
                  <div className="text-gray-500 text-sm font-bold uppercase mb-2">Sequential</div>
                  <div className="text-4xl font-mono text-white mb-1">
                    {(results.sequential.detection_rate * 100).toFixed(1)}%
                  </div>
                  <div className="text-xs text-gray-500">Detection Rate</div>
                </div>

                <div className="bg-dark-surface rounded-lg p-6 border border-accent-green/50 text-center relative overflow-hidden shadow-[0_0_30px_rgba(0,255,136,0.1)]">
                  <div className="absolute top-0 left-0 w-full h-1 bg-accent-green"></div>
                  <div className="text-accent-green text-sm font-bold uppercase mb-2 flex items-center justify-center">
                    <Zap className="w-4 h-4 mr-1"/> SmartScan
                  </div>
                  <div className="text-5xl font-mono text-white mb-1 font-bold">
                    {(results.smartscan.detection_rate * 100).toFixed(1)}%
                  </div>
                  <div className="text-xs text-gray-400">Detection Rate</div>
                </div>
              </div>

              <div className="flex justify-center items-center space-x-4 text-center">
                <div className="bg-accent-green/10 text-accent-green px-4 py-2 rounded-full font-bold border border-accent-green/30">
                  + {((results.smartscan.detection_rate - results.sequential.detection_rate) * 100).toFixed(1)}% Improvement
                </div>
                <div className="bg-accent-blue/10 text-accent-blue px-4 py-2 rounded-full font-bold border border-accent-blue/30">
                  {results.sequential.average_intercept_time > 0 ? 
                    ((results.sequential.average_intercept_time / (results.smartscan.average_intercept_time || 1)).toFixed(1)) : '∞'}x Faster Intercept
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="bg-gray-900 p-4 flex justify-end">
          <button 
            onClick={onClose}
            className="bg-gray-800 hover:bg-gray-700 text-white px-6 py-2 rounded transition-colors"
          >
            {results ? 'Close Results' : 'Cancel Demo'}
          </button>
        </div>
      </div>
    </div>
  );
}
