"""Redis connection shared by the response cache and the job queue."""

import json
from functools import lru_cache
from typing import Any

import redis

from app.core.config import get_settings

CACHE_TTL_SECONDS = 60


@lru_cache
def get_redis() -> redis.Redis | None:
    """Return a Redis client, or None when REDIS_URL is not configured."""
    url = get_settings().redis_url
    # Raw bytes (no decode_responses): RQ stores pickled job data in Redis.
    return redis.Redis.from_url(url) if url else None


def cache_get(key: str) -> Any | None:
    """Return a cached JSON value, or None on miss or cache outage."""
    client = get_redis()
    if client is None:
        return None
    try:
        value = client.get(key)
    except redis.RedisError:
        return None
    return json.loads(value) if value is not None else None


def cache_set(key: str, value: Any) -> None:
    """Store a JSON value with a TTL; cache outages are ignored."""
    client = get_redis()
    if client is None:
        return
    try:
        client.setex(key, CACHE_TTL_SECONDS, json.dumps(value))
    except redis.RedisError:
        pass


def cache_delete(key: str) -> None:
    """Drop a cached value; the TTL bounds staleness if Redis is down."""
    client = get_redis()
    if client is None:
        return
    try:
        client.delete(key)
    except redis.RedisError:
        pass
