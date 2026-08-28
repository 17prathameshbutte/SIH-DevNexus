import React, { useState } from 'react';
import { Folder, FolderOpen, FileText, ChevronRight, ChevronDown } from 'lucide-react';

export default function HDF5Tree({ structure, onSelectDataset }) {
  if (!structure) return <div className="text-gray-500 text-sm p-4">Loading structure...</div>;

  return (
    <div className="text-sm font-mono text-gray-300">
      {structure.groups?.map(group => (
        <TreeNode 
          key={group.path || group.name} 
          node={group} 
          onSelectDataset={onSelectDataset} 
        />
      ))}
      {structure.datasets?.map(dataset => (
        <DatasetNode 
          key={dataset.path} 
          dataset={dataset} 
          onSelectDataset={onSelectDataset} 
        />
      ))}
    </div>
  );
}

function TreeNode({ node, onSelectDataset, depth = 0 }) {
  const [isOpen, setIsOpen] = useState(true);
  
  return (
    <div className="ml-2">
      <div 
        className="flex items-center py-1 hover:bg-gray-800 cursor-pointer rounded px-1"
        onClick={() => setIsOpen(!isOpen)}
        style={{ paddingLeft: `${depth * 12}px` }}
      >
        {isOpen ? <ChevronDown className="w-3.5 h-3.5 mr-1 text-gray-500"/> : <ChevronRight className="w-3.5 h-3.5 mr-1 text-gray-500"/>}
        {isOpen ? <FolderOpen className="w-4 h-4 mr-2 text-accent-amber"/> : <Folder className="w-4 h-4 mr-2 text-accent-amber"/>}
        <span>{node.name || node.path.split('/').pop()}</span>
      </div>
      
      {isOpen && (
        <div className="border-l border-gray-800 ml-3">
          {node.groups?.map(g => (
            <TreeNode key={g.path} node={g} onSelectDataset={onSelectDataset} depth={depth + 1} />
          ))}
          {node.datasets?.map(d => (
            <DatasetNode key={d.path} dataset={d} onSelectDataset={onSelectDataset} depth={depth + 1} />
          ))}
        </div>
      )}
    </div>
  );
}

function DatasetNode({ dataset, onSelectDataset, depth = 0 }) {
  const name = dataset.path.split('/').pop();
  return (
    <div 
      className="flex items-center py-1 hover:bg-gray-800 cursor-pointer rounded px-1 ml-2 text-accent-cyan"
      onClick={() => onSelectDataset(dataset)}
      style={{ paddingLeft: `${depth * 12}px` }}
    >
      <FileText className="w-4 h-4 mr-2 ml-4 text-gray-400"/>
      <span>{name}</span>
      <span className="ml-2 text-xs text-gray-600">[{dataset.shape.join(', ')}]</span>
    </div>
  );
}
