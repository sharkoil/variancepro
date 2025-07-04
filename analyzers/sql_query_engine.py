"""
SQL Query Engine for VariancePro
Executes SQL queries on CSV data using in-memory SQLite
"""

import pandas as pd
import sqlite3
import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from .base_analyzer import AnalysisFormatter


@dataclass
class SQLQueryResult:
    """Result object for SQL query execution"""
    success: bool
    data: Optional[pd.DataFrame] = None
    error_message: Optional[str] = None
    row_count: int = 0
    
    def __post_init__(self):
        if self.data is not None:
            self.row_count = len(self.data)


class SQLQueryEngine:
    """Execute SQL queries on CSV data using in-memory SQLite"""
    
    def __init__(self, settings: Dict = None):
        self.settings = settings or {}
        self.connection = None
        self.table_name = "financial_data"
        self.schema_info = {}
        self.formatter = AnalysisFormatter()
        
    def load_dataframe_to_sql(self, df: pd.DataFrame, table_name: str = None) -> bool:
        """Load pandas DataFrame into SQLite for querying"""
        try:
            if table_name:
                self.table_name = table_name
                
            # Close existing connection if any
            if self.connection:
                self.connection.close()
                
            # Create in-memory SQLite database
            self.connection = sqlite3.connect(':memory:')
            
            # Clean column names for SQL compatibility
            df_clean = df.copy()
            df_clean.columns = [self._clean_column_name(col) for col in df_clean.columns]
            
            # Load DataFrame into SQLite
            df_clean.to_sql(self.table_name, self.connection, index=False, if_exists='replace')
            
            # Store schema information
            self.schema_info = self._extract_schema_info(df_clean)
            
            print(f"[SQL] Loaded {len(df)} rows into table '{self.table_name}'")
            return True
            
        except Exception as e:
            print(f"[SQL ERROR] Failed to load data: {str(e)}")
            return False
    
    def execute_query(self, sql_query: str) -> SQLQueryResult:
        """Execute SQL query and return results"""
        try:
            if not self.connection:
                return SQLQueryResult(
                    success=False,
                    error_message="No data loaded. Please load CSV data first."
                )
            
            # Security: Basic SQL injection prevention
            if not self._is_safe_query(sql_query):
                return SQLQueryResult(
                    success=False,
                    error_message="Query contains potentially unsafe operations"
                )
            
            # Execute query
            result_df = pd.read_sql_query(sql_query, self.connection)
            
            print(f"[SQL] Query executed successfully, returned {len(result_df)} rows")
            return SQLQueryResult(
                success=True,
                data=result_df
            )
            
        except Exception as e:
            error_msg = str(e)
            print(f"[SQL ERROR] Query execution failed: {error_msg}")
            return SQLQueryResult(
                success=False,
                error_message=f"SQL Error: {error_msg}"
            )
    
    def get_table_schema(self) -> Dict:
        """Get information about the loaded table structure"""
        if not self.connection:
            return {"error": "No data loaded"}
            
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"PRAGMA table_info({self.table_name})")
            columns = cursor.fetchall()
            
            schema = {
                "table_name": self.table_name,
                "columns": [],
                "sample_data": {}
            }
            
            for col in columns:
                col_info = {
                    "name": col[1],
                    "type": col[2],
                    "nullable": not col[3]
                }
                schema["columns"].append(col_info)
            
            # Add sample data for each column
            cursor.execute(f"SELECT * FROM {self.table_name} LIMIT 3")
            sample_rows = cursor.fetchall()
            if sample_rows:
                column_names = [desc[0] for desc in cursor.description]
                for i, col_name in enumerate(column_names):
                    schema["sample_data"][col_name] = [row[i] for row in sample_rows]
            
            return schema
            
        except Exception as e:
            return {"error": f"Schema extraction failed: {str(e)}"}
    
    def _extract_schema_info(self, df: pd.DataFrame) -> Dict:
        """Extract helpful schema information from DataFrame"""
        schema = {
            "columns": list(df.columns),
            "dtypes": {str(k): str(v) for k, v in df.dtypes.to_dict().items()},
            "numeric_columns": df.select_dtypes(include=['number']).columns.tolist(),
            "date_columns": df.select_dtypes(include=['datetime']).columns.tolist(),
            "categorical_columns": df.select_dtypes(include=['object']).columns.tolist(),
            "row_count": len(df),
            "null_counts": df.isnull().sum().to_dict()
        }
        return schema
    
    def _clean_column_name(self, col_name: str) -> str:
        """Clean column names for SQL compatibility"""
        # Remove special characters and spaces, replace with underscores
        cleaned = re.sub(r'[^\w]', '_', str(col_name))
        # Remove consecutive underscores
        cleaned = re.sub(r'_+', '_', cleaned)
        # Remove leading/trailing underscores
        cleaned = cleaned.strip('_')
        # Ensure it doesn't start with a number
        if cleaned and cleaned[0].isdigit():
            cleaned = f"col_{cleaned}"
        return cleaned or 'unnamed_column'
    
    def _is_safe_query(self, query: str) -> bool:
        """Basic SQL injection prevention"""
        query_lower = query.lower().strip()
        
        # Block dangerous operations
        dangerous_keywords = [
            'drop', 'delete', 'insert', 'update', 'alter', 'create',
            'truncate', 'exec', 'execute', 'sp_', 'xp_', 'pragma'
        ]
        
        for keyword in dangerous_keywords:
            if keyword in query_lower:
                return False
        
        # Only allow SELECT queries and common SQL functions
        allowed_starts = ['select', 'with']
        if not any(query_lower.startswith(start) for start in allowed_starts):
            return False
            
        return True
    
    def format_sql_results(self, results_df: pd.DataFrame, sql_query: str, original_query: str) -> str:
        """Format SQL query results for chat display"""
        try:
            # Create summary section
            explanation = f"Executed SQL query to answer: '{original_query}'"
            assumptions = [
                f"Generated SQL: {sql_query}",
                f"Returned {len(results_df)} rows",
                "Results filtered and formatted for readability"
            ]
            
            output = self.formatter.create_summary_section(
                "SQL Query Results", 
                explanation, 
                assumptions
            )
            
            # Add results table
            if len(results_df) > 0:
                # Limit results for display
                display_df = results_df.head(50)  # Show up to 50 rows
                
                output += "\n\n📊 **QUERY RESULTS:**\n"
                
                # Convert DataFrame to list of dictionaries for the formatter
                table_data = display_df.to_dict('records')
                headers = list(display_df.columns)
                
                output += "\n" + self.formatter.create_banded_table(
                    table_data, 
                    headers, 
                    max_rows=52  # 50 data rows + 2 for headers
                )
                
                # Add summary statistics if numeric columns
                numeric_cols = display_df.select_dtypes(include=['number']).columns
                if len(numeric_cols) > 0:
                    summary_stats = {}
                    for col in numeric_cols[:5]:  # Limit to first 5 numeric columns
                        try:
                            total = display_df[col].sum()
                            avg = display_df[col].mean()
                            
                            # Format based on data type
                            if abs(total) > 1000 or abs(avg) > 1000:
                                summary_stats[f"{col}_Total"] = self.formatter.format_currency(total)
                                summary_stats[f"{col}_Average"] = self.formatter.format_currency(avg)
                            else:
                                summary_stats[f"{col}_Total"] = f"{total:,.2f}"
                                summary_stats[f"{col}_Average"] = f"{avg:,.2f}"
                        except Exception:
                            # Skip columns that can't be aggregated
                            continue
                    
                    if summary_stats:
                        output += "\n\n" + self.formatter.create_metrics_grid(
                            summary_stats, 
                            "Summary Statistics"
                        )
                        
                # Add row count information
                if len(results_df) > 50:
                    output += f"\n\n*Note: Showing first 50 rows of {len(results_df)} total results.*"
                    
            else:
                output += "\n\n📋 **No results found for this query.**"
            
            return output
            
        except Exception as e:
            return f"❌ **Results formatting error**: {str(e)}"
    
    def close_connection(self):
        """Close the SQLite connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
            print("[SQL] Connection closed")
    
    def __del__(self):
        """Cleanup on object destruction"""
        self.close_connection()

