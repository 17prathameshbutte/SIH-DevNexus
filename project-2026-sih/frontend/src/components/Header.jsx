import React from 'react';
import { NavLink } from 'react-router-dom';
import { Activity, Database, Radio, CheckCircle, XCircle } from 'lucide-react';
import { useWebSocket } from '../hooks/useWebSocket';

export default function Header() {
  const { connected } = useWebSocket();

  return (
    <header className="sticky top-0 z-50 border-b border-teal-950/80 bg-[#09171a]/90 px-4 py-3 backdrop-blur-xl sm:px-6 lg:px-10">
      <div className="flex items-center space-x-2">
        <Radio className="w-6 h-6 text-teal-300 animate-pulse-glow" />
        <span className="font-mono font-bold text-xl tracking-widest text-white drop-shadow-[0_0_8px_rgba(6,182,212,0.5)]">
          SMARTSCAN-EW
        </span>
      </div>

      <nav className="flex space-x-1">
        <NavLink
          to="/"
          className={({ isActive }) =>
            `px-4 py-2 rounded-md font-medium text-sm transition-colors ${
              isActive
                ? 'bg-teal-400/15 text-teal-200'
                : 'text-gray-400 hover:text-white hover:bg-teal-400/10'
            }`
          }
        >
          <div className="flex items-center space-x-2">
            <Activity className="w-4 h-4" />
            <span>Dashboard</span>
          </div>
        </NavLink>
        <NavLink
          to="/dataset"
          className={({ isActive }) =>
            `px-4 py-2 rounded-md font-medium text-sm transition-colors ${
              isActive
                ? 'bg-teal-400/15 text-teal-200'
                : 'text-gray-400 hover:text-white hover:bg-teal-400/10'
            }`
          }
        >
          <div className="flex items-center space-x-2">
            <Database className="w-4 h-4" />
            <span>Dataset</span>
          </div>
        </NavLink>
      </nav>

      <div className="flex items-center space-x-4">
        <div className="flex items-center space-x-2 bg-dark-surface px-3 py-1 rounded-full border border-gray-700">
          <div className="text-xs text-gray-400 font-mono">SIMULATION</div>
          <div className="w-2 h-2 rounded-full bg-gray-500"></div>
          {/* Simulation status dot could be dynamic here */}
        </div>
        <div className="flex items-center space-x-2">
          {connected ? (
            <>
              <CheckCircle className="w-4 h-4 text-accent-green" />
              <span className="text-xs font-bold text-accent-green tracking-wide">ONLINE</span>
            </>
          ) : (
            <>
              <XCircle className="w-4 h-4 text-accent-red" />
              <span className="text-xs font-bold text-accent-red tracking-wide">OFFLINE</span>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
