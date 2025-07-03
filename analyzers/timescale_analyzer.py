"""
TimescaleAnalyzer - Automatic timescale analysis for financial data
Provides comprehensive time-series analysis at multiple timescales
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from .base_analyzer import BaseAnalyzer, AnalysisError


class TimescaleAnalyzer(BaseAnalyzer):
    """
    Automatic timescale analysis analyzer
    Provides YoY, QoQ, MoM, and WoW analysis with executive insights
    """
    
    def __init__(self, settings):
        super().__init__(settings)
        self.name = "TimescaleAnalyzer"
        self.description = "Automatic timescale analysis for financial data"
        self.analysis_cache = {}
    
    def analyze(self, data: pd.DataFrame, date_col: str, value_cols: Optional[List[str]] = None, **kwargs) -> Dict:
        """
        Perform comprehensive timescale analysis
        
        Args:
            data: DataFrame with time-series data
            date_col: Name of the date column
            value_cols: List of value columns to analyze (optional, auto-detect if None)
            
        Returns:
            Dictionary with analysis results
        """
        try:
            print(f"[DEBUG][TimescaleAnalyzer] Starting analysis with date_col={date_col}")
            print(f"[DEBUG][TimescaleAnalyzer] Value columns: {value_cols}")
            print(f"[DEBUG][TimescaleAnalyzer] Data shape: {data.shape}")
            
            self.status = "running"
            self.errors = []
            
            # Validate inputs
            if date_col not in data.columns:
                print(f"[DEBUG][TimescaleAnalyzer] Date column '{date_col}' not found in data. Available columns: {data.columns.tolist()}")
                raise AnalysisError(f"Date column '{date_col}' not found in data")
            
            # Auto-detect value columns if not provided
            if value_cols is None:
                value_cols = data.select_dtypes(include=[np.number]).columns.tolist()
                # Remove date column if it's somehow in the numeric columns
                if date_col in value_cols:
                    value_cols.remove(date_col)
                print(f"[DEBUG][TimescaleAnalyzer] Auto-detected value columns: {value_cols}")
            
            if not value_cols:
                print("[DEBUG][TimescaleAnalyzer] No numeric columns found for analysis")
                raise AnalysisError("No numeric columns found for analysis")
            
            # Prepare data
            print(f"[DEBUG][TimescaleAnalyzer] Preparing data")
            analysis_data = self._prepare_data(data, date_col, value_cols)
            print(f"[DEBUG][TimescaleAnalyzer] Data prepared, shape: {analysis_data.shape}")
            
            # Perform timescale analysis
            print(f"[DEBUG][TimescaleAnalyzer] Performing timescale analysis")
            results = self._perform_timescale_analysis(analysis_data, date_col, value_cols)
            print(f"[DEBUG][TimescaleAnalyzer] Analysis complete")
            
            # Store results
            self.results = {
                'analysis_type': 'timescale',
                'data': results['data'],
                'insights': results['insights'],
                'parameters': {
                    'date_col': date_col,
                    'value_cols': value_cols,
                    'data_rows': len(analysis_data),
                    'date_range': f"{analysis_data[date_col].min()} to {analysis_data[date_col].max()}"
                }
            }
            
            print(f"[DEBUG][TimescaleAnalyzer] Results stored successfully")
            self.status = "completed"
            return self.results
            
        except Exception as e:
            print(f"[DEBUG][TimescaleAnalyzer] Error in analysis: {str(e)}")
            import traceback
            print(f"[DEBUG][TimescaleAnalyzer] Traceback: {traceback.format_exc()}")
            self.status = "failed"
            self.errors.append(str(e))
            if isinstance(e, AnalysisError):
                raise
            raise AnalysisError(f"Timescale analysis failed: {str(e)}")
    
    def _prepare_data(self, data: pd.DataFrame, date_col: str, value_cols: List[str]) -> pd.DataFrame:
        """Prepare data for timescale analysis"""
        prepared_data = data.copy()
        
        # Convert date column to datetime
        prepared_data[date_col] = pd.to_datetime(prepared_data[date_col])
        
        # Sort by date
        prepared_data = prepared_data.sort_values(by=date_col)
        
        # Remove rows with missing dates or all missing values
        prepared_data = prepared_data.dropna(subset=[date_col])
        
        return prepared_data
    
    def _perform_timescale_analysis(self, data: pd.DataFrame, date_col: str, value_cols: List[str]) -> Dict:
        """Perform the core timescale analysis"""
        
        # Prepare aggregations at different time scales
        aggregations = self._prepare_aggregations(data, date_col, value_cols)
        
        # Calculate period-over-period analysis
        pop_analysis = self._calculate_pop_analysis(aggregations, value_cols)
        
        # Generate insights
        insights = self._generate_insights(pop_analysis)
        
        return {
            'data': pop_analysis,
            'insights': insights
        }
    
    def _prepare_aggregations(self, data: pd.DataFrame, date_col: str, value_cols: List[str]) -> Dict:
        """Prepare aggregations at different time scales"""
        aggregations = {
            "weekly": {},
            "monthly": {},
            "quarterly": {},
            "yearly": {}
        }
        
        df = data.copy()
        
        try:
            # Weekly aggregation
            df['week'] = df[date_col].dt.to_period('W').astype(str)
            weekly = df.groupby('week')[value_cols].sum().reset_index()
            aggregations["weekly"]["data"] = weekly
            aggregations["weekly"]["periods"] = weekly['week'].tolist()
        except:
            aggregations["weekly"] = {}
        
        try:
            # Monthly aggregation
            df['month'] = df[date_col].dt.to_period('M').astype(str)
            monthly = df.groupby('month')[value_cols].sum().reset_index()
            aggregations["monthly"]["data"] = monthly
            aggregations["monthly"]["periods"] = monthly['month'].tolist()
        except:
            aggregations["monthly"] = {}
        
        try:
            # Quarterly aggregation
            df['quarter'] = df[date_col].dt.to_period('Q').astype(str)
            quarterly = df.groupby('quarter')[value_cols].sum().reset_index()
            aggregations["quarterly"]["data"] = quarterly
            aggregations["quarterly"]["periods"] = quarterly['quarter'].tolist()
        except:
            aggregations["quarterly"] = {}
        
        try:
            # Yearly aggregation
            df['year'] = df[date_col].dt.to_period('Y').astype(str)
            yearly = df.groupby('year')[value_cols].sum().reset_index()
            aggregations["yearly"]["data"] = yearly
            aggregations["yearly"]["periods"] = yearly['year'].tolist()
        except:
            aggregations["yearly"] = {}
        
        return aggregations
    
    def _calculate_pop_analysis(self, aggregations: Dict, value_cols: List[str]) -> Dict:
        """Calculate period-over-period metrics"""
        result = {
            "weekly": {},
            "monthly": {},
            "quarterly": {},
            "yearly": {}
        }
        
        for time_scale in ["weekly", "monthly", "quarterly", "yearly"]:
            if time_scale not in aggregations or "data" not in aggregations[time_scale]:
                continue
                
            data = aggregations[time_scale]["data"]
            if data.empty:
                continue
                
            time_col = data.columns[0]  # First column is the time period
            
            for value_col in value_cols:
                if value_col not in data.columns:
                    continue
                
                # Calculate changes
                data[f'{value_col}_prev'] = data[value_col].shift(1)
                data[f'{value_col}_abs_change'] = data[value_col] - data[f'{value_col}_prev']
                data[f'{value_col}_pct_change'] = (data[value_col] / data[f'{value_col}_prev'] - 1) * 100
                
                # Calculate summary statistics
                total_periods = len(data)
                valid_changes = data[f'{value_col}_pct_change'].dropna()
                
                if len(valid_changes) == 0:
                    continue
                
                positive_changes = sum(valid_changes > 0)
                negative_changes = sum(valid_changes < 0)
                
                result[time_scale][value_col] = {
                    "periods": data[time_col].tolist(),
                    "values": data[value_col].tolist(),
                    "pct_changes": data[f'{value_col}_pct_change'].tolist(),
                    "summary": {
                        "total_periods": total_periods,
                        "positive_periods": positive_changes,
                        "negative_periods": negative_changes,
                        "avg_pct_change": valid_changes.mean(),
                        "max_pct_change": valid_changes.max(),
                        "min_pct_change": valid_changes.min(),
                        "latest_value": data[value_col].iloc[-1] if total_periods > 0 else None,
                        "latest_change": data[f'{value_col}_pct_change'].iloc[-1] if total_periods > 0 else None
                    }
                }
        
        return result
    
    def _generate_insights(self, pop_analysis: Dict) -> str:
        """Generate natural language insights"""
        insights = []
        
        # Add header
        insights.append("[ANALYSIS] Automatic Timescale Analysis")
        insights.append("Analysis generated based on time series patterns in your data")
        insights.append("")
        
        # Process each time scale
        for time_scale in ["yearly", "quarterly", "monthly", "weekly"]:
            if time_scale not in pop_analysis or not pop_analysis[time_scale]:
                continue
                
            # Add section header
            header_map = {
                "yearly": "[YEARLY] Year-over-Year (YoY) Analysis",
                "quarterly": "[QUARTERLY] Quarter-over-Quarter (QoQ) Analysis", 
                "monthly": "[MONTHLY] Month-over-Month (MoM) Analysis",
                "weekly": "[WEEKLY] Week-over-Week (WoW) Analysis"
            }
            insights.append(header_map[time_scale])
            
            # Process each metric
            for metric, data in pop_analysis[time_scale].items():
                summary = data["summary"]
                periods = data["periods"]
                
                # Only process if we have enough data
                if summary["total_periods"] < 2:
                    insights.append(f"Insufficient {time_scale} data for {metric} analysis")
                    insights.append("")
                    continue
                
                # Metric name
                metric_name = metric.replace('_', ' ').title()
                insights.append(f"{metric_name}")
                
                # Latest period change
                latest_period = periods[-1] if periods else "Unknown"
                latest_change = summary["latest_change"]
                if pd.notna(latest_change):
                    change_direction = "increased" if latest_change > 0 else "decreased"
                    insights.append(f"Latest {time_scale[:-2]} ({latest_period}): {change_direction} by {abs(latest_change):.2f}%")
                
                # Overall trend
                trend_ratio = summary["positive_periods"] / max(summary["total_periods"] - 1, 1)
                if trend_ratio > 0.6:
                    trend = "mostly increasing"
                elif trend_ratio < 0.4:
                    trend = "mostly decreasing"
                else:
                    trend = "fluctuating"
                
                insights.append(f"Overall trend: {trend} over {summary['total_periods']} periods")
                
                # Extreme periods
                if summary["max_pct_change"] > 0:
                    try:
                        max_idx = data["pct_changes"].index(summary["max_pct_change"])
                        max_period = periods[max_idx] if max_idx < len(periods) else "Unknown"
                        insights.append(f"Largest increase: {summary['max_pct_change']:.2f}% in {max_period}")
                    except:
                        insights.append(f"Largest increase: {summary['max_pct_change']:.2f}%")
                
                if summary["min_pct_change"] < 0:
                    try:
                        min_idx = data["pct_changes"].index(summary["min_pct_change"])
                        min_period = periods[min_idx] if min_idx < len(periods) else "Unknown"
                        insights.append(f"Largest decrease: {summary['min_pct_change']:.2f}% in {min_period}")
                    except:
                        insights.append(f"Largest decrease: {summary['min_pct_change']:.2f}%")
                
                # Average change
                time_unit = time_scale[:-2] if time_scale.endswith('ly') else time_scale
                insights.append(f"Average change: {summary['avg_pct_change']:.2f}% per {time_unit}")
                insights.append("")
        
        # Executive summary
        insights.append("[SUMMARY] Executive Summary")
        insights.append("Key takeaways from the automatic time series analysis:")
        insights.append("")
        insights.append("Insufficient time series data for executive insights")
        
        return "\n".join(insights)
    
    def format_for_chat(self) -> str:
        """
        Format analysis results for chat display using standardized formatting
        
        Returns:
            Formatted string for chat interface
        """
        if self.status != "completed" or not self.results:
            return "❌ **Analysis not completed or failed**"
        
        # Extract results data
        period_analysis = self.results.get('period_analysis', {})
        summary = self.results.get('summary', {})
        insights_text = self.results.get('insights', '')
        
        # 1. Summary section
        explanation = "Analyzes financial performance across multiple time periods (YoY, QoQ, MoM) to identify trends and patterns."
        assumptions = [
            f"Analysis performed on {summary.get('total_columns', 'N/A')} numeric columns",
            f"Data period: {summary.get('date_range', 'N/A')}",
            f"Total data points: {summary.get('total_periods', 'N/A')}",
            "Growth rates calculated period-over-period",
            "Trends identified using statistical analysis"
        ]
        
        formatted_output = self.formatter.create_summary_section(
            "Comprehensive Timescale Analysis",
            explanation,
            assumptions
        )
        
        # 2. Key metrics from summary
        key_metrics = {}
        if summary:
            key_metrics.update({
                "Time_Periods_Analyzed": summary.get('total_periods', 'N/A'),
                "Numeric_Columns": summary.get('total_columns', 'N/A'),
                "Date_Range": summary.get('date_range', 'N/A')
            })
            
            # Add growth metrics if available
            if 'yoy_growth' in summary:
                key_metrics["YoY_Growth"] = f"{summary['yoy_growth']:.1f}%"
            if 'qoq_growth' in summary:
                key_metrics["QoQ_Growth"] = f"{summary['qoq_growth']:.1f}%"
            if 'mom_growth' in summary:
                key_metrics["MoM_Growth"] = f"{summary['mom_growth']:.1f}%"
        
        formatted_output += "\n\n" + self.formatter.create_metrics_grid(key_metrics, "Timescale Performance Summary")
        
        # 3. Period analysis table if available
        if period_analysis:
            formatted_output += "\n\n📊 **PERIOD ANALYSIS TABLE:**\n"
            
            # Convert period analysis to table format
            table_data = []
            for period_type, metrics in period_analysis.items():
                if isinstance(metrics, dict):
                    table_data.append({
                        "Period_Type": period_type.upper(),
                        "Current_Value": metrics.get('current_value', 'N/A'),
                        "Previous_Value": metrics.get('previous_value', 'N/A'),
                        "Growth_Rate": f"{metrics.get('growth_rate', 0):.1f}%",
                        "Trend": metrics.get('trend', 'N/A').title()
                    })
            
            if table_data:
                headers = ["Period_Type", "Current_Value", "Previous_Value", "Growth_Rate", "Trend"]
                formatted_output += "\n" + self.formatter.create_banded_table(table_data, headers, max_rows=10)
        
        # 4. AI-generated insights
        if insights_text and insights_text != 'No insights generated':
            # Parse insights if they contain structured data
            insights_lines = insights_text.split('\n')
            clean_insights = []
            recommendations = []
            
            for line in insights_lines:
                line = line.strip()
                if not line or line.startswith('**') or line.startswith('#'):
                    continue
                    
                # Clean up formatting
                clean_line = line.replace('🎯', '').replace('💡', '').replace('📊', '').replace('**', '').strip()
                
                if any(keyword in clean_line.lower() for keyword in ['recommend', 'suggest', 'should', 'consider']):
                    recommendations.append(clean_line)
                elif clean_line and not clean_line.startswith('•'):
                    clean_insights.append(clean_line)
            
            # If we couldn't parse structured insights, use the full text
            if not clean_insights and not recommendations:
                clean_insights = [insights_text]
            
            formatted_output += "\n\n" + self.formatter.create_insights_section(clean_insights, recommendations)
        
        # 5. Analysis warnings
        if self.warnings:
            formatted_output += "\n\n⚠️ **ANALYSIS NOTES:**\n"
            for warning in self.warnings:
                formatted_output += f"• {warning}\n"
        
        return formatted_output
