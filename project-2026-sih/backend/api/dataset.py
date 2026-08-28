from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app_state import app_state
from data.h5_inspector import H5Inspector
from data.h5_loader import H5Loader

router = APIRouter(prefix='/api/dataset', tags=['dataset'])

class LoadRequest(BaseModel):
    filepath: Optional[str] = None

@router.get('/structure')
def get_structure():
    if not app_state.settings:
        raise HTTPException(status_code=500, detail="Settings not loaded")
    filepath = app_state.settings.h5_dataset_path
    try:
        inspector = H5Inspector()
        return inspector.inspect(filepath)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/summary')
def get_summary():
    try:
        return {
            'filename': app_state.settings.h5_dataset_path if app_state.settings else None,
            'num_transmitters': len(app_state.emitters),
            'num_pulses': len(app_state.pulses),
            'num_bands': len(app_state.bands),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post('/load')
def load_dataset(req: LoadRequest):
    filepath = req.filepath
    if not filepath and app_state.settings:
        filepath = app_state.settings.h5_dataset_path
    if not filepath:
        raise HTTPException(status_code=400, detail="No filepath provided")
        
    try:
        loader = H5Loader()
        data = loader.load(filepath)
        app_state.emitters = data.get('emitters', [])
        app_state.pulses = data.get('pulses', [])
        return get_summary()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
