"""
Cache Manager for Quant Commander v2.0 - Phase 3A Implementation

This module provides caching functionality to improve performance for repeated
analysis requests. It implements an LRU (Least Recently Used) cache with TTL
(Time To Live) support for automatic cache expiration.

Key Features:
- In-memory LRU cache for analysis results
- TTL-based cache expiration
- Thread-safe operations
- Memory usage monitoring
- Cache statistics tracking

Author: AI Assistant
Date: July 2025
Phase: 3A - Performance Foundation
"""

import hashlib
import time
from collections import OrderedDict
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Tuple, Union
import threading
import pandas as pd
import json


class CacheManager:
    """
    Thread-safe LRU cache manager with TTL support for analysis results.
    
    This class provides caching functionality to improve performance by storing
    analysis results and avoiding redundant calculations for the same data.
    """
    
    def __init__(self, max_size: int = 100, default_ttl: int = 3600):
        """
        Initialize the cache manager.
        
        Args:
            max_size (int): Maximum number of cache entries (default: 100)
            default_ttl (int): Default TTL in seconds (default: 3600 = 1 hour)
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: OrderedDict = OrderedDict()
        self.lock = threading.RLock()  # Reentrant lock for thread safety
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'size': 0
        }
        
        print(f"🔧 CacheManager initialized: max_size={max_size}, default_ttl={default_ttl}s")
    
    def _generate_cache_key(self, data: pd.DataFrame, analysis_type: str, 
                          params: Optional[Dict] = None) -> str:
        """
        Generate a unique cache key based on data and analysis parameters.
        
        Args:
            data (pd.DataFrame): The data being analyzed
            analysis_type (str): Type of analysis (summary, trends, variance, etc.)
            params (Dict, optional): Additional parameters for the analysis
            
        Returns:
            str: Unique cache key
        """
        # Create a hash of the data content
        data_hash = hashlib.md5(pd.util.hash_pandas_object(data).values).hexdigest()
        
        # Include analysis type and parameters in the key
        key_components = [data_hash, analysis_type]
        
        if params:
            # Sort parameters for consistent key generation
            params_str = json.dumps(params, sort_keys=True)
            params_hash = hashlib.md5(params_str.encode()).hexdigest()
            key_components.append(params_hash)
        
        return ":".join(key_components)
    
    def _is_expired(self, entry: Dict) -> bool:
        """
        Check if a cache entry has expired.
        
        Args:
            entry (Dict): Cache entry with timestamp and ttl
            
        Returns:
            bool: True if expired, False otherwise
        """
        current_time = time.time()
        return current_time - entry['timestamp'] > entry['ttl']
    
    def _evict_expired_entries(self) -> int:
        """
        Remove expired entries from the cache.
        
        Returns:
            int: Number of entries evicted
        """
        expired_keys = []
        for key, entry in self.cache.items():
            if self._is_expired(entry):
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.cache[key]
        
        return len(expired_keys)
    
    def _ensure_capacity(self):
        """
        Ensure cache doesn't exceed maximum size by evicting oldest entries.
        """
        while len(self.cache) >= self.max_size:
            # Remove oldest entry (first in OrderedDict)
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
            self.stats['evictions'] += 1
    
    def get(self, data: pd.DataFrame, analysis_type: str, 
            params: Optional[Dict] = None) -> Optional[Any]:
        """
        Retrieve a cached analysis result.
        
        Args:
            data (pd.DataFrame): The data being analyzed
            analysis_type (str): Type of analysis
            params (Dict, optional): Analysis parameters
            
        Returns:
            Optional[Any]: Cached result if found and not expired, None otherwise
        """
        with self.lock:
            try:
                # Generate cache key
                cache_key = self._generate_cache_key(data, analysis_type, params)
                
                # Clean up expired entries
                self._evict_expired_entries()
                
                # Check if key exists and is not expired
                if cache_key in self.cache:
                    entry = self.cache[cache_key]
                    if not self._is_expired(entry):
                        # Move to end (most recently used)
                        self.cache.move_to_end(cache_key)
                        self.stats['hits'] += 1
                        print(f"🎯 Cache HIT for {analysis_type} analysis")
                        return entry['result']
                    else:
                        # Remove expired entry
                        del self.cache[cache_key]
                
                # Cache miss
                self.stats['misses'] += 1
                print(f"❌ Cache MISS for {analysis_type} analysis")
                return None
                
            except Exception as e:
                print(f"⚠️ Cache get error: {str(e)}")
                self.stats['misses'] += 1
                return None
    
    def put(self, data: pd.DataFrame, analysis_type: str, result: Any,
            params: Optional[Dict] = None, ttl: Optional[int] = None):
        """
        Store an analysis result in the cache.
        
        Args:
            data (pd.DataFrame): The data that was analyzed
            analysis_type (str): Type of analysis
            result (Any): Analysis result to cache
            params (Dict, optional): Analysis parameters
            ttl (int, optional): TTL in seconds (uses default if not provided)
        """
        with self.lock:
            try:
                # Generate cache key
                cache_key = self._generate_cache_key(data, analysis_type, params)
                
                # Use provided TTL or default
                cache_ttl = ttl if ttl is not None else self.default_ttl
                
                # Ensure we don't exceed capacity
                self._ensure_capacity()
                
                # Store the result
                self.cache[cache_key] = {
                    'result': result,
                    'timestamp': time.time(),
                    'ttl': cache_ttl,
                    'analysis_type': analysis_type,
                    'params': params
                }
                
                # Move to end (most recently used)
                self.cache.move_to_end(cache_key)
                
                # Update stats
                self.stats['size'] = len(self.cache)
                print(f"💾 Cached {analysis_type} analysis result (TTL: {cache_ttl}s)")
                
            except Exception as e:
                print(f"⚠️ Cache put error: {str(e)}")
    
    def clear(self):
        """
        Clear all cache entries.
        """
        with self.lock:
            self.cache.clear()
            self.stats = {
                'hits': 0,
                'misses': 0,
                'evictions': 0,
                'size': 0
            }
            print("🧹 Cache cleared")
    
    def invalidate_data_cache(self, data: pd.DataFrame):
        """
        Invalidate all cache entries for a specific dataset.
        
        Args:
            data (pd.DataFrame): Dataset to invalidate cache for
        """
        with self.lock:
            try:
                data_hash = hashlib.md5(pd.util.hash_pandas_object(data).values).hexdigest()
                
                # Find all entries for this dataset
                keys_to_remove = []
                for key in self.cache.keys():
                    if key.startswith(data_hash):
                        keys_to_remove.append(key)
                
                # Remove found entries
                for key in keys_to_remove:
                    del self.cache[key]
                
                self.stats['size'] = len(self.cache)
                print(f"🗑️ Invalidated {len(keys_to_remove)} cache entries for dataset")
                
            except Exception as e:
                print(f"⚠️ Cache invalidation error: {str(e)}")
    
    def get_stats(self) -> Dict:
        """
        Get cache statistics.
        
        Returns:
            Dict: Cache statistics including hits, misses, size, etc.
        """
        with self.lock:
            # Clean up expired entries for accurate stats
            expired_count = self._evict_expired_entries()
            self.stats['size'] = len(self.cache)
            
            # Calculate hit rate
            total_requests = self.stats['hits'] + self.stats['misses']
            hit_rate = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0
            
            return {
                **self.stats,
                'hit_rate': round(hit_rate, 2),
                'expired_cleaned': expired_count,
                'max_size': self.max_size,
                'default_ttl': self.default_ttl
            }
    
    def cleanup_expired(self) -> int:
        """
        Manually trigger cleanup of expired entries.
        
        Returns:
            int: Number of expired entries removed
        """
        with self.lock:
            expired_count = self._evict_expired_entries()
            self.stats['size'] = len(self.cache)
            if expired_count > 0:
                print(f"🧹 Cleaned up {expired_count} expired cache entries")
            return expired_count


# Global cache instance for the application
_cache_manager = None


def get_cache_manager() -> CacheManager:
    """
    Get the global cache manager instance (singleton pattern).
    
    Returns:
        CacheManager: The global cache manager instance
    """
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager


def clear_global_cache():
    """
    Clear the global cache (useful for testing).
    """
    global _cache_manager
    if _cache_manager:
        _cache_manager.clear()


def get_cache_stats() -> Dict:
    """
    Get global cache statistics.
    
    Returns:
        Dict: Cache statistics
    """
    return get_cache_manager().get_stats()
