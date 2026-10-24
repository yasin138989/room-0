from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get('/api/health')
    assert response.status_code == 200
    assert response.json()['status'] == 'ok'


def test_ready_endpoint() -> None:
    response = client.get('/api/v1/ready')
    assert response.status_code == 200
    assert response.json()['status'] == 'ready'


def test_security_headers() -> None:
    response = client.get('/api/health')
    assert response.headers['X-Frame-Options'] == 'DENY'
    assert response.headers['X-Content-Type-Options'] == 'nosniff'
