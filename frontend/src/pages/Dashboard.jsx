import React, { useState, useEffect } from 'react';
import DatasetStatus from '../components/DatasetStatus';
import SimulationControls from '../components/SimulationControls';
import SpectrumHeatmap from '../components/SpectrumHeatmap';
import FrequencyPriority from '../components/FrequencyPriority';
import CurrentScan from '../components/CurrentScan';
import PredictionCard from '../components/PredictionCard';
import ScanTimeline from '../components/ScanTimeline';
import MetricsCards from '../components/MetricsCards';
import ComparisonChart from '../components/ComparisonChart';
import EmitterTable from '../components/EmitterTable';
import ModelStatus from '../components/ModelStatus';
import DemoMode from '../components/DemoMode';

import { useSimulation } from '../hooks/useSimulation';
import * as api from '../services/api';

export default function Dashboard() {
  const simulation = useSimulation();
  const [bands, setBands] = useState([]);
  const [emitters, setEmitters] = useState([]);
  const [showDemo, setShowDemo] = useState(false);

  useEffect(() => {
    // Initial data load
    api.getBands().then(setBands).catch(console.error);
    api.getEmitters().then(setEmitters).catch(console.error);
  }, []);

  return (
    <div className="space-y-4 max-w-[1600px] mx-auto">
      {showDemo && <DemoMode onClose={() => setShowDemo(false)} />}

      <section className="flex flex-col justify-between gap-4 border-b border-teal-900/70 pb-5 md:flex-row md:items-end">
        <div>
          <p className="mb-2 font-mono text-[10px] uppercase tracking-[0.28em] text-teal-300/70">Operations console / live experiment</p>
          <h1 className="text-2xl font-semibold tracking-tight text-white sm:text-3xl">Spectrum intelligence <span className="text-teal-300">in motion.</span></h1>
          <p className="mt-2 max-w-2xl text-sm text-slate-400">Observe how the scheduler prioritizes the next frequency window from the current RF picture.</p>
        </div>
        <div className="flex items-center gap-2 font-mono text-[10px] uppercase tracking-widest text-slate-500">
          <span className="h-2 w-2 rounded-full bg-teal-300 shadow-[0_0_12px_rgba(94,234,212,0.8)]" />
          Live telemetry
        </div>
      </section>
      
      {/* Top row metrics */}
      <MetricsCards metrics={simulation.metrics} />

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        {/* Left Sidebar */}
        <div className="lg:col-span-3 space-y-4">
          <DatasetStatus />
          <SimulationControls simulation={simulation} onDemoMode={() => setShowDemo(true)} />
          <ModelStatus />
        </div>

        {/* Main Content Area */}
        <div className="lg:col-span-9 space-y-4">
          {/* Top Main - Heatmap */}
          <div className="h-[350px]">
            <SpectrumHeatmap bands={bands} scanHistory={simulation.scanHistory} />
          </div>

          {/* Middle Main - Split */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
            <div className="lg:col-span-8">
              <FrequencyPriority rankings={simulation.schedulerDecision?.ranking || []} />
            </div>
            <div className="lg:col-span-4 space-y-4">
              <CurrentScan step={simulation.currentStep} />
              <PredictionCard decision={simulation.schedulerDecision} />
            </div>
          </div>

          {/* Timeline strip */}
          <ScanTimeline history={simulation.scanHistory} />
        </div>
      </div>

      {/* Bottom Area */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        <div className="lg:col-span-5 h-[400px]">
          <ComparisonChart />
        </div>
        <div className="lg:col-span-7 h-[400px] flex flex-col">
          <EmitterTable emitters={emitters} />
        </div>
      </div>
    </div>
  );
}
