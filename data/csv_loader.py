"""
CSV Loader for Quant Commander
Handles CSV file loading, validation, and column detection
"""

import pandas as pd
import io
from typing import Dict, List, Optional, Tuple, Union
from pathlib import Path
from config.settings import Settings


class CSVLoadError(Exception):
    """Custom exception for CSV loading errors"""
    pass


class CSVLoader:
    """
    Handles CSV file loading and basic validation
    Provides automatic column type detection and data quality checks
    """
    
    def __init__(self, settings: Settings):
        """
        Initialize CSV loader with settings
        
        Args:
            settings: Application settings instance
        """
        self.settings = settings
        self.raw_data: Optional[pd.DataFrame] = None
        self.file_path: Optional[str] = None
        self.status: str = "not_loaded"
        self.column_info: Dict[str, any] = {}
        self.data_quality: Dict[str, any] = {}
    
    def load_csv(self, file_input: Union[str, bytes, io.StringIO]) -> pd.DataFrame:
        """
        Load and validate CSV file from various input types
        
        Args:
            file_input: File path string, file bytes, or StringIO object
            
        Returns:
            Loaded DataFrame
            
        Raises:
            CSVLoadError: If loading or validation fails
        """
        try:
            # Handle different input types
            if isinstance(file_input, str):
                # File path
                self.file_path = file_input
                if not Path(file_input).exists():
                    raise CSVLoadError(f"File not found: {file_input}")
                
                # Check file size
                file_size = Path(file_input).stat().st_size
                if file_size > self.settings.max_file_size:
                    raise CSVLoadError(
                        f"File too large: {file_size:,} bytes. "
                        f"Maximum allowed: {self.settings.max_file_size:,} bytes"
                    )
                
                self.raw_data = pd.read_csv(file_input)
                
            elif isinstance(file_input, bytes):
                # File bytes
                if len(file_input) > self.settings.max_file_size:
                    raise CSVLoadError(
                        f"File too large: {len(file_input):,} bytes. "
                        f"Maximum allowed: {self.settings.max_file_size:,} bytes"
                    )
                
                # Decode bytes to string and create StringIO
                try:
                    file_content = file_input.decode('utf-8')
                except UnicodeDecodeError:
                    # Try other encodings
                    try:
                        file_content = file_input.decode('latin-1')
                    except UnicodeDecodeError:
                        raise CSVLoadError("Unable to decode file. Please ensure it's a valid CSV file.")
                
                self.raw_data = pd.read_csv(io.StringIO(file_content))
                
            elif isinstance(file_input, io.StringIO):
                # StringIO object
                self.raw_data = pd.read_csv(file_input)
                
            else:
                raise CSVLoadError(f"Unsupported input type: {type(file_input)}")
            
            # Validate the loaded data
            if not self._validate_structure():
                raise CSVLoadError("CSV validation failed")
            
            # Detect column types
            self.column_info = self._detect_columns()
            
            # Analyze data quality
            self.data_quality = self._analyze_data_quality()
            
            self.status = "loaded"
            return self.raw_data
            
        except pd.errors.EmptyDataError:
            raise CSVLoadError("CSV file is empty")
        except pd.errors.ParserError as e:
            raise CSVLoadError(f"CSV parsing error: {str(e)}")
        except Exception as e:
            if isinstance(e, CSVLoadError):
                raise
            raise CSVLoadError(f"Unexpected error loading CSV: {str(e)}")
    
    def _validate_structure(self) -> bool:
        """
        Validate CSV structure and basic requirements
        
        Returns:
            True if validation passes
            
        Raises:
            CSVLoadError: If validation fails
        """
        if self.raw_data is None:
            raise CSVLoadError("No data to validate")
        
        # Check minimum requirements
        if self.raw_data.empty:
            raise CSVLoadError("CSV file contains no data")
        
        if len(self.raw_data.columns) == 0:
            raise CSVLoadError("CSV file contains no columns")
        
        if len(self.raw_data) == 0:
            raise CSVLoadError("CSV file contains no rows")
        
        # Check for reasonable data size
        if len(self.raw_data) > 1_000_000:  # 1M rows
            raise CSVLoadError(
                f"Dataset too large: {len(self.raw_data):,} rows. "
                "Please consider splitting into smaller files."
            )
        
        if len(self.raw_data.columns) > 1000:  # 1000 columns
            raise CSVLoadError(
                f"Too many columns: {len(self.raw_data.columns)}. "
                "Maximum 1000 columns supported."
            )
        
        return True
    
    def _detect_columns(self) -> Dict[str, any]:
        """
        Auto-detect column types and patterns
        
        Returns:
            Dictionary with column analysis
        """
        if self.raw_data is None:
            return {}
        
        print(f"[DEBUG][CSVLoader] Detecting columns for data with shape: {self.raw_data.shape}")
        print(f"[DEBUG][CSVLoader] Column dtypes: {self.raw_data.dtypes.to_dict()}")
        
        # First pass: convert potential date columns to datetime
        raw_data_copy = self.raw_data.copy()
        for col in self.raw_data.columns:
            col_lower = col.lower()
            
            # Look for columns that might be dates
            if any(term in col_lower for term in ['date', 'time', 'period', 'day', 'month', 'year']):
                try:
                    # Try to convert to datetime
                    raw_data_copy[col] = pd.to_datetime(raw_data_copy[col], errors='coerce')
                    if raw_data_copy[col].notna().sum() > 0:
                        print(f"[DEBUG][CSVLoader] Successfully converted {col} to datetime")
                except Exception as e:
                    print(f"[DEBUG][CSVLoader] Failed to convert {col} to datetime: {str(e)}")
        
        # Update the raw_data with the converted columns
        self.raw_data = raw_data_copy
        
        column_info = {
            'numeric_columns': [],
            'text_columns': [],
            'date_columns': [],
            'potential_date_columns': [],
            'financial_columns': {},
            'total_columns': len(self.raw_data.columns),
            'column_list': self.raw_data.columns.tolist()
        }
        
        # Analyze each column
        for col in self.raw_data.columns:
            col_lower = col.lower()
            dtype_str = str(self.raw_data[col].dtype)
            print(f"[DEBUG][CSVLoader] Analyzing column: {col}, type: {dtype_str}")
            
            # Check data types
            if 'datetime' in dtype_str:
                column_info['date_columns'].append(col)
                print(f"[DEBUG][CSVLoader] {col} detected as datetime and added to date_columns")
            elif self.raw_data[col].dtype in ['int64', 'float64', 'int32', 'float32']:
                column_info['numeric_columns'].append(col)
                print(f"[DEBUG][CSVLoader] {col} added to numeric_columns")
                
                # Check for financial patterns
                if any(term in col_lower for term in ['sales', 'revenue', 'amount', 'value', 'price']):
                    column_info['financial_columns']['value_columns'] = column_info['financial_columns'].get('value_columns', [])
                    column_info['financial_columns']['value_columns'].append(col)
                
                if any(term in col_lower for term in ['budget', 'target', 'plan']):
                    column_info['financial_columns']['budget_columns'] = column_info['financial_columns'].get('budget_columns', [])
                    column_info['financial_columns']['budget_columns'].append(col)
                
                if any(term in col_lower for term in ['actual', 'real']):
                    column_info['financial_columns']['actual_columns'] = column_info['financial_columns'].get('actual_columns', [])
                    column_info['financial_columns']['actual_columns'].append(col)
            elif self.raw_data[col].dtype == 'object':
                # Try to detect if it could be a date but wasn't converted
                try:
                    sample = self.raw_data[col].dropna().head(5)
                    print(f"[DEBUG][CSVLoader] Checking if {col} might be a date. Sample: {sample.tolist()}")
                    
                    # Try to convert to datetime
                    date_sample = pd.to_datetime(sample, errors='coerce')
                    
                    # If at least 80% could be converted, consider it a date
                    valid_dates = date_sample.notna().sum()
                    if len(sample) > 0 and valid_dates / len(sample) >= 0.8:
                        # Convert the whole column
                        self.raw_data[col] = pd.to_datetime(self.raw_data[col], errors='coerce')
                        column_info['date_columns'].append(col)
                        print(f"[DEBUG][CSVLoader] {col} identified as date. Sample converted: {date_sample}")
                    else:
                        column_info['text_columns'].append(col)
                        print(f"[DEBUG][CSVLoader] {col} not a date. Valid conversions: {valid_dates}/{len(sample)}")
                except Exception as e:
                    column_info['text_columns'].append(col)
                    print(f"[DEBUG][CSVLoader] Error checking if {col} is a date: {str(e)}")
                
                # Check for category patterns if not identified as a date
                if col not in column_info['date_columns'] and any(term in col_lower for term in ['product', 'category', 'region', 'customer']):
                    column_info['financial_columns']['category_columns'] = column_info['financial_columns'].get('category_columns', [])
                    column_info['financial_columns']['category_columns'].append(col)
                    print(f"[DEBUG][CSVLoader] {col} added to category_columns")
        
        # Ensure we have 'category_columns' in financial_columns
        if 'category_columns' not in column_info['financial_columns']:
            column_info['financial_columns']['category_columns'] = []
        
        # Ensure we have 'value_columns' in financial_columns
        if 'value_columns' not in column_info['financial_columns']:
            # Use all numeric columns as value columns if no specific ones were detected
            column_info['financial_columns']['value_columns'] = column_info['numeric_columns']
        
        print(f"[DEBUG][CSVLoader] Final column detection results: {column_info}")
        return column_info
    
    def _analyze_data_quality(self) -> Dict[str, any]:
        """
        Analyze data quality metrics
        
        Returns:
            Dictionary with data quality information
        """
        if self.raw_data is None:
            return {}
        
        quality_info = {
            'total_rows': len(self.raw_data),
            'total_columns': len(self.raw_data.columns),
            'missing_data': {},
            'duplicate_rows': 0,
            'data_types': {},
            'summary_stats': {}
        }
        
        # Check for missing data
        for col in self.raw_data.columns:
            missing_count = self.raw_data[col].isna().sum()
            if missing_count > 0:
                quality_info['missing_data'][col] = {
                    'count': int(missing_count),
                    'percentage': float(missing_count / len(self.raw_data) * 100)
                }
        
        # Check for duplicate rows
        quality_info['duplicate_rows'] = int(self.raw_data.duplicated().sum())
        
        # Data types summary
        for col in self.raw_data.columns:
            quality_info['data_types'][col] = str(self.raw_data[col].dtype)
        
        # Basic statistics for numeric columns
        numeric_cols = self.raw_data.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            stats = self.raw_data[numeric_cols].describe()
            quality_info['summary_stats'] = stats.to_dict()
        
        return quality_info
    
    def get_column_suggestions(self) -> Dict[str, List[str]]:
        """
        Get suggestions for column usage in analysis
        
        Returns:
            Dictionary with suggested columns for different analysis types
        """
        if not self.column_info:
            return {}
        
        suggestions = {
            'value_columns': [],
            'category_columns': [],
            'date_columns': [],
            'budget_vs_actual': {}
        }
        
        # Suggest value columns (for contribution analysis)
        financial_cols = self.column_info.get('financial_columns', {})
        
        # Ensure financial_cols is a dictionary
        if not isinstance(financial_cols, dict):
            financial_cols = {}
        
        if 'value_columns' in financial_cols:
            suggestions['value_columns'] = financial_cols['value_columns']
        else:
            # Fall back to any numeric columns
            numeric_cols = self.column_info.get('numeric_columns', [])
            if isinstance(numeric_cols, list):
                suggestions['value_columns'] = numeric_cols[:3]
        
        # Suggest category columns
        if 'category_columns' in financial_cols:
            suggestions['category_columns'] = financial_cols['category_columns']
        else:
            # Fall back to text columns
            text_cols = self.column_info.get('text_columns', [])
            if isinstance(text_cols, list):
                suggestions['category_columns'] = text_cols[:3]
        
        # Suggest date columns
        date_cols = self.column_info.get('date_columns', [])
        if isinstance(date_cols, list):
            suggestions['date_columns'] = date_cols
        
        # Suggest budget vs actual pairs
        budget_cols = financial_cols.get('budget_columns', [])
        actual_cols = financial_cols.get('actual_columns', [])
        
        if isinstance(budget_cols, list) and isinstance(actual_cols, list) and budget_cols and actual_cols:
            for budget_col in budget_cols:
                for actual_col in actual_cols:
                    # Try to match similar names
                    budget_base = budget_col.lower().replace('budget', '').replace('_', '').strip()
                    actual_base = actual_col.lower().replace('actual', '').replace('_', '').strip()
                    
                    if budget_base == actual_base or budget_base in actual_base or actual_base in budget_base:
                        suggestions['budget_vs_actual'][budget_col] = actual_col
        
        return suggestions
    
    def get_data_summary(self) -> str:
        """
        Get a formatted summary of the loaded data
        
        Returns:
            Formatted string with data summary
        """
        if self.raw_data is None:
            return "No data loaded"
        
        summary_parts = [
            f"📊 **Dataset Overview**:",
            f"• **Rows**: {len(self.raw_data):,}",
            f"• **Columns**: {len(self.raw_data.columns)}",
        ]
        
        # Add column type breakdown
        if self.column_info:
            numeric_count = len(self.column_info.get('numeric_columns', []))
            text_count = len(self.column_info.get('text_columns', []))
            date_count = len(self.column_info.get('date_columns', []))
            
            summary_parts.extend([
                f"• **Numeric Columns**: {numeric_count}",
                f"• **Text Columns**: {text_count}",
                f"• **Date Columns**: {date_count}",
            ])
        
        # Add data quality info
        if self.data_quality:
            missing_cols = len(self.data_quality.get('missing_data', {}))
            duplicate_rows = self.data_quality.get('duplicate_rows', 0)
            
            if missing_cols > 0 or duplicate_rows > 0:
                summary_parts.append("")
                summary_parts.append("⚠️ **Data Quality Notes**:")
                if missing_cols > 0:
                    summary_parts.append(f"• {missing_cols} columns have missing values")
                if duplicate_rows > 0:
                    summary_parts.append(f"• {duplicate_rows} duplicate rows detected")
        
        return "\n".join(summary_parts)
