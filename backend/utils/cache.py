"""
Redis caching utility module for Trekking Management Application - V2.
Provides decorators and helpers for caching frequently accessed endpoints with TTL and invalidation.
"""
import functools
import json
import redis
from flask import request, jsonify
from config import Config

try:
    # Initialize Redis connection client for caching (DB 0)
    redis_client = redis.Redis.from_url(Config.REDIS_CACHE_URL, decode_responses=True)
    redis_client.ping()
    REDIS_AVAILABLE = True
except Exception as e:
    print(f"[CACHE WARNING] Redis connection failed ({e}). Running with in-memory fallback cache.")
    redis_client = None
    REDIS_AVAILABLE = False
_fallback_cache = {}

def get_cache(key: str):
    """Retrieve cached JSON string and return parsed object, or None."""
    if REDIS_AVAILABLE and redis_client:
        try:
            val = redis_client.get(key)
            if val:
                return json.loads(val)
        except Exception:
            pass
    elif key in _fallback_cache:
        return _fallback_cache.get(key)
    return None

def set_cache(key: str, value, timeout: int = Config.CACHE_DEFAULT_TIMEOUT):
    """Store serializable python object into Redis with TTL expiry."""
    if REDIS_AVAILABLE and redis_client:
        try:
            redis_client.setex(key, timeout, json.dumps(value))
        except Exception:
            pass
    else:
        _fallback_cache[key] = value

def delete_cache_pattern(pattern: str):
    """Invalidate all cache keys matching a glob pattern (e.g. 'treks:*')."""
    global _fallback_cache
    if REDIS_AVAILABLE and redis_client:
        try:
            keys = redis_client.keys(pattern)
            if keys:
                redis_client.delete(*keys)
        except Exception:
            pass
    _fallback_cache.clear()

def cached_endpoint(timeout=300, key_prefix='view'):
    """Decorator for caching API endpoint JSON responses based on request query parameters."""
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            # Only cache GET requests
            if request.method != 'GET':
                return f(*args, **kwargs)

            # Build unique cache key including query parameters
            query_str = json.dumps(request.args.to_dict(flat=True), sort_keys=True)
            cache_key = f"{key_prefix}:{request.path}:{query_str}"

            cached_data = get_cache(cache_key)
            if cached_data is not None:
                response = jsonify(cached_data)
                response.headers['X-Cache-Status'] = 'HIT'
                return response

            # Execute real endpoint function
            res = f(*args, **kwargs)

            # If response is successful tuple (response, status_code) or response object
            status_code = 200
            data = None

            if isinstance(res, tuple):
                data_obj, status_code = res[0], res[1]
                if status_code == 200 and hasattr(data_obj, 'get_json'):
                    data = data_obj.get_json()
            elif hasattr(res, 'get_json') and getattr(res, 'status_code', 200) == 200:
                data = res.get_json()

            if data is not None and status_code == 200:
                set_cache(cache_key, data, timeout=timeout)
                if hasattr(res, 'headers'):
                    res.headers['X-Cache-Status'] = 'MISS'

            return res
        return wrapper
    return decorator
