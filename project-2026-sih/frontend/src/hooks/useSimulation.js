import { useState, useEffect, useCallback, useRef } from 'react';
import * as api from '../services/api';

export function useSimulation() {
  const [isRunning, setIsRunning] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [currentStep, setCurrentStep] = useState(null);
  const [scanHistory, setScanHistory] = useState([]);
  const [metrics, setMetrics] = useState(null);
  const [schedulerDecision, setSchedulerDecision] = useState(null);
  const [speed, setSpeed] = useState(1);
  const intervalRef = useRef(null);

  const fetchState = useCallback(async () => {
    try {
      const state = await api.getSimulationState();
      setIsRunning(state.is_running);
    } catch (e) {
      console.error('Failed to fetch state', e);
    }
  }, []);

  const doStep = useCallback(async () => {
    try {
      const result = await api.stepSimulation();
      setCurrentStep(result);
      setScanHistory(prev => [...prev, result].slice(-30));
      
      const newMetrics = await api.getMetrics();
      setMetrics(newMetrics);
      
      const decision = await api.getSchedulerDecision();
      setSchedulerDecision(decision);
      
      return result;
    } catch (e) {
      console.error('Step error', e);
      setIsRunning(false);
      setIsPaused(true);
    }
  }, []);

  useEffect(() => {
    if (isRunning && !isPaused) {
      intervalRef.current = setInterval(() => {
        doStep();
      }, 1000 / speed);
    } else {
      clearInterval(intervalRef.current);
    }
    return () => clearInterval(intervalRef.current);
  }, [isRunning, isPaused, speed, doStep]);

  const start = async (config) => {
    try {
      await api.startSimulation(config);
      setIsRunning(true);
      setIsPaused(false);
      setScanHistory([]);
    } catch (e) {
      console.error('Failed to start simulation', e);
    }
  };

  const pause = () => setIsPaused(true);
  const resume = () => setIsPaused(false);
  const step = () => {
    setIsPaused(true);
    return doStep();
  };

  const reset = async () => {
    try {
      await api.resetSimulation();
      setIsRunning(false);
      setIsPaused(false);
      setCurrentStep(null);
      setScanHistory([]);
      setMetrics(null);
      setSchedulerDecision(null);
    } catch (e) {
      console.error('Failed to reset simulation', e);
    }
  };

  return {
    isRunning,
    isPaused,
    currentStep,
    scanHistory,
    metrics,
    schedulerDecision,
    speed,
    start,
    pause,
    resume,
    step,
    reset,
    setSpeed
  };
}
