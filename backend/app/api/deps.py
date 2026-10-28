"""Shared request dependencies: resources created once at startup and kept on `app.state`."""

from fastapi import Request
from psycopg_pool import AsyncConnectionPool
from redis.asyncio import Redis

from app.config import Settings, get_settings


def get_pool(request: Request) -> AsyncConnectionPool:
    return request.app.state.pool


def get_redis(request: Request) -> Redis:
    return request.app.state.redis


def settings() -> Settings:
    return get_settings()
