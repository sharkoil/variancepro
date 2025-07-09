"""
Data Utilities for VariancePro v2.0

This module provides utility functions for data analysis including:
- Date column detection
- Data type analysis
- Common data processing functions

Following modular design principles to keep utilities focused and reusable.
"""

import pandas as pd
from typing import List


class DataUtils:
    """
    Utility functions for data analysis and processing.
    
    This class provides common data processing functions
    that can be reused across different analysis modules.
    """
    
    @staticmethod
    def detect_date_columns(df: pd.DataFrame) -> List[str]:
        """
        Detect potential date columns in the DataFrame.
        
        Args:
            df: The DataFrame to analyze
            
        Returns:
            List[str]: List of potential date column names
        """
        date_columns = []
        
        for col in df.columns:
            col_lower = col.lower()
            # Check for common date column names
            if any(date_word in col_lower for date_word in ['date', 'time', 'day', 'month', 'year']):
                date_columns.append(col)
                continue
            
            # Check if the column can be parsed as dates
            try:
                pd.to_datetime(df[col].dropna().head(10), errors='raise')
                date_columns.append(col)
            except:
                continue
        
        return date_columns
    
    @staticmethod
    def get_numeric_columns(df: pd.DataFrame) -> List[str]:
        """
        Get list of numeric columns in the DataFrame.
        
        Args:
            df: The DataFrame to analyze
            
        Returns:
            List[str]: List of numeric column names
        """
        return df.select_dtypes(include=['number']).columns.tolist()
    
    @staticmethod
    def get_categorical_columns(df: pd.DataFrame) -> List[str]:
        """
        Get list of categorical (object) columns in the DataFrame.
        
        Args:
            df: The DataFrame to analyze
            
        Returns:
            List[str]: List of categorical column names
        """
        return df.select_dtypes(include=['object']).columns.tolist()
    
    @staticmethod
    def get_data_overview(df: pd.DataFrame) -> dict:
        """
        Get basic overview statistics for the DataFrame.
        
        Args:
            df: The DataFrame to analyze
            
        Returns:
            dict: Dictionary containing overview statistics
        """
        return {
            'row_count': len(df),
            'column_count': len(df.columns),
            'numeric_columns': len(DataUtils.get_numeric_columns(df)),
            'categorical_columns': len(DataUtils.get_categorical_columns(df)),
            'date_columns': len(DataUtils.detect_date_columns(df)),
            'memory_usage': df.memory_usage(deep=True).sum(),
            'has_missing_values': df.isnull().any().any()
        }
