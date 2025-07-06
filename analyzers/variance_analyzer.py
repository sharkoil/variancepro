"""
Variance Analyzer for VariancePro v2.0

This module provides comprehensive variance analysis functionality including:
- Actual vs Planned comparisons
- Budget vs Sales analysis  
- Multi-timespan variance tracking
- Statistical variance calculations

Created as part of modular refactoring to add variance analysis capabilities.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import re


class VarianceAnalyzer:
    """
    Provides comprehensive variance analysis capabilities.
    
    This analyzer can compare different data series (actual vs planned, budget vs sales, etc.)
    across various time periods and provide detailed variance metrics.
    """
    
    def __init__(self):
        """Initialize the variance analyzer."""
        self.analysis_results: Optional[Dict[str, Any]] = None
        self.variance_types = {
            'actual_vs_planned': 'Actual vs Planned',
            'budget_vs_sales': 'Budget vs Sales', 
            'budget_vs_actual': 'Budget vs Actual',
            'forecast_vs_actual': 'Forecast vs Actual',
            'current_vs_previous': 'Current vs Previous Period'
        }
    
    def detect_variance_columns(self, df: pd.DataFrame) -> Dict[str, List[str]]:
        """
        Automatically detect potential variance comparison columns.
        
        Scans column names for common variance analysis patterns like:
        - Actual, Budget, Planned, Forecast
        - Sales, Revenue, Expenses
        - Current period vs historical data
        
        Args:
            df (pd.DataFrame): The DataFrame to scan
            
        Returns:
            Dict[str, List[str]]: Dictionary mapping variance types to available columns
        """
        columns = df.columns.tolist()
        detected_columns = {
            'actual': [],
            'planned': [],
            'budget': [],
            'forecast': [],
            'sales': [],
            'revenue': [],
            'expenses': [],
            'target': []
        }
        
        # Search patterns for each category
        patterns = {
            'actual': ['actual', 'real', 'current', 'ytd'],
            'planned': ['plan', 'planned', 'target', 'goal'],
            'budget': ['budget', 'budgeted', 'allocated'],
            'forecast': ['forecast', 'projected', 'estimated'],
            'sales': ['sales', 'revenue', 'income'],
            'revenue': ['revenue', 'income', 'sales'],
            'expenses': ['expense', 'cost', 'spend', 'expenditure'],
            'target': ['target', 'goal', 'objective']
        }
        
        # Match column names to patterns
        for col in columns:
            col_lower = col.lower()
            
            # Only consider numeric columns for variance analysis
            if df[col].dtype in ['int64', 'float64']:
                for category, pattern_list in patterns.items():
                    if any(pattern in col_lower for pattern in pattern_list):
                        detected_columns[category].append(col)
        
        return detected_columns
    
    def detect_variance_pairs(self, columns: List[str]) -> List[Dict[str, str]]:
        """
        Detect potential variance comparison pairs from column names.
        
        Args:
            columns (List[str]): List of column names to analyze
            
        Returns:
            List[Dict[str, str]]: List of dictionaries with 'actual', 'planned', and 'type' keys
        """
        pairs = []
        columns_lower = [col.lower() for col in columns]
        
        # Define comparison patterns
        comparison_patterns = [
            {
                'actual_patterns': ['actual', 'real', 'current'],
                'planned_patterns': ['plan', 'planned', 'budget', 'target', 'goal'],
                'type': 'actual_vs_planned'
            },
            {
                'actual_patterns': ['budget'],
                'planned_patterns': ['sales', 'revenue', 'actual'],
                'type': 'budget_vs_sales'
            },
            {
                'actual_patterns': ['sales', 'revenue'],
                'planned_patterns': ['budget', 'plan', 'target'],
                'type': 'sales_vs_budget'
            },
            {
                'actual_patterns': ['forecast', 'projected'],
                'planned_patterns': ['actual', 'real'],
                'type': 'forecast_vs_actual'
            }
        ]
        
        # Find pairs for each pattern
        for pattern in comparison_patterns:
            actual_cols = []
            planned_cols = []
            
            # Find columns matching actual patterns
            for i, col in enumerate(columns):
                col_lower = columns_lower[i]
                if any(pattern_word in col_lower for pattern_word in pattern['actual_patterns']):
                    actual_cols.append(col)
            
            # Find columns matching planned patterns  
            for i, col in enumerate(columns):
                col_lower = columns_lower[i]
                if any(pattern_word in col_lower for pattern_word in pattern['planned_patterns']):
                    planned_cols.append(col)
            
            # Create pairs from matches
            for actual_col in actual_cols:
                for planned_col in planned_cols:
                    if actual_col != planned_col:  # Don't pair column with itself
                        pairs.append({
                            'actual': actual_col,
                            'planned': planned_col,
                            'type': pattern['type']
                        })
        
        # Remove duplicates while preserving order
        seen = set()
        unique_pairs = []
        for pair in pairs:
            pair_key = f"{pair['actual']}_{pair['planned']}"
            if pair_key not in seen:
                seen.add(pair_key)
                unique_pairs.append(pair)
        
        return unique_pairs
    
    def calculate_variance(self, 
                          df: pd.DataFrame,
                          actual_col: str,
                          comparison_col: str,
                          date_col: Optional[str] = None,
                          group_by_col: Optional[str] = None) -> Dict[str, Any]:
        """
        Calculate variance between two data series.
        
        Args:
            df (pd.DataFrame): The data to analyze
            actual_col (str): Column name for actual values
            comparison_col (str): Column name for comparison values (budget, planned, etc.)
            date_col (str, optional): Date column for time-based analysis
            group_by_col (str, optional): Column to group analysis by
            
        Returns:
            Dict[str, Any]: Comprehensive variance analysis results
        """
        if actual_col not in df.columns or comparison_col not in df.columns:
            raise ValueError(f"Columns {actual_col} or {comparison_col} not found in data")
        
        # Prepare working DataFrame
        work_df = df[[actual_col, comparison_col]].copy()
        
        if date_col and date_col in df.columns:
            work_df['date'] = pd.to_datetime(df[date_col])
            
        if group_by_col and group_by_col in df.columns:
            work_df['group'] = df[group_by_col]
        
        # Calculate basic variance metrics
        work_df['variance_absolute'] = work_df[actual_col] - work_df[comparison_col]
        
        # Calculate percentage variance (handle division by zero)
        work_df['variance_percentage'] = np.where(
            work_df[comparison_col] != 0,
            (work_df['variance_absolute'] / work_df[comparison_col]) * 100,
            np.inf  # Infinite variance when comparison is zero
        )
        
        # Classify variance as favorable/unfavorable
        work_df['variance_favorable'] = work_df['variance_absolute'] > 0
        
        # Summary statistics
        results = {
            'analysis_type': f"{actual_col} vs {comparison_col}",
            'total_records': len(work_df),
            'summary_stats': {
                'total_actual': float(work_df[actual_col].sum()),
                'total_comparison': float(work_df[comparison_col].sum()),
                'total_variance': float(work_df['variance_absolute'].sum()),
                'avg_variance_pct': float(work_df['variance_percentage'].replace([np.inf, -np.inf], np.nan).mean()),
                'favorable_count': int(work_df['variance_favorable'].sum()),
                'unfavorable_count': int((~work_df['variance_favorable']).sum())
            },
            'variance_distribution': {
                'min_variance': float(work_df['variance_absolute'].min()),
                'max_variance': float(work_df['variance_absolute'].max()),
                'median_variance': float(work_df['variance_absolute'].median()),
                'std_variance': float(work_df['variance_absolute'].std())
            }
        }
        
        # Group-by analysis if requested
        if group_by_col and 'group' in work_df.columns:
            group_analysis = work_df.groupby('group').agg({
                actual_col: ['sum', 'mean'],
                comparison_col: ['sum', 'mean'], 
                'variance_absolute': ['sum', 'mean'],
                'variance_percentage': lambda x: x.replace([np.inf, -np.inf], np.nan).mean()
            }).round(2)
            
            results['group_analysis'] = group_analysis.to_dict()
        
        # Time-based analysis if date column provided
        if date_col and 'date' in work_df.columns:
            time_analysis = self._perform_time_based_variance(work_df, actual_col, comparison_col)
            results['time_analysis'] = time_analysis
        
        # Store results
        self.analysis_results = results
        
        return results
    
    def _perform_time_based_variance(self, 
                                   df: pd.DataFrame, 
                                   actual_col: str, 
                                   comparison_col: str) -> Dict[str, Any]:
        """
        Perform time-based variance analysis.
        
        Args:
            df (pd.DataFrame): DataFrame with date column
            actual_col (str): Actual values column
            comparison_col (str): Comparison values column
            
        Returns:
            Dict[str, Any]: Time-based variance analysis
        """
        # Sort by date
        df_sorted = df.sort_values('date')
        
        # Monthly aggregation
        df_sorted['year_month'] = df_sorted['date'].dt.to_period('M')
        monthly_variance = df_sorted.groupby('year_month').agg({
            actual_col: 'sum',
            comparison_col: 'sum',
            'variance_absolute': 'sum'
        }).round(2)
        
        # Quarterly aggregation  
        df_sorted['year_quarter'] = df_sorted['date'].dt.to_period('Q')
        quarterly_variance = df_sorted.groupby('year_quarter').agg({
            actual_col: 'sum',
            comparison_col: 'sum',
            'variance_absolute': 'sum'
        }).round(2)
        
        return {
            'monthly_variance': monthly_variance.to_dict(),
            'quarterly_variance': quarterly_variance.to_dict(),
            'date_range': {
                'start': df_sorted['date'].min().strftime('%Y-%m-%d'),
                'end': df_sorted['date'].max().strftime('%Y-%m-%d')
            }
        }
    
    def identify_significant_variances(self, 
                                     threshold_pct: float = 10.0,
                                     threshold_abs: Optional[float] = None) -> List[Dict[str, Any]]:
        """
        Identify records with significant variances based on thresholds.
        
        Args:
            threshold_pct (float): Percentage threshold for significance (default: 10%)
            threshold_abs (float, optional): Absolute value threshold
            
        Returns:
            List[Dict[str, Any]]: List of significant variance records
        """
        if not self.analysis_results:
            return []
        
        # This would work with the detailed variance data
        # Implementation depends on storing row-level variance data
        significant_variances = []
        
        # Add logic to identify outliers and significant variances
        # based on the provided thresholds
        
        return significant_variances
    
    def format_variance_report(self, results: Optional[Dict[str, Any]] = None) -> str:
        """
        Format variance analysis results into a readable report.
        
        Args:
            results (Dict[str, Any], optional): Analysis results. Uses stored results if None.
            
        Returns:
            str: Formatted variance analysis report
        """
        if results is None:
            results = self.analysis_results
            
        if not results:
            return "No variance analysis results available."
        
        report_lines = [
            f"📊 **{results['analysis_type']} Analysis**",
            "",
            "### Summary Statistics",
            f"• **Total Records**: {results['total_records']:,}",
            f"• **Total Actual**: ${results['summary_stats']['total_actual']:,.2f}",
            f"• **Total Comparison**: ${results['summary_stats']['total_comparison']:,.2f}",
            f"• **Total Variance**: ${results['summary_stats']['total_variance']:,.2f}",
            f"• **Average Variance %**: {results['summary_stats']['avg_variance_pct']:.1f}%",
            "",
            "### Variance Distribution",
            f"• **Favorable**: {results['summary_stats']['favorable_count']} records",
            f"• **Unfavorable**: {results['summary_stats']['unfavorable_count']} records",
            f"• **Min Variance**: ${results['variance_distribution']['min_variance']:,.2f}",
            f"• **Max Variance**: ${results['variance_distribution']['max_variance']:,.2f}",
            f"• **Median Variance**: ${results['variance_distribution']['median_variance']:,.2f}",
        ]
        
        # Add time analysis if available
        if 'time_analysis' in results:
            report_lines.extend([
                "",
                "### Time Period Analysis",
                f"• **Date Range**: {results['time_analysis']['date_range']['start']} to {results['time_analysis']['date_range']['end']}",
                "• Monthly and quarterly variance trends available"
            ])
        
        # Add group analysis if available
        if 'group_analysis' in results:
            report_lines.extend([
                "",
                "### Group Analysis",
                "• Variance breakdown by category available"
            ])
        
        return "\n".join(report_lines)
    
    def suggest_variance_analysis(self, df: pd.DataFrame) -> List[str]:
        """
        Suggest possible variance analyses based on available data.
        
        Args:
            df (pd.DataFrame): The DataFrame to analyze
            
        Returns:
            List[str]: List of suggested variance analysis options
        """
        detected_cols = self.detect_variance_columns(df)
        suggestions = []
        
        # Look for common variance combinations
        if detected_cols['actual'] and detected_cols['planned']:
            suggestions.append(f"Actual vs Planned analysis using {detected_cols['actual'][0]} and {detected_cols['planned'][0]}")
        
        if detected_cols['actual'] and detected_cols['budget']:
            suggestions.append(f"Budget vs Actual analysis using {detected_cols['budget'][0]} and {detected_cols['actual'][0]}")
        
        if detected_cols['sales'] and detected_cols['budget']:
            suggestions.append(f"Budget vs Sales analysis using {detected_cols['budget'][0]} and {detected_cols['sales'][0]}")
        
        if detected_cols['forecast'] and detected_cols['actual']:
            suggestions.append(f"Forecast vs Actual analysis using {detected_cols['forecast'][0]} and {detected_cols['actual'][0]}")
        
        if not suggestions:
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            if len(numeric_cols) >= 2:
                suggestions.append(f"Custom variance analysis between any two numeric columns")
        
        return suggestions
    
    def calculate_variance(self, data: pd.DataFrame, actual_col: str, planned_col: str, analysis_type: str = 'absolute') -> str:
        """
        Simple variance calculation method for quick analysis.
        
        Args:
            data (pd.DataFrame): The data to analyze
            actual_col (str): Column with actual values
            planned_col (str): Column with planned/comparison values  
            analysis_type (str): Type of analysis ('absolute', 'percentage')
            
        Returns:
            str: Formatted variance analysis result
        """
        try:
            # Basic validation
            if actual_col not in data.columns or planned_col not in data.columns:
                return f"❌ **Error**: Columns '{actual_col}' or '{planned_col}' not found in data."
            
            # Calculate basic variance metrics
            actual_total = data[actual_col].sum()
            planned_total = data[planned_col].sum()
            variance_absolute = actual_total - planned_total
            
            # Calculate percentage variance
            variance_percentage = 0
            if planned_total != 0:
                variance_percentage = (variance_absolute / planned_total) * 100
            
            # Determine if variance is favorable
            is_favorable = variance_absolute > 0
            direction = "favorable" if is_favorable else "unfavorable"
            
            # Format results
            result_lines = [
                f"**{actual_col}**: ${actual_total:,.2f}",
                f"**{planned_col}**: ${planned_total:,.2f}",
                f"**Variance**: ${variance_absolute:,.2f} ({variance_percentage:+.1f}%)",
                f"**Direction**: {direction.title()} ({'over' if is_favorable else 'under'} plan)",
                "",
                f"**Analysis**: The actual values are ${abs(variance_absolute):,.2f} {direction} compared to planned values."
            ]
            
            return "\n".join(result_lines)
            
        except Exception as e:
            return f"❌ **Variance Calculation Error**: {str(e)}"
