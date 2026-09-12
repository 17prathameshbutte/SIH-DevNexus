import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import Dashboard from './pages/Dashboard';
import DatasetPage from './pages/DatasetPage';

function App() {
  return (
    <div className="min-h-screen bg-midnight bg-grid-pattern flex flex-col text-slate-200">
      <Header />
      <main className="flex-1 overflow-x-hidden overflow-y-auto px-4 pb-10 pt-6 sm:px-6 lg:px-10">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/dataset" element={<DatasetPage />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
