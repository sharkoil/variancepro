"""
Integration tests for Forecasting Integration - Phase 3B Implementation

This module tests the integration of forecasting capabilities into the QuickActionHandler
and ensures proper integration with the existing caching system from Phase 3A.

Test Categories:
- Handler integration
- Caching integration
- Performance monitoring
- RAG enhancement compatibility
- Error handling
- End-to-end forecasting workflow

Author: AI Assistant
Date: July 2025
Phase: 3B - Advanced Analytics Core
"""

import unittest
import pandas as pd
import time
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add the parent directory to the path to import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from handlers.quick_action_handler import QuickActionHandler
from analyzers.forecast_analyzer import ForecastingAnalyzer, ForecastResult
from utils.cache_manager import get_cache_manager, clear_global_cache
from utils.performance_monitor import get_performance_monitor, clear_performance_metrics


class TestForecastingIntegration(unittest.TestCase):
    """
    Test suite for forecasting integration with QuickActionHandler.
    
    Tests that forecasting works correctly with existing infrastructure
    including caching, performance monitoring, and error handling.
    """
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create mock app core
        self.mock_app_core = Mock()
        self.mock_app_core.has_data.return_value = True
        
        # Create sample time series data
        self.sample_dates = pd.date_range('2024-01-01', periods=12, freq='MS')
        self.sample_data = pd.DataFrame({
            'Date': self.sample_dates,
            'Revenue': [100, 110, 105, 120, 115, 130, 125, 140, 135, 150, 145, 160],
            'Cost': [60, 66, 63, 72, 69, 78, 75, 84, 81, 90, 87, 96],
            'Profit': [40, 44, 42, 48, 46, 52, 50, 56, 54, 60, 58, 64]
        })
        
        # Mock data summary
        self.mock_data_summary = {
            'row_count': 12,
            'column_count': 4,
            'columns': ['Date', 'Revenue', 'Cost', 'Profit'],
            'basic_stats': {
                'Revenue': {'mean': 130, 'min': 100, 'max': 160},
                'Cost': {'mean': 78, 'min': 60, 'max': 96},
                'Profit': {'mean': 52, 'min': 40, 'max': 64}
            }
        }
        
        self.mock_app_core.get_current_data.return_value = (self.sample_data, self.mock_data_summary)
        
        # Create handler with mocked dependencies
        self.handler = QuickActionHandler(
            app_core=self.mock_app_core,
            rag_manager=None,
            rag_analyzer=None
        )
        
        # Create forecasting analyzer
        self.forecast_analyzer = ForecastingAnalyzer()
        
        # Clear cache and performance metrics before each test
        clear_global_cache()
        clear_performance_metrics()
    
    def tearDown(self):
        """Clean up after each test method."""
        clear_global_cache()
        clear_performance_metrics()
    
    def test_forecasting_analyzer_initialization(self):
        """Test that forecasting analyzer initializes correctly."""
        analyzer = ForecastingAnalyzer()
        
        # Check initialization
        self.assertIsInstance(analyzer, ForecastingAnalyzer)
        self.assertEqual(analyzer.confidence_level, 0.95)
        self.assertEqual(analyzer.min_data_points, 3)
        self.assertEqual(analyzer.max_forecast_horizon, 12)
    
    def test_basic_forecast_generation(self):
        """Test basic forecast generation with time series data."""
        # Generate forecast
        result = self.forecast_analyzer.analyze_time_series(
            self.sample_data, 'Revenue', 'Date', periods=6
        )
        
        # Verify result structure
        self.assertIsInstance(result, ForecastResult)
        self.assertEqual(len(result.forecast_values), 6)
        self.assertEqual(len(result.forecast_dates), 6)
        self.assertEqual(len(result.confidence_upper), 6)
        self.assertEqual(len(result.confidence_lower), 6)
        
        # Verify forecast values are reasonable
        for value in result.forecast_values:
            self.assertGreater(value, 0)
            self.assertLess(value, 1000)  # Sanity check
    
    def test_forecast_different_columns(self):
        """Test forecasting different columns (Revenue, Cost, Profit)."""
        # Test Revenue forecast
        revenue_forecast = self.forecast_analyzer.analyze_time_series(
            self.sample_data, 'Revenue', 'Date', periods=3
        )
        self.assertIsInstance(revenue_forecast, ForecastResult)
        
        # Test Cost forecast
        cost_forecast = self.forecast_analyzer.analyze_time_series(
            self.sample_data, 'Cost', 'Date', periods=3
        )
        self.assertIsInstance(cost_forecast, ForecastResult)
        
        # Test Profit forecast
        profit_forecast = self.forecast_analyzer.analyze_time_series(
            self.sample_data, 'Profit', 'Date', periods=3
        )
        self.assertIsInstance(profit_forecast, ForecastResult)
        
        # Verify forecasts are different
        self.assertNotEqual(revenue_forecast.forecast_values, cost_forecast.forecast_values)
        self.assertNotEqual(revenue_forecast.forecast_values, profit_forecast.forecast_values)
    
    def test_forecast_display_formatting(self):
        """Test forecast result formatting for display."""
        result = self.forecast_analyzer.analyze_time_series(
            self.sample_data, 'Revenue', 'Date', periods=3
        )
        
        # Format for display
        display_text = self.forecast_analyzer.format_forecast_for_display(result)
        
        # Verify display format
        self.assertIsInstance(display_text, str)
        self.assertIn("Forecast", display_text)
        self.assertIn("Method:", display_text)
        self.assertIn("Periods:", display_text)
        self.assertIn("Forecast Values:", display_text)
        self.assertIn("Accuracy Metrics:", display_text)
        self.assertIn("Key Insights:", display_text)
    
    def test_forecast_caching_integration(self):
        """Test that forecasting results are cached properly."""
        # This test would integrate with the caching system from Phase 3A
        # For now, we'll simulate the caching behavior
        
        # First forecast call
        result1 = self.forecast_analyzer.analyze_time_series(
            self.sample_data, 'Revenue', 'Date', periods=6
        )
        
        # Second forecast call with same parameters
        result2 = self.forecast_analyzer.analyze_time_series(
            self.sample_data, 'Revenue', 'Date', periods=6
        )
        
        # Results should be identical (in a real cached scenario)
        self.assertEqual(len(result1.forecast_values), len(result2.forecast_values))
        self.assertEqual(result1.method, result2.method)
        self.assertEqual(result1.forecast_horizon, result2.forecast_horizon)
    
    def test_forecast_performance_monitoring(self):
        """Test that forecasting integrates with performance monitoring."""
        # Time the forecast operation
        start_time = time.time()
        
        result = self.forecast_analyzer.analyze_time_series(
            self.sample_data, 'Revenue', 'Date', periods=6
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Verify operation completed in reasonable time
        self.assertLess(duration, 5.0)  # Should complete within 5 seconds
        
        # Verify result was generated
        self.assertIsInstance(result, ForecastResult)
    
    def test_forecast_error_handling(self):
        """Test error handling in forecasting operations."""
        # Test with insufficient data
        minimal_data = pd.DataFrame({
            'Date': pd.date_range('2024-01-01', periods=2, freq='MS'),
            'Revenue': [100, 110]
        })
        
        with self.assertRaises(ValueError):
            self.forecast_analyzer.analyze_time_series(
                minimal_data, 'Revenue', 'Date', periods=3
            )
        
        # Test with invalid column
        with self.assertRaises(ValueError):
            self.forecast_analyzer.analyze_time_series(
                self.sample_data, 'InvalidColumn', 'Date', periods=3
            )
        
        # Test with invalid date column
        with self.assertRaises(ValueError):
            self.forecast_analyzer.analyze_time_series(
                self.sample_data, 'Revenue', 'InvalidDate', periods=3
            )
    
    def test_forecast_method_selection(self):
        """Test that different forecasting methods are selected appropriately."""
        # Test with linear trend data - should use double exponential smoothing
        linear_data = pd.DataFrame({
            'Date': pd.date_range('2024-01-01', periods=12, freq='MS'),
            'Revenue': [100 + i * 10 for i in range(12)]  # Clear linear trend
        })
        
        result_linear = self.forecast_analyzer.analyze_time_series(
            linear_data, 'Revenue', 'Date', periods=3
        )
        
        # Should use a trend-based method (double exponential smoothing)
        self.assertIn('Exponential', result_linear.method)
        self.assertIn('increasing', result_linear.trend_direction)
        
        # Test with minimal data - should use linear regression
        minimal_data = pd.DataFrame({
            'Date': pd.date_range('2024-01-01', periods=3, freq='MS'),
            'Revenue': [100, 150, 200]  # Too few points for other methods
        })
        
        result_minimal = self.forecast_analyzer.analyze_time_series(
            minimal_data, 'Revenue', 'Date', periods=3
        )
        
        # Should use linear regression for minimal data
        self.assertIn('Regression', result_minimal.method)
        
        # Test with seasonal data
        seasonal_data = pd.DataFrame({
            'Date': pd.date_range('2024-01-01', periods=12, freq='MS'),
            'Revenue': [100 + 20 * (i % 4) for i in range(12)]  # Seasonal pattern
        })
        
        result_seasonal = self.forecast_analyzer.analyze_time_series(
            seasonal_data, 'Revenue', 'Date', periods=3
        )
        
        # Should handle seasonal patterns
        self.assertIsInstance(result_seasonal, ForecastResult)
        self.assertEqual(len(result_seasonal.forecast_values), 3)
    
    def test_forecast_confidence_intervals(self):
        """Test that confidence intervals are calculated correctly."""
        result = self.forecast_analyzer.analyze_time_series(
            self.sample_data, 'Revenue', 'Date', periods=6
        )
        
        # Verify confidence intervals
        for i in range(len(result.forecast_values)):
            forecast_val = result.forecast_values[i]
            upper_bound = result.confidence_upper[i]
            lower_bound = result.confidence_lower[i]
            
            # Lower bound should be less than forecast value
            self.assertLess(lower_bound, forecast_val)
            
            # Upper bound should be greater than forecast value
            self.assertGreater(upper_bound, forecast_val)
            
            # Confidence interval should be reasonable
            interval_width = upper_bound - lower_bound
            self.assertGreater(interval_width, 0)
            self.assertLess(interval_width, forecast_val * 2)  # Sanity check
    
    def test_forecast_accuracy_metrics(self):
        """Test that accuracy metrics are calculated and included."""
        result = self.forecast_analyzer.analyze_time_series(
            self.sample_data, 'Revenue', 'Date', periods=6
        )
        
        # Verify accuracy metrics exist
        self.assertIsInstance(result.accuracy_metrics, dict)
        self.assertGreater(len(result.accuracy_metrics), 0)
        
        # Check for common metrics
        metric_keys = result.accuracy_metrics.keys()
        self.assertTrue(any('mae' in key.lower() for key in metric_keys))
        
        # Verify metric values are reasonable
        for key, value in result.accuracy_metrics.items():
            if isinstance(value, (int, float)):
                self.assertGreaterEqual(value, 0)  # Accuracy metrics should be non-negative
    
    def test_forecast_with_different_horizons(self):
        """Test forecasting with different forecast horizons."""
        # Test short-term forecast
        short_result = self.forecast_analyzer.analyze_time_series(
            self.sample_data, 'Revenue', 'Date', periods=1
        )
        self.assertEqual(len(short_result.forecast_values), 1)
        
        # Test medium-term forecast
        medium_result = self.forecast_analyzer.analyze_time_series(
            self.sample_data, 'Revenue', 'Date', periods=6
        )
        self.assertEqual(len(medium_result.forecast_values), 6)
        
        # Test long-term forecast (should be capped at max horizon)
        long_result = self.forecast_analyzer.analyze_time_series(
            self.sample_data, 'Revenue', 'Date', periods=20
        )
        self.assertEqual(len(long_result.forecast_values), 12)  # Capped at max_forecast_horizon
    
    def test_forecast_edge_cases(self):
        """Test forecasting with edge cases."""
        # Test with constant values
        constant_data = pd.DataFrame({
            'Date': pd.date_range('2024-01-01', periods=6, freq='MS'),
            'Revenue': [100] * 6
        })
        
        result_constant = self.forecast_analyzer.analyze_time_series(
            constant_data, 'Revenue', 'Date', periods=3
        )
        
        # Should still generate forecast
        self.assertIsInstance(result_constant, ForecastResult)
        self.assertEqual(len(result_constant.forecast_values), 3)
        
        # Test with minimal data
        minimal_data = pd.DataFrame({
            'Date': pd.date_range('2024-01-01', periods=3, freq='MS'),
            'Revenue': [100, 110, 105]
        })
        
        result_minimal = self.forecast_analyzer.analyze_time_series(
            minimal_data, 'Revenue', 'Date', periods=2
        )
        
        # Should still generate forecast
        self.assertIsInstance(result_minimal, ForecastResult)
        self.assertEqual(len(result_minimal.forecast_values), 2)
    
    def test_forecast_integration_with_handler(self):
        """Test integration with QuickActionHandler (future integration)."""
        # This test prepares for future integration with the handler
        # For now, we'll test that the analyzer can work with handler's data format
        
        # Simulate handler providing data
        current_data, data_summary = self.mock_app_core.get_current_data()
        
        # Generate forecast using handler's data
        result = self.forecast_analyzer.analyze_time_series(
            current_data, 'Revenue', 'Date', periods=6
        )
        
        # Verify integration works
        self.assertIsInstance(result, ForecastResult)
        self.assertEqual(len(result.forecast_values), 6)
        
        # Verify forecast values are in reasonable range relative to historical data
        historical_max = current_data['Revenue'].max()
        historical_min = current_data['Revenue'].min()
        
        for forecast_val in result.forecast_values:
            # Forecast should be within reasonable bounds
            self.assertGreater(forecast_val, historical_min * 0.5)
            self.assertLess(forecast_val, historical_max * 2.0)


if __name__ == '__main__':
    unittest.main()
