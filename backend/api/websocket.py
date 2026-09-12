from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
import asyncio
from app_state import app_state

router = APIRouter()

@router.websocket('/ws/simulation')
async def websocket_simulation(websocket: WebSocket):
    await websocket.accept()
    is_streaming = False
    
    try:
        while True:
            if is_streaming:
                try:
                    data = await asyncio.wait_for(websocket.receive_text(), timeout=0.1)
                except asyncio.TimeoutError:
                    data = None
            else:
                data = await websocket.receive_text()
                
            if data:
                try:
                    msg = json.loads(data)
                    action = msg.get('action')
                    
                    if action == 'start':
                        is_streaming = True
                    elif action == 'stop':
                        is_streaming = False
                    elif action == 'step':
                        if app_state.engine:
                            result = app_state.engine.step()
                            await websocket.send_json(result)
                    elif action == 'reset':
                        if app_state.engine:
                            app_state.engine.reset()
                            is_streaming = False
                            await websocket.send_json({"status": "reset"})
                except json.JSONDecodeError:
                    pass

            if is_streaming and app_state.engine:
                result = app_state.engine.step()
                await websocket.send_json(result)
                await asyncio.sleep(0.5)
                
    except WebSocketDisconnect:
        print("WebSocket disconnected")
