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
        """Generate natural language insights with proper bullet formatting"""
        insights = []
        
        # Add header
        insights.append("📈 **AUTOMATIC TIMESCALE ANALYSIS**")
        insights.append("")
        insights.append("🎯 **Analysis Overview**")
        insights.append("   • Comprehensive time-series analysis across multiple periods")
        insights.append("   • Period-over-period growth calculations")
        insights.append("   • Trend identification and pattern analysis")
        insights.append("")
        
        # Process each time scale
        for time_scale in ["yearly", "quarterly", "monthly", "weekly"]:
            if time_scale not in pop_analysis or not pop_analysis[time_scale]:
                continue
                
            # Add section header
            header_map = {
                "yearly": "📊 **YEARLY ANALYSIS** - Year-over-Year (YoY)",
                "quarterly": "📊 **QUARTERLY ANALYSIS** - Quarter-over-Quarter (QoQ)", 
                "monthly": "📊 **MONTHLY ANALYSIS** - Month-over-Month (MoM)",
                "weekly": "📊 **WEEKLY ANALYSIS** - Week-over-Week (WoW)"
            }
            insights.append(header_map[time_scale])
            insights.append("")
            
            # Process each metric
            for metric, data in pop_analysis[time_scale].items():
                summary = data["summary"]
                periods = data["periods"]
                
                # Only process if we have enough data
                if summary["total_periods"] < 2:
                    insights.append(f"   • {metric.replace('_', ' ').title()}: Insufficient {time_scale[:-2]} data for analysis")
                    insights.append("")
                    continue
                
                # Metric name and details
                metric_name = metric.replace('_', ' ').title()
                insights.append(f"   • **{metric_name}**")
                
                # Latest period change
                latest_period = periods[-1] if periods else "Unknown"
                latest_change = summary["latest_change"]
                if pd.notna(latest_change):
                    change_direction = "increased" if latest_change > 0 else "decreased"
                    direction_icon = "↗️" if latest_change > 0 else "↘️"
                    insights.append(f"     • Latest {time_scale[:-2]} ({latest_period}): {direction_icon} {change_direction} by {abs(latest_change):.2f}%")
                
                # Overall trend
                trend_ratio = summary["positive_periods"] / max(summary["total_periods"] - 1, 1)
                if trend_ratio > 0.6:
                    trend = "📈 mostly increasing"
                elif trend_ratio < 0.4:
                    trend = "📉 mostly decreasing"
                else:
                    trend = "🔄 fluctuating"
                
                insights.append(f"     • Overall trend: {trend} over {summary['total_periods']} periods")
                
                # Extreme periods
                if summary["max_pct_change"] > 0:
                    try:
                        max_idx = data["pct_changes"].index(summary["max_pct_change"])
                        max_period = periods[max_idx] if max_idx < len(periods) else "Unknown"
                        insights.append(f"     • Largest increase: +{summary['max_pct_change']:.2f}% in {max_period}")
                    except:
                        insights.append(f"     • Largest increase: +{summary['max_pct_change']:.2f}%")
                
                if summary["min_pct_change"] < 0:
                    try:
                        min_idx = data["pct_changes"].index(summary["min_pct_change"])
                        min_period = periods[min_idx] if min_idx < len(periods) else "Unknown"
                        insights.append(f"     • Largest decrease: {summary['min_pct_change']:.2f}% in {min_period}")
                    except:
                        insights.append(f"     • Largest decrease: {summary['min_pct_change']:.2f}%")
                
                # Average change
                time_unit = time_scale[:-2] if time_scale.endswith('ly') else time_scale
                avg_change = summary['avg_pct_change']
                avg_icon = "📊" if abs(avg_change) < 5 else "⚡" if abs(avg_change) > 20 else "📈" if avg_change > 0 else "📉"
                insights.append(f"     • Average change: {avg_icon} {avg_change:.2f}% per {time_unit}")
                insights.append("")
        
        # Executive summary
        insights.append("🔍 **EXECUTIVE SUMMARY**")
        insights.append("")
        insights.append("📋 **KEY FINDINGS:**")
        insights.append("")
        
        # Generate dynamic summary based on available data
        has_data = any(pop_analysis.get(ts) for ts in ["yearly", "quarterly", "monthly", "weekly"])
        
        if has_data:
            # Find the most significant trends
            significant_trends = []
            
            for time_scale in ["yearly", "quarterly", "monthly", "weekly"]:
                if time_scale in pop_analysis and pop_analysis[time_scale]:
                    for metric, data in pop_analysis[time_scale].items():
                        summary = data["summary"]
                        if summary.get("total_periods", 0) >= 2:
                            latest_change = summary.get("latest_change")
                            if latest_change and abs(latest_change) > 10:  # Significant change threshold
                                trend_desc = f"{metric.replace('_', ' ').title()}"
                                time_period = time_scale[:-2].title()
                                direction = "📈 Strong growth" if latest_change > 0 else "📉 Declining performance"
                                significant_trends.append(f"   • **{trend_desc}** ({time_period}): {direction} ({latest_change:+.1f}%)")
            
            if significant_trends:
                insights.extend(significant_trends)
            else:
                insights.append("   • **Performance Stability**: Overall patterns show consistent trends across time periods")
                insights.append("   • **Volatility Assessment**: No significant fluctuations detected in recent periods")
        else:
            insights.append("   • **Data Limitation**: Insufficient time series data for comprehensive trend analysis")
            insights.append("   • **Recommendation**: Consider collecting data over longer periods for better insights")
        
        insights.append("")
        insights.append("💡 **RECOMMENDATIONS:**")
        insights.append("")
        insights.append("   • **Monitoring Strategy**: Track period-over-period changes for early trend detection")
        insights.append("   • **Focus Areas**: Prioritize metrics showing consistent directional movement")
        insights.append("   • **Investigation Targets**: Analyze periods with extreme positive or negative changes")
        insights.append("   • **Strategic Planning**: Use trend patterns to inform forward-looking business decisions")
        
        return "\n".join(insights)
    
    def format_for_chat(self) -> str:
        """
        Format analysis results for chat display with AI summary and collapsible details
        
        Returns:
            Formatted string for chat interface with summary and expandable details
        """
        if self.status != "completed" or not self.results:
            return "❌ **Analysis not completed or failed**"

        # Get the detailed analysis first
        detailed_analysis = self._generate_detailed_analysis()
        
        # Generate AI summary of the detailed analysis
        ai_summary = self._generate_ai_summary(detailed_analysis)
        
        # Create collapsible output with summary first, then details
        output = []
        output.append("📈 **TIMESCALE ANALYSIS SUMMARY**")
        output.append("")
        output.append("🎯 **Key Findings:**")
        output.append(ai_summary)
        output.append("")
        output.append("---")
        output.append("📊 **DETAILED ANALYSIS** *(Click to expand below)*")
        output.append("")
        output.append(detailed_analysis)
        
        return "\n".join(output)
    
    def _generate_detailed_analysis(self) -> str:
        """
        Generate the detailed analysis (original format_for_chat logic)
        
        Returns:
            Detailed formatted analysis
        """
        # Use the raw insights directly if available - they're already properly formatted
        insights_text = self.results.get('insights', '')
        if insights_text:
            return insights_text
        
        # Fallback formatting if no insights are available
        data = self.results.get('data', {})
        parameters = self.results.get('parameters', {})
        
        output = []
        output.append("📈 **DETAILED TIMESCALE ANALYSIS**")
        output.append("")
        output.append("🎯 **Analysis Overview**")
        output.append(f"   • Date Column: {parameters.get('date_col', 'N/A')}")
        output.append(f"   • Value Columns: {', '.join(parameters.get('value_cols', []))}")
        output.append(f"   • Data Range: {parameters.get('date_range', 'N/A')}")
        output.append(f"   • Total Records: {parameters.get('data_rows', 'N/A'):,}")
        output.append("")
        
        # Add timescale summaries
        for timescale in ["yearly", "quarterly", "monthly", "weekly"]:
            if timescale in data and data[timescale]:
                output.append(f"📊 **{timescale.upper()} ANALYSIS**")
                
                for metric, metric_data in data[timescale].items():
                    summary = metric_data.get('summary', {})
                    if summary:
                        output.append(f"   • {metric.replace('_', ' ').title()}")
                        output.append(f"     • Total Periods: {summary.get('total_periods', 'N/A')}")
                        if summary.get('latest_change') is not None:
                            change = summary['latest_change']
                            direction = "↗️" if change > 0 else "↘️" if change < 0 else "→"
                            output.append(f"     • Latest Change: {direction} {change:.1f}%")
                        if summary.get('avg_pct_change') is not None:
                            output.append(f"     • Average Change: {summary['avg_pct_change']:.1f}%")
                output.append("")
        
        return "\n".join(output)
    
    def _generate_ai_summary(self, detailed_analysis: str) -> str:
        """
        Generate AI summary of the detailed timescale analysis
        
        Args:
            detailed_analysis: The full detailed analysis text
            
        Returns:
            AI-generated summary paragraph
        """
        try:
            # Import LLM interpreter
            from ai.llm_interpreter import LLMInterpreter
            from config.settings import Settings
            
            # Create LLM interpreter instance with proper settings
            settings = Settings()
            llm = LLMInterpreter(settings)
            
            # Create prompt for summary generation
            summary_prompt = f"""
            Analyze the following timescale analysis results and provide a concise summary paragraph. Write exactly 2 sentences for each time period analyzed (quarterly, monthly, weekly). Each sentence should combine commentary with specific numerical facts from the data. Format as a flowing paragraph with no bullets or lists. Be concise but comprehensive.

            Guidelines:
            - Include specific percentage changes, trends, and numerical data
            - Provide business context and implications
            - Write in paragraph format (no bullets, lists, or headers)
            - Be factual and data-driven while maintaining readability
            - Be concise but include all relevant numerical insights

            Timescale Analysis Results:
            {detailed_analysis}

            Concise summary paragraph:
            """
            
            # Query the LLM for summary
            response = llm.query_llm(summary_prompt)
            
            if response.success and response.content:
                # Clean up the response and format nicely
                summary = response.content.strip()
                # Remove any "Summary:" prefix if the LLM added it
                if summary.lower().startswith('summary:'):
                    summary = summary[8:].strip()
                if summary.lower().startswith('summary paragraph:'):
                    summary = summary[18:].strip()
                
                return summary
            else:
                # Fallback to basic summary if LLM fails
                return self._generate_basic_summary()
                
        except Exception as e:
            print(f"[TIMESCALE] AI summary generation failed: {str(e)}")
            # Fallback to basic summary
            return self._generate_basic_summary()
    
    def _generate_basic_summary(self) -> str:
        """
        Generate a basic summary when AI summary fails
        
        Returns:
            Basic summary text with numerical facts
        """
        try:
            data = self.results.get('data', {})
            parameters = self.results.get('parameters', {})
            
            # Extract key metrics for basic summary
            value_cols = parameters.get('value_cols', [])
            summary_parts = []
            
            # Look for trends across different timescales
            for timescale in ["quarterly", "monthly", "weekly"]:
                if timescale in data:
                    timescale_trends = []
                    for metric, metric_data in data[timescale].items():
                        summary = metric_data.get('summary', {})
                        if summary.get('latest_change') is not None:
                            change = summary['latest_change']
                            direction = "increased" if change > 0 else "decreased" if change < 0 else "remained stable"
                            timescale_trends.append(f"{metric.replace('_', ' ')} {direction} by {abs(change):.1f}%")
                    
                    if timescale_trends:
                        trend_text = f"On a {timescale} basis, {' and '.join(timescale_trends[:2])}"
                        summary_parts.append(trend_text)
            
            if summary_parts:
                return f"{' '.join(summary_parts)}. These trends indicate significant volatility requiring management attention across multiple time horizons."
            else:
                return f"Analysis completed for {len(value_cols)} metrics showing various trend patterns across quarterly, monthly, and weekly timeframes with detailed breakdowns available for strategic planning."
            
        except Exception as e:
            return "Timescale analysis completed with comprehensive trend insights and numerical data available in the detailed view below."
