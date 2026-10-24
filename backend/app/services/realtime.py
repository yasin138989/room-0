from __future__ import annotations

import asyncio
import json
from collections import defaultdict
from datetime import datetime
from typing import Any

from fastapi import WebSocket


class RealtimeHub:
    _instance: 'RealtimeHub | None' = None

    def __new__(cls) -> 'RealtimeHub':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._tables: dict[int, set[WebSocket]] = defaultdict(set)
        return cls._instance

    async def connect(self, table_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        self._tables.setdefault(table_id, set()).add(websocket)
        await self.send_snapshot(table_id, websocket, {
            'table_id': table_id,
            'status': 'connected',
            'timestamp': datetime.utcnow().isoformat(),
            'players_online': len(self._tables.get(table_id, set())),
        })

    def disconnect(self, table_id: int, websocket: WebSocket) -> None:
        if table_id in self._tables:
            self._tables[table_id].discard(websocket)
            if not self._tables[table_id]:
                del self._tables[table_id]

    async def send_snapshot(self, table_id: int, websocket: WebSocket, payload: dict[str, Any] | None = None) -> None:
        snapshot = {
            'event': 'snapshot',
            'table_id': table_id,
            'payload': payload or {
                'table_id': table_id,
                'status': 'ready',
                'timestamp': datetime.utcnow().isoformat(),
            },
        }
        await websocket.send_text(json.dumps(snapshot, ensure_ascii=False))

    async def broadcast(self, table_id: int, event_name: str, payload: dict[str, Any]) -> None:
        message = json.dumps(
            {
                'event': event_name,
                'table_id': table_id,
                'payload': payload,
                'timestamp': datetime.utcnow().isoformat(),
            },
            ensure_ascii=False,
        )
        dead: list[WebSocket] = []
        for websocket in list(self._tables.get(table_id, set())):
            try:
                await websocket.send_text(message)
            except Exception:
                dead.append(websocket)
        for websocket in dead:
            self.disconnect(table_id, websocket)


realtime_hub = RealtimeHub()
