import axios from 'axios';

const api = axios.create({
  baseURL: '/api'
});

export const getHealth = () => api.get('/health').then(res => res.data);
export const getDatasetStructure = () => api.get('/dataset/structure').then(res => res.data);
export const getDatasetSummary = () => api.get('/dataset/summary').then(res => res.data);
export const loadDataset = (summary) => api.post('/dataset/load', { summary }).then(res => res.data);

export const getBands = () => api.get('/bands').then(res => res.data);
export const getEmitters = () => api.get('/emitters').then(res => res.data);
export const getEmitter = (id) => api.get(`/emitters/${id}`).then(res => res.data);

export const startSimulation = (config) => api.post('/simulation/start', config).then(res => res.data);
export const stepSimulation = () => api.post('/simulation/step').then(res => res.data);
export const runSimulation = (steps) => api.post('/simulation/run', { steps }).then(res => res.data);
export const resetSimulation = () => api.post('/simulation/reset').then(res => res.data);
export const getSimulationState = () => api.get('/simulation/state').then(res => res.data);

export const getSchedulerRanking = () => api.get('/scheduler/ranking').then(res => res.data);
export const getSchedulerDecision = () => api.get('/scheduler/decision').then(res => res.data);

export const getMetrics = () => api.get('/metrics').then(res => res.data);
export const getComparison = () => api.get('/comparison').then(res => res.data);

export const trainModel = () => api.post('/ml/train').then(res => res.data);
export const getModelStatus = () => api.get('/ml/status').then(res => res.data);
export const getPipelineStatus = () => api.get('/ml/pipeline/status').then(res => res.data);
