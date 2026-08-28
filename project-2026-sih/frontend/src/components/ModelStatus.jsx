import React, { useState, useEffect } from 'react';
import { BrainCircuit, Loader2 } from 'lucide-react';
import * as api from '../services/api';

export default function ModelStatus() {
  const [status, setStatus] = useState(null);
  const [pipelineStatus, setPipelineStatus] = useState(null);
  const [training, setTraining] = useState(false);

  const fetchStatus = () => {
    Promise.all([api.getModelStatus(), api.getPipelineStatus()])
      .then(([model, pipeline]) => {
        setStatus(model);
        setPipelineStatus(pipeline);
      })
      .catch(console.error);
  };

  useEffect(() => {
    fetchStatus();
  }, []);

  const handleTrain = async () => {
    setTraining(true);
    try {
      await api.trainModel();
      fetchStatus();
    } catch (e) {
      console.error(e);
    }
    setTraining(false);
  };

  if (!status) return null;

  return (
    <div className="bg-panel rounded-lg border border-gray-800 p-4 shadow-lg">
      <div className="flex justify-between items-center border-b border-gray-800 pb-2 mb-3">
        <h3 className="text-xs font-bold text-gray-400 uppercase tracking-widest flex items-center">
          <BrainCircuit className="w-4 h-4 mr-2" /> Model Status
        </h3>
        {status.model_loaded ? (
          <span className="text-[10px] bg-accent-blue/20 text-accent-blue px-2 py-0.5 rounded border border-accent-blue/50">LOADED</span>
        ) : (
          <span className="text-[10px] bg-gray-800 text-gray-400 px-2 py-0.5 rounded">NO MODEL</span>
        )}
      </div>

      <div className="space-y-2 mb-4">
        <div className="flex justify-between text-sm">
          <span className="text-gray-500">Accuracy</span>
          <span className="font-mono text-white">
            {status.accuracy == null ? 'N/A' : `${(status.accuracy * 100).toFixed(1)}%`}
          </span>
        </div>
        <div className="flex justify-between text-sm">
          <span className="text-gray-500">Features</span>
          <span className="font-mono text-white">{status.feature_count || 0}</span>
        </div>
      </div>

      {pipelineStatus && (
        <div className="mb-4 border-t border-gray-800 pt-3 text-xs">
          <div className="flex justify-between">
            <span className="text-gray-500">Occupancy pipeline</span>
            <span className={pipelineStatus.scheduler_model === 'ready' ? 'text-accent-green' : 'text-accent-amber'}>
              {pipelineStatus.scheduler_model === 'ready' ? 'READY' : 'WEIGHTS ONLY'}
            </span>
          </div>
          <div className="mt-1 flex justify-between text-gray-500">
            <span>Input window</span>
            <span className="font-mono text-gray-300">{pipelineStatus.input_shape.join(' x ')}</span>
          </div>
        </div>
      )}

      <button 
        onClick={handleTrain}
        disabled={training}
        className="w-full bg-gray-800 hover:bg-gray-700 text-white text-sm py-2 rounded transition-colors flex items-center justify-center border border-gray-700"
      >
        {training ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <BrainCircuit className="w-4 h-4 mr-2" />}
        {training ? 'Training...' : 'Retrain Model'}
      </button>
    </div>
  );
}
