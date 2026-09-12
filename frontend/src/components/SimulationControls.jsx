import React, { useState } from 'react';
import { Play, Pause, SkipForward, RotateCcw, Zap } from 'lucide-react';

export default function SimulationControls({ 
  simulation, 
  onDemoMode 
}) {
  const [config, setConfig] = useState({
    scenario: 'Mixed',
    scheduler: 'SmartScan',
    num_steps: 1000,
    speed: 1,
    epsilon: 0.1,
    prediction_horizon: 1.0,
    seed: 42
  });

  const handleChange = (k, v) => setConfig(prev => ({ ...prev, [k]: v }));

  const handleStart = () => simulation.start(config);
  
  return (
    <div className="bg-panel rounded-lg border border-gray-800 p-4 space-y-4 shadow-lg">
      <h3 className="text-xs font-bold text-gray-400 uppercase tracking-widest border-b border-gray-800 pb-2">
        Simulation Controls
      </h3>

      <div className="space-y-3">
        <div>
          <label className="block text-xs text-gray-400 mb-1">Scenario</label>
          <select 
            className="w-full bg-dark-surface border border-gray-700 rounded p-1.5 text-sm text-white focus:border-accent-cyan focus:ring-1 focus:ring-accent-cyan outline-none"
            value={config.scenario}
            onChange={(e) => handleChange('scenario', e.target.value)}
            disabled={simulation.isRunning || simulation.isPaused}
          >
            <option>Mixed</option>
            <option>Periodic</option>
            <option>Frequency Agile</option>
            <option>Intermittent</option>
            <option>Multiple</option>
          </select>
        </div>

        <div>
          <label className="block text-xs text-gray-400 mb-1">Scheduler</label>
          <select 
            className="w-full bg-dark-surface border border-gray-700 rounded p-1.5 text-sm text-white focus:border-accent-cyan focus:ring-1 focus:ring-accent-cyan outline-none"
            value={config.scheduler}
            onChange={(e) => handleChange('scheduler', e.target.value)}
            disabled={simulation.isRunning || simulation.isPaused}
          >
            <option>SmartScan</option>
            <option>Sequential</option>
            <option>Random</option>
          </select>
        </div>

        <div className="grid grid-cols-2 gap-2">
          <div>
            <label className="block text-xs text-gray-400 mb-1">Speed</label>
            <select 
              className="w-full bg-dark-surface border border-gray-700 rounded p-1.5 text-sm text-white focus:border-accent-cyan outline-none"
              value={config.speed}
              onChange={(e) => {
                const s = parseFloat(e.target.value);
                handleChange('speed', s);
                simulation.setSpeed(s);
              }}
            >
              <option value="0.5">0.5x</option>
              <option value="1">1.0x</option>
              <option value="2">2.0x</option>
              <option value="5">5.0x</option>
              <option value="10">10.0x</option>
            </select>
          </div>
          <div>
             <label className="block text-xs text-gray-400 mb-1">Epsilon</label>
             <input 
               type="number" 
               step="0.05"
               min="0" max="1"
               className="w-full bg-dark-surface border border-gray-700 rounded p-1.5 text-sm text-white focus:border-accent-cyan outline-none"
               value={config.epsilon}
               onChange={(e) => handleChange('epsilon', parseFloat(e.target.value))}
               disabled={simulation.isRunning || simulation.isPaused}
             />
          </div>
        </div>
      </div>

      <div className="pt-2 grid grid-cols-2 gap-2">
        {!simulation.isRunning || simulation.isPaused ? (
          <button 
            onClick={simulation.isPaused ? simulation.resume : handleStart}
            className="flex items-center justify-center space-x-1 bg-green-600/20 hover:bg-green-600 text-accent-green hover:text-white border border-green-600 rounded py-1.5 transition-colors"
          >
            <Play className="w-4 h-4" /> <span>{simulation.isPaused ? 'Resume' : 'Start'}</span>
          </button>
        ) : (
          <button 
            onClick={simulation.pause}
            className="flex items-center justify-center space-x-1 bg-amber-600/20 hover:bg-amber-600 text-accent-amber hover:text-white border border-amber-600 rounded py-1.5 transition-colors"
          >
            <Pause className="w-4 h-4" /> <span>Pause</span>
          </button>
        )}
        
        <button 
          onClick={simulation.step}
          className="flex items-center justify-center space-x-1 bg-blue-600/20 hover:bg-blue-600 text-accent-blue hover:text-white border border-blue-600 rounded py-1.5 transition-colors"
        >
          <SkipForward className="w-4 h-4" /> <span>Step</span>
        </button>
        
        <button 
          onClick={simulation.reset}
          className="col-span-2 flex items-center justify-center space-x-1 border border-red-500/50 text-accent-red hover:bg-red-500/10 rounded py-1.5 transition-colors"
        >
          <RotateCcw className="w-4 h-4" /> <span>Reset</span>
        </button>

        <button 
          onClick={onDemoMode}
          className="col-span-2 flex items-center justify-center space-x-2 bg-purple-600 hover:bg-purple-500 text-white rounded py-2 transition-colors mt-2 font-bold"
        >
          <Zap className="w-4 h-4" /> <span>DEMO MODE</span>
        </button>
      </div>
    </div>
  );
}
