"""
Forecasting Analyzer for Quant Commander v2.0 - Phase 3B Implementation

This module provides time series forecasting capabilities for financial data analysis.
It implements multiple forecasting methods including linear regression, exponential smoothing,
and seasonal decomposition to predict future trends in revenue, costs, and profits.

Key Features:
- Linear trend forecasting
- Exponential smoothing (simple and double)
- Seasonal pattern detection
- Confidence interval calculation
- Multiple forecast horizons
- Integration with caching system

Author: AI Assistant
Date: July 2025
Phase: 3B - Advanced Analytics Core
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import warnings
from dataclasses import dataclass


@dataclass
class ForecastResult:
    """
    Data class to hold forecasting results.
    
    This structure contains all forecast information including predictions,
    confidence intervals, and metadata about the forecasting method used.
    """
    method: str                    # Forecasting method used
    forecast_values: List[float]   # Predicted values
    forecast_dates: List[str]      # Corresponding dates
    confidence_upper: List[float]  # Upper confidence interval
    confidence_lower: List[float]  # Lower confidence interval
    accuracy_metrics: Dict[str, float]  # R², MAE, RMSE, etc.
    seasonal_detected: bool        # Whether seasonal patterns were found
    trend_direction: str           # 'increasing', 'decreasing', 'stable'
    last_actual_value: float       # Last known actual value
    forecast_horizon: int          # Number of periods forecasted


class ForecastingAnalyzer:
    """
    Advanced forecasting analyzer for financial time series data.
    
    This class provides comprehensive forecasting capabilities using multiple
    statistical methods to predict future values of financial metrics.
    """
    
    def __init__(self, confidence_level: float = 0.95):
        """
        Initialize the forecasting analyzer.
        
        Args:
            confidence_level (float): Confidence level for prediction intervals (default: 0.95)
        """
        self.confidence_level = confidence_level
        self.min_data_points = 3  # Minimum points needed for forecasting
        self.max_forecast_horizon = 12  # Maximum periods to forecast
        
        print(f"📈 ForecastingAnalyzer initialized: confidence_level={confidence_level}")
    
    def analyze_time_series(self, data: pd.DataFrame, 
                           target_column: str,
                           date_column: str = 'Date',
                           periods: int = 6) -> ForecastResult:
        """
        Analyze time series data and generate forecasts.
        
        This is the main entry point for forecasting analysis. It automatically
        selects the best forecasting method based on data characteristics.
        
        Args:
            data (pd.DataFrame): Time series data
            target_column (str): Column to forecast (e.g., 'Revenue', 'Profit')
            date_column (str): Date column name (default: 'Date')
            periods (int): Number of periods to forecast (default: 6)
            
        Returns:
            ForecastResult: Comprehensive forecast results
            
        Raises:
            ValueError: If data is insufficient or invalid
        """
        try:
            # Validate input data
            self._validate_input_data(data, target_column, date_column)
            
            # Prepare time series data
            ts_data = self._prepare_time_series(data, target_column, date_column)
            
            # Detect data characteristics
            characteristics = self._analyze_data_characteristics(ts_data)
            
            # Select best forecasting method
            method = self._select_forecasting_method(characteristics)
            
            # Generate forecast
            forecast_result = self._generate_forecast(
                ts_data, method, periods, target_column
            )
            
            print(f"✅ Forecast generated: {method} method, {periods} periods")
            return forecast_result
            
        except Exception as e:
            print(f"❌ Forecasting error: {str(e)}")
            raise ValueError(f"Failed to generate forecast: {str(e)}")
    
    def _validate_input_data(self, data: pd.DataFrame, 
                            target_column: str, 
                            date_column: str) -> None:
        """
        Validate input data for forecasting.
        
        Args:
            data (pd.DataFrame): Input data
            target_column (str): Target column name
            date_column (str): Date column name
            
        Raises:
            ValueError: If data is invalid
        """
        if data.empty:
            raise ValueError("Data cannot be empty")
        
        if target_column not in data.columns:
            raise ValueError(f"Target column '{target_column}' not found in data")
        
        if date_column not in data.columns:
            raise ValueError(f"Date column '{date_column}' not found in data")
        
        if len(data) < self.min_data_points:
            raise ValueError(f"Insufficient data points. Need at least {self.min_data_points}")
        
        # Check for numeric target column
        if not pd.api.types.is_numeric_dtype(data[target_column]):
            raise ValueError(f"Target column '{target_column}' must be numeric")
    
    def _prepare_time_series(self, data: pd.DataFrame, 
                           target_column: str, 
                           date_column: str) -> pd.Series:
        """
        Prepare time series data for forecasting.
        
        Args:
            data (pd.DataFrame): Input data
            target_column (str): Target column name
            date_column (str): Date column name
            
        Returns:
            pd.Series: Prepared time series with datetime index
        """
        # Create a copy to avoid modifying original data
        df = data.copy()
        
        # Convert date column to datetime if needed
        if not pd.api.types.is_datetime64_any_dtype(df[date_column]):
            df[date_column] = pd.to_datetime(df[date_column])
        
        # Sort by date
        df = df.sort_values(date_column)
        
        # Set date as index
        df.set_index(date_column, inplace=True)
        
        # Return the target column as a series
        return df[target_column].dropna()
    
    def _analyze_data_characteristics(self, ts_data: pd.Series) -> Dict[str, Any]:
        """
        Analyze characteristics of the time series data.
        
        Args:
            ts_data (pd.Series): Time series data
            
        Returns:
            Dict[str, Any]: Data characteristics
        """
        characteristics = {
            'length': len(ts_data),
            'has_trend': self._detect_trend(ts_data),
            'has_seasonality': self._detect_seasonality(ts_data),
            'volatility': self._calculate_volatility(ts_data),
            'missing_values': ts_data.isna().sum(),
            'outliers': self._detect_outliers(ts_data)
        }
        
        return characteristics
    
    def _detect_trend(self, ts_data: pd.Series) -> bool:
        """
        Detect if there's a significant trend in the data.
        
        Args:
            ts_data (pd.Series): Time series data
            
        Returns:
            bool: True if trend is detected
        """
        # Simple trend detection using correlation with time
        x = np.arange(len(ts_data))
        correlation = np.corrcoef(x, ts_data)[0, 1]
        
        # Consider trend significant if correlation > 0.3
        return bool(abs(correlation) > 0.3)
    
    def _detect_seasonality(self, ts_data: pd.Series) -> bool:
        """
        Detect seasonal patterns in the data.
        
        Args:
            ts_data (pd.Series): Time series data
            
        Returns:
            bool: True if seasonality is detected
        """
        # Simple seasonality detection for monthly data
        if len(ts_data) < 12:
            return False
        
        # Check if data has regular patterns (simplified check)
        # In a real implementation, you'd use more sophisticated methods
        return bool(len(ts_data) >= 12)
    
    def _calculate_volatility(self, ts_data: pd.Series) -> float:
        """
        Calculate volatility (standard deviation) of the time series.
        
        Args:
            ts_data (pd.Series): Time series data
            
        Returns:
            float: Volatility measure
        """
        return ts_data.std()
    
    def _detect_outliers(self, ts_data: pd.Series) -> int:
        """
        Detect outliers in the time series using IQR method.
        
        Args:
            ts_data (pd.Series): Time series data
            
        Returns:
            int: Number of outliers detected
        """
        Q1 = ts_data.quantile(0.25)
        Q3 = ts_data.quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outliers = ((ts_data < lower_bound) | (ts_data > upper_bound)).sum()
        return outliers
    
    def _select_forecasting_method(self, characteristics: Dict[str, Any]) -> str:
        """
        Select the best forecasting method based on data characteristics.
        
        Args:
            characteristics (Dict[str, Any]): Data characteristics
            
        Returns:
            str: Selected forecasting method
        """
        # Simple method selection logic
        if characteristics['length'] < 6:
            return 'linear_regression'
        elif characteristics['has_trend'] and characteristics['volatility'] < 50:
            return 'double_exponential_smoothing'
        elif characteristics['has_seasonality']:
            return 'seasonal_decomposition'
        else:
            return 'simple_exponential_smoothing'
    
    def _generate_forecast(self, ts_data: pd.Series, 
                          method: str, 
                          periods: int, 
                          target_column: str) -> ForecastResult:
        """
        Generate forecast using the selected method.
        
        Args:
            ts_data (pd.Series): Time series data
            method (str): Forecasting method to use
            periods (int): Number of periods to forecast
            target_column (str): Target column name
            
        Returns:
            ForecastResult: Forecast results
        """
        from .forecast_methods import (
            linear_regression_forecast,
            simple_exponential_smoothing_forecast,
            double_exponential_smoothing_forecast,
            seasonal_forecast
        )
        
        # Cap periods to maximum allowed
        periods = min(periods, self.max_forecast_horizon)
        
        # Generate forecast based on method
        if method == 'linear_regression':
            return linear_regression_forecast(ts_data, periods, target_column, self.confidence_level)
        elif method == 'simple_exponential_smoothing':
            return simple_exponential_smoothing_forecast(ts_data, periods, target_column, self.confidence_level)
        elif method == 'double_exponential_smoothing':
            return double_exponential_smoothing_forecast(ts_data, periods, target_column, self.confidence_level)
        elif method == 'seasonal_decomposition':
            return seasonal_forecast(ts_data, periods, target_column, self.confidence_level)
        else:
            # Default to linear regression
            return linear_regression_forecast(ts_data, periods, target_column, self.confidence_level)
    
    def format_forecast_for_display(self, forecast_result: ForecastResult) -> str:
        """
        Format forecast results for display in the UI.
        
        Args:
            forecast_result (ForecastResult): Forecast results
            
        Returns:
            str: Formatted forecast display string
        """
        # Create formatted output for the UI
        output = f"📈 **{forecast_result.method} Forecast**\n\n"
        
        # Add forecast overview
        output += f"**Forecast Summary:**\n"
        output += f"• Method: {forecast_result.method}\n"
        output += f"• Periods: {forecast_result.forecast_horizon}\n"
        output += f"• Trend: {forecast_result.trend_direction.title()}\n"
        output += f"• Seasonal: {'Yes' if forecast_result.seasonal_detected else 'No'}\n"
        output += f"• Last Value: ${forecast_result.last_actual_value:,.2f}\n\n"
        
        # Add forecast values
        output += "**Forecast Values:**\n"
        for i, (date, value, upper, lower) in enumerate(zip(
            forecast_result.forecast_dates,
            forecast_result.forecast_values,
            forecast_result.confidence_upper,
            forecast_result.confidence_lower
        )):
            output += f"• {date}: ${value:,.2f} (${lower:,.2f} - ${upper:,.2f})\n"
        
        # Add accuracy metrics
        output += f"\n**Accuracy Metrics:**\n"
        for metric, value in forecast_result.accuracy_metrics.items():
            if isinstance(value, float):
                output += f"• {metric.replace('_', ' ').title()}: {value:.3f}\n"
            else:
                output += f"• {metric.replace('_', ' ').title()}: {value}\n"
        
        # Add insights
        output += f"\n**Key Insights:**\n"
        if forecast_result.trend_direction == 'increasing':
            output += "• Positive growth trend detected\n"
        elif forecast_result.trend_direction == 'decreasing':
            output += "• Declining trend detected\n"
        else:
            output += "• Stable trend with minimal change\n"
        
        if forecast_result.seasonal_detected:
            output += "• Seasonal patterns incorporated in forecast\n"
        
        return output
