"""
Phase 3B Forecasting Integration Tests

This module tests the integration of forecasting functionality
into the QuickActionHandler with caching and performance monitoring.

Author: AI Assistant
Date: July 2025
Phase: 3B - Advanced Analytics Core
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


class TestPhase3BForecastingIntegration(unittest.TestCase):
    """
    Test suite for Phase 3B forecasting integration with QuickActionHandler.
    
    Tests that forecasting works correctly with caching and performance monitoring.
    """
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create mock app core
        self.mock_app_core = Mock()
        self.mock_app_core.has_data.return_value = True
        
        # Create sample test data with date column
        self.test_data = pd.DataFrame({
            'Date': pd.date_range('2024-01-01', periods=12, freq='MS'),
            'Revenue': [100 + i * 10 for i in range(12)],
            'Cost': [50 + i * 5 for i in range(12)],
            'Profit': [50 + i * 5 for i in range(12)]
        })
        
        # Mock the data summary
        self.mock_data_summary = {
            'row_count': 12,
            'column_count': 4,
            'columns': ['Date', 'Revenue', 'Cost', 'Profit'],
            'basic_stats': {
                'Revenue': {'mean': 165, 'min': 100, 'max': 210},
                'Cost': {'mean': 82.5, 'min': 50, 'max': 105}
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
    
    def test_forecasting_analyzer_initialization(self):
        """Test that forecasting analyzer is properly initialized."""
        # Verify forecasting analyzer is available
        self.assertIsNotNone(self.handler.forecasting_analyzer)
        
        # Verify it has the correct confidence level
        self.assertEqual(self.handler.forecasting_analyzer.confidence_level, 0.95)
    
    def test_forecast_action_basic_functionality(self):
        """Test basic forecast action functionality."""
        # Call forecast action
        result = self.handler._handle_forecast_action()
        
        # Verify result structure
        self.assertIsInstance(result, str)
        self.assertIn("Forecast", result)
        
        # Verify it contains expected forecast information
        self.assertIn("Method:", result)
        self.assertIn("Periods:", result)
        self.assertIn("Forecast Values:", result)
    
    def test_forecast_action_caching(self):
        """Test that forecast action results are cached correctly."""
        # First call should be a cache miss
        result1 = self.handler._handle_forecast_action()
        self.assertIsInstance(result1, str)
        
        # Verify cache miss and entry was created
        stats1 = self.handler.get_cache_stats()
        self.assertEqual(stats1['misses'], 1)
        self.assertEqual(stats1['hits'], 0)
        self.assertEqual(stats1['size'], 1)
        
        # Second call should be a cache hit
        result2 = self.handler._handle_forecast_action()
        self.assertEqual(result1, result2)
        
        # Verify cache hit
        stats2 = self.handler.get_cache_stats()
        self.assertEqual(stats2['misses'], 1)
        self.assertEqual(stats2['hits'], 1)
        self.assertEqual(stats2['size'], 1)
    
    def test_forecast_action_performance_monitoring(self):
        """Test that forecast action performance is monitored."""
        # Perform forecast action
        self.handler._handle_forecast_action()
        
        # Get performance stats
        perf_stats = self.handler.get_performance_stats()
        
        # Verify performance data is collected
        self.assertIn('operations', perf_stats)
        self.assertIn('forecast_analysis', perf_stats['operations'])
        
        # Verify operation was recorded
        forecast_stats = perf_stats['operations']['forecast_analysis']
        self.assertEqual(forecast_stats['count'], 1)
        self.assertGreater(forecast_stats['avg_duration'], 0)
    
    def test_forecast_action_with_no_numeric_columns(self):
        """Test forecast action with data that has no numeric columns."""
        # Create data with only text columns
        text_data = pd.DataFrame({
            'Date': pd.date_range('2024-01-01', periods=5, freq='D'),
            'Category': ['A', 'B', 'C', 'D', 'E'],
            'Description': ['Desc1', 'Desc2', 'Desc3', 'Desc4', 'Desc5']
        })
        
        self.mock_app_core.get_current_data.return_value = (text_data, {})
        
        # Call forecast action
        result = self.handler._handle_forecast_action()
        
        # Should return error about no numeric columns
        self.assertIn("No numeric columns found", result)
        self.assertIn("⚠️", result)
    
    def test_forecast_action_with_no_date_column(self):
        """Test forecast action with data that has no date column."""
        # Create data without date column
        no_date_data = pd.DataFrame({
            'Revenue': [100, 110, 120, 130, 140],
            'Cost': [50, 55, 60, 65, 70]
        })
        
        self.mock_app_core.get_current_data.return_value = (no_date_data, {})
        
        # Call forecast action
        result = self.handler._handle_forecast_action()
        
        # Should return error (could be about no date column or forecasting error)
        self.assertIn("⚠️", result)
        self.assertIn("Error", result)
    
    def test_forecast_action_column_selection(self):
        """Test that forecast action selects appropriate columns."""
        # Create data with revenue column (should be preferred)
        revenue_data = pd.DataFrame({
            'Date': pd.date_range('2024-01-01', periods=10, freq='D'),
            'Revenue': [100 + i * 10 for i in range(10)],
            'Other': [50 + i * 5 for i in range(10)]
        })
        
        self.mock_app_core.get_current_data.return_value = (revenue_data, {})
        
        # Call forecast action
        result = self.handler._handle_forecast_action()
        
        # Should successfully use Revenue column
        self.assertIn("Forecast", result)
        self.assertNotIn("⚠️", result)
    
    def test_forecast_action_error_handling(self):
        """Test forecast action error handling."""
        # Mock an error in get_current_data
        self.mock_app_core.get_current_data.side_effect = Exception("Data error")
        
        # Error should be handled gracefully
        result = self.handler._handle_forecast_action()
        self.assertIn("Forecast Analysis Error", result)
        self.assertIn("⚠️", result)
    
    def test_forecast_action_with_rag_enhancement(self):
        """Test forecast action with RAG enhancement."""
        # Mock RAG components
        mock_rag_manager = Mock()
        mock_rag_manager.has_documents.return_value = True
        
        mock_rag_analyzer = Mock()
        mock_rag_analyzer.enhance_general_analysis.return_value = {
            'success': True,
            'enhanced_analysis': 'RAG-enhanced forecasting insights',
            'documents_used': 3
        }
        
        # Create handler with RAG components
        handler_with_rag = QuickActionHandler(
            app_core=self.mock_app_core,
            rag_manager=mock_rag_manager,
            rag_analyzer=mock_rag_analyzer
        )
        
        # Call forecast action
        result = handler_with_rag._handle_forecast_action()
        
        # Should include RAG enhancement
        self.assertIn("RAG Enhancement", result)
        self.assertIn("RAG-enhanced forecasting insights", result)
        
        # Verify RAG was called
        mock_rag_analyzer.enhance_general_analysis.assert_called_once()
    
    def test_forecast_action_routing(self):
        """Test that forecast action is properly routed."""
        # Test forecast action routing
        result = self.handler._route_action("forecast")
        
        # Should call forecast handler
        self.assertIsInstance(result, str)
        self.assertIn("Forecast", result)
    
    def test_forecast_cache_invalidation(self):
        """Test that forecast cache is invalidated on data change."""
        # Cache a forecast result
        result1 = self.handler._handle_forecast_action()
        self.assertIsInstance(result1, str)
        
        # Verify cache has entry
        stats1 = self.handler.get_cache_stats()
        self.assertEqual(stats1['size'], 1)
        
        # Simulate data change
        self.handler.invalidate_cache_for_data_change()
        
        # Verify cache is invalidated
        stats2 = self.handler.get_cache_stats()
        self.assertEqual(stats2['size'], 0)


if __name__ == '__main__':
    unittest.main()
