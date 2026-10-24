from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class TableOut(BaseModel):
    id: int
    name: str
    status: str
    max_players: int = 6
    spectator_capacity: int = 4
    start_time: datetime | None = None


class ReservationCreate(BaseModel):
    table_id: int
    seat_index: int | None = None


class ReservationOut(BaseModel):
    id: int
    table_id: int
    status: str
    is_confirmed: bool
