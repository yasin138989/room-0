from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes.admin import router as admin_router
from app.api.routes.health import router as health_router
from app.api.routes.livekit import router as livekit_router
from app.api.routes.monitoring import router as monitoring_router
from app.api.routes.tables import router as tables_router
from app.api.routes.ws import router as ws_router
from app.core.config import settings
from app.core.middleware import rate_limit_middleware, security_headers_middleware

app = FastAPI(title=settings.app_name, version=settings.app_version)

app.middleware('http')(security_headers_middleware)
app.middleware('http')(rate_limit_middleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(health_router)
app.include_router(tables_router)
app.include_router(ws_router)
app.include_router(livekit_router)
app.include_router(admin_router)
app.include_router(monitoring_router)


@app.get('/')
async def root() -> dict[str, str]:
    return {'message': 'ROOM 0 API is running'}


@app.exception_handler(HTTPException)
async def http_exception_handler(_, exc: HTTPException) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={'detail': exc.detail})
