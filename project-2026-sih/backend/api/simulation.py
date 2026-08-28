from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app_state import app_state
from schedulers.sequential_scheduler import SequentialScheduler
from schedulers.random_scheduler import RandomScheduler
from schedulers.ml_scheduler import MLScheduler
from simulation.engine import SimulationEngine

router = APIRouter(prefix='/api/simulation', tags=['simulation'])

class StartRequest(BaseModel):
    scenario: str = 'mixed'
    scheduler: str = 'smartscan'
    num_steps: int = 200
    speed: float = 1.0
    epsilon: float = 0.1
    prediction_horizon: float = 1.0
    seed: int = 42

class RunRequest(BaseModel):
    num_steps: int = 10

@router.post('/start')
def start_simulation(req: StartRequest):
    try:
        if req.scheduler == 'sequential':
            app_state.current_scheduler = SequentialScheduler()
        elif req.scheduler == 'random':
            app_state.current_scheduler = RandomScheduler(seed=req.seed)
        else: # smartscan
            if app_state.predictor is None:
                raise ValueError("ML model not loaded")
            app_state.current_scheduler = MLScheduler(
                predictor=app_state.predictor,
                feature_extractor=app_state.feature_extractor,
                epsilon=req.epsilon,
                seed=req.seed
            )
            
        app_state.engine = SimulationEngine(
            environment=app_state.environment,
            receiver=app_state.receiver,
            scheduler=app_state.current_scheduler,
            bands=app_state.bands,
            step_duration=app_state.settings.simulation_step_sec if app_state.settings else 1.0,
            seed=req.seed
        )
        app_state.engine.start()
        
        return {
            'status': 'started',
            'total_steps': req.num_steps,
            'scenario': req.scenario,
            'scheduler': req.scheduler
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post('/step')
def step_simulation():
    if not app_state.engine:
        raise HTTPException(status_code=400, detail="Engine not started")
    try:
        return app_state.engine.step()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post('/run')
def run_simulation(req: RunRequest):
    if not app_state.engine:
        raise HTTPException(status_code=400, detail="Engine not started")
    try:
        return app_state.engine.run(req.num_steps)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post('/reset')
def reset_simulation():
    if not app_state.engine:
        raise HTTPException(status_code=400, detail="Engine not started")
    try:
        app_state.engine.reset()
        return {"status": "reset"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/state')
def get_state():
    if not app_state.engine:
        raise HTTPException(status_code=400, detail="Engine not started")
    try:
        return app_state.engine.get_state()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
