"""
Top/Bottom N Analysis Handler for Quant Commander v2.0

This module handles top/bottom N analysis functionality including:
- Top N analysis (top 5, top 10)
- Bottom N analysis (bottom 5, bottom 10) 
- Enhanced analysis generation
- Results formatting

Following modular design principles to keep files focused and maintainable.
"""

import pandas as pd
from typing import Dict, Any


class TopBottomAnalysisHandler:
    """
    Handles top/bottom N analysis functionality.
    
    This class focuses solely on top/bottom analysis
    to maintain single responsibility principle.
    """
    
    def __init__(self, app_core):
        """
        Initialize the top/bottom analysis handler.
        
        Args:
            app_core: Reference to the main application core for data access
        """
        self.app_core = app_core
    
    def handle_top_bottom_analysis(self, action: str) -> str:
        """
        Handle top/bottom N analysis actions.
        
        Args:
            action (str): The action (top5, bottom10, etc.)
            
        Returns:
            str: Analysis response
        """
        try:
            current_data, _ = self.app_core.get_current_data()
            
            # Parse the action to get N and direction
            direction, n = self._parse_action(action)
            
            # Get numeric columns for analysis
            numeric_columns = current_data.select_dtypes(include=['number']).columns.tolist()
            
            if not numeric_columns:
                return f"⚠️ **{direction.title()} {n} Analysis**: No numeric columns found in your data."
            
            # Get categorical columns for grouping
            categorical_columns = current_data.select_dtypes(include=['object']).columns.tolist()
            
            # Use the first numeric column for values
            value_col = numeric_columns[0]
            
            # Perform analysis based on data structure
            if categorical_columns:
                return self._analyze_with_categories(current_data, direction, n, value_col, categorical_columns[0])
            else:
                return self._analyze_numeric_only(current_data, direction, n, value_col)
                
        except Exception as e:
            return f"❌ **{action.title()} Analysis Error**: {str(e)}"
    
    def _parse_action(self, action: str) -> tuple[str, int]:
        """
        Parse the action string to extract direction and N.
        
        Args:
            action: The action string (e.g., "top 5", "bottom 10")
            
        Returns:
            tuple: (direction, n) where direction is 'top' or 'bottom' and n is the number
        """
        action_lower = action.lower()
        
        if "top" in action_lower:
            direction = "top"
        elif "bottom" in action_lower:
            direction = "bottom"
        else:
            raise ValueError(f"Unrecognized action '{action}'")
        
        # Extract the number
        if "5" in action_lower:
            n = 5
        elif "10" in action_lower:
            n = 10
        else:
            n = 5  # default
        
        return direction, n
    
    def _analyze_with_categories(self, current_data: pd.DataFrame, direction: str, n: int, 
                                value_col: str, category_col: str) -> str:
        """
        Perform top/bottom analysis with categorical grouping.
        
        Args:
            current_data: The DataFrame to analyze
            direction: 'top' or 'bottom'
            n: Number of results to return
            value_col: The numeric column to analyze
            category_col: The categorical column for grouping
            
        Returns:
            str: Formatted analysis results
        """
        # Group by category and sum values
        grouped_data = current_data.groupby(category_col)[value_col].sum().reset_index()
        
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
        
        # Generate comprehensive analysis
        analysis_result = self._generate_enhanced_top_bottom_analysis(
            result_data, direction, n, value_col, current_data, category_col, total_sum
        )
        
        return f"""🔍 **{direction.title()} {n} Analysis by {category_col}**

{result_text}

{analysis_result}"""
    
    def _analyze_numeric_only(self, current_data: pd.DataFrame, direction: str, n: int, 
                             value_col: str) -> str:
        """
        Perform top/bottom analysis without categorical grouping.
        
        Args:
            current_data: The DataFrame to analyze
            direction: 'top' or 'bottom'
            n: Number of results to return
            value_col: The numeric column to analyze
            
        Returns:
            str: Formatted analysis results
        """
        # Sort by the numeric column
        if direction == "top":
            result_data = current_data.nlargest(n, value_col)
        else:
            result_data = current_data.nsmallest(n, value_col)
        
        # Create enhanced analysis for non-categorical data
        analysis_result = self._generate_enhanced_numeric_analysis(
            result_data, direction, n, value_col, current_data
        )
        
        return f"""🔍 **{direction.title()} {n} Analysis**

{analysis_result}"""
    
    def _generate_enhanced_top_bottom_analysis(self, result_data: pd.DataFrame, direction: str, 
                                              n: int, value_col: str, current_data: pd.DataFrame, 
                                              category_col: str, total_sum: float) -> str:
        """
        Generate enhanced analysis for top/bottom N results with categorical grouping.
        
        Args:
            result_data: The filtered top/bottom data
            direction: 'top' or 'bottom'
            n: Number of results
            value_col: The numeric column being analyzed
            current_data: The original dataset
            category_col: The categorical column used for grouping
            total_sum: Total sum of all values
            
        Returns:
            str: Enhanced analysis text
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
                f"• Total categories analyzed: {len(current_data[category_col].unique())}",
                f"• {direction.title()} {n} represents {(n / len(current_data[category_col].unique())) * 100:.1f}% of all categories"
            ]
            
            return "\n".join(analysis_parts)
            
        except Exception as e:
            return f"**Analysis**: {direction.title()} {n} {category_col} by {value_col} (detailed analysis unavailable: {str(e)})"
    
    def _generate_enhanced_numeric_analysis(self, result_data: pd.DataFrame, direction: str, 
                                           n: int, value_col: str, current_data: pd.DataFrame) -> str:
        """
        Generate enhanced analysis for top/bottom N results without categorical grouping.
        
        Args:
            result_data: The filtered top/bottom data
            direction: 'top' or 'bottom'
            n: Number of results
            value_col: The numeric column being analyzed
            current_data: The original dataset
            
        Returns:
            str: Enhanced analysis text
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
            total_avg = current_data[value_col].mean()
            
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
