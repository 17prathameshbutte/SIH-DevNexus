from fastapi import APIRouter, HTTPException
from app_state import app_state

router = APIRouter(prefix='/api', tags=['scheduler'])

@router.get('/bands')
def get_bands():
    if not app_state.band_manager:
        return []
    return app_state.band_manager.to_dict_list()

@router.get('/emitters')
def get_emitters():
    return [e.__dict__ if hasattr(e, '__dict__') else e for e in app_state.emitters]

@router.get('/emitters/{emitter_id}')
def get_emitter(emitter_id: str):
    for e in app_state.emitters:
        eid = getattr(e, 'id', None) or (e.get('id') if isinstance(e, dict) else None)
        if str(eid) == emitter_id:
            return e.__dict__ if hasattr(e, '__dict__') else e
    raise HTTPException(status_code=404, detail="Emitter not found")

@router.get('/scheduler/ranking')
def get_ranking():
    if not app_state.current_scheduler or not hasattr(app_state.current_scheduler, 'get_ranking'):
        return {"rankings": []}
    return app_state.current_scheduler.get_ranking()

@router.get('/scheduler/decision')
def get_decision():
    if not app_state.current_scheduler or not hasattr(app_state.current_scheduler, 'get_last_decision'):
        return {}
    return app_state.current_scheduler.get_last_decision()
