"""
Forecasting Methods for Quant Commander v2.0 - Phase 3B Implementation

This module contains the specific forecasting method implementations.
Each method is kept in a separate function to maintain modularity and clarity.

Methods Implemented:
- Linear Regression Forecasting
- Simple Exponential Smoothing
- Double Exponential Smoothing (Holt's method)
- Seasonal Decomposition Forecasting

Author: AI Assistant
Date: July 2025
Phase: 3B - Advanced Analytics Core
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from .forecast_analyzer import ForecastResult


def linear_regression_forecast(ts_data: pd.Series, 
                             periods: int, 
                             target_column: str,
                             confidence_level: float = 0.95) -> ForecastResult:
    """
    Generate forecast using linear regression.
    
    This method fits a linear trend to the historical data and extrapolates
    it into the future. Best for data with clear linear trends.
    
    Args:
        ts_data (pd.Series): Time series data
        periods (int): Number of periods to forecast
        target_column (str): Target column name
        confidence_level (float): Confidence level for intervals
        
    Returns:
        ForecastResult: Forecast results with linear trend
    """
    # Prepare data for linear regression
    n = len(ts_data)
    x = np.arange(n)
    y = ts_data.values
    
    # Calculate linear regression coefficients
    slope, intercept = np.polyfit(x, y, 1)
    
    # Generate forecast values
    forecast_x = np.arange(n, n + periods)
    forecast_values = [slope * xi + intercept for xi in forecast_x]
    
    # Calculate residuals for confidence intervals
    fitted_values = slope * x + intercept
    residuals = y - fitted_values
    residual_std = np.std(residuals)
    
    # Calculate confidence intervals
    z_score = 1.96 if confidence_level == 0.95 else 2.576  # 95% or 99%
    margin_of_error = z_score * residual_std
    
    confidence_upper = [val + margin_of_error for val in forecast_values]
    confidence_lower = [val - margin_of_error for val in forecast_values]
    
    # Generate forecast dates
    last_date = ts_data.index[-1]
    forecast_dates = _generate_forecast_dates(last_date, periods)
    
    # Calculate accuracy metrics
    r_squared = _calculate_r_squared(y, fitted_values)
    mae = _calculate_mae(y, fitted_values)
    rmse = _calculate_rmse(y, fitted_values)
    
    accuracy_metrics = {
        'r_squared': r_squared,
        'mae': mae,
        'rmse': rmse,
        'method_confidence': 'high' if r_squared > 0.7 else 'medium' if r_squared > 0.4 else 'low'
    }
    
    # Determine trend direction
    trend_direction = 'increasing' if slope > 0 else 'decreasing' if slope < 0 else 'stable'
    
    return ForecastResult(
        method='Linear Regression',
        forecast_values=forecast_values,
        forecast_dates=forecast_dates,
        confidence_upper=confidence_upper,
        confidence_lower=confidence_lower,
        accuracy_metrics=accuracy_metrics,
        seasonal_detected=False,
        trend_direction=trend_direction,
        last_actual_value=float(ts_data.iloc[-1]),
        forecast_horizon=periods
    )


def simple_exponential_smoothing_forecast(ts_data: pd.Series, 
                                        periods: int, 
                                        target_column: str,
                                        confidence_level: float = 0.95,
                                        alpha: float = 0.3) -> ForecastResult:
    """
    Generate forecast using simple exponential smoothing.
    
    This method uses exponential smoothing to forecast future values,
    giving more weight to recent observations.
    
    Args:
        ts_data (pd.Series): Time series data
        periods (int): Number of periods to forecast
        target_column (str): Target column name
        confidence_level (float): Confidence level for intervals
        alpha (float): Smoothing parameter (0 < alpha < 1)
        
    Returns:
        ForecastResult: Forecast results with exponential smoothing
    """
    values = ts_data.values
    n = len(values)
    
    # Initialize smoothed values
    smoothed = np.zeros(n)
    smoothed[0] = values[0]
    
    # Apply exponential smoothing
    for i in range(1, n):
        smoothed[i] = alpha * values[i] + (1 - alpha) * smoothed[i-1]
    
    # Forecast future values (constant at last smoothed value)
    last_smoothed = smoothed[-1]
    forecast_values = [last_smoothed] * periods
    
    # Calculate residuals and confidence intervals
    residuals = values - smoothed
    residual_std = np.std(residuals)
    
    z_score = 1.96 if confidence_level == 0.95 else 2.576
    margin_of_error = z_score * residual_std
    
    confidence_upper = [val + margin_of_error for val in forecast_values]
    confidence_lower = [val - margin_of_error for val in forecast_values]
    
    # Generate forecast dates
    last_date = ts_data.index[-1]
    forecast_dates = _generate_forecast_dates(last_date, periods)
    
    # Calculate accuracy metrics
    mae = _calculate_mae(values, smoothed)
    rmse = _calculate_rmse(values, smoothed)
    
    accuracy_metrics = {
        'mae': mae,
        'rmse': rmse,
        'alpha': alpha,
        'method_confidence': 'medium'
    }
    
    return ForecastResult(
        method='Simple Exponential Smoothing',
        forecast_values=forecast_values,
        forecast_dates=forecast_dates,
        confidence_upper=confidence_upper,
        confidence_lower=confidence_lower,
        accuracy_metrics=accuracy_metrics,
        seasonal_detected=False,
        trend_direction='stable',
        last_actual_value=float(ts_data.iloc[-1]),
        forecast_horizon=periods
    )


def double_exponential_smoothing_forecast(ts_data: pd.Series, 
                                        periods: int, 
                                        target_column: str,
                                        confidence_level: float = 0.95,
                                        alpha: float = 0.3,
                                        beta: float = 0.1) -> ForecastResult:
    """
    Generate forecast using double exponential smoothing (Holt's method).
    
    This method captures both level and trend in the data, making it
    suitable for data with linear trends.
    
    Args:
        ts_data (pd.Series): Time series data
        periods (int): Number of periods to forecast
        target_column (str): Target column name
        confidence_level (float): Confidence level for intervals
        alpha (float): Level smoothing parameter
        beta (float): Trend smoothing parameter
        
    Returns:
        ForecastResult: Forecast results with trend smoothing
    """
    values = ts_data.values
    n = len(values)
    
    # Initialize level and trend
    level = values[0]
    trend = values[1] - values[0] if n > 1 else 0
    
    # Store smoothed values for error calculation
    smoothed = np.zeros(n)
    smoothed[0] = level
    
    # Apply double exponential smoothing
    for i in range(1, n):
        prev_level = level
        level = alpha * values[i] + (1 - alpha) * (level + trend)
        trend = beta * (level - prev_level) + (1 - beta) * trend
        smoothed[i] = level
    
    # Generate forecast values
    forecast_values = []
    for h in range(1, periods + 1):
        forecast_val = level + h * trend
        forecast_values.append(forecast_val)
    
    # Calculate residuals and confidence intervals
    residuals = values - smoothed
    residual_std = np.std(residuals)
    
    z_score = 1.96 if confidence_level == 0.95 else 2.576
    margin_of_error = z_score * residual_std
    
    confidence_upper = [val + margin_of_error for val in forecast_values]
    confidence_lower = [val - margin_of_error for val in forecast_values]
    
    # Generate forecast dates
    last_date = ts_data.index[-1]
    forecast_dates = _generate_forecast_dates(last_date, periods)
    
    # Calculate accuracy metrics
    mae = _calculate_mae(values, smoothed)
    rmse = _calculate_rmse(values, smoothed)
    
    accuracy_metrics = {
        'mae': mae,
        'rmse': rmse,
        'alpha': alpha,
        'beta': beta,
        'final_trend': trend,
        'method_confidence': 'high' if abs(trend) > 0.1 else 'medium'
    }
    
    # Determine trend direction
    trend_direction = 'increasing' if trend > 0 else 'decreasing' if trend < 0 else 'stable'
    
    return ForecastResult(
        method='Double Exponential Smoothing',
        forecast_values=forecast_values,
        forecast_dates=forecast_dates,
        confidence_upper=confidence_upper,
        confidence_lower=confidence_lower,
        accuracy_metrics=accuracy_metrics,
        seasonal_detected=False,
        trend_direction=trend_direction,
        last_actual_value=float(ts_data.iloc[-1]),
        forecast_horizon=periods
    )


def seasonal_forecast(ts_data: pd.Series, 
                     periods: int, 
                     target_column: str,
                     confidence_level: float = 0.95) -> ForecastResult:
    """
    Generate forecast using seasonal decomposition.
    
    This method decomposes the time series into trend, seasonal, and residual
    components, then forecasts each component separately.
    
    Args:
        ts_data (pd.Series): Time series data
        periods (int): Number of periods to forecast
        target_column (str): Target column name
        confidence_level (float): Confidence level for intervals
        
    Returns:
        ForecastResult: Forecast results with seasonal patterns
    """
    values = ts_data.values
    n = len(values)
    
    # Simple seasonal decomposition (assuming monthly data)
    season_length = min(12, n // 2)  # Adaptive season length
    
    # Calculate seasonal components
    seasonal_pattern = _calculate_seasonal_pattern(values, season_length)
    
    # Deseasonalize data
    deseasonalized = _deseasonalize_data(values, seasonal_pattern, season_length)
    
    # Forecast trend component using linear regression
    trend_forecast = _forecast_trend(deseasonalized, periods)
    
    # Add seasonal pattern to trend forecast
    forecast_values = []
    for i in range(periods):
        seasonal_index = i % season_length
        seasonal_factor = seasonal_pattern[seasonal_index]
        forecast_val = trend_forecast[i] + seasonal_factor
        forecast_values.append(forecast_val)
    
    # Calculate confidence intervals
    residuals = values - (deseasonalized + np.tile(seasonal_pattern, n // season_length + 1)[:n])
    residual_std = np.std(residuals)
    
    z_score = 1.96 if confidence_level == 0.95 else 2.576
    margin_of_error = z_score * residual_std
    
    confidence_upper = [val + margin_of_error for val in forecast_values]
    confidence_lower = [val - margin_of_error for val in forecast_values]
    
    # Generate forecast dates
    last_date = ts_data.index[-1]
    forecast_dates = _generate_forecast_dates(last_date, periods)
    
    # Calculate accuracy metrics
    mae = _calculate_mae(values, deseasonalized + np.tile(seasonal_pattern, n // season_length + 1)[:n])
    rmse = _calculate_rmse(values, deseasonalized + np.tile(seasonal_pattern, n // season_length + 1)[:n])
    
    accuracy_metrics = {
        'mae': mae,
        'rmse': rmse,
        'seasonal_strength': np.std(seasonal_pattern),
        'method_confidence': 'high'
    }
    
    return ForecastResult(
        method='Seasonal Decomposition',
        forecast_values=forecast_values,
        forecast_dates=forecast_dates,
        confidence_upper=confidence_upper,
        confidence_lower=confidence_lower,
        accuracy_metrics=accuracy_metrics,
        seasonal_detected=True,
        trend_direction='seasonal',
        last_actual_value=float(ts_data.iloc[-1]),
        forecast_horizon=periods
    )


# Helper functions for forecasting methods

def _generate_forecast_dates(last_date: datetime, periods: int) -> List[str]:
    """Generate forecast dates based on the last date."""
    forecast_dates = []
    for i in range(1, periods + 1):
        next_date = last_date + timedelta(days=30 * i)  # Assume monthly data
        forecast_dates.append(next_date.strftime('%Y-%m-%d'))
    return forecast_dates


def _calculate_r_squared(actual: np.ndarray, predicted: np.ndarray) -> float:
    """Calculate R-squared statistic."""
    ss_res = np.sum((actual - predicted) ** 2)
    ss_tot = np.sum((actual - np.mean(actual)) ** 2)
    return 1 - (ss_res / ss_tot) if ss_tot != 0 else 0


def _calculate_mae(actual: np.ndarray, predicted: np.ndarray) -> float:
    """Calculate Mean Absolute Error."""
    return np.mean(np.abs(actual - predicted))


def _calculate_rmse(actual: np.ndarray, predicted: np.ndarray) -> float:
    """Calculate Root Mean Square Error."""
    return np.sqrt(np.mean((actual - predicted) ** 2))


def _calculate_seasonal_pattern(values: np.ndarray, season_length: int) -> np.ndarray:
    """Calculate seasonal pattern from time series data."""
    n = len(values)
    seasonal_sums = np.zeros(season_length)
    seasonal_counts = np.zeros(season_length)
    
    for i, val in enumerate(values):
        seasonal_index = i % season_length
        seasonal_sums[seasonal_index] += val
        seasonal_counts[seasonal_index] += 1
    
    # Calculate seasonal averages
    seasonal_averages = seasonal_sums / seasonal_counts
    overall_average = np.mean(values)
    
    # Return seasonal factors (deviations from overall average)
    return seasonal_averages - overall_average


def _deseasonalize_data(values: np.ndarray, seasonal_pattern: np.ndarray, season_length: int) -> np.ndarray:
    """Remove seasonal pattern from time series data."""
    deseasonalized = np.zeros_like(values)
    
    for i, val in enumerate(values):
        seasonal_index = i % season_length
        deseasonalized[i] = val - seasonal_pattern[seasonal_index]
    
    return deseasonalized


def _forecast_trend(deseasonalized: np.ndarray, periods: int) -> List[float]:
    """Forecast trend component using linear regression."""
    n = len(deseasonalized)
    x = np.arange(n)
    
    # Linear regression on deseasonalized data
    slope, intercept = np.polyfit(x, deseasonalized, 1)
    
    # Generate trend forecast
    forecast_x = np.arange(n, n + periods)
    trend_forecast = [slope * xi + intercept for xi in forecast_x]
    
    return trend_forecast
