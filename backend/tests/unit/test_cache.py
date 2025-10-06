# backend/tests/unit/test_cache.py

import pytest
import time
from src.utils.cache import CacheManager


class TestCacheManager:
    """Test suite for CacheManager"""

    def test_cache_initialization(self):
        """Test cache manager initialization with default parameters"""
        cache = CacheManager()
        assert cache._cache.maxsize == 100
        assert cache._cache.ttl == 3600

    def test_cache_initialization_with_custom_params(self):
        """Test cache manager initialization with custom parameters"""
        cache = CacheManager(maxsize=50, ttl=1800)
        assert cache._cache.maxsize == 50
        assert cache._cache.ttl == 1800

    def test_cache_set_and_get(self):
        """Test basic cache set and get operations"""
        cache = CacheManager()
        cache.set("test_key", "test_value")

        value = cache.get("test_key")
        assert value == "test_value"

    def test_cache_miss(self):
        """Test cache miss returns None"""
        cache = CacheManager()
        value = cache.get("nonexistent_key")
        assert value is None

    def test_cache_stats_hit(self):
        """Test cache statistics for cache hits"""
        cache = CacheManager()
        cache.set("key1", "value1")

        cache.get("key1")
        cache.get("key1")

        stats = cache.get_stats()
        assert stats["hits"] == 2
        assert stats["misses"] == 0
        assert stats["sets"] == 1

    def test_cache_stats_miss(self):
        """Test cache statistics for cache misses"""
        cache = CacheManager()

        cache.get("nonexistent1")
        cache.get("nonexistent2")

        stats = cache.get_stats()
        assert stats["hits"] == 0
        assert stats["misses"] == 2

    def test_cache_hit_rate(self):
        """Test cache hit rate calculation"""
        cache = CacheManager()
        cache.set("key1", "value1")

        # 2 hits, 2 misses = 50% hit rate
        cache.get("key1")
        cache.get("key1")
        cache.get("nonexistent1")
        cache.get("nonexistent2")

        stats = cache.get_stats()
        assert stats["hit_rate_percent"] == 50.0

    def test_cache_invalidation(self):
        """Test cache invalidation"""
        cache = CacheManager()
        cache.set("test_key", "test_value")

        assert cache.get("test_key") == "test_value"

        cache.invalidate("test_key")
        assert cache.get("test_key") is None

    def test_cache_clear(self):
        """Test cache clear operation"""
        cache = CacheManager()
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")

        stats = cache.get_stats()
        assert stats["size"] == 3

        cache.clear()
        stats = cache.get_stats()
        assert stats["size"] == 0

    def test_cache_ttl_expiration(self):
        """Test that cache entries expire after TTL"""
        # Use very short TTL for testing
        cache = CacheManager(maxsize=10, ttl=1)  # 1 second TTL

        cache.set("test_key", "test_value")
        assert cache.get("test_key") == "test_value"

        # Wait for TTL to expire
        time.sleep(1.1)

        # Should be expired now
        assert cache.get("test_key") is None

    def test_cache_maxsize_limit(self):
        """Test that cache respects maxsize limit"""
        cache = CacheManager(maxsize=3, ttl=3600)

        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")

        stats = cache.get_stats()
        assert stats["size"] <= 3

    def test_cache_with_complex_objects(self):
        """Test caching with complex objects like lists and dicts"""
        cache = CacheManager()

        test_list = [1, 2, 3, 4, 5]
        test_dict = {"name": "Knight", "elixir": 3}

        cache.set("list_key", test_list)
        cache.set("dict_key", test_dict)

        assert cache.get("list_key") == test_list
        assert cache.get("dict_key") == test_dict

    def test_cache_stats_total_requests(self):
        """Test total requests calculation in stats"""
        cache = CacheManager()
        cache.set("key1", "value1")

        cache.get("key1")  # hit
        cache.get("key2")  # miss
        cache.get("key1")  # hit

        stats = cache.get_stats()
        assert stats["total_requests"] == 3
        assert stats["hits"] == 2
        assert stats["misses"] == 1
