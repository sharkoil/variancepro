"""
Top/Bottom N Analysis Handler for Quant Commander v2.0

This module handles top/bottom N analysis functionality.
Extracted from quick_action_handler.py to follow modular design principles.
"""

import pandas as pd
from typing import Dict, Any


class TopBottomAnalyzer:
    """
    Handles top/bottom N analysis for quick actions.
    
    This class provides focused functionality for ranking and analyzing
    top and bottom performers in datasets.
    """
    
    def __init__(self):
        """Initialize the top/bottom analyzer."""
        pass
    
    def analyze_top_bottom(self, data: pd.DataFrame, action: str) -> str:
        """
        Perform top/bottom N analysis on the dataset.
        
        Args:
            data: The DataFrame to analyze
            action: The action string (e.g., "top 5", "bottom 10")
            
        Returns:
            str: Formatted analysis results
        """
        try:
            # Parse the action to get N and direction
            action_lower = action.lower()
            
            if "top" in action_lower:
                direction = "top"
                if "5" in action_lower:
                    n = 5
                elif "10" in action_lower:
                    n = 10
                else:
                    n = 5  # default
            elif "bottom" in action_lower:
                direction = "bottom"
                if "5" in action_lower:
                    n = 5
                elif "10" in action_lower:
                    n = 10
                else:
                    n = 5  # default
            else:
                return f"❌ **Analysis Error**: Unrecognized action '{action}'"
            
            # Get numeric columns for analysis
            numeric_columns = data.select_dtypes(include=['number']).columns.tolist()
            
            if not numeric_columns:
                return f"⚠️ **{direction.title()} {n} Analysis**: No numeric columns found in your data."
            
            # Get categorical columns for grouping
            categorical_columns = data.select_dtypes(include=['object']).columns.tolist()
            
            # Use the first numeric column for values
            value_col = numeric_columns[0]
            
            # Use the first categorical column for categories (if available)
            if categorical_columns:
                return self._analyze_categorical_data(
                    data, direction, n, value_col, categorical_columns[0]
                )
            else:
                return self._analyze_numeric_data(
                    data, direction, n, value_col
                )
                
        except Exception as e:
            return f"❌ **{action.title()} Analysis Error**: {str(e)}"
    
    def _analyze_categorical_data(self, data: pd.DataFrame, direction: str, n: int, 
                                value_col: str, category_col: str) -> str:
        """
        Analyze top/bottom N with categorical grouping.
        
        Args:
            data: The DataFrame to analyze
            direction: 'top' or 'bottom'
            n: Number of results to show
            value_col: The numeric column for values
            category_col: The categorical column for grouping
            
        Returns:
            str: Formatted analysis results
        """
        # Group by category and sum values
        grouped_data = data.groupby(category_col)[value_col].sum().reset_index()
        
        # Sort and get top/bottom N
        if direction == "top":
            result_data = grouped_data.nlargest(n, value_col)
        else:
            result_data = grouped_data.nsmallest(n, value_col)
            
        # Format results with more detail
        result_text = ""
        total_sum = grouped_data[value_col].sum()
        
        for idx, (_, row) in enumerate(result_data.iterrows(), 1):
            percentage = (row[value_col] / total_sum) * 100 if total_sum > 0 else 0
            result_text += f"• **#{idx} {row[category_col]}**: ${row[value_col]:,.2f} ({percentage:.1f}% of total)\n"
        
        # Generate enhanced analysis
        analysis_result = self._generate_categorical_insights(
            result_data, direction, n, value_col, data, category_col, total_sum
        )
        
        return f"""🔍 **{direction.title()} {n} Analysis by {category_col}**

{result_text}

{analysis_result}"""
    
    def _analyze_numeric_data(self, data: pd.DataFrame, direction: str, n: int, 
                            value_col: str) -> str:
        """
        Analyze top/bottom N without categorical grouping.
        
        Args:
            data: The DataFrame to analyze
            direction: 'top' or 'bottom'
            n: Number of results to show
            value_col: The numeric column for values
            
        Returns:
            str: Formatted analysis results
        """
        # Sort by the numeric column
        if direction == "top":
            result_data = data.nlargest(n, value_col)
        else:
            result_data = data.nsmallest(n, value_col)
        
        # Generate enhanced analysis
        analysis_result = self._generate_numeric_insights(
            result_data, direction, n, value_col, data
        )
        
        return f"""🔍 **{direction.title()} {n} Analysis**

{analysis_result}"""
    
    def _generate_categorical_insights(self, result_data: pd.DataFrame, direction: str, 
                                     n: int, value_col: str, original_data: pd.DataFrame, 
                                     category_col: str, total_sum: float) -> str:
        """
        Generate insights for categorical top/bottom analysis.
        
        Args:
            result_data: The filtered results
            direction: 'top' or 'bottom'
            n: Number of results
            value_col: The numeric column
            original_data: The original dataset
            category_col: The categorical column
            total_sum: Total sum of all values
            
        Returns:
            str: Analysis insights
        """
        try:
            # Calculate insights
            top_value = result_data[value_col].iloc[0]
            bottom_value = result_data[value_col].iloc[-1]
            avg_value = result_data[value_col].mean()
            
            # Get the category names
            top_category = result_data[category_col].iloc[0]
            
            # Calculate concentration
            top_n_percentage = (result_data[value_col].sum() / total_sum) * 100 if total_sum > 0 else 0
            
            analysis_parts = [
                "**📈 Analysis Insights**:",
                f"• **Leading performer**: {top_category} accounts for {(top_value / total_sum) * 100:.1f}% of total",
                f"• **{direction.title()} {n} concentration**: {top_n_percentage:.1f}% of total value",
                f"• **Average in {direction} {n}**: ${avg_value:,.2f}",
                "",
                "**💡 Key Observations**:",
                f"• Performance range: ${bottom_value:,.2f} to ${top_value:,.2f}",
                f"• Total categories analyzed: {len(original_data[category_col].unique())}",
                f"• {direction.title()} {n} represents {(n / len(original_data[category_col].unique())) * 100:.1f}% of all categories"
            ]
            
            return "\n".join(analysis_parts)
            
        except Exception as e:
            return f"**Analysis**: {direction.title()} {n} {category_col} by {value_col} (detailed analysis unavailable: {str(e)})"
    
    def _generate_numeric_insights(self, result_data: pd.DataFrame, direction: str, 
                                 n: int, value_col: str, original_data: pd.DataFrame) -> str:
        """
        Generate insights for numeric top/bottom analysis.
        
        Args:
            result_data: The filtered results
            direction: 'top' or 'bottom'
            n: Number of results
            value_col: The numeric column
            original_data: The original dataset
            
        Returns:
            str: Analysis insights
        """
        try:
            # Show the actual values
            result_text = ""
            for idx, (_, row) in enumerate(result_data.iterrows(), 1):
                result_text += f"• **#{idx}**: ${row[value_col]:,.2f}\n"
            
            # Calculate insights
            top_value = result_data[value_col].iloc[0]
            bottom_value = result_data[value_col].iloc[-1]
            avg_value = result_data[value_col].mean()
            total_avg = original_data[value_col].mean()
            
            analysis_parts = [
                result_text,
                "",
                "**📈 Analysis Insights**:",
                f"• **{direction.title()} value**: ${top_value:,.2f}",
                f"• **Average in {direction} {n}**: ${avg_value:,.2f}",
                f"• **Overall dataset average**: ${total_avg:,.2f}",
                f"• **Performance range**: ${bottom_value:,.2f} to ${top_value:,.2f}",
                "",
                f"**💡 Key Observation**: {direction.title()} {n} values are {'above' if avg_value > total_avg else 'below'} dataset average"
            ]
            
            return "\n".join(analysis_parts)
            
        except Exception as e:
            return f"**Analysis**: {direction.title()} {n} values by {value_col} (detailed analysis unavailable: {str(e)})"
