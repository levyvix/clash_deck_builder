# backend/src/utils/cache.py

import logging
from typing import Any, Optional, Callable
from datetime import datetime, timedelta
from functools import wraps
from cachetools import TTLCache

logger = logging.getLogger(__name__)


class CacheManager:
    """
    Centralized cache manager for application-wide caching.

    Uses TTLCache for time-based expiration of cached data.
    """

    def __init__(self, maxsize: int = 100, ttl: int = 3600):
        """
        Initialize cache manager.

        Args:
            maxsize: Maximum number of items in cache
            ttl: Time-to-live in seconds (default: 1 hour)
        """
        self._cache = TTLCache(maxsize=maxsize, ttl=ttl)
        self._stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "invalidations": 0
        }

    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve item from cache.

        Args:
            key: Cache key

        Returns:
            Cached value if found, None otherwise
        """
        try:
            value = self._cache.get(key)
            if value is not None:
                self._stats["hits"] += 1
                logger.debug(f"Cache HIT for key: {key}")
            else:
                self._stats["misses"] += 1
                logger.debug(f"Cache MISS for key: {key}")
            return value
        except Exception as e:
            logger.warning(f"Cache get error for key {key}: {e}")
            self._stats["misses"] += 1
            return None

    def set(self, key: str, value: Any) -> None:
        """
        Store item in cache.

        Args:
            key: Cache key
            value: Value to cache
        """
        try:
            self._cache[key] = value
            self._stats["sets"] += 1
            logger.debug(f"Cache SET for key: {key}")
        except Exception as e:
            logger.warning(f"Cache set error for key {key}: {e}")

    def invalidate(self, key: str) -> None:
        """
        Remove item from cache.

        Args:
            key: Cache key to invalidate
        """
        try:
            if key in self._cache:
                del self._cache[key]
                self._stats["invalidations"] += 1
                logger.debug(f"Cache INVALIDATED for key: {key}")
        except Exception as e:
            logger.warning(f"Cache invalidation error for key {key}: {e}")

    def clear(self) -> None:
        """Clear all items from cache."""
        self._cache.clear()
        logger.info("Cache cleared")

    def get_stats(self) -> dict:
        """
        Get cache statistics.

        Returns:
            Dictionary containing cache hit/miss/set statistics
        """
        total_requests = self._stats["hits"] + self._stats["misses"]
        hit_rate = (self._stats["hits"] / total_requests * 100) if total_requests > 0 else 0

        return {
            **self._stats,
            "size": len(self._cache),
            "maxsize": self._cache.maxsize,
            "ttl": self._cache.ttl,
            "hit_rate_percent": round(hit_rate, 2),
            "total_requests": total_requests
        }


def cache_result(cache_manager: CacheManager, key_prefix: str = "", ttl_override: Optional[int] = None):
    """
    Decorator to cache function results.

    Args:
        cache_manager: CacheManager instance to use
        key_prefix: Prefix for cache key
        ttl_override: Optional TTL override for this specific cache entry

    Usage:
        @cache_result(cache_manager, key_prefix="cards")
        async def get_all_cards():
            return await fetch_from_db()
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            cache_key = f"{key_prefix}:{func.__name__}"

            # Try to get from cache
            cached_value = cache_manager.get(cache_key)
            if cached_value is not None:
                return cached_value

            # Call the function and cache the result
            result = await func(*args, **kwargs)
            cache_manager.set(cache_key, result)

            return result

        return wrapper
    return decorator


# Global cache instances with different TTLs for different data types
# Cards data: 24 hours (cards rarely change)
cards_cache = CacheManager(maxsize=10, ttl=86400)  # 24 hours

# User data: 1 hour (may change more frequently)
user_cache = CacheManager(maxsize=100, ttl=3600)  # 1 hour

# Deck data: 5 minutes (changes frequently)
deck_cache = CacheManager(maxsize=200, ttl=300)  # 5 minutes
