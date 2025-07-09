"""
Unit tests for Cache Manager - Phase 3A Implementation

This module tests the caching functionality to ensure it works correctly
with various scenarios including cache hits, misses, expiration, and
thread safety.

Author: AI Assistant
Date: July 2025
Phase: 3A - Performance Foundation
"""

import unittest
import pandas as pd
import time
import threading
from unittest.mock import patch, MagicMock

# Add the parent directory to the path to import our modules
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.cache_manager import CacheManager, get_cache_manager, clear_global_cache


class TestCacheManager(unittest.TestCase):
    """
    Test suite for the CacheManager class.
    
    Tests cache functionality including storage, retrieval, expiration,
    and thread safety under various conditions.
    """
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.cache_manager = CacheManager(max_size=10, default_ttl=3600)
        self.test_data = pd.DataFrame({
            'Date': pd.date_range('2024-01-01', periods=10, freq='D'),
            'Revenue': [100, 150, 200, 180, 220, 250, 300, 280, 320, 350],
            'Cost': [50, 75, 100, 90, 110, 125, 150, 140, 160, 175]
        })
        
    def tearDown(self):
        """Clean up after each test method."""
        self.cache_manager.clear()
        clear_global_cache()
    
    def test_cache_manager_initialization(self):
        """Test that CacheManager initializes correctly."""
        # Test default initialization
        cache = CacheManager()
        self.assertEqual(cache.max_size, 100)
        self.assertEqual(cache.default_ttl, 3600)
        self.assertEqual(len(cache.cache), 0)
        
        # Test custom initialization
        cache = CacheManager(max_size=50, default_ttl=1800)
        self.assertEqual(cache.max_size, 50)
        self.assertEqual(cache.default_ttl, 1800)
    
    def test_cache_key_generation(self):
        """Test cache key generation for different scenarios."""
        # Test basic key generation
        key1 = self.cache_manager._generate_cache_key(self.test_data, 'summary')
        key2 = self.cache_manager._generate_cache_key(self.test_data, 'summary')
        self.assertEqual(key1, key2)  # Same data and type should generate same key
        
        # Test different analysis types generate different keys
        key_summary = self.cache_manager._generate_cache_key(self.test_data, 'summary')
        key_trends = self.cache_manager._generate_cache_key(self.test_data, 'trends')
        self.assertNotEqual(key_summary, key_trends)
        
        # Test parameters affect key generation
        key_no_params = self.cache_manager._generate_cache_key(self.test_data, 'summary')
        key_with_params = self.cache_manager._generate_cache_key(
            self.test_data, 'summary', {'param1': 'value1'}
        )
        self.assertNotEqual(key_no_params, key_with_params)
        
        # Test different data generates different keys
        different_data = self.test_data.copy()
        different_data['Revenue'] = different_data['Revenue'] * 2
        key_different = self.cache_manager._generate_cache_key(different_data, 'summary')
        self.assertNotEqual(key1, key_different)
    
    def test_cache_put_and_get(self):
        """Test basic cache put and get operations."""
        # Test storing and retrieving a result
        test_result = "This is a test analysis result"
        self.cache_manager.put(self.test_data, 'summary', test_result)
        
        retrieved_result = self.cache_manager.get(self.test_data, 'summary')
        self.assertEqual(retrieved_result, test_result)
        
        # Test cache hit statistics
        stats = self.cache_manager.get_stats()
        self.assertEqual(stats['hits'], 1)
        self.assertEqual(stats['misses'], 0)
        self.assertEqual(stats['size'], 1)
    
    def test_cache_miss(self):
        """Test cache miss scenarios."""
        # Test cache miss for non-existent key
        result = self.cache_manager.get(self.test_data, 'nonexistent')
        self.assertIsNone(result)
        
        # Test cache miss statistics
        stats = self.cache_manager.get_stats()
        self.assertEqual(stats['hits'], 0)
        self.assertEqual(stats['misses'], 1)
        self.assertEqual(stats['size'], 0)
    
    def test_cache_expiration(self):
        """Test cache entry expiration (TTL)."""
        # Store a result with very short TTL
        test_result = "This will expire soon"
        self.cache_manager.put(self.test_data, 'summary', test_result, ttl=1)
        
        # Should be available immediately
        retrieved_result = self.cache_manager.get(self.test_data, 'summary')
        self.assertEqual(retrieved_result, test_result)
        
        # Wait for expiration
        time.sleep(1.1)
        
        # Should be expired now
        expired_result = self.cache_manager.get(self.test_data, 'summary')
        self.assertIsNone(expired_result)
    
    def test_cache_capacity_management(self):
        """Test cache capacity management and LRU eviction."""
        # Fill cache to capacity
        for i in range(10):
            test_data = self.test_data.copy()
            test_data['Revenue'] = test_data['Revenue'] + i  # Make each dataset unique
            self.cache_manager.put(test_data, 'summary', f"result_{i}")
        
        # Cache should be at capacity
        stats = self.cache_manager.get_stats()
        self.assertEqual(stats['size'], 10)
        
        # Add one more entry, should evict oldest
        new_data = self.test_data.copy()
        new_data['Revenue'] = new_data['Revenue'] + 100
        self.cache_manager.put(new_data, 'summary', "new_result")
        
        # Cache should still be at capacity, but with eviction
        stats = self.cache_manager.get_stats()
        self.assertEqual(stats['size'], 10)
        self.assertEqual(stats['evictions'], 1)
    
    def test_cache_with_parameters(self):
        """Test caching with different parameters."""
        # Store results with different parameters
        self.cache_manager.put(self.test_data, 'top_n', "top_5_result", {'n': 5})
        self.cache_manager.put(self.test_data, 'top_n', "top_10_result", {'n': 10})
        
        # Retrieve with specific parameters
        result_5 = self.cache_manager.get(self.test_data, 'top_n', {'n': 5})
        result_10 = self.cache_manager.get(self.test_data, 'top_n', {'n': 10})
        
        self.assertEqual(result_5, "top_5_result")
        self.assertEqual(result_10, "top_10_result")
        
        # Test cache miss with different parameters
        result_20 = self.cache_manager.get(self.test_data, 'top_n', {'n': 20})
        self.assertIsNone(result_20)
    
    def test_cache_invalidation(self):
        """Test cache invalidation for specific datasets."""
        # Store results for the test data
        self.cache_manager.put(self.test_data, 'summary', "summary_result")
        self.cache_manager.put(self.test_data, 'trends', "trends_result")
        
        # Store result for different data
        different_data = pd.DataFrame({'col1': [1, 2, 3], 'col2': [4, 5, 6]})
        self.cache_manager.put(different_data, 'summary', "different_summary")
        
        # Verify all results are cached
        self.assertEqual(self.cache_manager.get(self.test_data, 'summary'), "summary_result")
        self.assertEqual(self.cache_manager.get(self.test_data, 'trends'), "trends_result")
        self.assertEqual(self.cache_manager.get(different_data, 'summary'), "different_summary")
        
        # Invalidate cache for test_data
        self.cache_manager.invalidate_data_cache(self.test_data)
        
        # test_data results should be invalidated
        self.assertIsNone(self.cache_manager.get(self.test_data, 'summary'))
        self.assertIsNone(self.cache_manager.get(self.test_data, 'trends'))
        
        # different_data result should still be cached
        self.assertEqual(self.cache_manager.get(different_data, 'summary'), "different_summary")
    
    def test_cache_clear(self):
        """Test clearing all cache entries."""
        # Store multiple results
        self.cache_manager.put(self.test_data, 'summary', "summary_result")
        self.cache_manager.put(self.test_data, 'trends', "trends_result")
        
        # Verify cache has entries
        stats = self.cache_manager.get_stats()
        self.assertGreater(stats['size'], 0)
        
        # Clear cache
        self.cache_manager.clear()
        
        # Verify cache is empty
        stats = self.cache_manager.get_stats()
        self.assertEqual(stats['size'], 0)
        self.assertIsNone(self.cache_manager.get(self.test_data, 'summary'))
    
    def test_cache_statistics(self):
        """Test cache statistics tracking."""
        # Perform various cache operations
        self.cache_manager.put(self.test_data, 'summary', "result")
        self.cache_manager.get(self.test_data, 'summary')  # Hit
        self.cache_manager.get(self.test_data, 'nonexistent')  # Miss
        
        # Check statistics
        stats = self.cache_manager.get_stats()
        self.assertEqual(stats['hits'], 1)
        self.assertEqual(stats['misses'], 1)
        self.assertEqual(stats['hit_rate'], 50.0)
        self.assertEqual(stats['size'], 1)
    
    def test_thread_safety(self):
        """Test thread safety of cache operations."""
        results = []
        errors = []
        
        def cache_worker(thread_id):
            """Worker function for thread safety testing."""
            try:
                # Each thread works with slightly different data
                data = self.test_data.copy()
                data['Revenue'] = data['Revenue'] + thread_id
                
                # Store and retrieve results
                test_result = f"result_from_thread_{thread_id}"
                self.cache_manager.put(data, 'summary', test_result)
                retrieved = self.cache_manager.get(data, 'summary')
                
                results.append((thread_id, retrieved))
            except Exception as e:
                errors.append((thread_id, str(e)))
        
        # Create and start multiple threads
        threads = []
        for i in range(10):
            thread = threading.Thread(target=cache_worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify no errors occurred
        self.assertEqual(len(errors), 0, f"Thread errors: {errors}")
        
        # Verify all threads got correct results
        self.assertEqual(len(results), 10)
        for thread_id, result in results:
            expected = f"result_from_thread_{thread_id}"
            self.assertEqual(result, expected)
    
    def test_global_cache_manager(self):
        """Test global cache manager singleton."""
        # Test singleton behavior
        cache1 = get_cache_manager()
        cache2 = get_cache_manager()
        self.assertIs(cache1, cache2)
        
        # Test global cache operations
        cache1.put(self.test_data, 'summary', "global_test")
        result = cache2.get(self.test_data, 'summary')
        self.assertEqual(result, "global_test")
        
        # Test global cache clear
        clear_global_cache()
        result = cache1.get(self.test_data, 'summary')
        self.assertIsNone(result)
    
    def test_error_handling(self):
        """Test error handling in cache operations."""
        # Test with malformed data (should handle gracefully)
        with patch('pandas.util.hash_pandas_object') as mock_hash:
            mock_hash.side_effect = Exception("Hash error")
            
            # Should not raise exception, just return None
            result = self.cache_manager.get(self.test_data, 'summary')
            self.assertIsNone(result)
            
            # Should not raise exception when storing
            self.cache_manager.put(self.test_data, 'summary', "test")
            # No assertion needed, just verify no exception is raised
    
    def test_cleanup_expired_entries(self):
        """Test cleanup of expired entries."""
        # Store entries with different TTLs
        self.cache_manager.put(self.test_data, 'summary', "short_ttl", ttl=1)
        
        different_data = self.test_data.copy()
        different_data['Revenue'] = different_data['Revenue'] * 2
        self.cache_manager.put(different_data, 'summary', "long_ttl", ttl=3600)
        
        # Verify both are cached
        stats = self.cache_manager.get_stats()
        self.assertEqual(stats['size'], 2)
        
        # Wait for first entry to expire
        time.sleep(1.1)
        
        # Cleanup expired entries
        expired_count = self.cache_manager.cleanup_expired()
        self.assertEqual(expired_count, 1)
        
        # Verify only one entry remains
        stats = self.cache_manager.get_stats()
        self.assertEqual(stats['size'], 1)
        
        # Verify the right entry remains
        self.assertIsNone(self.cache_manager.get(self.test_data, 'summary'))
        self.assertEqual(self.cache_manager.get(different_data, 'summary'), "long_ttl")


if __name__ == '__main__':
    unittest.main()
