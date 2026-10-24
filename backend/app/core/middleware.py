from __future__ import annotations

from collections import defaultdict, deque
from time import monotonic

from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.config import settings

api_rate_limit: dict[str, deque[float]] = defaultdict(deque)


async def security_headers_middleware(request: Request, call_next):
    if settings.security_headers_enabled:
        response = await call_next(request)
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=()'
        response.headers['Cache-Control'] = 'no-store'
        return response
    return await call_next(request)


async def rate_limit_middleware(request: Request, call_next):
    if request.url.path.startswith('/api/'):
        client_key = request.client.host if request.client else 'unknown'
        now = monotonic()
        window = api_rate_limit[client_key]
        while window and now - window[0] > 60:
            window.popleft()
        if len(window) >= settings.rate_limit_per_minute:
            return JSONResponse(status_code=429, content={'detail': 'Rate limit exceeded'})
        window.append(now)
    return await call_next(request)
