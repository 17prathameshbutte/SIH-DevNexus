import React, { useRef, useEffect } from 'react';

export default function ScanTimeline({ history }) {
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollLeft = scrollRef.current.scrollWidth;
    }
  }, [history]);

  return (
    <div className="bg-panel rounded-lg border border-gray-800 p-3 shadow-lg">
      <h3 className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">Scan Timeline</h3>
      <div 
        ref={scrollRef}
        className="flex space-x-1 overflow-x-auto pb-2 scroll-smooth scrollbar-thin"
      >
        {history.length === 0 ? (
          <div className="text-sm text-gray-600 italic">No scan history yet</div>
        ) : (
          history.map((step, idx) => {
            const isHit = step.result;
            return (
              <div 
                key={idx} 
                className={`flex-shrink-0 w-8 h-12 rounded flex flex-col items-center justify-center border ${
                  isHit 
                    ? 'bg-accent-green/20 border-accent-green text-accent-green shadow-[0_0_8px_rgba(0,255,136,0.3)]' 
                    : 'bg-dark-surface border-gray-700 text-gray-500'
                }`}
                title={`Step ${step.step} - Band ${step.band_id}`}
              >
                <span className="text-[10px] opacity-70">B{step.band_id}</span>
                <span className="text-xs font-bold">{isHit ? 'H' : 'M'}</span>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
