"""
Contributor Analyzer for VariancePro
Implements 80/20 Pareto analysis for identifying key contributors
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, Tuple, List
from .base_analyzer import BaseAnalyzer, AnalysisError


class ContributorAnalyzer(BaseAnalyzer):
    """
    Analyzer for contribution analysis using 80/20 Pareto principle
    Identifies top contributors to revenue, sales, or other metrics
    """
    
    def __init__(self, settings):
        """
        Initialize contributor analyzer
        
        Args:
            settings: Application settings instance
        """
        super().__init__(settings)
        self.analysis_type = "contribution"
        self.threshold = settings.contribution_threshold  # Default 0.8 for 80/20
    
    def analyze(self, data: pd.DataFrame, 
                category_col: str, 
                value_col: str, 
                time_col: Optional[str] = None,
                threshold: Optional[float] = None,
                **kwargs) -> Dict[str, Any]:
        """
        Perform contribution analysis
        
        Args:
            data: Input DataFrame
            category_col: Column name for categories (e.g., Product, Customer)
            value_col: Column name for values (e.g., Sales, Revenue)
            time_col: Optional time column for time-based filtering
            threshold: Contribution threshold (default from settings)
            
        Returns:
            Dictionary with analysis results
            
        Raises:
            AnalysisError: If analysis fails
        """
        try:
            # Reset state
            self.reset()
            self.data = data.copy()
            
            # Validate inputs
            self.validate_data(data)
            self.validate_columns(data, [category_col, value_col])
            self.validate_numeric_columns(data, [value_col])
            
            # Set threshold
            if threshold is not None:
                self.threshold = threshold
            
            # Clean data
            analysis_data = self._prepare_data(data, category_col, value_col, time_col)
            
            # Perform contribution analysis
            contribution_results = self._calculate_contributions(analysis_data, category_col, value_col)
            
            # Calculate Pareto analysis
            pareto_results = self._calculate_pareto(contribution_results, self.threshold)
            
            # Generate insights
            insights = self._generate_insights(contribution_results, pareto_results, category_col, value_col)
            
            # Store results
            self.results = {
                'contribution_data': contribution_results,
                'pareto_analysis': pareto_results,
                'insights': insights,
                'parameters': {
                    'category_col': category_col,
                    'value_col': value_col,
                    'time_col': time_col,
                    'threshold': self.threshold,
                    'data_rows': len(analysis_data),
                    'unique_categories': len(analysis_data[category_col].unique())
                }
            }
            
            self.status = "completed"
            return self.results
            
        except Exception as e:
            self.status = "failed"
            self.errors.append(str(e))
            if isinstance(e, AnalysisError):
                raise
            raise AnalysisError(f"Contribution analysis failed: {str(e)}")
    
    def _prepare_data(self, data: pd.DataFrame, category_col: str, value_col: str, time_col: Optional[str]) -> pd.DataFrame:
        """
        Prepare data for analysis
        
        Args:
            data: Input DataFrame
            category_col: Category column name
            value_col: Value column name
            time_col: Optional time column name
            
        Returns:
            Prepared DataFrame
        """
        # Start with copy of data
        prepared_data = data.copy()
        
        # Handle time-based filtering if time column provided
        if time_col and time_col in data.columns:
            # Try to convert time column to datetime
            try:
                prepared_data[time_col] = pd.to_datetime(prepared_data[time_col])
                
                # If timescale auto-detect is enabled, use most recent period
                if self.settings.timescale_auto_detect:
                    # Get the most recent 12 months or most recent period
                    max_date = prepared_data[time_col].max()
                    cutoff_date = max_date - pd.DateOffset(months=12)
                    
                    recent_data = prepared_data[prepared_data[time_col] >= cutoff_date]
                    if len(recent_data) > 0:
                        prepared_data = recent_data
                        self.warnings.append(
                            f"Using recent 12-month period for analysis: "
                            f"{cutoff_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}"
                        )
                    
            except Exception as e:
                self.warnings.append(f"Could not process time column '{time_col}': {str(e)}")
        
        # Clean numeric data
        prepared_data = self.clean_numeric_data(prepared_data, [value_col])
        
        # Remove rows with missing category or value data
        initial_rows = len(prepared_data)
        prepared_data = prepared_data.dropna(subset=[category_col, value_col])
        
        if len(prepared_data) < initial_rows:
            self.warnings.append(
                f"Removed {initial_rows - len(prepared_data)} rows with missing data"
            )
        
        # Remove rows with zero or negative values (for contribution analysis)
        positive_data = prepared_data[prepared_data[value_col] > 0]
        if len(positive_data) < len(prepared_data):
            removed_count = len(prepared_data) - len(positive_data)
            self.warnings.append(
                f"Removed {removed_count} rows with zero or negative values"
            )
            prepared_data = positive_data
        
        if len(prepared_data) == 0:
            raise AnalysisError("No valid data remaining after cleaning")
        
        return prepared_data
    
    def _calculate_contributions(self, data: pd.DataFrame, category_col: str, value_col: str) -> pd.DataFrame:
        """
        Calculate contribution metrics for each category
        
        Args:
            data: Prepared DataFrame
            category_col: Category column name
            value_col: Value column name
            
        Returns:
            DataFrame with contribution metrics
        """
        # Group by category and sum values
        contribution_data = data.groupby(category_col).agg({
            value_col: ['sum', 'count', 'mean', 'std']
        }).round(2)
        
        # Flatten column names
        contribution_data.columns = ['total_value', 'transaction_count', 'avg_value', 'std_value']
        
        # Calculate percentages
        total_value = contribution_data['total_value'].sum()
        contribution_data['value_percentage'] = (contribution_data['total_value'] / total_value * 100).round(2)
        
        # Sort by total value descending
        contribution_data = contribution_data.sort_values('total_value', ascending=False)
        
        # Calculate cumulative percentage
        contribution_data['cumulative_percentage'] = contribution_data['value_percentage'].cumsum().round(2)
        
        # Add rank
        contribution_data['rank'] = range(1, len(contribution_data) + 1)
        
        # Reset index to make category a column
        contribution_data = contribution_data.reset_index()
        
        return contribution_data
    
    def _calculate_pareto(self, contribution_data: pd.DataFrame, threshold: float) -> Dict[str, Any]:
        """
        Calculate Pareto analysis results
        
        Args:
            contribution_data: DataFrame with contribution metrics
            threshold: Contribution threshold (e.g., 0.8 for 80%)
            
        Returns:
            Dictionary with Pareto analysis results
        """
        threshold_percentage = threshold * 100
        
        # Find contributors that make up the threshold percentage
        top_contributors = contribution_data[
            contribution_data['cumulative_percentage'] <= threshold_percentage
        ]
        
        # If no contributors meet the exact threshold, include the first one that exceeds it
        if len(top_contributors) == 0:
            top_contributors = contribution_data.head(1)
        elif len(top_contributors) < len(contribution_data):
            # Include the next contributor that pushes us over the threshold
            next_index = len(top_contributors)
            if next_index < len(contribution_data):
                top_contributors = contribution_data.head(next_index + 1)
        
        # Calculate metrics
        top_contributor_count = len(top_contributors)
        total_contributors = len(contribution_data)
        top_contributor_percentage = top_contributor_count / total_contributors * 100
        
        actual_value_percentage = top_contributors['value_percentage'].sum()
        
        # Calculate the complement (remaining contributors)
        remaining_contributors = contribution_data.iloc[top_contributor_count:]
        remaining_count = len(remaining_contributors)
        remaining_percentage = remaining_count / total_contributors * 100 if total_contributors > 0 else 0
        remaining_value_percentage = remaining_contributors['value_percentage'].sum() if not remaining_contributors.empty else 0
        
        return {
            'threshold': threshold,
            'threshold_percentage': threshold_percentage,
            'top_contributors': {
                'count': top_contributor_count,
                'percentage_of_total': round(top_contributor_percentage, 1),
                'value_percentage': round(actual_value_percentage, 1),
                'data': top_contributors.to_dict('records')
            },
            'remaining_contributors': {
                'count': remaining_count,
                'percentage_of_total': round(remaining_percentage, 1),
                'value_percentage': round(remaining_value_percentage, 1)
            },
            'pareto_ratio': f"{top_contributor_count}/{total_contributors}",
            'pareto_description': f"Top {top_contributor_count} contributors ({top_contributor_percentage:.1f}%) generate {actual_value_percentage:.1f}% of total value"
        }
    
    def _generate_insights(self, contribution_data: pd.DataFrame, pareto_data: Dict[str, Any], category_col: str, value_col: str) -> Dict[str, Any]:
        """
        Generate business insights from the analysis
        
        Args:
            contribution_data: DataFrame with contribution metrics
            pareto_data: Dictionary with Pareto analysis results
            category_col: Category column name
            value_col: Value column name
            
        Returns:
            Dictionary with insights
        """
        insights = {
            'summary': {},
            'recommendations': [],
            'key_findings': [],
            'risk_factors': []
        }
        
        # Summary insights
        top_contributors = pareto_data['top_contributors']
        total_value = contribution_data['total_value'].sum()
        
        insights['summary'] = {
            'analysis_type': f"80/20 Contribution Analysis on {value_col} by {category_col}",
            'total_value': self.format_currency(total_value),
            'total_contributors': len(contribution_data),
            'top_contributor_count': top_contributors['count'],
            'concentration_ratio': f"{top_contributors['value_percentage']:.1f}%"
        }
        
        # Key findings
        if top_contributors['count'] <= 3:
            insights['key_findings'].append(
                f"🎯 **High Concentration**: Just {top_contributors['count']} contributors drive "
                f"{top_contributors['value_percentage']:.1f}% of total {value_col.lower()}"
            )
        
        # Get top performer
        if not contribution_data.empty:
            top_performer = contribution_data.iloc[0]
            insights['key_findings'].append(
                f"🥇 **Top Performer**: {top_performer[category_col]} contributes "
                f"{self.format_currency(top_performer['total_value'])} "
                f"({top_performer['value_percentage']:.1f}% of total)"
            )
        
        # Recommendations
        if top_contributors['percentage_of_total'] < 20:
            insights['recommendations'].append(
                "🎯 **Focus Strategy**: Concentrate resources on your top performers for maximum impact"
            )
        
        if top_contributors['value_percentage'] > 80:
            insights['recommendations'].append(
                "⚠️ **Diversification**: Consider diversifying to reduce dependency on key contributors"
            )
            
            insights['risk_factors'].append(
                "High concentration risk - significant portion of value comes from few contributors"
            )
        
        # Performance gap analysis
        if len(contribution_data) >= 2:
            top_value = contribution_data.iloc[0]['total_value']
            second_value = contribution_data.iloc[1]['total_value']
            gap_ratio = top_value / second_value if second_value > 0 else float('inf')
            
            if gap_ratio > 2:
                insights['key_findings'].append(
                    f"📊 **Performance Gap**: Top performer is {gap_ratio:.1f}x larger than second place"
                )
        
        # Long tail analysis
        bottom_20_percent = int(len(contribution_data) * 0.2)
        if bottom_20_percent > 0:
            bottom_contributors = contribution_data.tail(bottom_20_percent)
            bottom_value_percentage = bottom_contributors['value_percentage'].sum()
            
            if bottom_value_percentage < 5:
                insights['recommendations'].append(
                    f"🧹 **Optimization Opportunity**: Bottom 20% of contributors generate only "
                    f"{bottom_value_percentage:.1f}% of value - consider resource reallocation"
                )
        
        return insights
    
    def format_for_chat(self) -> str:
        """
        Format analysis results for chat display
        
        Returns:
            Formatted string for chat interface
        """
        if self.status != "completed" or not self.results:
            return "❌ **Analysis not completed or failed**"
        
        results = self.results
        insights = results['insights']
        pareto = results['pareto_analysis']
        params = results['parameters']
        
        # Build chat response
        response_parts = [
            "📊 **CONTRIBUTION ANALYSIS RESULTS (80/20 Pareto Principle)**",
            "",
            f"**Analysis**: {insights['summary']['analysis_type']}",
            f"**Total Value**: {insights['summary']['total_value']}",
            f"**Contributors Analyzed**: {insights['summary']['total_contributors']:,}",
            "",
            "🎯 **KEY FINDINGS**:"
        ]
        
        # Add key findings
        for finding in insights['key_findings']:
            response_parts.append(f"• {finding}")
        
        response_parts.append("")
        response_parts.append("📈 **PARETO ANALYSIS**:")
        response_parts.append(f"• **Top {pareto['top_contributors']['count']} contributors** ({pareto['top_contributors']['percentage_of_total']:.1f}% of total)")
        response_parts.append(f"• **Generate {pareto['top_contributors']['value_percentage']:.1f}% of total value**")
        response_parts.append(f"• **Remaining {pareto['remaining_contributors']['count']} contributors** generate {pareto['remaining_contributors']['value_percentage']:.1f}% of value")
        
        # Add top contributors table
        if pareto['top_contributors']['data']:
            response_parts.append("")
            response_parts.append("🏆 **TOP CONTRIBUTORS**:")
            
            for i, contributor in enumerate(pareto['top_contributors']['data'][:5], 1):  # Show top 5
                response_parts.append(
                    f"{i}. **{contributor[params['category_col']]}**: "
                    f"{self.format_currency(contributor['total_value'])} "
                    f"({contributor['value_percentage']:.1f}%)"
                )
        
        # Add recommendations
        if insights['recommendations']:
            response_parts.append("")
            response_parts.append("💡 **RECOMMENDATIONS**:")
            for rec in insights['recommendations']:
                response_parts.append(f"• {rec}")
        
        # Add warnings if any
        if self.warnings:
            response_parts.append("")
            response_parts.append("⚠️ **ANALYSIS NOTES**:")
            for warning in self.warnings:
                response_parts.append(f"• {warning}")
        
        return "\n".join(response_parts)
