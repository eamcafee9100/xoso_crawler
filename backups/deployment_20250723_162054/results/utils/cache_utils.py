"""
Cache utilities with Redis fallback handling
Provides safe cache operations that won't break the application if Redis is unavailable
"""
import logging
from django.core.cache import cache
from typing import Any, Optional

logger = logging.getLogger(__name__)

def safe_cache_get(key: str) -> Optional[Any]:
    """
    Safely get value from cache with Redis fallback handling
    
    Args:
        key: Cache key
        
    Returns:
        Cached value or None if cache is unavailable or key doesn't exist
    """
    try:
        return cache.get(key)
    except Exception as e:
        logger.warning(f"Cache get failed for key '{key}': {e}")
        return None

def safe_cache_set(key: str, value: Any, timeout: int = 3600) -> bool:
    """
    Safely set value in cache with Redis fallback handling
    
    Args:
        key: Cache key
        value: Value to cache
        timeout: Cache timeout in seconds
        
    Returns:
        True if successful, False if cache operation failed
    """
    try:
        cache.set(key, value, timeout)
        return True
    except Exception as e:
        logger.warning(f"Cache set failed for key '{key}': {e}")
        return False

def safe_cache_delete(key: str) -> bool:
    """
    Safely delete value from cache
    
    Args:
        key: Cache key to delete
        
    Returns:
        True if successful, False if cache operation failed
    """
    try:
        cache.delete(key)
        return True
    except Exception as e:
        logger.warning(f"Cache delete failed for key '{key}': {e}")
        return False

def safe_cache_clear() -> bool:
    """
    Safely clear all cache
    
    Returns:
        True if successful, False if cache operation failed
    """
    try:
        cache.clear()
        return True
    except Exception as e:
        logger.warning(f"Cache clear failed: {e}")
        return False

def safe_cache_get_many(keys: list) -> dict:
    """
    Safely get multiple values from cache
    
    Args:
        keys: List of cache keys
        
    Returns:
        Dictionary of key-value pairs found in cache
    """
    try:
        return cache.get_many(keys)
    except Exception as e:
        logger.warning(f"Cache get_many failed for keys {keys}: {e}")
        return {}

def safe_cache_set_many(data: dict, timeout: int = 3600) -> bool:
    """
    Safely set multiple values in cache
    
    Args:
        data: Dictionary of key-value pairs to cache
        timeout: Cache timeout in seconds
        
    Returns:
        True if successful, False if cache operation failed
    """
    try:
        cache.set_many(data, timeout)
        return True
    except Exception as e:
        logger.warning(f"Cache set_many failed: {e}")
        return False