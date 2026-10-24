from __future__ import annotations

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services.realtime import realtime_hub

router = APIRouter(prefix='/ws', tags=['realtime'])


@router.websocket('/table/{table_id}')
async def table_realtime(websocket: WebSocket, table_id: int) -> None:
    await realtime_hub.connect(table_id, websocket)
    try:
        while True:
            raw = await websocket.receive_text()
            if raw == 'ping':
                await websocket.send_text('{"event":"pong"}')
    except WebSocketDisconnect:
        realtime_hub.disconnect(table_id, websocket)


@router.get('/ws/status')
def ws_status() -> dict[str, str]:
    return {'status': 'ready', 'transport': 'websocket'}
