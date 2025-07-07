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
    
    def comprehensive_variance_analysis(self, data: pd.DataFrame, actual_col: str, planned_col: str, 
                                      date_col: Optional[str] = None) -> Dict[str, Any]:
        """
        Perform comprehensive variance analysis across multiple time periods.
        
        Args:
            data (pd.DataFrame): The data to analyze
            actual_col (str): Column with actual values
            planned_col (str): Column with planned/comparison values
            date_col (str, optional): Date column for time-based aggregation
            
        Returns:
            Dict[str, Any]: Comprehensive variance analysis results
        """
        try:
            results = {
                'summary': {},
                'time_periods': {},
                'statistical_analysis': {},
                'insights': []
            }
            
            # Basic variance calculations
            actual_total = data[actual_col].sum()
            planned_total = data[planned_col].sum()
            variance_absolute = actual_total - planned_total
            variance_percentage = (variance_absolute / planned_total * 100) if planned_total != 0 else 0
            
            results['summary'] = {
                'actual_total': actual_total,
                'planned_total': planned_total,
                'variance_absolute': variance_absolute,
                'variance_percentage': variance_percentage,
                'is_favorable': variance_absolute > 0,
                'record_count': len(data)
            }
            
            # Time-based analysis if date column provided
            if date_col and date_col in data.columns:
                # Convert date column to datetime
                data_with_dates = data.copy()
                data_with_dates[date_col] = pd.to_datetime(data_with_dates[date_col])
                
                # Analyze different time periods
                time_periods = self._analyze_time_periods(data_with_dates, actual_col, planned_col, date_col)
                results['time_periods'] = time_periods
            
            # Statistical analysis
            data['variance'] = data[actual_col] - data[planned_col]
            data['variance_pct'] = (data['variance'] / data[planned_col] * 100).replace([np.inf, -np.inf], 0)
            
            results['statistical_analysis'] = {
                'variance_mean': float(data['variance'].mean()),
                'variance_std': float(data['variance'].std()),
                'variance_min': float(data['variance'].min()),
                'variance_max': float(data['variance'].max()),
                'variance_median': float(data['variance'].median()),
                'positive_variances': int((data['variance'] > 0).sum()),
                'negative_variances': int((data['variance'] < 0).sum()),
                'zero_variances': int((data['variance'] == 0).sum())
            }
            
            # Generate insights
            results['insights'] = self._generate_variance_insights(results)
            
            return results
            
        except Exception as e:
            return {'error': f"Comprehensive variance analysis failed: {str(e)}"}
    
    def _analyze_time_periods(self, data: pd.DataFrame, actual_col: str, planned_col: str, date_col: str) -> Dict[str, Any]:
        """
        Analyze variance across different time periods.
        
        Args:
            data (pd.DataFrame): Data with datetime column
            actual_col (str): Actual values column
            planned_col (str): Planned values column
            date_col (str): Date column name
            
        Returns:
            Dict[str, Any]: Time period analysis results
        """
        time_analysis = {}
        
        # Determine data span
        date_range = data[date_col].max() - data[date_col].min()
        
        try:
            # Daily analysis (if data spans multiple days)
            if date_range.days > 1:
                daily_data = data.groupby(data[date_col].dt.date).agg({
                    actual_col: 'sum',
                    planned_col: 'sum'
                })
                daily_data['variance'] = daily_data[actual_col] - daily_data[planned_col]
                daily_data['variance_pct'] = (daily_data['variance'] / daily_data[planned_col] * 100).replace([np.inf, -np.inf], 0)
                
                time_analysis['daily'] = {
                    'periods': len(daily_data),
                    'avg_daily_variance': float(daily_data['variance'].mean()),
                    'best_day': {
                        'date': str(daily_data['variance'].idxmax()),
                        'variance': float(daily_data['variance'].max())
                    },
                    'worst_day': {
                        'date': str(daily_data['variance'].idxmin()),
                        'variance': float(daily_data['variance'].min())
                    }
                }
        except Exception as e:
            time_analysis['daily'] = {'error': str(e)}
        
        try:
            # Weekly analysis (if data spans multiple weeks)
            if date_range.days > 7:
                weekly_data = data.groupby(data[date_col].dt.to_period('W')).agg({
                    actual_col: 'sum',
                    planned_col: 'sum'
                })
                weekly_data['variance'] = weekly_data[actual_col] - weekly_data[planned_col]
                weekly_data['variance_pct'] = (weekly_data['variance'] / weekly_data[planned_col] * 100).replace([np.inf, -np.inf], 0)
                
                time_analysis['weekly'] = {
                    'periods': len(weekly_data),
                    'avg_weekly_variance': float(weekly_data['variance'].mean()),
                    'best_week': {
                        'period': str(weekly_data['variance'].idxmax()),
                        'variance': float(weekly_data['variance'].max())
                    },
                    'worst_week': {
                        'period': str(weekly_data['variance'].idxmin()),
                        'variance': float(weekly_data['variance'].min())
                    }
                }
        except Exception as e:
            time_analysis['weekly'] = {'error': str(e)}
        
        try:
            # Monthly analysis (if data spans multiple months)
            if date_range.days > 30:
                monthly_data = data.groupby(data[date_col].dt.to_period('M')).agg({
                    actual_col: 'sum',
                    planned_col: 'sum'
                })
                monthly_data['variance'] = monthly_data[actual_col] - monthly_data[planned_col]
                monthly_data['variance_pct'] = (monthly_data['variance'] / monthly_data[planned_col] * 100).replace([np.inf, -np.inf], 0)
                
                time_analysis['monthly'] = {
                    'periods': len(monthly_data),
                    'avg_monthly_variance': float(monthly_data['variance'].mean()),
                    'best_month': {
                        'period': str(monthly_data['variance'].idxmax()),
                        'variance': float(monthly_data['variance'].max())
                    },
                    'worst_month': {
                        'period': str(monthly_data['variance'].idxmin()),
                        'variance': float(monthly_data['variance'].min())
                    }
                }
        except Exception as e:
            time_analysis['monthly'] = {'error': str(e)}
        
        try:
            # Quarterly analysis (if data spans multiple quarters)
            if date_range.days > 90:
                quarterly_data = data.groupby(data[date_col].dt.to_period('Q')).agg({
                    actual_col: 'sum',
                    planned_col: 'sum'
                })
                quarterly_data['variance'] = quarterly_data[actual_col] - quarterly_data[planned_col]
                quarterly_data['variance_pct'] = (quarterly_data['variance'] / quarterly_data[planned_col] * 100).replace([np.inf, -np.inf], 0)
                
                time_analysis['quarterly'] = {
                    'periods': len(quarterly_data),
                    'avg_quarterly_variance': float(quarterly_data['variance'].mean()),
                    'best_quarter': {
                        'period': str(quarterly_data['variance'].idxmax()),
                        'variance': float(quarterly_data['variance'].max())
                    },
                    'worst_quarter': {
                        'period': str(quarterly_data['variance'].idxmin()),
                        'variance': float(quarterly_data['variance'].min())
                    }
                }
        except Exception as e:
            time_analysis['quarterly'] = {'error': str(e)}
        
        try:
            # Yearly analysis (if data spans multiple years)
            if date_range.days > 365:
                yearly_data = data.groupby(data[date_col].dt.to_period('Y')).agg({
                    actual_col: 'sum',
                    planned_col: 'sum'
                })
                yearly_data['variance'] = yearly_data[actual_col] - yearly_data[planned_col]
                yearly_data['variance_pct'] = (yearly_data['variance'] / yearly_data[planned_col] * 100).replace([np.inf, -np.inf], 0)
                
                time_analysis['yearly'] = {
                    'periods': len(yearly_data),
                    'avg_yearly_variance': float(yearly_data['variance'].mean()),
                    'best_year': {
                        'period': str(yearly_data['variance'].idxmax()),
                        'variance': float(yearly_data['variance'].max())
                    },
                    'worst_year': {
                        'period': str(yearly_data['variance'].idxmin()),
                        'variance': float(yearly_data['variance'].min())
                    }
                }
        except Exception as e:
            time_analysis['yearly'] = {'error': str(e)}
        
        return time_analysis
    
    def _generate_variance_insights(self, results: Dict[str, Any]) -> List[str]:
        """
        Generate business insights from variance analysis results.
        
        Args:
            results (Dict[str, Any]): Variance analysis results
            
        Returns:
            List[str]: List of business insights
        """
        insights = []
        
        try:
            summary = results['summary']
            
            # Overall performance insight
            if summary['is_favorable']:
                insights.append(f"📈 **Positive Performance**: Actuals exceeded plan by ${summary['variance_absolute']:,.2f} ({summary['variance_percentage']:+.1f}%)")
            else:
                insights.append(f"📉 **Performance Gap**: Actuals fell short of plan by ${abs(summary['variance_absolute']):,.2f} ({summary['variance_percentage']:+.1f}%)")
            
            # Statistical insights
            if 'statistical_analysis' in results:
                stats = results['statistical_analysis']
                
                if stats['variance_std'] > abs(stats['variance_mean']) * 0.5:
                    insights.append("⚠️ **High Variability**: Performance shows significant inconsistency across periods")
                
                positive_ratio = stats['positive_variances'] / (stats['positive_variances'] + stats['negative_variances'])
                if positive_ratio > 0.7:
                    insights.append(f"✅ **Consistent Outperformance**: {positive_ratio:.0%} of periods exceeded plan")
                elif positive_ratio < 0.3:
                    insights.append(f"❌ **Consistent Underperformance**: {(1-positive_ratio):.0%} of periods fell short of plan")
            
            # Time-based insights
            if 'time_periods' in results:
                time_periods = results['time_periods']
                
                for period_type, period_data in time_periods.items():
                    if 'error' not in period_data and 'avg_' + period_type + '_variance' in period_data:
                        avg_variance = period_data[f'avg_{period_type}_variance']
                        if abs(avg_variance) > abs(summary['variance_absolute']) * 0.1:
                            if avg_variance > 0:
                                insights.append(f"📊 **{period_type.title()} Trend**: Average {period_type} outperformance of ${avg_variance:,.2f}")
                            else:
                                insights.append(f"📊 **{period_type.title()} Trend**: Average {period_type} shortfall of ${abs(avg_variance):,.2f}")
            
        except Exception as e:
            insights.append(f"❌ Error generating insights: {str(e)}")
        
        return insights
    
    def generate_llm_variance_insights(self, results: Dict[str, Any], ollama_connector=None) -> str:
        """
        Generate LLM-powered insights for variance analysis results.
        
        Args:
            results (Dict[str, Any]): Variance analysis results
            ollama_connector: Ollama connector instance for LLM calls
            
        Returns:
            str: LLM-generated business insights or fallback analysis
        """
        try:
            if not ollama_connector:
                return self._generate_enhanced_fallback_insights(results)
            
            # Check if Ollama is available
            connection_status = ollama_connector.check_connection()
            if "❌" in connection_status:
                return self._generate_enhanced_fallback_insights(results)
            
            # Prepare comprehensive context for LLM
            summary = results['summary']
            stats = results.get('statistical_analysis', {})
            time_periods = results.get('time_periods', {})
            
            # Build detailed prompt
            prompt = f"""
As a senior financial analyst and business strategist, analyze this comprehensive variance report and provide strategic insights:

EXECUTIVE SUMMARY:
- Actual Performance: ${summary['actual_total']:,.2f}
- Planned/Budget: ${summary['planned_total']:,.2f}
- Total Variance: ${summary['variance_absolute']:,.2f} ({summary['variance_percentage']:+.1f}%)
- Performance Direction: {'Favorable (Over-performance)' if summary['is_favorable'] else 'Unfavorable (Under-performance)'}
- Data Points Analyzed: {summary['record_count']:,} records

STATISTICAL PROFILE:
- Average Variance: ${stats.get('variance_mean', 0):,.2f}
- Volatility (Std Dev): ${stats.get('variance_std', 0):,.2f}
- Performance Range: ${stats.get('variance_min', 0):,.2f} to ${stats.get('variance_max', 0):,.2f}
- Consistency: {stats.get('positive_variances', 0)} positive vs {stats.get('negative_variances', 0)} negative periods
"""

            # Add time-based context if available
            if time_periods:
                prompt += "\n\nTIME-BASED PERFORMANCE:\n"
                for period_type, period_data in time_periods.items():
                    if 'error' not in period_data and 'periods' in period_data:
                        avg_key = f'avg_{period_type}_variance'
                        if avg_key in period_data:
                            prompt += f"- {period_type.title()}: {period_data['periods']} periods, avg variance ${period_data[avg_key]:,.2f}\n"
                            if 'best_' + period_type in period_data and 'worst_' + period_type in period_data:
                                best = period_data[f'best_{period_type}']
                                worst = period_data[f'worst_{period_type}']
                                prompt += f"  Best: ${best['variance']:,.2f}, Worst: ${worst['variance']:,.2f}\n"

            prompt += """

ANALYSIS REQUIREMENTS:
Please provide a comprehensive business analysis covering:

1. PERFORMANCE ASSESSMENT:
   - Overall performance interpretation and business implications
   - Variance magnitude assessment (significant/normal/concerning)
   - Consistency and predictability evaluation

2. ROOT CAUSE ANALYSIS:
   - Potential drivers of the observed variance patterns
   - Market conditions or operational factors that might explain results
   - Areas requiring immediate investigation

3. STRATEGIC RECOMMENDATIONS:
   - Immediate actions to address performance gaps or capitalize on strengths
   - Process improvements for better forecasting/planning
   - Risk mitigation strategies for identified volatility

4. FORWARD-LOOKING INSIGHTS:
   - Trends that require monitoring
   - Early warning indicators to track
   - Scenario planning considerations

Format your response with clear sections and actionable bullet points. Focus on business value and strategic decision-making. Keep the total response under 300 words but ensure high analytical value.
"""
            
            # Get LLM response
            llm_response = ollama_connector.generate_text(prompt)
            
            return f"""### 🤖 **AI Strategic Analysis**

{llm_response}

---
*Analysis generated using advanced language model with comprehensive variance data context*"""
            
        except Exception as e:
            return self._generate_enhanced_fallback_insights(results)
    
    def _generate_enhanced_fallback_insights(self, results: Dict[str, Any]) -> str:
        """
        Generate enhanced fallback insights when LLM is not available.
        
        Args:
            results (Dict[str, Any]): Variance analysis results
            
        Returns:
            str: Enhanced statistical and business insights
        """
        try:
            summary = results['summary']
            stats = results.get('statistical_analysis', {})
            time_periods = results.get('time_periods', {})
            
            insights = []
            
            # Performance Assessment
            insights.append("### 📊 **Performance Assessment**")
            
            variance_pct = abs(summary['variance_percentage'])
            if variance_pct > 20:
                insights.append("• **🚨 HIGH IMPACT VARIANCE**: Significant deviation requiring immediate attention")
            elif variance_pct > 10:
                insights.append("• **⚠️ MODERATE VARIANCE**: Notable deviation warranting investigation")
            elif variance_pct > 5:
                insights.append("• **📈 MINOR VARIANCE**: Small deviation within acceptable range")
            else:
                insights.append("• **✅ MINIMAL VARIANCE**: Performance closely aligned with plan")
            
            # Direction and magnitude
            direction = "exceeded" if summary['is_favorable'] else "fell short of"
            insights.append(f"• **Performance Direction**: Actuals {direction} plan by ${abs(summary['variance_absolute']):,.2f}")
            
            # Consistency Analysis
            if stats:
                insights.append("\n### 🎯 **Consistency Analysis**")
                
                total_periods = stats.get('positive_variances', 0) + stats.get('negative_variances', 0)
                if total_periods > 0:
                    consistency_ratio = stats.get('positive_variances', 0) / total_periods
                    
                    if consistency_ratio > 0.8:
                        insights.append("• **🟢 HIGH CONSISTENCY**: Predominantly positive performance")
                    elif consistency_ratio > 0.6:
                        insights.append("• **🟡 MODERATE CONSISTENCY**: Generally positive with some volatility")
                    elif consistency_ratio > 0.4:
                        insights.append("• **🟠 MIXED PERFORMANCE**: Balanced positive and negative periods")
                    else:
                        insights.append("• **🔴 LOW CONSISTENCY**: Predominantly negative performance")
                
                # Volatility assessment
                variance_mean = stats.get('variance_mean', 0)
                variance_std = stats.get('variance_std', 0)
                
                if variance_std > 0 and variance_mean != 0:
                    coefficient_variation = abs(variance_std / variance_mean) if variance_mean != 0 else 0
                    
                    if coefficient_variation > 1.0:
                        insights.append("• **📊 HIGH VOLATILITY**: Significant fluctuations in performance")
                    elif coefficient_variation > 0.5:
                        insights.append("• **📊 MODERATE VOLATILITY**: Some variability in results")
                    else:
                        insights.append("• **📊 LOW VOLATILITY**: Stable and predictable performance")
            
            # Time-based insights
            if time_periods:
                insights.append("\n### 📅 **Time Period Insights**")
                
                period_count = len([p for p in time_periods.values() if 'error' not in p])
                if period_count > 0:
                    insights.append(f"• **Analysis Depth**: {period_count} time period types analyzed")
                
                # Find most volatile period
                most_volatile = None
                max_range = 0
                
                for period_type, period_data in time_periods.items():
                    if 'error' not in period_data and 'best_' + period_type in period_data:
                        best = period_data[f'best_{period_type}']['variance']
                        worst = period_data[f'worst_{period_type}']['variance']
                        variance_range = abs(best - worst)
                        
                        if variance_range > max_range:
                            max_range = variance_range
                            most_volatile = period_type
                
                if most_volatile:
                    insights.append(f"• **Most Volatile Period**: {most_volatile.title()} analysis shows highest variance range (${max_range:,.2f})")
            
            # Business Recommendations
            insights.append("\n### 💡 **Strategic Recommendations**")
            
            if summary['is_favorable']:
                insights.append("• **✅ CAPITALIZE**: Analyze success factors for replication")
                insights.append("• **📈 SCALE**: Consider increasing targets based on demonstrated capability")
                if stats.get('variance_std', 0) > abs(stats.get('variance_mean', 0)) * 0.5:
                    insights.append("• **🎯 STABILIZE**: Focus on consistency to reduce volatility")
            else:
                insights.append("• **🔍 INVESTIGATE**: Identify root causes of underperformance")
                insights.append("• **⚡ CORRECTIVE ACTION**: Implement measures to close performance gap")
                insights.append("• **📊 FORECAST REVISION**: Consider updating future planning assumptions")
            
            # Risk Assessment
            insights.append("\n### ⚠️ **Risk Indicators**")
            
            if variance_pct > 15:
                insights.append("• **HIGH RISK**: Large variances may indicate process or market issues")
            
            if stats and stats.get('variance_std', 0) > abs(stats.get('variance_mean', 0)):
                insights.append("• **VOLATILITY RISK**: High variability may impact future predictability")
            
            negative_periods = stats.get('negative_variances', 0) if stats else 0
            total_periods = negative_periods + stats.get('positive_variances', 0) if stats else 1
            
            if negative_periods / total_periods > 0.6:
                insights.append("• **TREND RISK**: Consistent underperformance trend identified")
            
            return "\n".join(insights)
            
        except Exception as e:
            return f"### 📊 **Statistical Summary**\n• Advanced analysis completed\n• Detailed insights unavailable: {str(e)}"
    
    def format_comprehensive_analysis(self, analysis_result: Dict[str, Any]) -> str:
        """
        Format comprehensive variance analysis results for display.
        
        Args:
            analysis_result (Dict[str, Any]): Results from comprehensive_variance_analysis
            
        Returns:
            str: Formatted analysis report
        """
        try:
            if 'error' in analysis_result:
                return f"❌ **Variance Analysis Error**: {analysis_result['error']}"
            
            summary = analysis_result.get('summary', {})
            time_periods = analysis_result.get('time_periods', {})
            stats = analysis_result.get('statistical_analysis', {})
            insights = analysis_result.get('insights', [])
            
            # Build formatted output
            output_lines = []
            
            # Header
            output_lines.append("## 📊 **Comprehensive Variance Analysis**")
            output_lines.append("")
            
            # Summary section
            actual_total = summary.get('actual_total', 0)
            planned_total = summary.get('planned_total', 0)
            variance_absolute = summary.get('variance_absolute', 0)
            variance_percentage = summary.get('variance_percentage', 0)
            is_favorable = summary.get('is_favorable', False)
            record_count = summary.get('record_count', 0)
            
            variance_symbol = "📈" if is_favorable else "📉"
            variance_status = "**FAVORABLE**" if is_favorable else "**UNFAVORABLE**"
            
            output_lines.append("### 📋 **Executive Summary**")
            output_lines.append(f"• **Total Actual**: ${actual_total:,.2f}")
            output_lines.append(f"• **Total Planned**: ${planned_total:,.2f}")
            output_lines.append(f"• **Variance**: ${variance_absolute:,.2f} ({variance_percentage:+.1f}%) {variance_symbol}")
            output_lines.append(f"• **Status**: {variance_status}")
            output_lines.append(f"• **Records Analyzed**: {record_count:,}")
            output_lines.append("")
            
            # Statistical analysis
            if stats:
                output_lines.append("### 📈 **Statistical Analysis**")
                output_lines.append(f"• **Mean Variance**: ${stats.get('variance_mean', 0):,.2f}")
                output_lines.append(f"• **Standard Deviation**: ${stats.get('variance_std', 0):,.2f}")
                output_lines.append(f"• **Range**: ${stats.get('variance_min', 0):,.2f} to ${stats.get('variance_max', 0):,.2f}")
                output_lines.append(f"• **Median Variance**: ${stats.get('variance_median', 0):,.2f}")
                output_lines.append("")
                
                positive = stats.get('positive_variances', 0)
                negative = stats.get('negative_variances', 0)
                zero = stats.get('zero_variances', 0)
                total = positive + negative + zero
                
                if total > 0:
                    output_lines.append("### 📊 **Variance Distribution**")
                    output_lines.append(f"• **Favorable Variances**: {positive} ({positive/total*100:.1f}%)")
                    output_lines.append(f"• **Unfavorable Variances**: {negative} ({negative/total*100:.1f}%)")
                    output_lines.append(f"• **On-Target**: {zero} ({zero/total*100:.1f}%)")
                    output_lines.append("")
            
            # Time period analysis
            if time_periods:
                output_lines.append("### 📅 **Time Period Analysis**")
                
                if 'monthly' in time_periods:
                    monthly = time_periods['monthly']
                    output_lines.append(f"• **Monthly Periods**: {monthly.get('periods', 0)}")
                    output_lines.append(f"• **Best Month**: {monthly.get('best_variance', 0):+.1f}%")
                    output_lines.append(f"• **Worst Month**: {monthly.get('worst_variance', 0):+.1f}%")
                
                if 'weekly' in time_periods:
                    weekly = time_periods['weekly']
                    output_lines.append(f"• **Weekly Periods**: {weekly.get('periods', 0)}")
                    output_lines.append(f"• **Best Week**: {weekly.get('best_variance', 0):+.1f}%")
                    output_lines.append(f"• **Worst Week**: {weekly.get('worst_variance', 0):+.1f}%")
                
                output_lines.append("")
            
            # Key insights
            if insights:
                output_lines.append("### 💡 **Key Insights**")
                for insight in insights:
                    output_lines.append(f"• {insight}")
                output_lines.append("")
            
            # Recommendations
            output_lines.append("### 🎯 **Recommendations**")
            
            if abs(variance_percentage) > 10:
                output_lines.append("• **HIGH VARIANCE**: Review underlying drivers and adjust forecasting models")
            
            if stats and stats.get('variance_std', 0) > abs(stats.get('variance_mean', 0)):
                output_lines.append("• **HIGH VOLATILITY**: Implement stronger variance controls and monitoring")
            
            if is_favorable and variance_percentage > 5:
                output_lines.append("• **INVESTIGATE SUCCESS**: Document favorable variance drivers for replication")
            elif not is_favorable and variance_percentage < -5:
                output_lines.append("• **CORRECTIVE ACTION**: Develop action plan to address unfavorable variances")
            
            output_lines.append("• **REGULAR MONITORING**: Continue variance tracking for trend identification")
            
            return "\n".join(output_lines)
            
        except Exception as e:
            return f"❌ **Formatting Error**: {str(e)}"

    def format_comprehensive_analysis(self) -> str:
        """
        Format the comprehensive variance analysis results for display
        
        Returns:
            str: Formatted analysis results ready for chat display
        """
        if not self.analysis_results:
            return "❌ **No variance analysis results available**. Please run analysis first."
        
        try:
            results = self.analysis_results
            output_lines = []
            
            # Header
            output_lines.append("# 📊 **Comprehensive Variance Analysis**")
            output_lines.append("")
            
            # Summary section
            if 'summary' in results:
                summary = results['summary']
                output_lines.append("## 📋 **Executive Summary**")
                output_lines.append(f"• **Total Variance**: ${summary.get('total_variance', 0):,.2f}")
                output_lines.append(f"• **Variance %**: {summary.get('variance_percentage', 0):.1f}%")
                output_lines.append(f"• **Status**: {'✅ Favorable' if summary.get('is_favorable', False) else '⚠️ Unfavorable'}")
                output_lines.append("")
            
            # Detailed variance breakdown
            if 'variance_breakdown' in results:
                breakdown = results['variance_breakdown']
                output_lines.append("## 📈 **Variance Breakdown**")
                
                for item in breakdown[:5]:  # Show top 5
                    variance = item.get('variance', 0)
                    percentage = item.get('variance_percentage', 0)
                    name = item.get('category', 'Unknown')
                    
                    status = "✅" if variance >= 0 else "❌"
                    output_lines.append(f"• **{name}**: {status} ${variance:,.2f} ({percentage:+.1f}%)")
                
                output_lines.append("")
            
            # Key insights
            if 'insights' in results:
                insights = results['insights']
                output_lines.append("## 💡 **Key Insights**")
                for insight in insights[:3]:  # Show top 3 insights
                    output_lines.append(f"• {insight}")
                output_lines.append("")
            
            # Recommendations
            output_lines.append("## 🎯 **Recommendations**")
            output_lines.append("• **Focus Areas**: Review items with highest absolute variance")
            output_lines.append("• **Trend Monitoring**: Track variance patterns over time")
            output_lines.append("• **Process Review**: Investigate root causes of significant variances")
            
            return "\n".join(output_lines)
            
        except Exception as e:
            return f"❌ **Formatting Error**: {str(e)}"

    # ...existing code...
