"""
Unit tests for ForecastingAnalyzer - Phase 3B Implementation

This module contains comprehensive unit tests for the forecasting analyzer
to ensure all forecasting methods work correctly and handle edge cases.

Test Categories:
- Initialization and configuration
- Data validation and preparation
- Characteristic analysis
- Method selection
- Forecast generation
- Error handling
- Edge cases

Author: AI Assistant
Date: July 2025
Phase: 3B - Advanced Analytics Core
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import sys
import os

# Add the parent directory to the path to import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analyzers.forecast_analyzer import ForecastingAnalyzer, ForecastResult


class TestForecastingAnalyzer(unittest.TestCase):
    """
    Test suite for ForecastingAnalyzer class.
    
    Tests all core functionality including initialization, data validation,
    forecasting methods, and error handling.
    """
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create forecasting analyzer instance
        self.analyzer = ForecastingAnalyzer(confidence_level=0.95)
        
        # Create sample time series data
        self.sample_dates = pd.date_range('2024-01-01', periods=12, freq='MS')
        self.sample_values = [100, 110, 105, 120, 115, 130, 125, 140, 135, 150, 145, 160]
        
        self.sample_data = pd.DataFrame({
            'Date': self.sample_dates,
            'Revenue': self.sample_values,
            'Cost': [val * 0.6 for val in self.sample_values],
            'Profit': [val * 0.4 for val in self.sample_values]
        })
        
        # Create data with different characteristics
        self.linear_trend_data = pd.DataFrame({
            'Date': self.sample_dates,
            'Revenue': [100 + i * 10 for i in range(12)]  # Clear linear trend
        })
        
        self.seasonal_data = pd.DataFrame({
            'Date': self.sample_dates,
            'Revenue': [100 + 10 * np.sin(i * np.pi / 6) for i in range(12)]  # Seasonal pattern
        })
        
        self.minimal_data = pd.DataFrame({
            'Date': pd.date_range('2024-01-01', periods=3, freq='MS'),
            'Revenue': [100, 110, 105]
        })
    
    def test_analyzer_initialization(self):
        """Test that forecasting analyzer initializes correctly."""
        # Test default initialization
        analyzer = ForecastingAnalyzer()
        self.assertEqual(analyzer.confidence_level, 0.95)
        self.assertEqual(analyzer.min_data_points, 3)
        self.assertEqual(analyzer.max_forecast_horizon, 12)
        
        # Test custom initialization
        custom_analyzer = ForecastingAnalyzer(confidence_level=0.99)
        self.assertEqual(custom_analyzer.confidence_level, 0.99)
    
    def test_data_validation_success(self):
        """Test successful data validation."""
        # Should not raise any exceptions
        try:
            self.analyzer._validate_input_data(self.sample_data, 'Revenue', 'Date')
        except Exception as e:
            self.fail(f"Data validation failed unexpectedly: {e}")
    
    def test_data_validation_empty_data(self):
        """Test data validation with empty data."""
        empty_data = pd.DataFrame()
        with self.assertRaises(ValueError) as context:
            self.analyzer._validate_input_data(empty_data, 'Revenue', 'Date')
        self.assertIn("cannot be empty", str(context.exception))
    
    def test_data_validation_missing_columns(self):
        """Test data validation with missing columns."""
        # Missing target column
        with self.assertRaises(ValueError) as context:
            self.analyzer._validate_input_data(self.sample_data, 'NonExistent', 'Date')
        self.assertIn("not found in data", str(context.exception))
        
        # Missing date column
        with self.assertRaises(ValueError) as context:
            self.analyzer._validate_input_data(self.sample_data, 'Revenue', 'NonExistent')
        self.assertIn("not found in data", str(context.exception))
    
    def test_data_validation_insufficient_data(self):
        """Test data validation with insufficient data points."""
        insufficient_data = pd.DataFrame({
            'Date': pd.date_range('2024-01-01', periods=2, freq='MS'),
            'Revenue': [100, 110]
        })
        
        with self.assertRaises(ValueError) as context:
            self.analyzer._validate_input_data(insufficient_data, 'Revenue', 'Date')
        self.assertIn("Insufficient data points", str(context.exception))
    
    def test_data_validation_non_numeric_target(self):
        """Test data validation with non-numeric target column."""
        invalid_data = self.sample_data.copy()
        invalid_data['Revenue'] = ['high', 'medium', 'low'] * 4
        
        with self.assertRaises(ValueError) as context:
            self.analyzer._validate_input_data(invalid_data, 'Revenue', 'Date')
        self.assertIn("must be numeric", str(context.exception))
    
    def test_time_series_preparation(self):
        """Test time series data preparation."""
        ts_data = self.analyzer._prepare_time_series(self.sample_data, 'Revenue', 'Date')
        
        # Check that result is a pandas Series
        self.assertIsInstance(ts_data, pd.Series)
        
        # Check that index is datetime
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(ts_data.index))
        
        # Check that data is sorted by date
        self.assertTrue(ts_data.index.is_monotonic_increasing)
        
        # Check that values are correct
        self.assertEqual(len(ts_data), 12)
        self.assertEqual(ts_data.iloc[0], 100)
        self.assertEqual(ts_data.iloc[-1], 160)
    
    def test_trend_detection(self):
        """Test trend detection in time series data."""
        # Test with linear trend data
        ts_linear = self.analyzer._prepare_time_series(self.linear_trend_data, 'Revenue', 'Date')
        has_trend = self.analyzer._detect_trend(ts_linear)
        self.assertTrue(has_trend, "Should detect trend in linear data")
        
        # Test with flat data
        flat_data = pd.DataFrame({
            'Date': self.sample_dates,
            'Revenue': [100] * 12  # No trend
        })
        ts_flat = self.analyzer._prepare_time_series(flat_data, 'Revenue', 'Date')
        has_trend = self.analyzer._detect_trend(ts_flat)
        self.assertFalse(has_trend, "Should not detect trend in flat data")
    
    def test_seasonality_detection(self):
        """Test seasonality detection in time series data."""
        # Test with sufficient data
        ts_data = self.analyzer._prepare_time_series(self.sample_data, 'Revenue', 'Date')
        has_seasonality = self.analyzer._detect_seasonality(ts_data)
        self.assertTrue(has_seasonality, "Should detect seasonality with 12+ data points")
        
        # Test with insufficient data
        ts_minimal = self.analyzer._prepare_time_series(self.minimal_data, 'Revenue', 'Date')
        has_seasonality = self.analyzer._detect_seasonality(ts_minimal)
        self.assertFalse(has_seasonality, "Should not detect seasonality with <12 data points")
    
    def test_volatility_calculation(self):
        """Test volatility calculation."""
        ts_data = self.analyzer._prepare_time_series(self.sample_data, 'Revenue', 'Date')
        volatility = self.analyzer._calculate_volatility(ts_data)
        
        # Check that volatility is a positive number
        self.assertIsInstance(volatility, float)
        self.assertGreater(volatility, 0)
        
        # Check that volatility matches expected standard deviation
        expected_std = ts_data.std()
        self.assertAlmostEqual(volatility, expected_std, places=5)
    
    def test_outlier_detection(self):
        """Test outlier detection in time series data."""
        # Create data with outliers
        outlier_data = self.sample_data.copy()
        outlier_data.loc[5, 'Revenue'] = 1000  # Add outlier
        
        ts_outlier = self.analyzer._prepare_time_series(outlier_data, 'Revenue', 'Date')
        num_outliers = self.analyzer._detect_outliers(ts_outlier)
        
        self.assertGreater(num_outliers, 0, "Should detect outliers")
    
    def test_data_characteristics_analysis(self):
        """Test comprehensive data characteristics analysis."""
        ts_data = self.analyzer._prepare_time_series(self.sample_data, 'Revenue', 'Date')
        characteristics = self.analyzer._analyze_data_characteristics(ts_data)
        
        # Check that all expected keys are present
        expected_keys = ['length', 'has_trend', 'has_seasonality', 'volatility', 'missing_values', 'outliers']
        for key in expected_keys:
            self.assertIn(key, characteristics)
        
        # Check data types
        self.assertIsInstance(characteristics['length'], int)
        self.assertIsInstance(characteristics['has_trend'], bool)
        self.assertIsInstance(characteristics['has_seasonality'], bool)
        self.assertIsInstance(characteristics['volatility'], float)
        self.assertIsInstance(characteristics['missing_values'], (int, np.integer))
        self.assertIsInstance(characteristics['outliers'], (int, np.integer))
    
    def test_forecasting_method_selection(self):
        """Test forecasting method selection based on characteristics."""
        # Test with minimal data
        minimal_chars = {'length': 3, 'has_trend': False, 'has_seasonality': False, 'volatility': 10, 'missing_values': 0, 'outliers': 0}
        method = self.analyzer._select_forecasting_method(minimal_chars)
        self.assertEqual(method, 'linear_regression')
        
        # Test with trending data
        trend_chars = {'length': 12, 'has_trend': True, 'has_seasonality': False, 'volatility': 20, 'missing_values': 0, 'outliers': 0}
        method = self.analyzer._select_forecasting_method(trend_chars)
        self.assertEqual(method, 'double_exponential_smoothing')
        
        # Test with seasonal data
        seasonal_chars = {'length': 12, 'has_trend': False, 'has_seasonality': True, 'volatility': 30, 'missing_values': 0, 'outliers': 0}
        method = self.analyzer._select_forecasting_method(seasonal_chars)
        self.assertEqual(method, 'seasonal_decomposition')
    
    def test_forecast_generation_linear_regression(self):
        """Test forecast generation using linear regression."""
        # Use minimal data (< 6 points) to trigger linear regression
        result = self.analyzer.analyze_time_series(self.minimal_data, 'Revenue', 'Date', periods=3)
        
        # Check result structure
        self.assertIsInstance(result, ForecastResult)
        self.assertEqual(result.method, 'Linear Regression')
        self.assertEqual(len(result.forecast_values), 3)
        self.assertEqual(len(result.forecast_dates), 3)
        self.assertEqual(len(result.confidence_upper), 3)
        self.assertEqual(len(result.confidence_lower), 3)
        
        # Check that forecast values are reasonable
        self.assertGreater(result.forecast_values[0], 0)
        self.assertLess(result.forecast_values[0], 10000)  # Sanity check
    
    def test_forecast_generation_with_different_periods(self):
        """Test forecast generation with different forecast horizons."""
        # Test with 1 period
        result_1 = self.analyzer.analyze_time_series(self.sample_data, 'Revenue', 'Date', periods=1)
        self.assertEqual(len(result_1.forecast_values), 1)
        
        # Test with 6 periods
        result_6 = self.analyzer.analyze_time_series(self.sample_data, 'Revenue', 'Date', periods=6)
        self.assertEqual(len(result_6.forecast_values), 6)
        
        # Test with maximum periods (should be capped)
        result_max = self.analyzer.analyze_time_series(self.sample_data, 'Revenue', 'Date', periods=20)
        self.assertEqual(len(result_max.forecast_values), 12)  # Should be capped at max_forecast_horizon
    
    def test_forecast_result_structure(self):
        """Test that forecast results have correct structure."""
        result = self.analyzer.analyze_time_series(self.sample_data, 'Revenue', 'Date', periods=3)
        
        # Check all required attributes are present
        self.assertIsInstance(result.method, str)
        self.assertIsInstance(result.forecast_values, list)
        self.assertIsInstance(result.forecast_dates, list)
        self.assertIsInstance(result.confidence_upper, list)
        self.assertIsInstance(result.confidence_lower, list)
        self.assertIsInstance(result.accuracy_metrics, dict)
        self.assertIsInstance(result.seasonal_detected, bool)
        self.assertIsInstance(result.trend_direction, str)
        self.assertIsInstance(result.last_actual_value, float)
        self.assertIsInstance(result.forecast_horizon, int)
        
        # Check that confidence intervals make sense
        for i in range(len(result.forecast_values)):
            self.assertLessEqual(result.confidence_lower[i], result.forecast_values[i])
            self.assertGreaterEqual(result.confidence_upper[i], result.forecast_values[i])
    
    def test_forecast_display_formatting(self):
        """Test forecast result formatting for display."""
        result = self.analyzer.analyze_time_series(self.sample_data, 'Revenue', 'Date', periods=3)
        display_text = self.analyzer.format_forecast_for_display(result)
        
        # Check that display text is a string
        self.assertIsInstance(display_text, str)
        
        # Check that key information is included
        self.assertIn("Forecast", display_text)
        self.assertIn("Method:", display_text)
        self.assertIn("Periods:", display_text)
        self.assertIn("Trend:", display_text)
        self.assertIn("Forecast Values:", display_text)
        self.assertIn("Accuracy Metrics:", display_text)
        self.assertIn("Key Insights:", display_text)
    
    def test_error_handling_invalid_input(self):
        """Test error handling with invalid input data."""
        # Test with invalid target column
        with self.assertRaises(ValueError):
            self.analyzer.analyze_time_series(self.sample_data, 'InvalidColumn', 'Date', periods=3)
        
        # Test with invalid date column
        with self.assertRaises(ValueError):
            self.analyzer.analyze_time_series(self.sample_data, 'Revenue', 'InvalidDate', periods=3)
    
    def test_edge_case_minimal_data(self):
        """Test forecasting with minimal data points."""
        result = self.analyzer.analyze_time_series(self.minimal_data, 'Revenue', 'Date', periods=2)
        
        # Should still generate forecast
        self.assertIsInstance(result, ForecastResult)
        self.assertEqual(len(result.forecast_values), 2)
        self.assertEqual(result.method, 'Linear Regression')  # Should fall back to linear regression
    
    def test_edge_case_single_value_data(self):
        """Test forecasting with constant values."""
        constant_data = pd.DataFrame({
            'Date': pd.date_range('2024-01-01', periods=6, freq='MS'),
            'Revenue': [100] * 6  # All same value
        })
        
        result = self.analyzer.analyze_time_series(constant_data, 'Revenue', 'Date', periods=3)
        
        # Should still generate forecast
        self.assertIsInstance(result, ForecastResult)
        self.assertEqual(len(result.forecast_values), 3)
    
    def test_confidence_level_parameter(self):
        """Test that confidence level parameter affects results."""
        # Test with different confidence levels
        analyzer_95 = ForecastingAnalyzer(confidence_level=0.95)
        analyzer_99 = ForecastingAnalyzer(confidence_level=0.99)
        
        result_95 = analyzer_95.analyze_time_series(self.sample_data, 'Revenue', 'Date', periods=3)
        result_99 = analyzer_99.analyze_time_series(self.sample_data, 'Revenue', 'Date', periods=3)
        
        # 99% confidence intervals should be wider than 95%
        for i in range(len(result_95.forecast_values)):
            interval_95 = result_95.confidence_upper[i] - result_95.confidence_lower[i]
            interval_99 = result_99.confidence_upper[i] - result_99.confidence_lower[i]
            self.assertGreater(interval_99, interval_95)


if __name__ == '__main__':
    unittest.main()
