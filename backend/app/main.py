from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings

app = FastAPI(title=settings.app_name, version='0.1.0')

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.get('/api/health')
async def health_check() -> dict[str, str]:
    return {'status': 'ok', 'service': settings.app_name}


@app.get('/')
async def root() -> dict[str, str]:
    return {'message': 'ROOM 0 API is running'}


@app.exception_handler(HTTPException)
async def http_exception_handler(_, exc: HTTPException) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={'detail': exc.detail})


@app.get('/api/v1/overview')
async def overview() -> dict[str, Any]:
    return {
        'app_name': settings.app_name,
        'environment': settings.environment,
        'livekit_enabled': settings.enable_livekit,
        'demo_mode': settings.enable_demo_mode,
    }
