import React, { useState, useEffect } from 'react';
import HDF5Tree from '../components/HDF5Tree';
import * as api from '../services/api';
import { Database, FileJson, Server, Activity } from 'lucide-react';

export default function DatasetPage() {
  const [structure, setStructure] = useState(null);
  const [summary, setSummary] = useState(null);
  const [selectedDataset, setSelectedDataset] = useState(null);

  useEffect(() => {
    api.getDatasetStructure().then(setStructure).catch(console.error);
    api.getDatasetSummary().then(setSummary).catch(console.error);
  }, []);

  return (
    <div className="max-w-[1600px] mx-auto space-y-4">
      {/* Top stats */}
      {summary && (
        <div className="grid grid-cols-4 gap-4">
          <div className="bg-panel p-4 rounded-lg border border-gray-800 flex items-center">
            <Database className="w-8 h-8 text-accent-blue mr-4 opacity-70" />
            <div>
              <div className="text-xs text-gray-500 uppercase">File Size</div>
              <div className="text-xl font-mono text-white">{summary.file_size_mb?.toFixed(2)} MB</div>
            </div>
          </div>
          <div className="bg-panel p-4 rounded-lg border border-gray-800 flex items-center">
            <Activity className="w-8 h-8 text-accent-green mr-4 opacity-70" />
            <div>
              <div className="text-xs text-gray-500 uppercase">Transmitters</div>
              <div className="text-xl font-mono text-white">{summary.num_transmitters}</div>
            </div>
          </div>
          <div className="bg-panel p-4 rounded-lg border border-gray-800 flex items-center">
            <Server className="w-8 h-8 text-accent-cyan mr-4 opacity-70" />
            <div>
              <div className="text-xs text-gray-500 uppercase">Total Datasets</div>
              <div className="text-xl font-mono text-white">{summary.num_datasets}</div>
            </div>
          </div>
          <div className="bg-panel p-4 rounded-lg border border-gray-800 flex items-center">
            <FileJson className="w-8 h-8 text-accent-amber mr-4 opacity-70" />
            <div>
              <div className="text-xs text-gray-500 uppercase">Pulses</div>
              <div className="text-xl font-mono text-white">{summary.num_pulses?.toLocaleString()}</div>
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 h-[calc(100vh-220px)]">
        {/* Tree view */}
        <div className="lg:col-span-4 bg-panel rounded-lg border border-gray-800 shadow-lg flex flex-col overflow-hidden">
          <div className="p-3 border-b border-gray-800 bg-dark-surface">
            <h3 className="text-xs font-bold text-gray-400 uppercase tracking-widest">HDF5 Structure</h3>
          </div>
          <div className="p-4 overflow-y-auto flex-1 custom-scrollbar">
            <HDF5Tree structure={structure} onSelectDataset={setSelectedDataset} />
          </div>
        </div>

        {/* Dataset Details */}
        <div className="lg:col-span-8 bg-panel rounded-lg border border-gray-800 shadow-lg flex flex-col overflow-hidden">
          <div className="p-3 border-b border-gray-800 bg-dark-surface">
            <h3 className="text-xs font-bold text-gray-400 uppercase tracking-widest">Dataset Explorer</h3>
          </div>
          <div className="p-6 overflow-y-auto flex-1">
            {selectedDataset ? (
              <div className="space-y-6">
                <div>
                  <h2 className="text-2xl font-mono text-white mb-2">{selectedDataset.path}</h2>
                  <div className="flex space-x-4 text-sm">
                    <span className="bg-gray-800 px-3 py-1 rounded border border-gray-700">Shape: [{selectedDataset.shape.join(', ')}]</span>
                    <span className="bg-gray-800 px-3 py-1 rounded border border-gray-700">Type: {selectedDataset.dtype}</span>
                  </div>
                </div>

                {selectedDataset.attributes && Object.keys(selectedDataset.attributes).length > 0 && (
                  <div>
                    <h4 className="text-xs font-bold text-gray-500 uppercase mb-2">Attributes</h4>
                    <div className="bg-dark-surface rounded border border-gray-800 p-4">
                      <pre className="text-sm font-mono text-accent-cyan whitespace-pre-wrap">
                        {JSON.stringify(selectedDataset.attributes, null, 2)}
                      </pre>
                    </div>
                  </div>
                )}

                <div>
                  <h4 className="text-xs font-bold text-gray-500 uppercase mb-2">Data Sample (First 5 records)</h4>
                  <div className="bg-dark-surface rounded border border-gray-800 p-4 overflow-x-auto">
                    <pre className="text-sm font-mono text-gray-300">
                      {JSON.stringify(selectedDataset.sample, null, 2)}
                    </pre>
                  </div>
                </div>
              </div>
            ) : (
              <div className="h-full flex items-center justify-center text-gray-500 flex-col">
                <Database className="w-16 h-16 mb-4 opacity-20" />
                <p>Select a dataset from the tree to view details</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
