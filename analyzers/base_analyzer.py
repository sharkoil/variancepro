"""
Base Analyzer for VariancePro
Provides common functionality for all financial analyzers
"""

import pandas as pd
from typing import Dict, Any, Optional, List, Union
from abc import ABC, abstractmethod
from config.settings import Settings


class AnalysisError(Exception):
    """Custom exception for analysis errors"""
    pass


class BaseAnalyzer(ABC):
    """
    Base class for all financial analyzers
    Provides common functionality and defines the analyzer interface
    """
    
    def __init__(self, settings: Settings):
        """
        Initialize base analyzer
        
        Args:
            settings: Application settings instance
        """
        self.settings = settings
        self.data: Optional[pd.DataFrame] = None
        self.results: Dict[str, Any] = {}
        self.status: str = "not_analyzed"
        self.analysis_type: str = "base"
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    @abstractmethod
    def analyze(self, data: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        """
        Main analysis method - must be implemented by subclasses
        
        Args:
            data: Input DataFrame to analyze
            **kwargs: Additional analysis parameters
            
        Returns:
            Dictionary with analysis results
            
        Raises:
            AnalysisError: If analysis fails
        """
        pass
    
    def validate_data(self, data: pd.DataFrame) -> bool:
        """
        Validate data before analysis
        
        Args:
            data: DataFrame to validate
            
        Returns:
            True if validation passes
            
        Raises:
            AnalysisError: If validation fails
        """
        if data is None or data.empty:
            raise AnalysisError("Data is empty or None")
        
        if len(data) == 0:
            raise AnalysisError("Data contains no rows")
        
        if len(data.columns) == 0:
            raise AnalysisError("Data contains no columns")
        
        # Check for reasonable data size
        max_rows = getattr(self.settings, 'max_analysis_rows', 100_000)
        if len(data) > max_rows:
            self.warnings.append(
                f"Large dataset: {len(data):,} rows. "
                f"Consider sampling for better performance."
            )
        
        return True
    
    def validate_columns(self, data: pd.DataFrame, required_columns: List[str]) -> bool:
        """
        Validate required columns exist in data
        
        Args:
            data: DataFrame to check
            required_columns: List of required column names
            
        Returns:
            True if all columns exist
            
        Raises:
            AnalysisError: If required columns are missing
        """
        missing_columns = [col for col in required_columns if col not in data.columns]
        
        if missing_columns:
            raise AnalysisError(
                f"Missing required columns: {missing_columns}. "
                f"Available columns: {list(data.columns)}"
            )
        
        return True
    
    def validate_numeric_columns(self, data: pd.DataFrame, columns: List[str]) -> bool:
        """
        Validate that specified columns are numeric
        
        Args:
            data: DataFrame to check
            columns: List of column names that should be numeric
            
        Returns:
            True if all columns are numeric
            
        Raises:
            AnalysisError: If columns are not numeric
        """
        non_numeric = []
        
        for col in columns:
            if col in data.columns:
                if not pd.api.types.is_numeric_dtype(data[col]):
                    # Try to convert to numeric
                    try:
                        pd.to_numeric(data[col], errors='raise')
                    except (ValueError, TypeError):
                        non_numeric.append(col)
        
        if non_numeric:
            raise AnalysisError(
                f"Columns must be numeric: {non_numeric}. "
                f"Please ensure these columns contain only numbers."
            )
        
        return True
    
    def clean_numeric_data(self, data: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """
        Clean and prepare numeric data for analysis
        
        Args:
            data: Input DataFrame
            columns: List of numeric columns to clean
            
        Returns:
            DataFrame with cleaned numeric data
        """
        cleaned_data = data.copy()
        
        for col in columns:
            if col in cleaned_data.columns:
                # Convert to numeric, replacing errors with NaN
                cleaned_data[col] = pd.to_numeric(cleaned_data[col], errors='coerce')
                
                # Check for infinite values
                inf_count = np.isinf(cleaned_data[col]).sum()
                if inf_count > 0:
                    self.warnings.append(f"Column '{col}' contains {inf_count} infinite values")
                    cleaned_data[col] = cleaned_data[col].replace([np.inf, -np.inf], np.nan)
                
                # Check for missing values
                na_count = cleaned_data[col].isna().sum()
                if na_count > 0:
                    self.warnings.append(
                        f"Column '{col}' contains {na_count} missing values "
                        f"({na_count/len(cleaned_data)*100:.1f}%)"
                    )
        
        return cleaned_data
    
    def format_currency(self, value: Union[int, float], currency_symbol: str = "$") -> str:
        """
        Format numeric value as currency
        
        Args:
            value: Numeric value to format
            currency_symbol: Currency symbol to use
            
        Returns:
            Formatted currency string
        """
        if pd.isna(value):
            return "N/A"
        
        if abs(value) >= 1_000_000:
            return f"{currency_symbol}{value/1_000_000:.1f}M"
        elif abs(value) >= 1_000:
            return f"{currency_symbol}{value/1_000:.1f}K"
        else:
            return f"{currency_symbol}{value:.2f}"
    
    def format_percentage(self, value: Union[int, float], decimal_places: int = 1) -> str:
        """
        Format numeric value as percentage
        
        Args:
            value: Numeric value to format (0.1 = 10%)
            decimal_places: Number of decimal places
            
        Returns:
            Formatted percentage string
        """
        if pd.isna(value):
            return "N/A"
        
        return f"{value * 100:.{decimal_places}f}%"
    
    def calculate_summary_stats(self, data: pd.DataFrame, column: str) -> Dict[str, float]:
        """
        Calculate summary statistics for a numeric column
        
        Args:
            data: Input DataFrame
            column: Column name to analyze
            
        Returns:
            Dictionary with summary statistics
        """
        if column not in data.columns:
            return {}
        
        series = pd.to_numeric(data[column], errors='coerce')
        
        return {
            'count': int(series.count()),
            'mean': float(series.mean()) if not series.empty else 0.0,
            'median': float(series.median()) if not series.empty else 0.0,
            'std': float(series.std()) if not series.empty else 0.0,
            'min': float(series.min()) if not series.empty else 0.0,
            'max': float(series.max()) if not series.empty else 0.0,
            'sum': float(series.sum()) if not series.empty else 0.0,
            'missing_count': int(data[column].isna().sum()),
            'missing_percentage': float(data[column].isna().sum() / len(data) * 100)
        }
    
    def detect_outliers(self, data: pd.DataFrame, column: str, method: str = 'iqr') -> Dict[str, Any]:
        """
        Detect outliers in a numeric column
        
        Args:
            data: Input DataFrame
            column: Column name to analyze
            method: Method to use ('iqr' or 'zscore')
            
        Returns:
            Dictionary with outlier information
        """
        if column not in data.columns:
            return {}
        
        series = pd.to_numeric(data[column], errors='coerce').dropna()
        
        if method == 'iqr':
            Q1 = series.quantile(0.25)
            Q3 = series.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = series[(series < lower_bound) | (series > upper_bound)]
            
            return {
                'method': 'IQR',
                'lower_bound': float(lower_bound),
                'upper_bound': float(upper_bound),
                'outlier_count': len(outliers),
                'outlier_percentage': float(len(outliers) / len(series) * 100),
                'outlier_values': outliers.tolist()[:10]  # Limit to first 10
            }
        
        elif method == 'zscore':
            z_scores = np.abs((series - series.mean()) / series.std())
            threshold = 3  # Standard threshold for z-score
            
            outliers = series[z_scores > threshold]
            
            return {
                'method': 'Z-Score',
                'threshold': threshold,
                'outlier_count': len(outliers),
                'outlier_percentage': float(len(outliers) / len(series) * 100),
                'outlier_values': outliers.tolist()[:10]  # Limit to first 10
            }
        
        return {}
    
    def get_analysis_summary(self) -> Dict[str, Any]:
        """
        Get summary of analysis results
        
        Returns:
            Dictionary with analysis summary
        """
        return {
            'analysis_type': self.analysis_type,
            'status': self.status,
            'data_shape': (len(self.data), len(self.data.columns)) if self.data is not None else (0, 0),
            'errors': self.errors,
            'warnings': self.warnings,
            'results_keys': list(self.results.keys()),
            'timestamp': pd.Timestamp.now().isoformat()
        }
    
    def reset(self):
        """Reset analyzer state for new analysis"""
        self.data = None
        self.results = {}
        self.status = "not_analyzed"
        self.errors = []
        self.warnings = []


# Import numpy for numeric operations
import numpy as np
