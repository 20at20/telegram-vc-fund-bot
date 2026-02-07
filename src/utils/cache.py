"""
Caching utilities for reducing API calls.
"""

import functools
import time
from typing import Any, Callable

from cachetools import TTLCache

from config.settings import settings

# Global cache instance
_cache = TTLCache(maxsize=100, ttl=settings.cache_ttl_seconds)


def cache_with_ttl(ttl: int = None):
    """
    Decorator to cache function results with TTL.

    Args:
        ttl: Time to live in seconds. If None, uses settings.cache_ttl_seconds
    """
    cache_ttl = ttl or settings.cache_ttl_seconds

    def decorator(func: Callable) -> Callable:
        # Create a dedicated cache for this function
        func_cache = TTLCache(maxsize=50, ttl=cache_ttl)

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"

            # Check cache
            if cache_key in func_cache:
                return func_cache[cache_key]

            # Call function and cache result
            result = await func(*args, **kwargs)
            func_cache[cache_key] = result
            return result

        # Add method to clear cache
        wrapper.clear_cache = func_cache.clear

        return wrapper

    return decorator


def clear_all_caches():
    """Clear all cached data."""
    _cache.clear()
