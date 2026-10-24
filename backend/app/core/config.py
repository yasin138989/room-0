from __future__ import annotations

from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    app_name: str = 'ROOM 0'
    environment: Literal['development', 'staging', 'production'] = 'development'
    debug: bool = False
    backend_host: str = '0.0.0.0'
    backend_port: int = 8000
    jwt_secret_key: str = 'change-me'
    telegram_bot_token: str = 'replace-me'
    telegram_bot_username: str = 'room0bot'
    telegram_webhook_path: str = '/telegram/webhook'
    telegram_app_url: str = 'https://example.com'
    telegram_allowed_origins: list[str] = Field(default_factory=lambda: ['https://example.com'])
    database_url: str = 'postgresql+psycopg://postgres:postgres@localhost:5432/room0'
    redis_url: str = 'redis://localhost:6379/0'
    livekit_url: str = 'wss://livekit.example.com'
    livekit_api_key: str = 'devkey'
    livekit_api_secret: str = 'devsecret'
    cors_origins: list[str] = Field(default_factory=lambda: ['http://localhost:5173'])
    admin_email: str = 'admin@example.com'
    admin_username: str = 'room0admin'
    enable_livekit: bool = False
    enable_demo_mode: bool = True
    enable_rewards: bool = False
    timezone: str = 'Asia/Tehran'
    app_version: str = '0.1.0'
    security_headers_enabled: bool = True
    rate_limit_per_minute: int = 60


settings = Settings()
