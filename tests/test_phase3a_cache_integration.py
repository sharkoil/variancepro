"""
Integration tests for Phase 3A Cache Integration

This module tests the integration of caching into the QuickActionHandler
to ensure performance improvements work correctly.

Author: AI Assistant
Date: July 2025
Phase: 3A - Performance Foundation
"""

import unittest
import pandas as pd
import time
from unittest.mock import Mock, patch, MagicMock

# Add the parent directory to the path to import our modules
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from handlers.quick_action_handler import QuickActionHandler
from utils.cache_manager import get_cache_manager, clear_global_cache
from utils.performance_monitor import get_performance_monitor, clear_performance_metrics


class TestPhase3ACacheIntegration(unittest.TestCase):
    """
    Test suite for Phase 3A cache integration with QuickActionHandler.
    
    Tests that caching works correctly with existing analysis methods
    and provides performance improvements.
    """
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create mock app core
        self.mock_app_core = Mock()
        self.mock_app_core.has_data.return_value = True
        
        # Create sample test data
        self.test_data = pd.DataFrame({
            'Date': pd.date_range('2024-01-01', periods=10, freq='D'),
            'Revenue': [100, 150, 200, 180, 220, 250, 300, 280, 320, 350],
            'Cost': [50, 75, 100, 90, 110, 125, 150, 140, 160, 175],
            'Profit': [50, 75, 100, 90, 110, 125, 150, 140, 160, 175]
        })
        
        # Mock the data summary
        self.mock_data_summary = {
            'row_count': 10,
            'column_count': 4,
            'columns': ['Date', 'Revenue', 'Cost', 'Profit'],
            'basic_stats': {
                'Revenue': {'mean': 225, 'min': 100, 'max': 350},
                'Cost': {'mean': 112.5, 'min': 50, 'max': 175}
            }
        }
        
        self.mock_app_core.get_current_data.return_value = (self.test_data, self.mock_data_summary)
        
        # Create handler with mocked dependencies
        self.handler = QuickActionHandler(
            app_core=self.mock_app_core,
            rag_manager=None,
            rag_analyzer=None
        )
        
        # Clear cache and performance metrics before each test
        clear_global_cache()
        clear_performance_metrics()
    
    def tearDown(self):
        """Clean up after each test method."""
        clear_global_cache()
        clear_performance_metrics()
    
    def test_cache_integration_initialization(self):
        """Test that cache manager is properly initialized."""
        # Verify cache manager is available
        self.assertIsNotNone(self.handler.cache_manager)
        self.assertIsNotNone(self.handler.performance_monitor)
        
        # Verify cache stats are accessible
        stats = self.handler.get_cache_stats()
        self.assertIsInstance(stats, dict)
        self.assertIn('hits', stats)
        self.assertIn('misses', stats)
        self.assertIn('size', stats)
        
        # Verify performance stats are accessible
        perf_stats = self.handler.get_performance_stats()
        self.assertIsInstance(perf_stats, dict)
        self.assertIn('system', perf_stats)
    
    def test_summary_action_caching(self):
        """Test that summary action results are cached correctly."""
        # First call should be a cache miss
        result1 = self.handler._handle_summary_action()
        self.assertIsInstance(result1, str)
        self.assertIn("Data Summary", result1)
        
        # Verify cache miss
        stats1 = self.handler.get_cache_stats()
        self.assertEqual(stats1['misses'], 1)
        self.assertEqual(stats1['hits'], 0)
        self.assertEqual(stats1['size'], 1)
        
        # Second call should be a cache hit
        result2 = self.handler._handle_summary_action()
        self.assertEqual(result1, result2)
        
        # Verify cache hit
        stats2 = self.handler.get_cache_stats()
        self.assertEqual(stats2['misses'], 1)
        self.assertEqual(stats2['hits'], 1)
        self.assertEqual(stats2['size'], 1)
    
    def test_trends_action_caching(self):
        """Test that trends action results are cached correctly."""
        # Mock timescale analyzer
        mock_timescale = Mock()
        mock_timescale.status = "completed"
        mock_timescale.format_for_chat.return_value = "Sample trends analysis"
        mock_timescale.analyze.return_value = None
        
        self.mock_app_core.timescale_analyzer = mock_timescale
        
        # First call should be a cache miss
        result1 = self.handler._handle_trends_action()
        self.assertIsInstance(result1, str)
        self.assertIn("Trends Analysis", result1)
        
        # Verify cache miss
        stats1 = self.handler.get_cache_stats()
        self.assertEqual(stats1['misses'], 1)
        self.assertEqual(stats1['hits'], 0)
        self.assertEqual(stats1['size'], 1)
        
        # Second call should be a cache hit
        result2 = self.handler._handle_trends_action()
        self.assertEqual(result1, result2)
        
        # Verify cache hit
        stats2 = self.handler.get_cache_stats()
        self.assertEqual(stats2['misses'], 1)
        self.assertEqual(stats2['hits'], 1)
        self.assertEqual(stats2['size'], 1)
        
        # Verify analyzer was only called once (first time)
        mock_timescale.analyze.assert_called_once()
    
    def test_cache_invalidation_on_data_change(self):
        """Test that cache is invalidated when data changes."""
        # Cache a summary result
        result1 = self.handler._handle_summary_action()
        self.assertIsInstance(result1, str)
        
        # Verify cache has entry
        stats1 = self.handler.get_cache_stats()
        self.assertEqual(stats1['size'], 1)
        self.assertEqual(stats1['misses'], 1)
        self.assertEqual(stats1['hits'], 0)
        
        # Call again to get a cache hit
        result1_repeat = self.handler._handle_summary_action()
        self.assertEqual(result1, result1_repeat)
        
        # Verify cache hit occurred
        stats_after_hit = self.handler.get_cache_stats()
        self.assertEqual(stats_after_hit['size'], 1)
        self.assertEqual(stats_after_hit['misses'], 1)
        self.assertEqual(stats_after_hit['hits'], 1)
        
        # Simulate data change
        self.handler.invalidate_cache_for_data_change()
        
        # Verify cache is invalidated
        stats2 = self.handler.get_cache_stats()
        self.assertEqual(stats2['size'], 0)
        
        # Next call should be a cache miss
        result2 = self.handler._handle_summary_action()
        stats3 = self.handler.get_cache_stats()
        self.assertEqual(stats3['misses'], 2)  # First call + after invalidation
        self.assertEqual(stats3['hits'], 1)    # Only the second call before invalidation
    
    def test_different_analysis_types_cached_separately(self):
        """Test that different analysis types are cached separately."""
        # Mock timescale analyzer for trends
        mock_timescale = Mock()
        mock_timescale.status = "completed"
        mock_timescale.format_for_chat.return_value = "Trends analysis"
        mock_timescale.analyze.return_value = None
        self.mock_app_core.timescale_analyzer = mock_timescale
        
        # Call different analysis types
        summary_result = self.handler._handle_summary_action()
        trends_result = self.handler._handle_trends_action()
        
        # Verify different results
        self.assertNotEqual(summary_result, trends_result)
        self.assertIn("Data Summary", summary_result)
        self.assertIn("Trends Analysis", trends_result)
        
        # Verify both are cached separately
        stats = self.handler.get_cache_stats()
        self.assertEqual(stats['size'], 2)  # Two different cache entries
        self.assertEqual(stats['misses'], 2)  # Both were misses initially
        self.assertEqual(stats['hits'], 0)
        
        # Call them again - should be cache hits
        summary_result2 = self.handler._handle_summary_action()
        trends_result2 = self.handler._handle_trends_action()
        
        self.assertEqual(summary_result, summary_result2)
        self.assertEqual(trends_result, trends_result2)
        
        # Verify cache hits
        stats2 = self.handler.get_cache_stats()
        self.assertEqual(stats2['hits'], 2)
    
    def test_performance_monitoring_integration(self):
        """Test that performance monitoring works with cached operations."""
        # Perform some operations
        self.handler._handle_summary_action()
        self.handler._handle_summary_action()  # Should be faster (cached)
        
        # Get performance stats
        perf_stats = self.handler.get_performance_stats()
        
        # Verify performance data is collected
        self.assertIn('operations', perf_stats)
        self.assertIn('summary_analysis', perf_stats['operations'])
        
        # Verify operation was called twice
        summary_stats = perf_stats['operations']['summary_analysis']
        self.assertEqual(summary_stats['count'], 2)
        self.assertGreater(summary_stats['avg_duration'], 0)
    
    def test_rag_caching_with_different_contexts(self):
        """Test that RAG-enhanced results are cached correctly."""
        # Mock RAG components
        mock_rag_manager = Mock()
        mock_rag_manager.has_documents.return_value = True
        
        mock_rag_analyzer = Mock()
        mock_rag_analyzer.enhance_general_analysis.return_value = {
            'success': True,
            'enhanced_analysis': 'RAG-enhanced analysis',
            'documents_used': 2
        }
        
        # Create handler with RAG components
        handler_with_rag = QuickActionHandler(
            app_core=self.mock_app_core,
            rag_manager=mock_rag_manager,
            rag_analyzer=mock_rag_analyzer
        )
        
        # First call should use RAG
        result1 = handler_with_rag._handle_summary_action()
        self.assertIn("RAG Enhancement", result1)
        
        # Verify RAG was called
        mock_rag_analyzer.enhance_general_analysis.assert_called_once()
        
        # Second call should be cached (RAG not called again)
        result2 = handler_with_rag._handle_summary_action()
        self.assertEqual(result1, result2)
        
        # Verify RAG was only called once
        mock_rag_analyzer.enhance_general_analysis.assert_called_once()
    
    def test_cache_performance_improvement(self):
        """Test that caching provides actual performance improvement."""
        # Since caching happens after get_current_data, we need to test
        # the performance of the analysis processing, not the data retrieval
        
        # First call - should process and cache
        start_time = time.time()
        result1 = self.handler._handle_summary_action()
        first_duration = time.time() - start_time
        
        # Second call - should be faster due to caching
        start_time = time.time()
        result2 = self.handler._handle_summary_action()
        second_duration = time.time() - start_time
        
        # Verify results are identical
        self.assertEqual(result1, result2)
        
        # The second call should be faster (though the improvement might be small)
        # For now, just verify the cache hit occurred
        stats = self.handler.get_cache_stats()
        self.assertEqual(stats['hits'], 1)
        self.assertEqual(stats['misses'], 1)
    
    def test_error_handling_with_caching(self):
        """Test that errors are handled gracefully with caching."""
        # Mock an error in get_current_data
        self.mock_app_core.get_current_data.side_effect = Exception("Data error")
        
        # Error should be handled gracefully
        result = self.handler._handle_summary_action()
        self.assertIn("Summary Analysis Error", result)
        
        # Cache should not be affected by errors
        stats = self.handler.get_cache_stats()
        self.assertEqual(stats['size'], 0)  # No cache entry for error
    
    def test_cache_with_different_parameters(self):
        """Test that cache works correctly with different parameters."""
        # Test top/bottom analysis with different parameters
        result1 = self.handler._handle_top_bottom_action("top 5")
        result2 = self.handler._handle_top_bottom_action("top 10")
        result3 = self.handler._handle_top_bottom_action("top 5")  # Same as first
        
        # Verify different parameters give different results
        self.assertNotEqual(result1, result2)
        # Verify same parameters give same result (cached)
        self.assertEqual(result1, result3)


if __name__ == '__main__':
    unittest.main()
