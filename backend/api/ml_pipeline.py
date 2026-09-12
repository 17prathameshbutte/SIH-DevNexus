"""API endpoints for the contributed occupancy and PDW ML pipeline."""
from typing import List, Optional
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix='/api/ml/pipeline', tags=['ml-pipeline'])
PIPELINE_DIR = Path(__file__).resolve().parents[1] / 'ml_pipeline' / 'ml_engine'


class PipelinePredictionRequest(BaseModel):
    occupancy_matrix: List[List[float]] = Field(..., min_length=10, max_length=10)
    pdw_batch: Optional[List[List[float]]] = None


@router.get('/status')
def pipeline_status():
    return {
        'scheduler_model': 'ready' if (PIPELINE_DIR / 'smart_scan_v1.pkl').exists() else 'not_exported',
        'fallback_weights': (PIPELINE_DIR / 'smart_scan_v1.pth').exists(),
        'input_shape': [10, 50],
        'outputs': ['predicted_dwell_time_ms', 'next_sweep_band_index', 'band_confidence'],
    }


@router.post('/predict')
def pipeline_predict(request: PipelinePredictionRequest):
    try:
        from ml_pipeline.ml_engine.api_wrapper import predict_step

        payload = request.model_dump()
        if any(len(row) != 50 for row in payload['occupancy_matrix']):
            raise ValueError('occupancy_matrix must be shape (10, 50)')
        if payload.get('pdw_batch') and any(len(row) != 4 for row in payload['pdw_batch']):
            raise ValueError('pdw_batch rows must contain 4 values')
        return predict_step(payload)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
