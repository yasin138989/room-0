from __future__ import annotations

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    service: str


class OverviewResponse(BaseModel):
    app_name: str
    environment: str
    livekit_enabled: bool
    demo_mode: bool
