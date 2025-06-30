import pandas as pd
import numpy as np
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

class DataProcessor:
    """Handles data processing and analysis for financial datasets"""
    
    def __init__(self):
        self.data = None
    
    def get_data_info(self, df):
        """Get basic information about the dataset"""
        if df is None or df.empty:
            return {}
        
        info = {
            "Total Rows": len(df),
            "Total Columns": len(df.columns),
            "Numeric Columns": len(df.select_dtypes(include=[np.number]).columns),
            "Text Columns": len(df.select_dtypes(include=['object']).columns),
            "Missing Values": df.isnull().sum().sum(),
            "Memory Usage (MB)": round(df.memory_usage(deep=True).sum() / 1024**2, 2)
        }
        return info
    
    def detect_financial_columns(self, df):
        """Detect common financial column types"""
        if df is None or df.empty:
            return {}
        
        financial_columns = {
            'date_columns': [],
            'price_columns': [],
            'volume_columns': [],
            'symbol_columns': [],
            'percentage_columns': []
        }
        
        for col in df.columns:
            col_lower = col.lower()
            
            # Date columns
            if any(keyword in col_lower for keyword in ['date', 'time', 'timestamp']):
                financial_columns['date_columns'].append(col)
            
            # Price columns
            elif any(keyword in col_lower for keyword in ['price', 'close', 'open', 'high', 'low', 'value', 'amount']):
                financial_columns['price_columns'].append(col)
            
            # Volume columns
            elif any(keyword in col_lower for keyword in ['volume', 'quantity', 'shares', 'count']):
                financial_columns['volume_columns'].append(col)
            
            # Symbol columns
            elif any(keyword in col_lower for keyword in ['symbol', 'ticker', 'stock', 'company', 'name']):
                financial_columns['symbol_columns'].append(col)
            
            # Percentage columns
            elif any(keyword in col_lower for keyword in ['percent', 'change', 'return', 'yield', '%']):
                financial_columns['percentage_columns'].append(col)
        
        return financial_columns
    
    def get_summary_statistics(self, df):
        """Get summary statistics for numeric columns"""
        if df is None or df.empty:
            return {}
        
        numeric_df = df.select_dtypes(include=[np.number])
        if numeric_df.empty:
            return {}
        
        stats = {
            'mean': numeric_df.mean().to_dict(),
            'median': numeric_df.median().to_dict(),
            'std': numeric_df.std().to_dict(),
            'min': numeric_df.min().to_dict(),
            'max': numeric_df.max().to_dict()
        }
        
        return stats
    
    def analyze_trends(self, df, date_col=None, value_col=None):
        """Analyze trends in the data"""
        if df is None or df.empty:
            return "No data available for trend analysis."
        
        # Auto-detect date and value columns if not provided
        if date_col is None:
            date_columns = [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower()]
            date_col = date_columns[0] if date_columns else None
        
        if value_col is None:
            numeric_columns = df.select_dtypes(include=[np.number]).columns
            value_col = numeric_columns[0] if len(numeric_columns) > 0 else None
        
        if date_col is None or value_col is None:
            return "Unable to detect appropriate date and value columns for trend analysis."
        
        try:
            # Convert date column to datetime if it's not already
            if not pd.api.types.is_datetime64_any_dtype(df[date_col]):
                df[date_col] = pd.to_datetime(df[date_col])
            
            # Sort by date
            df_sorted = df.sort_values(date_col)
            
            # Calculate basic trend metrics
            first_value = df_sorted[value_col].iloc[0]
            last_value = df_sorted[value_col].iloc[-1]
            change = last_value - first_value
            change_percent = (change / first_value) * 100 if first_value != 0 else 0
            
            trend_direction = "increasing" if change > 0 else "decreasing" if change < 0 else "stable"
            
            return f"Trend Analysis: {trend_direction.title()} trend with {change_percent:.2f}% change from {first_value:.2f} to {last_value:.2f}"
        
        except Exception as e:
            return f"Error in trend analysis: {str(e)}"
    
    def generate_insights(self, df):
        """Generate automated insights from the data"""
        if df is None or df.empty:
            return ["No data available for analysis."]
        
        insights = []
        
        # Basic data insights
        insights.append(f"Dataset contains {len(df)} rows and {len(df.columns)} columns.")
        
        # Missing data insights
        missing_data = df.isnull().sum().sum()
        if missing_data > 0:
            insights.append(f"Found {missing_data} missing values in the dataset.")
        else:
            insights.append("No missing values detected in the dataset.")
        
        # Numeric column insights
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            insights.append(f"Found {len(numeric_cols)} numeric columns for analysis.")
            
            # Check for outliers
            for col in numeric_cols[:3]:  # Limit to first 3 numeric columns
                q1 = df[col].quantile(0.25)
                q3 = df[col].quantile(0.75)
                iqr = q3 - q1
                outliers = len(df[(df[col] < q1 - 1.5*iqr) | (df[col] > q3 + 1.5*iqr)])
                if outliers > 0:
                    insights.append(f"Column '{col}' has {outliers} potential outliers.")
        
        # Financial column detection
        financial_cols = self.detect_financial_columns(df)
        if financial_cols['price_columns']:
            insights.append(f"Detected price columns: {', '.join(financial_cols['price_columns'])}")
        if financial_cols['volume_columns']:
            insights.append(f"Detected volume columns: {', '.join(financial_cols['volume_columns'])}")
        
        return insights
