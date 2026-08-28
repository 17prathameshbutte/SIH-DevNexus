import React, { useRef, useEffect } from 'react';

export default function SpectrumHeatmap({ bands, scanHistory }) {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !bands || bands.length === 0) return;
    
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;
    
    // Clear
    ctx.fillStyle = '#0a0a0f';
    ctx.fillRect(0, 0, width, height);

    const numBands = bands.length;
    const maxSteps = 100; // Show last 100 steps
    
    const cellW = width / maxSteps;
    const cellH = height / numBands;

    // Draw grid
    ctx.strokeStyle = '#1f2937';
    ctx.lineWidth = 1;
    for(let i=0; i<=maxSteps; i++) {
      ctx.beginPath();
      ctx.moveTo(i*cellW, 0);
      ctx.lineTo(i*cellW, height);
      ctx.stroke();
    }
    for(let j=0; j<=numBands; j++) {
      ctx.beginPath();
      ctx.moveTo(0, j*cellH);
      ctx.lineTo(width, j*cellH);
      ctx.stroke();
    }

    // Draw history
    const historyToShow = scanHistory.slice(-maxSteps);
    const startXOffset = maxSteps - historyToShow.length;

    historyToShow.forEach((step, i) => {
      const x = (startXOffset + i) * cellW;
      
      // We don't have full ground truth here unless passed in, 
      // but we can draw the scan result at least.
      const y = (numBands - 1 - (step.band_id % numBands)) * cellH; // assume band_id roughly matches index, or find it

      // Draw scan box
      ctx.fillStyle = step.result ? '#00ff88' : 'rgba(255, 51, 102, 0.3)';
      ctx.fillRect(x, y, cellW, cellH);
      
      // Draw scan path
      if (i > 0) {
        const prevStep = historyToShow[i-1];
        const prevY = (numBands - 1 - (prevStep.band_id % numBands)) * cellH;
        const prevX = (startXOffset + i - 1) * cellW + cellW/2;
        ctx.strokeStyle = '#06b6d4';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(prevX, prevY + cellH/2);
        ctx.lineTo(x + cellW/2, y + cellH/2);
        ctx.stroke();
      }
    });

  }, [bands, scanHistory]);

  return (
    <div className="bg-panel rounded-lg border border-gray-800 shadow-lg flex flex-col h-full">
      <div className="p-3 border-b border-gray-800 flex justify-between items-center">
        <h3 className="text-xs font-bold text-gray-400 uppercase tracking-widest">
          Spectrum Heatmap (Frequency × Time)
        </h3>
        <div className="flex space-x-3 text-xs">
          <span className="flex items-center"><div className="w-3 h-3 bg-accent-green mr-1 rounded-sm"></div> Hit</span>
          <span className="flex items-center"><div className="w-3 h-3 bg-accent-red/30 mr-1 rounded-sm"></div> Miss</span>
          <span className="flex items-center"><div className="w-4 h-0.5 bg-accent-cyan mr-1"></div> Scanner Path</span>
        </div>
      </div>
      <div className="flex-1 p-2 relative min-h-[300px]">
        {/* Y-axis labels mock */}
        <div className="absolute left-2 top-2 bottom-2 w-12 flex flex-col justify-between text-[10px] text-gray-500 font-mono">
          <span>Max Freq</span>
          <span>Center</span>
          <span>Min Freq</span>
        </div>
        <div className="ml-14 w-[calc(100%-3.5rem)] h-full">
          <canvas 
            ref={canvasRef}
            width={800} 
            height={300}
            className="w-full h-full object-fill rounded bg-midnight"
          />
        </div>
      </div>
    </div>
  );
}
