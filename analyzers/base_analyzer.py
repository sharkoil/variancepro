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


class AnalysisFormatter:
    """
    Centralized formatter for all analysis outputs
    Provides consistent formatting with banded tables and clear structure
    """
    
    @staticmethod
    def format_currency(value: Union[int, float], currency_symbol: str = "$") -> str:
        """Format numeric value as currency"""
        if pd.isna(value):
            return "N/A"
        
        if abs(value) >= 1_000_000_000:
            return f"{currency_symbol}{value/1_000_000_000:.1f}B"
        elif abs(value) >= 1_000_000:
            return f"{currency_symbol}{value/1_000_000:.1f}M"
        elif abs(value) >= 1_000:
            return f"{currency_symbol}{value/1_000:.1f}K"
        else:
            return f"{currency_symbol}{value:.2f}"
    
    @staticmethod
    def format_percentage(value: Union[int, float], decimal_places: int = 1) -> str:
        """Format numeric value as percentage"""
        if pd.isna(value):
            return "N/A"
        return f"{value * 100:.{decimal_places}f}%"
    
    @staticmethod
    def format_number(value: Union[int, float], decimal_places: int = 0) -> str:
        """Format large numbers with K/M/B suffixes"""
        if pd.isna(value):
            return "N/A"
        
        if abs(value) >= 1_000_000_000:
            return f"{value/1_000_000_000:.1f}B"
        elif abs(value) >= 1_000_000:
            return f"{value/1_000_000:.1f}M"
        elif abs(value) >= 1_000:
            return f"{value/1_000:.1f}K"
        else:
            return f"{value:.{decimal_places}f}"
    
    @staticmethod
    def create_banded_table(data: List[Dict], headers: List[str], max_rows: int = 10) -> str:
        """
        Create a banded table with alternating row styling for better readability
        
        Args:
            data: List of dictionaries with row data
            headers: List of column headers
            max_rows: Maximum number of rows to display
            
        Returns:
            Formatted table string
        """
        if not data or not headers:
            return "_No data to display_"
        
        # Limit rows if necessary
        display_data = data[:max_rows]
        
        # Calculate column widths
        col_widths = {}
        for header in headers:
            col_widths[header] = len(header)
            for row in display_data:
                if header in row:
                    value_str = str(row[header])
                    col_widths[header] = max(col_widths[header], len(value_str))
        
        # Create table
        table_lines = []
        
        # Header
        header_line = "| " + " | ".join(header.ljust(col_widths[header]) for header in headers) + " |"
        table_lines.append(header_line)
        
        # Separator
        separator = "| " + " | ".join("-" * col_widths[header] for header in headers) + " |"
        table_lines.append(separator)
        
        # Data rows
        for i, row in enumerate(display_data):
            row_values = []
            for header in headers:
                value = row.get(header, "")
                if isinstance(value, (int, float)) and not pd.isna(value):
                    if header.lower() in ['percentage', 'percent', '%'] or 'pct' in header.lower():
                        value_str = f"{value:.1f}%"
                    elif header.lower() in ['value', 'amount', 'total', 'revenue', 'sales', 'cost']:
                        value_str = AnalysisFormatter.format_currency(value)
                    else:
                        value_str = AnalysisFormatter.format_number(value, 1)
                else:
                    value_str = str(value)
                row_values.append(value_str.ljust(col_widths[header]))
            
            # Add row styling indicator for banded effect
            row_indicator = "🔸" if i % 2 == 0 else "🔹"
            row_line = f"| {' | '.join(row_values)} |"
            table_lines.append(row_line)
        
        # Add truncation note if data was limited
        if len(data) > max_rows:
            table_lines.append(f"\n_Showing top {max_rows} of {len(data)} total rows_")
        
        return "\n".join(table_lines)
    
    @staticmethod
    def create_summary_section(title: str, explanation: str, assumptions: List[str] = None) -> str:
        """
        Create a standardized summary section with title, explanation, and assumptions
        
        Args:
            title: Section title
            explanation: Simple explanation of the analysis
            assumptions: List of assumptions made during analysis
            
        Returns:
            Formatted summary section
        """
        lines = [
            f"📊 **{title.upper()}**",
            "",
            f"**Analysis Summary:** {explanation}",
            ""
        ]
        
        if assumptions:
            lines.extend([
                "**Key Assumptions:**",
                *[f"• {assumption}" for assumption in assumptions],
                ""
            ])
        
        return "\n".join(lines)
    
    @staticmethod
    def create_insights_section(insights: List[str], recommendations: List[str] = None) -> str:
        """
        Create standardized insights and recommendations section
        
        Args:
            insights: List of key insights
            recommendations: Optional list of recommendations
            
        Returns:
            Formatted insights section
        """
        lines = ["🎯 **KEY INSIGHTS:**"]
        
        for i, insight in enumerate(insights, 1):
            lines.append(f"{i}. {insight}")
        
        if recommendations:
            lines.extend([
                "",
                "💡 **RECOMMENDATIONS:**",
                *[f"• {rec}" for rec in recommendations]
            ])
        
        return "\n".join(lines)
    
    @staticmethod
    def create_metrics_grid(metrics: Dict[str, Any], title: str = "Key Metrics") -> str:
        """
        Create a formatted metrics grid
        
        Args:
            metrics: Dictionary of metric name to value
            title: Title for the metrics section
            
        Returns:
            Formatted metrics grid
        """
        lines = [
            f"📈 **{title.upper()}:**",
            ""
        ]
        
        # Format metrics in a grid
        for metric_name, value in metrics.items():
            if isinstance(value, (int, float)) and not pd.isna(value):
                if metric_name.lower() in ['percentage', 'percent', '%'] or 'pct' in metric_name.lower():
                    formatted_value = f"{value:.1f}%"
                elif metric_name.lower() in ['value', 'amount', 'total', 'revenue', 'sales', 'cost']:
                    formatted_value = AnalysisFormatter.format_currency(value)
                else:
                    formatted_value = AnalysisFormatter.format_number(value)
            else:
                formatted_value = str(value)
            
            lines.append(f"• **{metric_name.replace('_', ' ').title()}**: {formatted_value}")
        
        return "\n".join(lines)


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
        self.formatter = AnalysisFormatter()
    
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
    
    @abstractmethod
    def format_for_chat(self) -> str:
        """
        Format analysis results for chat display using standardized formatting
        Must be implemented by subclasses
        
        Returns:
            Formatted string for chat interface with consistent structure
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
    
    def perform_top_n_analysis(self, data: pd.DataFrame, n: int = 5, 
                              exclude_date_cols: bool = True) -> Dict[str, Any]:
        """
        Perform Top N analysis across all numeric columns
        
        Args:
            data: Input DataFrame
            n: Number of top records to return
            exclude_date_cols: Whether to exclude date columns from ranking
            
        Returns:
            Dictionary with top N analysis results
        """
        results = {}
        
        # Identify numeric columns for analysis
        numeric_cols = data.select_dtypes(include=[np.number]).columns.tolist()
        
        # Identify date columns to handle specially
        date_cols = []
        for col in data.columns:
            if any(date_word in col.lower() for date_word in ['date', 'time', 'timestamp', 'created', 'updated', 'day', 'month', 'year']):
                date_cols.append(col)
        
        # Remove date columns from numeric analysis if requested
        if exclude_date_cols:
            numeric_cols = [col for col in numeric_cols if col not in date_cols]
        
        # Perform Top N analysis for each numeric column
        for col in numeric_cols:
            if col in data.columns:
                top_n_data = data.nlargest(n, col)
                results[f'top_{n}_{col}'] = {
                    'column': col,
                    'type': 'top',
                    'n': n,
                    'data': top_n_data.to_dict('records'),
                    'total_sum': float(top_n_data[col].sum()),
                    'percentage_of_total': float(top_n_data[col].sum() / data[col].sum() * 100) if data[col].sum() != 0 else 0
                }
        
        # Add date-based analysis if date columns exist
        if date_cols:
            results['date_analysis'] = self._analyze_by_date_dimension(data, date_cols[0], n)
        
        return results

    def perform_bottom_n_analysis(self, data: pd.DataFrame, n: int = 5,
                                 exclude_date_cols: bool = True) -> Dict[str, Any]:
        """
        Perform Bottom N analysis across all numeric columns
        
        Args:
            data: Input DataFrame  
            n: Number of bottom records to return
            exclude_date_cols: Whether to exclude date columns from ranking
            
        Returns:
            Dictionary with bottom N analysis results
        """
        results = {}
        
        # Identify numeric columns for analysis
        numeric_cols = data.select_dtypes(include=[np.number]).columns.tolist()
        
        # Identify date columns to handle specially  
        date_cols = []
        for col in data.columns:
            if any(date_word in col.lower() for date_word in ['date', 'time', 'timestamp', 'created', 'updated', 'day', 'month', 'year']):
                date_cols.append(col)
        
        # Remove date columns from numeric analysis if requested
        if exclude_date_cols:
            numeric_cols = [col for col in numeric_cols if col not in date_cols]
        
        # Perform Bottom N analysis for each numeric column
        for col in numeric_cols:
            if col in data.columns:
                bottom_n_data = data.nsmallest(n, col)
                results[f'bottom_{n}_{col}'] = {
                    'column': col,
                    'type': 'bottom', 
                    'n': n,
                    'data': bottom_n_data.to_dict('records'),
                    'total_sum': float(bottom_n_data[col].sum()),
                    'percentage_of_total': float(bottom_n_data[col].sum() / data[col].sum() * 100) if data[col].sum() != 0 else 0
                }
        
        # Add date-based analysis if date columns exist
        if date_cols:
            results['date_analysis'] = self._analyze_by_date_dimension(data, date_cols[0], n, analysis_type='bottom')
        
        return results

    def _analyze_by_date_dimension(self, data: pd.DataFrame, date_col: str, n: int = 5, 
                                  analysis_type: str = 'top') -> Dict[str, Any]:
        """
        Special handling for date dimension analysis
        
        Args:
            data: Input DataFrame
            date_col: Date column name
            n: Number of records to return
            analysis_type: 'top' or 'bottom'
            
        Returns:
            Dictionary with date-based analysis
        """
        try:
            # Convert date column
            data_copy = data.copy()
            data_copy[date_col] = pd.to_datetime(data_copy[date_col], errors='coerce')
            
            # Remove rows with invalid dates
            data_copy = data_copy.dropna(subset=[date_col])
            
            # Find numeric columns for aggregation
            numeric_cols = data_copy.select_dtypes(include=[np.number]).columns.tolist()
            
            if not numeric_cols:
                return {'error': 'No numeric columns found for date analysis'}
            
            # Group by date and sum numeric columns
            date_summary = data_copy.groupby(date_col)[numeric_cols].sum().reset_index()
            
            # Get most recent dates (for top) or oldest dates (for bottom)
            if analysis_type == 'top':
                date_analysis = date_summary.nlargest(n, date_col)
            else:
                date_analysis = date_summary.nsmallest(n, date_col)
            
            return {
                'analysis_type': f'{analysis_type}_by_date',
                'date_column': date_col,
                'n': n,
                'data': date_analysis.to_dict('records'),
                'date_range': {
                    'start': str(date_analysis[date_col].min()),
                    'end': str(date_analysis[date_col].max())
                }
            }
        except Exception as e:
            return {'error': f'Date analysis failed: {str(e)}'}
    
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
