from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class TelegramUserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None


class AuthResponse(BaseModel):
    ok: bool = True
    user: TelegramUserOut


class TableCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    status: str = 'waiting'
    max_players: int = 6
    spectator_capacity: int = 4


class TableResponse(BaseModel):
    id: int
    name: str
    status: str
    max_players: int
    spectator_capacity: int


class PlayerActionRequest(BaseModel):
    action_type: str
    payload: dict | None = None


class VoteRequest(BaseModel):
    target_user_id: int
