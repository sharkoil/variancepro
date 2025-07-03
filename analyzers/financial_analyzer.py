"""
Financial Analyzer for VariancePro
Implements TTM and budget vs actual variance analysis
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List, Tuple, Union
from datetime import datetime, timedelta
from .base_analyzer import BaseAnalyzer, AnalysisError


class FinancialAnalyzer(BaseAnalyzer):
    """
    Financial analyzer for time-based financial analysis
    Provides TTM (Trailing Twelve Months) and variance analysis
    """
    
    def __init__(self, settings):
        """
        Initialize financial analyzer
        
        Args:
            settings: Application settings instance
        """
        super().__init__(settings)
        self.analysis_type = "financial"
        self.date_formats = [
            '%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y%m%d',
            '%b %Y', '%B %Y', '%Y-%m', '%m-%Y', '%Y/%m'
        ]
    
    def analyze(self, data: pd.DataFrame, 
                date_col: str,
                value_col: str,
                category_col: Optional[str] = None,
                budget_col: Optional[str] = None,
                analysis_type: str = "ttm",
                **kwargs) -> Dict[str, Any]:
        """
        Perform financial analysis
        
        Args:
            data: Input DataFrame
            date_col: Date column name
            value_col: Value column name (e.g., Sales, Revenue)
            category_col: Optional category column for segmentation
            budget_col: Optional budget column for variance analysis
            analysis_type: Analysis type ('ttm', 'variance', 'trend')
            
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
            self.validate_columns(data, [date_col, value_col])
            self.validate_numeric_columns(data, [value_col])
            
            if budget_col:
                self.validate_columns(data, [budget_col])
                self.validate_numeric_columns(data, [budget_col])
            
            # Process data
            analysis_data = self._prepare_data(data, date_col, value_col, budget_col)
            
            # Select analysis type
            if analysis_type == "ttm":
                results = self._calculate_ttm(analysis_data, date_col, value_col, category_col)
            elif analysis_type == "variance":
                if not budget_col:
                    raise AnalysisError("Budget column required for variance analysis")
                results = self._calculate_variance(analysis_data, date_col, value_col, budget_col, category_col)
            elif analysis_type == "trend":
                results = self._calculate_trend(analysis_data, date_col, value_col, category_col)
            else:
                raise AnalysisError(f"Unknown analysis type: {analysis_type}")
            
            # Generate insights
            insights = self._generate_insights(results, analysis_type)
            
            # Store results
            self.results = {
                'analysis_type': analysis_type,
                'data': results['data'],
                'metrics': results['metrics'],
                'insights': insights,
                'parameters': {
                    'date_col': date_col,
                    'value_col': value_col,
                    'category_col': category_col,
                    'budget_col': budget_col,
                    'data_rows': len(analysis_data),
                    'date_range': results.get('date_range', '')
                }
            }
            
            self.status = "completed"
            return self.results
            
        except Exception as e:
            self.status = "failed"
            self.errors.append(str(e))
            if isinstance(e, AnalysisError):
                raise
            raise AnalysisError(f"Financial analysis failed: {str(e)}")
    
    def _prepare_data(self, data: pd.DataFrame, date_col: str, value_col: str, budget_col: Optional[str] = None) -> pd.DataFrame:
        """
        Prepare data for financial analysis
        
        Args:
            data: Input DataFrame
            date_col: Date column name
            value_col: Value column name
            budget_col: Optional budget column name
            
        Returns:
            Prepared DataFrame
        """
        # Start with copy of data
        prepared_data = data.copy()
        
        # Convert date column to datetime
        prepared_data = self._convert_date_column(prepared_data, date_col)
        
        # Clean numeric data
        numeric_cols = [value_col]
        if budget_col:
            numeric_cols.append(budget_col)
        
        prepared_data = self.clean_numeric_data(prepared_data, numeric_cols)
        
        # Remove rows with missing values in key columns
        initial_rows = len(prepared_data)
        prepared_data = prepared_data.dropna(subset=[date_col, value_col])
        
        if budget_col:
            # For variance analysis, keep only rows with budget values
            prepared_data = prepared_data.dropna(subset=[budget_col])
        
        if len(prepared_data) < initial_rows:
            self.warnings.append(
                f"Removed {initial_rows - len(prepared_data)} rows with missing data"
            )
        
        if len(prepared_data) == 0:
            raise AnalysisError("No valid data remaining after cleaning")
        
        return prepared_data
    
    def _convert_date_column(self, data: pd.DataFrame, date_col: str) -> pd.DataFrame:
        """
        Convert date column to datetime
        
        Args:
            data: Input DataFrame
            date_col: Date column name
            
        Returns:
            DataFrame with converted date column
            
        Raises:
            AnalysisError: If date conversion fails
        """
        # If already datetime, return as is
        if pd.api.types.is_datetime64_any_dtype(data[date_col]):
            return data
        
        # Try parsing the date column
        for date_format in self.date_formats:
            try:
                data[date_col] = pd.to_datetime(data[date_col], format=date_format)
                self.warnings.append(f"Converted '{date_col}' to datetime using format '{date_format}'")
                return data
            except:
                continue
        
        # If none of the specific formats worked, try pandas default parser
        try:
            data[date_col] = pd.to_datetime(data[date_col], errors='coerce')
            missing_dates = data[date_col].isna().sum()
            
            if missing_dates > 0:
                self.warnings.append(
                    f"Could not parse {missing_dates} dates in '{date_col}'. "
                    f"These rows will be excluded from analysis."
                )
            
            if missing_dates / len(data) > 0.5:
                raise AnalysisError(
                    f"More than 50% of dates in '{date_col}' could not be parsed. "
                    f"Please check the date format."
                )
            
            return data
        except Exception as e:
            if isinstance(e, AnalysisError):
                raise
                
            raise AnalysisError(
                f"Could not convert '{date_col}' to dates. "
                f"Please ensure this column contains valid dates."
            )
    
    def _calculate_ttm(self, data: pd.DataFrame, date_col: str, value_col: str, category_col: Optional[str] = None) -> Dict[str, Any]:
        """
        Calculate Trailing Twelve Months (TTM) analysis
        
        Args:
            data: Prepared DataFrame
            date_col: Date column name
            value_col: Value column name
            category_col: Optional category column
            
        Returns:
            Dictionary with TTM analysis results
        """
        # Ensure date column is datetime
        data[date_col] = pd.to_datetime(data[date_col])
        
        # Get date range
        min_date = data[date_col].min()
        max_date = data[date_col].max()
        
        # Calculate months in data
        months_in_data = (max_date.year - min_date.year) * 12 + max_date.month - min_date.month + 1
        
        # Check if we have enough data
        if months_in_data < 12:
            self.warnings.append(
                f"Data spans only {months_in_data} months. "
                f"TTM analysis typically requires at least 12 months of data."
            )
        
        # Create month-level aggregation
        data['year_month'] = data[date_col].dt.to_period('M')
        
        # Group by year-month and optional category
        if category_col:
            monthly_data = data.groupby(['year_month', category_col]).agg({
                value_col: 'sum'
            }).reset_index()
        else:
            monthly_data = data.groupby('year_month').agg({
                value_col: 'sum'
            }).reset_index()
        
        # Convert year_month to datetime (first day of month)
        monthly_data['date'] = monthly_data['year_month'].dt.to_timestamp()
        
        # Sort by date
        monthly_data = monthly_data.sort_values('date')
        
        # Calculate rolling 12-month sum (TTM)
        if category_col:
            ttm_data = monthly_data.groupby(category_col).apply(
                lambda x: x.set_index('date')[value_col].rolling('365D').sum()
            ).reset_index()
            ttm_data.columns = [category_col, 'date', f'{value_col}_ttm']
        else:
            ttm_data = pd.DataFrame({
                'date': monthly_data['date'],
                f'{value_col}_ttm': monthly_data.set_index('date')[value_col].rolling('365D').sum().values
            })
        
        # Filter out rows with NaN TTM (first 11 months)
        ttm_data = ttm_data.dropna()
        
        # Calculate YoY growth rate if we have enough data
        if len(ttm_data) >= 13:
            # Calculate year-over-year TTM growth
            ttm_data['date_shifted'] = ttm_data['date'] - pd.DateOffset(years=1)
            
            # Merge current TTM with TTM from a year ago
            if category_col:
                ttm_yoy = ttm_data.merge(
                    ttm_data[[category_col, 'date', f'{value_col}_ttm']],
                    left_on=[category_col, 'date_shifted'],
                    right_on=[category_col, 'date'],
                    suffixes=('', '_prev')
                )
            else:
                ttm_yoy = ttm_data.merge(
                    ttm_data[['date', f'{value_col}_ttm']],
                    left_on='date_shifted',
                    right_on='date',
                    suffixes=('', '_prev')
                )
            
            # Calculate growth rate
            ttm_yoy[f'{value_col}_growth'] = (
                (ttm_yoy[f'{value_col}_ttm'] - ttm_yoy[f'{value_col}_ttm_prev']) / 
                ttm_yoy[f'{value_col}_ttm_prev']
            ) * 100
            
            # Clean up merged dataframe
            if category_col:
                ttm_yoy = ttm_yoy[[category_col, 'date_x', f'{value_col}_ttm', f'{value_col}_ttm_prev', f'{value_col}_growth']]
                ttm_yoy.columns = [category_col, 'date', f'{value_col}_ttm', f'{value_col}_ttm_prev', f'{value_col}_growth']
            else:
                ttm_yoy = ttm_yoy[['date_x', f'{value_col}_ttm', f'{value_col}_ttm_prev', f'{value_col}_growth']]
                ttm_yoy.columns = ['date', f'{value_col}_ttm', f'{value_col}_ttm_prev', f'{value_col}_growth']
            
            final_ttm_data = ttm_yoy
        else:
            # Not enough data for YoY comparison
            self.warnings.append(
                "Not enough data for year-over-year growth calculation. "
                "At least 24 months of data is required."
            )
            final_ttm_data = ttm_data.drop('date_shifted', axis=1, errors='ignore')
        
        # Calculate metrics
        current_ttm = final_ttm_data.iloc[-1][f'{value_col}_ttm']
        
        metrics = {
            'current_ttm': float(current_ttm),
            'current_ttm_formatted': self.formatter.format_currency(current_ttm),
            'ttm_periods': len(final_ttm_data),
            'date_range': f"{min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}",
            'months_covered': months_in_data
        }
        
        # Add growth metrics if available
        if f'{value_col}_growth' in final_ttm_data.columns:
            current_growth = final_ttm_data.iloc[-1][f'{value_col}_growth']
            metrics.update({
                'current_growth': float(current_growth),
                'current_growth_formatted': self.formatter.format_percentage(current_growth / 100),
                'max_growth': float(final_ttm_data[f'{value_col}_growth'].max()),
                'min_growth': float(final_ttm_data[f'{value_col}_growth'].min()),
                'avg_growth': float(final_ttm_data[f'{value_col}_growth'].mean())
            })
        
        # Format for response
        if category_col:
            result_data = []
            for category, group in final_ttm_data.groupby(category_col):
                group_data = group.sort_values('date')
                group_dict = {
                    'category': category,
                    'dates': group_data['date'].dt.strftime('%Y-%m').tolist(),
                    'ttm_values': group_data[f'{value_col}_ttm'].tolist()
                }
                
                if f'{value_col}_growth' in group_data.columns:
                    group_dict['growth_values'] = group_data[f'{value_col}_growth'].tolist()
                
                result_data.append(group_dict)
        else:
            # Overall TTM series
            result_data = {
                'dates': final_ttm_data['date'].dt.strftime('%Y-%m').tolist(),
                'ttm_values': final_ttm_data[f'{value_col}_ttm'].tolist()
            }
            
            if f'{value_col}_growth' in final_ttm_data.columns:
                result_data['growth_values'] = final_ttm_data[f'{value_col}_growth'].tolist()
        
        return {
            'data': result_data,
            'metrics': metrics,
            'date_range': f"{min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}"
        }
    
    def _calculate_variance(self, data: pd.DataFrame, date_col: str, actual_col: str, budget_col: str, category_col: Optional[str] = None) -> Dict[str, Any]:
        """
        Calculate budget vs actual variance analysis
        
        Args:
            data: Prepared DataFrame
            date_col: Date column name
            actual_col: Actual value column name
            budget_col: Budget value column name
            category_col: Optional category column
            
        Returns:
            Dictionary with variance analysis results
        """
        # Ensure date column is datetime
        data[date_col] = pd.to_datetime(data[date_col])
        
        # Get date range
        min_date = data[date_col].min()
        max_date = data[date_col].max()
        
        # Create month-level aggregation
        data['year_month'] = data[date_col].dt.to_period('M')
        
        # Calculate variance
        data['variance'] = data[actual_col] - data[budget_col]
        data['variance_pct'] = (data['variance'] / data[budget_col]) * 100
        
        # Group by year-month and optional category
        if category_col:
            grouped_data = data.groupby(['year_month', category_col]).agg({
                actual_col: 'sum',
                budget_col: 'sum',
                'variance': 'sum',
                'variance_pct': 'mean'  # Average percentage variance
            }).reset_index()
        else:
            grouped_data = data.groupby('year_month').agg({
                actual_col: 'sum',
                budget_col: 'sum',
                'variance': 'sum',
                'variance_pct': 'mean'  # Average percentage variance
            }).reset_index()
        
        # Convert year_month to datetime (first day of month)
        grouped_data['date'] = grouped_data['year_month'].dt.to_timestamp()
        
        # Sort by date
        grouped_data = grouped_data.sort_values('date')
        
        # Calculate overall metrics
        total_actual = data[actual_col].sum()
        total_budget = data[budget_col].sum()
        total_variance = total_actual - total_budget
        total_variance_pct = (total_variance / total_budget) * 100 if total_budget != 0 else 0
        
        # Find periods with largest variance
        largest_over = grouped_data[grouped_data['variance'] > 0].sort_values('variance', ascending=False).head(3)
        largest_under = grouped_data[grouped_data['variance'] < 0].sort_values('variance').head(3)
        
        metrics = {
            'total_actual': float(total_actual),
            'total_actual_formatted': self.formatter.format_currency(total_actual),
            'total_budget': float(total_budget),
            'total_budget_formatted': self.formatter.format_currency(total_budget),
            'total_variance': float(total_variance),
            'total_variance_formatted': self.formatter.format_currency(total_variance),
            'total_variance_pct': float(total_variance_pct),
            'total_variance_pct_formatted': self.formatter.format_percentage(total_variance_pct / 100),
            'periods_over_budget': int((grouped_data['variance'] > 0).sum()),
            'periods_under_budget': int((grouped_data['variance'] < 0).sum()),
            'variance_trend': 'improving' if grouped_data['variance_pct'].iloc[-3:].mean() > 
                                           grouped_data['variance_pct'].iloc[:3].mean() else 'worsening',
            'date_range': f"{min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}"
        }
        
        # Format for response
        if category_col:
            result_data = []
            for category, group in grouped_data.groupby(category_col):
                group_data = group.sort_values('date')
                
                cat_total_actual = group_data[actual_col].sum()
                cat_total_budget = group_data[budget_col].sum()
                cat_total_variance = cat_total_actual - cat_total_budget
                cat_total_variance_pct = (cat_total_variance / cat_total_budget) * 100 if cat_total_budget != 0 else 0
                
                result_data.append({
                    'category': category,
                    'dates': group_data['date'].dt.strftime('%Y-%m').tolist(),
                    'actual_values': group_data[actual_col].tolist(),
                    'budget_values': group_data[budget_col].tolist(),
                    'variance_values': group_data['variance'].tolist(),
                    'variance_pct_values': group_data['variance_pct'].tolist(),
                    'total_actual': float(cat_total_actual),
                    'total_budget': float(cat_total_budget),
                    'total_variance': float(cat_total_variance),
                    'total_variance_pct': float(cat_total_variance_pct)
                })
        else:
            # Overall variance series
            result_data = {
                'dates': grouped_data['date'].dt.strftime('%Y-%m').tolist(),
                'actual_values': grouped_data[actual_col].tolist(),
                'budget_values': grouped_data[budget_col].tolist(),
                'variance_values': grouped_data['variance'].tolist(),
                'variance_pct_values': grouped_data['variance_pct'].tolist()
            }
        
        # Add largest variances
        top_variances = []
        
        for _, row in largest_over.iterrows():
            period = row['date'].strftime('%Y-%m')
            variance = float(row['variance'])
            variance_pct = float(row['variance_pct'])
            
            if category_col:
                category = row[category_col]
                top_variances.append({
                    'period': period,
                    'category': category,
                    'variance': variance,
                    'variance_formatted': self.formatter.format_currency(variance),
                    'variance_pct': variance_pct,
                    'variance_pct_formatted': self.formatter.format_percentage(variance_pct / 100),
                    'type': 'over_budget'
                })
            else:
                top_variances.append({
                    'period': period,
                    'variance': variance,
                    'variance_formatted': self.formatter.format_currency(variance),
                    'variance_pct': variance_pct,
                    'variance_pct_formatted': self.formatter.format_percentage(variance_pct / 100),
                    'type': 'over_budget'
                })
        
        for _, row in largest_under.iterrows():
            period = row['date'].strftime('%Y-%m')
            variance = float(row['variance'])
            variance_pct = float(row['variance_pct'])
            
            if category_col:
                category = row[category_col]
                top_variances.append({
                    'period': period,
                    'category': category,
                    'variance': variance,
                    'variance_formatted': self.formatter.format_currency(variance),
                    'variance_pct': variance_pct,
                    'variance_pct_formatted': self.formatter.format_percentage(variance_pct / 100),
                    'type': 'under_budget'
                })
            else:
                top_variances.append({
                    'period': period,
                    'variance': variance,
                    'variance_formatted': self.formatter.format_currency(variance),
                    'variance_pct': variance_pct,
                    'variance_pct_formatted': self.formatter.format_percentage(variance_pct / 100),
                    'type': 'under_budget'
                })
        
        return {
            'data': result_data,
            'metrics': metrics,
            'top_variances': top_variances,
            'date_range': f"{min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}"
        }
    
    def _calculate_trend(self, data: pd.DataFrame, date_col: str, value_col: str, category_col: Optional[str] = None) -> Dict[str, Any]:
        """
        Calculate trend analysis
        
        Args:
            data: Prepared DataFrame
            date_col: Date column name
            value_col: Value column name
            category_col: Optional category column
            
        Returns:
            Dictionary with trend analysis results
        """
        # Ensure date column is datetime
        data[date_col] = pd.to_datetime(data[date_col])
        
        # Get date range
        min_date = data[date_col].min()
        max_date = data[date_col].max()
        
        # Create month-level aggregation
        data['year_month'] = data[date_col].dt.to_period('M')
        
        # Group by year-month and optional category
        if category_col:
            monthly_data = data.groupby(['year_month', category_col]).agg({
                value_col: 'sum'
            }).reset_index()
        else:
            monthly_data = data.groupby('year_month').agg({
                value_col: 'sum'
            }).reset_index()
        
        # Convert year_month to datetime (first day of month)
        monthly_data['date'] = monthly_data['year_month'].dt.to_timestamp()
        
        # Sort by date
        monthly_data = monthly_data.sort_values('date')
        
        # Calculate month-over-month percentage change
        if category_col:
            monthly_data[f'{value_col}_pct_change'] = monthly_data.groupby(category_col)[value_col].pct_change() * 100
        else:
            monthly_data[f'{value_col}_pct_change'] = monthly_data[value_col].pct_change() * 100
        
        # Calculate statistics
        if category_col:
            # Calculate overall trend direction for each category
            trend_data = []
            
            for category, group in monthly_data.groupby(category_col):
                # Linear regression for trend
                x = np.arange(len(group))
                y = group[value_col].values
                
                if len(x) >= 3:  # Need at least 3 points for meaningful trend
                    slope, _ = np.polyfit(x, y, 1)
                    
                    # Normalize the slope by the mean value for percentage
                    trend_pct = (slope / group[value_col].mean()) * 100
                    
                    # Recent periods trend (last 3 months)
                    recent_slope = 0
                    if len(group) >= 3:
                        recent_x = np.arange(3)
                        recent_y = group[value_col].values[-3:]
                        recent_slope, _ = np.polyfit(recent_x, recent_y, 1)
                        recent_trend_pct = (recent_slope / group[value_col].iloc[-3:].mean()) * 100
                    else:
                        recent_trend_pct = trend_pct
                    
                    trend_direction = "up" if slope > 0 else "down"
                    recent_direction = "up" if recent_slope > 0 else "down"
                    
                    # Calculate volatility (standard deviation of percentage changes)
                    volatility = group[f'{value_col}_pct_change'].std()
                    
                    trend_data.append({
                        'category': category,
                        'overall_trend': trend_direction,
                        'overall_trend_pct': float(trend_pct),
                        'recent_trend': recent_direction,
                        'recent_trend_pct': float(recent_trend_pct),
                        'volatility': float(volatility),
                        'min_value': float(group[value_col].min()),
                        'max_value': float(group[value_col].max()),
                        'avg_value': float(group[value_col].mean()),
                        'current_value': float(group[value_col].iloc[-1]),
                        'values': group[value_col].tolist(),
                        'dates': group['date'].dt.strftime('%Y-%m').tolist(),
                        'pct_changes': group[f'{value_col}_pct_change'].tolist()
                    })
        else:
            # Linear regression for trend
            x = np.arange(len(monthly_data))
            y = monthly_data[value_col].values
            
            if len(x) >= 3:  # Need at least 3 points for meaningful trend
                slope, _ = np.polyfit(x, y, 1)
                
                # Normalize the slope by the mean value for percentage
                trend_pct = (slope / monthly_data[value_col].mean()) * 100
                
                # Recent periods trend (last 3 months)
                recent_slope = 0
                if len(monthly_data) >= 3:
                    recent_x = np.arange(3)
                    recent_y = monthly_data[value_col].values[-3:]
                    recent_slope, _ = np.polyfit(recent_x, recent_y, 1)
                    recent_trend_pct = (recent_slope / monthly_data[value_col].iloc[-3:].mean()) * 100
                else:
                    recent_trend_pct = trend_pct
                
                trend_direction = "up" if slope > 0 else "down"
                recent_direction = "up" if recent_slope > 0 else "down"
                
                # Calculate volatility (standard deviation of percentage changes)
                volatility = monthly_data[f'{value_col}_pct_change'].std()
                
                trend_data = {
                    'overall_trend': trend_direction,
                    'overall_trend_pct': float(trend_pct),
                    'recent_trend': recent_direction,
                    'recent_trend_pct': float(recent_trend_pct),
                    'volatility': float(volatility),
                    'min_value': float(monthly_data[value_col].min()),
                    'max_value': float(monthly_data[value_col].max()),
                    'avg_value': float(monthly_data[value_col].mean()),
                    'current_value': float(monthly_data[value_col].iloc[-1]),
                    'values': monthly_data[value_col].tolist(),
                    'dates': monthly_data['date'].dt.strftime('%Y-%m').tolist(),
                    'pct_changes': monthly_data[f'{value_col}_pct_change'].tolist()
                }
            else:
                self.warnings.append("Not enough data points for trend analysis. At least 3 months required.")
                trend_data = {
                    'overall_trend': "unknown",
                    'values': monthly_data[value_col].tolist(),
                    'dates': monthly_data['date'].dt.strftime('%Y-%m').tolist()
                }
        
        # Calculate metrics
        if category_col:
            # Aggregate metrics across categories
            metrics = {
                'total_categories': len(trend_data),
                'growing_categories': sum(1 for item in trend_data if item['overall_trend'] == 'up'),
                'declining_categories': sum(1 for item in trend_data if item['overall_trend'] == 'down'),
                'date_range': f"{min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}",
                'total_months': len(monthly_data['year_month'].unique())
            }
        else:
            metrics = {
                'overall_trend': trend_data.get('overall_trend', 'unknown'),
                'overall_trend_pct': trend_data.get('overall_trend_pct', 0),
                'recent_trend': trend_data.get('recent_trend', 'unknown'),
                'recent_trend_pct': trend_data.get('recent_trend_pct', 0),
                'volatility': trend_data.get('volatility', 0),
                'current_value': trend_data.get('current_value', 0),
                'current_value_formatted': self.formatter.format_currency(trend_data.get('current_value', 0)),
                'date_range': f"{min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}",
                'total_months': len(monthly_data['year_month'].unique())
            }
        
        return {
            'data': trend_data,
            'metrics': metrics,
            'date_range': f"{min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}"
        }
    
    def _generate_insights(self, results: Dict[str, Any], analysis_type: str) -> Dict[str, Any]:
        """
        Generate business insights from the analysis
        
        Args:
            results: Analysis results
            analysis_type: Analysis type
            
        Returns:
            Dictionary with insights
        """
        insights = {
            'summary': {},
            'key_findings': [],
            'trends': [],
            'recommendations': []
        }
        
        metrics = results['metrics']
        
        # Generate insights based on analysis type
        if analysis_type == "ttm":
            insights['summary'] = {
                'analysis_type': "Trailing Twelve Months (TTM) Analysis",
                'current_ttm': metrics['current_ttm_formatted'],
                'date_range': metrics['date_range'],
                'months_covered': metrics['months_covered']
            }
            
            # Add growth rate if available
            if 'current_growth' in metrics:
                insights['summary']['current_growth'] = metrics['current_growth_formatted']
                
                # Add key findings based on growth
                if metrics['current_growth'] > 0:
                    insights['key_findings'].append(
                        f"🔼 **Positive Growth**: Current TTM shows {metrics['current_growth_formatted']} "
                        f"year-over-year growth"
                    )
                else:
                    insights['key_findings'].append(
                        f"🔽 **Negative Growth**: Current TTM shows {metrics['current_growth_formatted']} "
                        f"year-over-year decline"
                    )
            
            # Add trend analysis
            data = results['data']
            if isinstance(data, list):  # Multiple categories
                # Find best and worst performing categories
                categories = sorted(data, key=lambda x: x.get('ttm_values', [])[-1], reverse=True)
                
                if len(categories) > 0:
                    top_category = categories[0]
                    insights['key_findings'].append(
                        f"🥇 **Top Performer**: {top_category['category']} is the highest "
                        f"contributor with {self.formatter.format_currency(top_category['ttm_values'][-1])}"
                    )
                
                if len(categories) > 1:
                    bottom_category = categories[-1]
                    insights['key_findings'].append(
                        f"⚠️ **Attention Needed**: {bottom_category['category']} has the lowest "
                        f"contribution with {self.formatter.format_currency(bottom_category['ttm_values'][-1])}"
                    )
            else:
                # Analyze overall TTM trend
                ttm_values = data.get('ttm_values', [])
                if len(ttm_values) >= 3:
                    recent_trend = ttm_values[-1] > ttm_values[-3]
                    if recent_trend:
                        insights['trends'].append("📈 **Upward Trend**: TTM values have been increasing over recent periods")
                    else:
                        insights['trends'].append("📉 **Downward Trend**: TTM values have been decreasing over recent periods")
            
            # Add recommendations
            if 'current_growth' in metrics:
                if metrics['current_growth'] < 0:
                    insights['recommendations'].append(
                        "🔍 **Investigate Decline**: Analyze contributing factors to the negative growth trend"
                    )
                elif 0 <= metrics['current_growth'] < 5:
                    insights['recommendations'].append(
                        "🚀 **Growth Strategy**: Current growth is positive but modest. Consider strategic initiatives to accelerate growth."
                    )
                else:
                    insights['recommendations'].append(
                        "💪 **Maintain Momentum**: Strong growth observed. Focus on sustaining successful strategies."
                    )
        
        elif analysis_type == "variance":
            variance_status = "over budget" if metrics['total_variance'] > 0 else "under budget"
            variance_icon = "🔼" if variance_status == "over budget" else "🔽"
            
            insights['summary'] = {
                'analysis_type': "Budget vs Actual Variance Analysis",
                'total_actual': metrics['total_actual_formatted'],
                'total_budget': metrics['total_budget_formatted'],
                'total_variance': metrics['total_variance_formatted'],
                'variance_percentage': metrics['total_variance_pct_formatted'],
                'variance_status': variance_status,
                'date_range': metrics['date_range']
            }
            
            # Add key findings
            insights['key_findings'].append(
                f"{variance_icon} **Overall Performance**: "
                f"{variance_status.title()} by {metrics['total_variance_formatted']} "
                f"({metrics['total_variance_pct_formatted']})"
            )
            
            # Periods analysis
            insights['key_findings'].append(
                f"📊 **Period Analysis**: {metrics['periods_over_budget']} periods over budget, "
                f"{metrics['periods_under_budget']} periods under budget"
            )
            
            # Trend analysis
            insights['trends'].append(
                f"📈 **Variance Trend**: Performance is {metrics['variance_trend']} over time"
            )
            
            # Add recommendations based on variance
            if metrics['total_variance'] < 0:
                # Under budget (negative variance)
                if metrics['total_variance_pct'] < -10:
                    insights['recommendations'].append(
                        "🚨 **Significant Shortfall**: Investigate root causes for the substantial negative variance"
                    )
                else:
                    insights['recommendations'].append(
                        "⚠️ **Below Target**: Review execution strategies to improve performance against budget"
                    )
            elif metrics['total_variance'] > 0:
                # Over budget (positive variance)
                if metrics['total_variance_pct'] > 10:
                    insights['recommendations'].append(
                        "🎯 **Exceeding Targets**: Consider whether budgets are too conservative or if exceptional factors contributed"
                    )
                else:
                    insights['recommendations'].append(
                        "✅ **Positive Performance**: Analyze successful strategies to maintain positive variance"
                    )
            else:
                insights['recommendations'].append(
                    "📊 **On Target**: Performance aligns with budget expectations"
                )
            
            # Add top variance insights
            top_variances = results.get('top_variances', [])
            if top_variances:
                # Get largest positive variance
                over_budget = [v for v in top_variances if v['type'] == 'over_budget']
                if over_budget:
                    top_over = over_budget[0]
                    period_str = f"{top_over['period']}"
                    if 'category' in top_over:
                        period_str += f" ({top_over['category']})"
                    
                    insights['key_findings'].append(
                        f"📈 **Highest Over-Performance**: {period_str} exceeded budget by "
                        f"{top_over['variance_formatted']} ({top_over['variance_pct_formatted']})"
                    )
                
                # Get largest negative variance
                under_budget = [v for v in top_variances if v['type'] == 'under_budget']
                if under_budget:
                    top_under = under_budget[0]
                    period_str = f"{top_under['period']}"
                    if 'category' in top_under:
                        period_str += f" ({top_under['category']})"
                    
                    insights['key_findings'].append(
                        f"📉 **Largest Shortfall**: {period_str} missed budget by "
                        f"{top_under['variance_formatted']} ({top_under['variance_pct_formatted']})"
                    )
        
        elif analysis_type == "trend":
            data = results['data']
            
            if isinstance(data, list):  # Multiple categories
                # Count trends
                up_trends = sum(1 for item in data if item['overall_trend'] == 'up')
                down_trends = sum(1 for item in data if item['overall_trend'] == 'down')
                
                trend_status = "mixed"
                if up_trends > down_trends * 2:
                    trend_status = "strongly positive"
                elif up_trends > down_trends:
                    trend_status = "positive"
                elif down_trends > up_trends * 2:
                    trend_status = "strongly negative"
                elif down_trends > up_trends:
                    trend_status = "negative"
                
                insights['summary'] = {
                    'analysis_type': "Trend Analysis by Category",
                    'total_categories': len(data),
                    'growing_categories': up_trends,
                    'declining_categories': down_trends,
                    'overall_trend': trend_status,
                    'date_range': metrics['date_range']
                }
                
                # Key findings
                insights['key_findings'].append(
                    f"📊 **Category Trends**: {up_trends} categories growing, {down_trends} categories declining"
                )
                
                # Find most volatile and most stable categories
                if len(data) > 1:
                    volatile_cat = max(data, key=lambda x: x.get('volatility', 0))
                    stable_cat = min(data, key=lambda x: x.get('volatility', 0))
                    
                    insights['key_findings'].append(
                        f"📈 **Most Volatile**: {volatile_cat['category']} shows highest volatility at {volatile_cat['volatility']:.2f}%"
                    )
                    insights['key_findings'].append(
                        f"📉 **Most Stable**: {stable_cat['category']} shows lowest volatility at {stable_cat['volatility']:.2f}%"
                    )
                
                # Find strongest and weakest trends
                if len(data) > 1:
                    strongest_up = None
                    strongest_down = None
                    
                    for item in data:
                        if item['overall_trend'] == 'up':
                            if strongest_up is None or item['overall_trend_pct'] > strongest_up['overall_trend_pct']:
                                strongest_up = item
                        elif item['overall_trend'] == 'down':
                            if strongest_down is None or item['overall_trend_pct'] < strongest_down['overall_trend_pct']:
                                strongest_down = item
                    
                    if strongest_up:
                        insights['trends'].append(
                            f"🚀 **Strongest Growth**: {strongest_up['category']} with {strongest_up['overall_trend_pct']:.2f}% trend"
                        )
                    
                    if strongest_down:
                        insights['trends'].append(
                            f"📉 **Steepest Decline**: {strongest_down['category']} with {strongest_down['overall_trend_pct']:.2f}% trend"
                        )
            else:
                # Single trend analysis
                trend_direction = data.get('overall_trend', 'unknown')
                trend_pct = data.get('overall_trend_pct', 0)
                
                trend_status = "unknown"
                if trend_direction == 'up':
                    if trend_pct > 10:
                        trend_status = "strongly positive"
                    else:
                        trend_status = "positive"
                elif trend_direction == 'down':
                    if trend_pct < -10:
                        trend_status = "strongly negative"
                    else:
                        trend_status = "negative"
                
                insights['summary'] = {
                    'analysis_type': "Trend Analysis",
                    'overall_trend': trend_status,
                    'trend_percentage': f"{trend_pct:.2f}%",
                    'current_value': metrics['current_value_formatted'],
                    'date_range': metrics['date_range']
                }
                
                # Key findings
                insights['key_findings'].append(
                    f"📈 **Overall Trend**: {trend_status.title()} with {trend_pct:.2f}% directional change"
                )
                
                # Recent trend
                recent_direction = data.get('recent_trend', 'unknown')
                recent_pct = data.get('recent_trend_pct', 0)
                
                if recent_direction != trend_direction:
                    insights['key_findings'].append(
                        f"⚠️ **Recent Shift**: Trend direction changed to {recent_direction} in recent periods"
                    )
                
                # Volatility
                volatility = data.get('volatility', 0)
                if volatility > 15:
                    insights['trends'].append(
                        f"🎢 **High Volatility**: Monthly changes average {volatility:.2f}%, indicating significant fluctuations"
                    )
                elif volatility < 5:
                    insights['trends'].append(
                        f"📊 **Stable Pattern**: Low volatility of {volatility:.2f}% suggests consistent performance"
                    )
            
            # Recommendations based on trends
            if isinstance(data, list):  # Multiple categories
                # If many categories declining
                if down_trends > up_trends:
                    insights['recommendations'].append(
                        "🔍 **Strategic Review**: With more declining categories than growing ones, conduct a comprehensive review"
                    )
                
                # If mixed picture
                if up_trends > 0 and down_trends > 0:
                    insights['recommendations'].append(
                        "📈 **Resource Allocation**: Shift resources from declining to growing categories for optimal returns"
                    )
            else:
                # Single trend recommendations
                if trend_direction == 'up':
                    insights['recommendations'].append(
                        "🚀 **Growth Support**: Maintain current trajectory by reinforcing successful strategies"
                    )
                elif trend_direction == 'down':
                    insights['recommendations'].append(
                        "⚠️ **Course Correction**: Implement corrective actions to reverse the downward trend"
                    )
                
                # Volatility recommendation
                if data.get('volatility', 0) > 15:
                    insights['recommendations'].append(
                        "🛡️ **Stability Measures**: Develop strategies to reduce high volatility for more predictable outcomes"
                    )
        
        return insights
    
    def format_for_chat(self) -> str:
        """
        Format analysis results for chat display using standardized formatting
        
        Returns:
            Formatted string for chat interface
        """
        if self.status != "completed" or not self.results:
            return "❌ **Analysis not completed or failed**"
        
        results = self.results
        analysis_type = results['analysis_type']
        insights = results['insights']
        metrics = results['metrics']
        params = results['parameters']
        
        # Build standardized format based on analysis type
        if analysis_type == "ttm":
            return self._format_ttm_analysis(results, insights, metrics, params)
        elif analysis_type == "variance":
            return self._format_variance_analysis(results, insights, metrics, params)
        elif analysis_type == "trend":
            return self._format_trend_analysis(results, insights, metrics, params)
        else:
            return self._format_generic_analysis(analysis_type, results)
    
    def _format_ttm_analysis(self, results: Dict, insights: Dict, metrics: Dict, params: Dict) -> str:
        """Format TTM analysis with standardized structure"""
        
        # 1. Summary section
        explanation = "Analyzes Trailing Twelve Months (TTM) performance to provide a rolling 12-month view of financial metrics."
        assumptions = [
            f"Analysis performed on '{params['value_col']}' column",
            f"Date range: {metrics['date_range']}",
            "TTM calculated as sum of most recent 12 months",
            "Growth calculated year-over-year where data available"
        ]
        
        if params.get('category_col'):
            assumptions.append(f"Segmented by '{params['category_col']}' categories")
        
        formatted_output = self.formatter.create_summary_section(
            "TTM Analysis (Trailing Twelve Months)",
            explanation,
            assumptions
        )
        
        # 2. Key metrics
        key_metrics = {
            "Current_TTM_Value": metrics.get('current_ttm', 0),
            "Period_Coverage": metrics.get('date_range', 'N/A')
        }
        
        if 'current_growth' in metrics:
            key_metrics["YoY_Growth"] = f"{metrics['current_growth']:.1f}%"
        
        formatted_output += "\n\n" + self.formatter.create_metrics_grid(key_metrics, "TTM Performance Summary")
        
        # 3. Insights and recommendations
        clean_findings = [finding.replace('🎯 **', '').replace('**', '') for finding in insights.get('key_findings', [])]
        clean_recs = [rec.replace('💡 **', '').replace('**', '') for rec in insights.get('recommendations', [])]
        
        formatted_output += "\n\n" + self.formatter.create_insights_section(clean_findings, clean_recs)
        
        # 4. Trend details
        if insights.get('trends'):
            formatted_output += "\n\n� **TREND DETAILS:**\n"
            for i, trend in enumerate(insights['trends'], 1):
                clean_trend = trend.replace('📈', '').replace('📊', '').strip()
                formatted_output += f"{i}. {clean_trend}\n"
        
        return formatted_output
    
    def _format_variance_analysis(self, results: Dict, insights: Dict, metrics: Dict, params: Dict) -> str:
        """Format variance analysis with standardized structure"""
        
        # 1. Summary section
        explanation = "Compares actual performance against budgeted targets to identify areas of over or under-performance."
        assumptions = [
            f"Actual values from '{params['value_col']}' column",
            f"Budget values from '{params.get('budget_col', 'Budget')}' column",
            f"Analysis period: {metrics['date_range']}",
            "Positive variance = actual exceeds budget",
            "Negative variance = actual below budget"
        ]
        
        formatted_output = self.formatter.create_summary_section(
            "Budget vs Actual Variance Analysis",
            explanation,
            assumptions
        )
        
        # 2. Key metrics
        key_metrics = {
            "Total_Actual": metrics.get('total_actual', 0),
            "Total_Budget": metrics.get('total_budget', 0),
            "Total_Variance": metrics.get('total_variance', 0),
            "Variance_Percentage": f"{metrics.get('total_variance_pct', 0):.1f}%"
        }
        
        formatted_output += "\n\n" + self.formatter.create_metrics_grid(key_metrics, "Variance Summary")
        
        # 3. Top variances table
        top_variances = results.get('top_variances', [])
        if top_variances:
            formatted_output += "\n\n📊 **NOTABLE VARIANCES TABLE:**\n"
            
            table_data = []
            for variance in top_variances[:10]:  # Top 10
                table_data.append({
                    "Period": variance.get('period', 'N/A'),
                    "Category": variance.get('category', 'All'),
                    "Actual": variance.get('actual', 0),
                    "Budget": variance.get('budget', 0),
                    "Variance": variance.get('variance', 0),
                    "Variance_Pct": f"{variance.get('variance_pct', 0):.1f}%"
                })
            
            headers = ["Period", "Category", "Actual", "Budget", "Variance", "Variance_Pct"]
            formatted_output += "\n" + self.formatter.create_banded_table(table_data, headers, max_rows=10)
        
        # 4. Insights and recommendations
        clean_findings = [finding.replace('🎯 **', '').replace('**', '') for finding in insights.get('key_findings', [])]
        clean_recs = [rec.replace('💡 **', '').replace('**', '') for rec in insights.get('recommendations', [])]
        
        formatted_output += "\n\n" + self.formatter.create_insights_section(clean_findings, clean_recs)
        
        return formatted_output
    
    def _format_trend_analysis(self, results: Dict, insights: Dict, metrics: Dict, params: Dict) -> str:
        """Format trend analysis with standardized structure"""
        
        # 1. Summary section
        explanation = "Analyzes patterns and trends in financial data over time to identify growth, decline, and seasonal patterns."
        assumptions = [
            f"Analysis performed on '{params['value_col']}' column",
            f"Date range: {metrics['date_range']}",
            "Trends calculated using period-over-period comparison",
            "Seasonal patterns identified where sufficient data available"
        ]
        
        if params.get('category_col'):
            assumptions.append(f"Trend analysis segmented by '{params['category_col']}'")
        
        formatted_output = self.formatter.create_summary_section(
            "Trend Analysis",
            explanation,
            assumptions
        )
        
        # 2. Key metrics
        key_metrics = {}
        
        if isinstance(results['data'], list):  # Multiple categories
            key_metrics.update({
                "Categories_Analyzed": metrics.get('total_categories', 0),
                "Growing_Categories": metrics.get('growing_categories', 0),
                "Declining_Categories": metrics.get('declining_categories', 0)
            })
        else:
            key_metrics.update({
                "Overall_Trend": metrics.get('overall_trend', 'N/A').title(),
                "Trend_Strength": f"{metrics.get('overall_trend_pct', 0):.1f}%",
                "Current_Value": metrics.get('current_value', 0)
            })
        
        formatted_output += "\n\n" + self.formatter.create_metrics_grid(key_metrics, "Trend Summary")
        
        # 3. Insights and recommendations
        clean_findings = [finding.replace('🎯 **', '').replace('**', '') for finding in insights.get('key_findings', [])]
        clean_recs = [rec.replace('💡 **', '').replace('**', '') for rec in insights.get('recommendations', [])]
        
        formatted_output += "\n\n" + self.formatter.create_insights_section(clean_findings, clean_recs)
        
        # 4. Detailed trends
        if insights.get('trends'):
            formatted_output += "\n\n� **DETAILED TREND ANALYSIS:**\n"
            for i, trend in enumerate(insights['trends'], 1):
                clean_trend = trend.replace('📊', '').replace('📈', '').strip()
                formatted_output += f"{i}. {clean_trend}\n"
        
        return formatted_output
    
    def _format_generic_analysis(self, analysis_type: str, results: Dict) -> str:
        """Format generic analysis when specific format not available"""
        explanation = f"Completed {analysis_type} analysis on financial data."
        assumptions = ["Standard financial analysis assumptions applied"]
        
        formatted_output = self.formatter.create_summary_section(
            f"{analysis_type.title()} Analysis",
            explanation,
            assumptions
        )
        
        formatted_output += f"\n\n📊 **Analysis Status**: Completed\n"
        formatted_output += f"**Type**: {analysis_type}\n"
        formatted_output += f"**Results Available**: {', '.join(results.keys())}"
        
        return formatted_output
