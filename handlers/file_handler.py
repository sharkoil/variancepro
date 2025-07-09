"""
File Handler for Quant Commander v2.0

This module handles CSV file upload, validation, and initial data processing.
It provides clean separation between file handling logic and the main application.

Extracted from app_v2.py to follow modular design principles.
"""

import os
import pandas as pd
from typing import Tuple, Optional, Dict, Any, List


class FileHandler:
    """
    Handles CSV file operations including upload, validation, and data analysis.
    
    This class encapsulates all file-related functionality to keep the main
    application focused on orchestration rather than file processing details.
    """
    
    def __init__(self, app_core=None):
        """
        Initialize the file handler.
        
        Args:
            app_core: Reference to the main application core (optional for backward compatibility)
        """
        self.app_core = app_core
        self.current_data: Optional[pd.DataFrame] = None
        self.data_summary: Optional[Dict[str, Any]] = None
    
    def validate_csv_file(self, file_path: str) -> Tuple[bool, str, Optional[pd.DataFrame]]:
        """
        Validate a CSV file and return its contents if valid.
        
        Performs comprehensive validation including:
        - File existence and extension checking
        - CSV format validation
        - Data content validation
        - Encoding handling
        
        Args:
            file_path (str): Path to the CSV file to validate
            
        Returns:
            Tuple[bool, str, Optional[pd.DataFrame]]: 
                - bool: True if valid, False if invalid
                - str: Status message describing validation result
                - DataFrame: Loaded data if valid, None if invalid
        """
        if not file_path:
            return False, "No file provided", None
        
        try:
            # Check file existence
            if not os.path.exists(file_path):
                return False, "File does not exist", None
            
            # Check file extension
            if not file_path.lower().endswith('.csv'):
                return False, "Please upload a CSV file (.csv extension required)", None
            
            # Try to read the CSV with different approaches
            df = None
            
            try:
                # First attempt: standard CSV reading
                df = pd.read_csv(file_path)
            except pd.errors.EmptyDataError:
                return False, "The CSV file is empty. Please upload a file with data.", None
            except pd.errors.ParserError as e:
                return False, f"CSV format error: {str(e)}. Please check your file format.", None
            except UnicodeDecodeError:
                # Second attempt: try different encoding
                try:
                    df = pd.read_csv(file_path, encoding='latin1')
                except Exception:
                    return False, "Unable to read file. Please check the file encoding and format.", None
            
            # Validate data content
            if df is None or df.empty:
                return False, "The CSV file contains no data rows. Please upload a file with actual data.", None
            
            if len(df.columns) == 0:
                return False, "The CSV file has no columns. Please check your file format.", None
            
            # Check for potential formatting issues
            if len(df.columns) == 1 and df.columns[0].count(',') > 0:
                return False, "It looks like your CSV might have formatting issues. Please ensure proper comma separation.", None
            
            return True, "File validation successful", df
            
        except Exception as e:
            return False, f"Unexpected error reading file: {str(e)}", None
    
    def analyze_csv_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze CSV data and create comprehensive summary.
        
        This method examines the DataFrame to extract metadata, statistics,
        and structural information useful for analysis and UI display.
        
        Args:
            df (pd.DataFrame): The DataFrame to analyze
            
        Returns:
            Dict[str, Any]: Comprehensive analysis including:
                - Basic info (rows, columns, types)
                - Sample data
                - Statistics for numeric columns
                - Data quality metrics
        """
        analysis = {
            'row_count': len(df),
            'column_count': len(df.columns),
            'columns': list(df.columns),
            'column_types': {},
            'sample_data': {},
            'basic_stats': {},
            'data_quality': {}
        }
        
        # Analyze each column
        for col in df.columns:
            # Get column type
            dtype = str(df[col].dtype)
            analysis['column_types'][col] = dtype
            
            # Get sample values (first 10 non-null values)
            sample_values = df[col].dropna().head(10).tolist()
            analysis['sample_data'][col] = sample_values
            
            # Data quality metrics
            null_count = int(df[col].isnull().sum())
            analysis['data_quality'][col] = {
                'null_count': null_count,
                'null_percentage': (null_count / len(df)) * 100,
                'unique_count': int(df[col].nunique())
            }
            
            # Basic statistics for numeric columns
            if df[col].dtype in ['int64', 'float64']:
                try:
                    stats = {
                        'min': float(df[col].min()),
                        'max': float(df[col].max()),
                        'mean': float(df[col].mean()),
                        'median': float(df[col].median()),
                        'std': float(df[col].std())
                    }
                    analysis['basic_stats'][col] = stats
                except Exception:
                    # Skip statistics if calculation fails
                    pass
        
        # Get sample rows for preview
        sample_rows = df.head(10).to_dict('records')
        analysis['sample_rows'] = sample_rows
        
        # Store analysis for later use
        self.data_summary = analysis
        
        return analysis
    
    def detect_date_columns(self, df: pd.DataFrame) -> List[str]:
        """
        Detect potential date columns in the DataFrame.
        
        Uses multiple heuristics to identify date columns:
        - Column name patterns
        - Data type detection
        - Sample data parsing
        
        Args:
            df (pd.DataFrame): The DataFrame to examine
            
        Returns:
            List[str]: List of column names that appear to contain dates
        """
        date_columns = []
        
        for col in df.columns:
            # Check column name patterns
            col_lower = col.lower()
            if any(date_word in col_lower for date_word in ['date', 'time', 'timestamp', 'created', 'updated', 'day', 'month', 'year']):
                date_columns.append(col)
                continue
            
            # Check data type
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                date_columns.append(col)
                continue
            
            # Try to parse sample values as dates
            sample_values = df[col].dropna().head(10)
            if len(sample_values) > 0:
                try:
                    parsed_count = 0
                    for value in sample_values:
                        try:
                            pd.to_datetime(str(value), infer_datetime_format=True)
                            parsed_count += 1
                        except Exception:
                            pass
                    
                    # If most samples parse as dates, consider it a date column
                    if parsed_count >= len(sample_values) * 0.7:  # 70% success rate
                        date_columns.append(col)
                except Exception:
                    pass
        
        return date_columns
    
    def format_column_info(self, analysis: Dict[str, Any]) -> str:
        """
        Format column information for display in the UI.
        
        Args:
            analysis (Dict[str, Any]): Analysis results from analyze_csv_data
            
        Returns:
            str: Formatted string listing all columns with their types
        """
        lines = []
        for col, dtype in analysis['column_types'].items():
            # Simplify data type names for user display
            if 'int' in dtype.lower():
                type_display = "Integer"
            elif 'float' in dtype.lower():
                type_display = "Decimal"
            elif 'datetime' in dtype.lower():
                type_display = "Date/Time"
            else:
                type_display = "Text"
            
            lines.append(f"• **{col}**: {type_display}")
        
        return '\n'.join(lines)
    
    def get_numeric_columns(self, df: pd.DataFrame = None) -> List[str]:
        """
        Get list of numeric columns from the DataFrame.
        
        Args:
            df (pd.DataFrame, optional): DataFrame to examine. Uses current_data if None.
            
        Returns:
            List[str]: List of numeric column names
        """
        if df is None:
            df = self.current_data
            
        if df is None:
            return []
            
        return df.select_dtypes(include=['number']).columns.tolist()
    
    def get_text_columns(self, df: pd.DataFrame = None) -> List[str]:
        """
        Get list of text/categorical columns from the DataFrame.
        
        Args:
            df (pd.DataFrame, optional): DataFrame to examine. Uses current_data if None.
            
        Returns:
            List[str]: List of text column names
        """
        if df is None:
            df = self.current_data
            
        if df is None:
            return []
            
        return df.select_dtypes(include=['object']).columns.tolist()
    
    def handle_upload(self, file, history: List[Dict]) -> Tuple[str, List[Dict]]:
        """
        Handle CSV file upload with validation and analysis.
        
        Args:
            file: The uploaded file object from Gradio
            history: Current chat history
            
        Returns:
            Tuple[str, List[Dict]]: (upload_status, updated_history)
        """
        if file is None:
            return "Please select a CSV file to upload.", history
        
        print(f"[DEBUG] Processing file: {file.name}")
        
        # Validate file
        is_valid, message, df = self.validate_csv_file(file.name)
        
        if not is_valid:
            return f"❌ **Upload Failed**: {message}", history
        
        # Store the data
        self.current_data = df
        
        # Update app_core if available
        if self.app_core:
            # Analyze the data
            analysis = self.analyze_csv_data(df)
            self.data_summary = analysis
            
            # Generate summary using LLM if available
            if self.app_core.is_ollama_available():
                summary_text = self._generate_llm_summary(analysis)
            else:
                summary_text = self._generate_fallback_summary(analysis)
            
            # Store in app core
            self.app_core.set_current_data(df, analysis)
            
            # Try automatic analysis if timescale analyzer is available
            auto_analysis = self._attempt_automatic_analysis(df)
            
            # Add upload success message to chat
            upload_message = {
                "role": "assistant",
                "content": f"✅ **File uploaded successfully!**\n\n{summary_text}"
            }
            
            # Add auto-analysis if available
            if auto_analysis:
                auto_message = {
                    "role": "assistant", 
                    "content": auto_analysis
                }
                history.extend([upload_message, auto_message])
            else:
                history.append(upload_message)
            
            return f"✅ **Upload Successful**\n\nFile: {file.name}\nRows: {len(df):,}\nColumns: {len(df.columns)}", history
        
        else:
            # Fallback without app_core
            return f"✅ **Upload Successful**\n\nFile: {file.name}\nRows: {len(df):,}\nColumns: {len(df.columns)}", history
    
    def _generate_llm_summary(self, analysis: Dict) -> str:
        """Generate LLM-based summary of the data."""
        if not self.app_core:
            return self._generate_fallback_summary(analysis)
        
        prompt = f"""
You are a financial data analyst. A user has uploaded a CSV file with the following characteristics:

DATASET OVERVIEW:
- Rows: {analysis['row_count']:,}
- Columns: {analysis['column_count']}
- Column Names: {', '.join(analysis['columns'])}

COLUMN DETAILS:
"""
        
        for col, dtype in analysis['column_types'].items():
            prompt += f"\n- {col}: {dtype}"
            if col in analysis['sample_data']:
                sample_vals = analysis['sample_data'][col][:5]  # First 5 samples
                prompt += f" (samples: {sample_vals})"
        
        if analysis['basic_stats']:
            prompt += f"\n\nNUMERIC STATISTICS:"
            for col, stats in analysis['basic_stats'].items():
                prompt += f"\n- {col}: min={stats['min']}, max={stats['max']}, avg={stats['mean']:.2f}"
        
        prompt += f"""

SAMPLE DATA (first few rows):
{analysis.get('sample_rows', [])[:3]}

Please provide a concise, friendly summary of this dataset. Focus on:
1. What type of data this appears to be (financial, sales, etc.)
2. What analyses might be useful
3. Any notable patterns or insights
4. Suggested questions the user might ask

Keep the response conversational and under 200 words.
"""
        
        return self.app_core.call_ollama(prompt)
    
    def _generate_fallback_summary(self, analysis: Dict) -> str:
        """Generate fallback summary without LLM."""
        return f"""📊 **Dataset Loaded Successfully**

**Overview**: {analysis['row_count']:,} rows × {analysis['column_count']} columns

**Columns**: {', '.join(analysis['columns'][:5])}{'...' if len(analysis['columns']) > 5 else ''}

**Suggested Actions**:
• Ask questions about your data
• Try queries like "summarize the data" or "show me trends"
• Use the analysis features to explore patterns

*Upload successful! You can now analyze your data.*"""
    
    def _attempt_automatic_analysis(self, df: pd.DataFrame) -> Optional[str]:
        """Attempt automatic time-series analysis if possible."""
        if not self.app_core or not self.app_core.timescale_analyzer:
            return None
        
        try:
            # Detect date columns
            date_columns = self._detect_date_columns(df)
            
            if not date_columns:
                return None
            
            # Use the first date column found
            date_col = date_columns[0]
            print(f"[DEBUG] Using date column: {date_col}")
            
            # Auto-detect numeric columns for analysis
            numeric_columns = df.select_dtypes(include=['number']).columns.tolist()
            
            if not numeric_columns:
                print("[DEBUG] No numeric columns found for timescale analysis")
                return "🔍 **Automatic Analysis**: Date column detected but no numeric data found for time-series analysis."
            
            # Limit to first 3 numeric columns to avoid overwhelming output
            value_cols = numeric_columns[:3]
            print(f"[DEBUG] Using value columns: {value_cols}")
            
            # Perform timescale analysis
            self.app_core.timescale_analyzer.analyze(
                data=df,
                date_col=date_col,
                value_cols=value_cols
            )
            
            # Format results for chat
            if self.app_core.timescale_analyzer.status == "completed":
                print("[DEBUG] OOB Timescale Analysis completed successfully")
                
                return f"""🚀 **Automatic Time-Series Analysis**

*I've automatically analyzed your data's time patterns. Here's what I found:*

{self.app_core.timescale_analyzer.format_for_chat()}

💡 **Next Steps**: Ask me about specific time periods, trends, or comparisons!"""
            else:
                print(f"[DEBUG] OOB Analysis failed with status: {self.app_core.timescale_analyzer.status}")
                return "🔍 **Automatic Analysis**: Time-series analysis attempted but encountered issues. You can manually request analysis using 'analyze trends'."
        
        except Exception as e:
            print(f"[DEBUG] Unexpected OOB Analysis error: {e}")
            return None
    
    def _detect_date_columns(self, df: pd.DataFrame) -> List[str]:
        """Detect potential date columns in the DataFrame."""
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
