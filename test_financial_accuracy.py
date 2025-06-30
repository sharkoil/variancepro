"""
VariancePro Financial Accuracy Tests

This test suite focuses on the financial accuracy of the TimescaleAnalyzer calculations,
ensuring that period-over-period calculations are correct and match industry standards.

The tests validate the accuracy of financial metrics including:
- Growth rates
- Compound Annual Growth Rate (CAGR)
- Year-over-Year (YoY) calculations
- Quarter-over-Quarter (QoQ) calculations
- Month-over-Month (MoM) calculations
"""

import unittest
import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime
import math

# Add parent directory to path to import from app.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the TimescaleAnalyzer class from app.py
from app import TimescaleAnalyzer

class TestFinancialAccuracy(unittest.TestCase):
    """Test suite for validating financial calculation accuracy"""
    
    def setUp(self):
        """Setup test environment before each test"""
        self.analyzer = TimescaleAnalyzer()
        
        # Create test dataset with predictable growth patterns
        self.linear_growth_df = self._create_linear_growth_dataset()
        self.compound_growth_df = self._create_compound_growth_dataset()
        self.seasonal_growth_df = self._create_seasonal_growth_dataset()
    
    def _create_linear_growth_dataset(self):
        """Create dataset with linear growth for testing"""
        # Monthly data over 3 years
        dates = pd.date_range(start='2020-01-01', end='2022-12-31', freq='M')
        
        # Linear growth: Start at 100, add 10 each month
        revenue = [100 + (i * 10) for i in range(len(dates))]
        
        # Costs grow at a slower rate: Start at 70, add 5 each month
        costs = [70 + (i * 5) for i in range(len(dates))]
        
        # Create DataFrame
        df = pd.DataFrame({
            'date': dates,
            'revenue': revenue,
            'costs': costs
        })
        
        # Calculate profit
        df['profit'] = df['revenue'] - df['costs']
        
        return df
    
    def _create_compound_growth_dataset(self):
        """Create dataset with compound growth for testing"""
        # Monthly data over 3 years
        dates = pd.date_range(start='2020-01-01', end='2022-12-31', freq='M')
        
        # Compound growth: 5% month-over-month growth
        base_revenue = 1000
        revenue = [base_revenue * (1.05 ** i) for i in range(len(dates))]
        
        # Costs grow at 3% month-over-month
        base_costs = 700
        costs = [base_costs * (1.03 ** i) for i in range(len(dates))]
        
        # Create DataFrame
        df = pd.DataFrame({
            'date': dates,
            'revenue': revenue,
            'costs': costs
        })
        
        # Calculate profit
        df['profit'] = df['revenue'] - df['costs']
        
        return df
    
    def _create_seasonal_growth_dataset(self):
        """Create dataset with seasonal patterns plus growth for testing"""
        # Monthly data over 3 years
        dates = pd.date_range(start='2020-01-01', end='2022-12-31', freq='M')
        
        # Base trend: 3% month-over-month growth
        base_revenue = 1000
        revenue_trend = [base_revenue * (1.03 ** i) for i in range(len(dates))]
        
        # Add seasonal pattern
        revenue = []
        for i, date in enumerate(dates):
            # Q4 boost
            seasonal_factor = 1.0
            if date.month in [10, 11, 12]:  # Q4 months
                seasonal_factor = 1.2
            elif date.month in [1, 2]:  # Post-holiday slump
                seasonal_factor = 0.9
            
            revenue.append(revenue_trend[i] * seasonal_factor)
        
        # Costs follow similar pattern but less seasonal variation
        base_costs = 700
        costs_trend = [base_costs * (1.02 ** i) for i in range(len(dates))]
        
        costs = []
        for i, date in enumerate(dates):
            # Less seasonal variation in costs
            seasonal_factor = 1.0
            if date.month in [10, 11, 12]:  # Q4 months
                seasonal_factor = 1.1
            elif date.month in [1, 2]:  # Post-holiday adjustment
                seasonal_factor = 0.95
            
            costs.append(costs_trend[i] * seasonal_factor)
        
        # Create DataFrame
        df = pd.DataFrame({
            'date': dates,
            'revenue': revenue,
            'costs': costs
        })
        
        # Calculate profit
        df['profit'] = df['revenue'] - df['costs']
        
        return df
    
    def test_linear_growth_calculations(self):
        """Test period-over-period calculations with linear growth"""
        # Calculate aggregations and analysis
        aggs = self.analyzer.prepare_timescale_aggregations(
            self.linear_growth_df, 'date', ['revenue', 'costs', 'profit']
        )
        
        pop_analysis = self.analyzer.calculate_period_over_period_analysis(
            aggs, ['revenue', 'costs', 'profit']
        )
        
        # Check monthly revenue calculations
        monthly_revenue = pop_analysis['monthly']['revenue']
        
        # With linear growth of +10 per month from base 100,
        # the percentage change should decrease over time
        # First few percentage changes should be:
        # From 100 to 110: 10%
        # From 110 to 120: 9.09%
        # From 120 to 130: 8.33%
        
        # Allow for small floating point errors
        self.assertAlmostEqual(monthly_revenue['pct_changes'][1], 10.0, delta=0.1)
        self.assertAlmostEqual(monthly_revenue['pct_changes'][2], 9.09, delta=0.1)
        self.assertAlmostEqual(monthly_revenue['pct_changes'][3], 8.33, delta=0.1)
        
        # Verify the absolute changes (should be consistent at +10)
        for i in range(1, len(monthly_revenue['abs_changes'])):
            if not pd.isna(monthly_revenue['abs_changes'][i]):
                self.assertAlmostEqual(monthly_revenue['abs_changes'][i], 10.0, delta=0.1)
        
        # Check quarterly aggregation
        quarterly_revenue = pop_analysis['quarterly']['revenue']
        
        # For quarterly, we expect each quarter to increase by 10*3 = 30
        # over the previous quarter
        for i in range(1, len(quarterly_revenue['abs_changes'])):
            if not pd.isna(quarterly_revenue['abs_changes'][i]):
                self.assertAlmostEqual(quarterly_revenue['abs_changes'][i], 30.0, delta=1.0)
        
        # Check profit calculation (should be revenue - costs)
        for i in range(len(monthly_revenue['values'])):
            expected_profit = monthly_revenue['values'][i] - pop_analysis['monthly']['costs']['values'][i]
            actual_profit = pop_analysis['monthly']['profit']['values'][i]
            self.assertAlmostEqual(actual_profit, expected_profit, delta=0.1)
    
    def test_compound_growth_calculations(self):
        """Test period-over-period calculations with compound growth"""
        # Calculate aggregations and analysis
        aggs = self.analyzer.prepare_timescale_aggregations(
            self.compound_growth_df, 'date', ['revenue', 'costs', 'profit']
        )
        
        pop_analysis = self.analyzer.calculate_period_over_period_analysis(
            aggs, ['revenue', 'costs', 'profit']
        )
        
        # Check monthly revenue calculations
        monthly_revenue = pop_analysis['monthly']['revenue']
        
        # With compound growth of 5% per month,
        # the percentage change should be consistent at around 5%
        for i in range(1, len(monthly_revenue['pct_changes'])):
            if not pd.isna(monthly_revenue['pct_changes'][i]):
                self.assertAlmostEqual(monthly_revenue['pct_changes'][i], 5.0, delta=0.2)
        
        # Check yearly aggregation - compound annual growth rate (CAGR)
        # For 5% monthly growth, annual growth is (1.05^12 - 1) = 79.6%
        yearly_revenue = pop_analysis['yearly']['revenue']
        for i in range(1, len(yearly_revenue['pct_changes'])):
            if not pd.isna(yearly_revenue['pct_changes'][i]):
                expected_annual_growth = (1.05 ** 12) - 1
                self.assertAlmostEqual(yearly_revenue['pct_changes'][i] / 100, expected_annual_growth, delta=0.02)
    
    def test_seasonal_growth_calculations(self):
        """Test period-over-period calculations with seasonal patterns"""
        # Calculate aggregations and analysis
        aggs = self.analyzer.prepare_timescale_aggregations(
            self.seasonal_growth_df, 'date', ['revenue', 'costs', 'profit']
        )
        
        pop_analysis = self.analyzer.calculate_period_over_period_analysis(
            aggs, ['revenue', 'costs', 'profit']
        )
        
        # Check quarterly pattern - Q4 should be higher than Q3
        quarterly_revenue = pop_analysis['quarterly']['revenue']
        
        # Get values by quarter
        q_values = quarterly_revenue['values']
        
        # Check seasonal pattern within each year (only if we have enough quarters)
        if len(q_values) >= 8:  # At least 2 full years
            # Check Q4 vs Q3 for first year
            q3_yr1 = q_values[2]  # 0-indexed, so this is Q3
            q4_yr1 = q_values[3]  # Q4
            self.assertGreater(q4_yr1, q3_yr1)
            
            # Check Q4 vs Q3 for second year
            q3_yr2 = q_values[6]  # Q3 of second year
            q4_yr2 = q_values[7]  # Q4 of second year
            self.assertGreater(q4_yr2, q3_yr2)
        
        # Check yearly growth - should be approximately (1.03^12 * appropriate_seasonal_factor)
        yearly_revenue = pop_analysis['yearly']['revenue']
        if len(yearly_revenue['values']) >= 3:  # We need at least 3 years
            yr1 = yearly_revenue['values'][0]
            yr2 = yearly_revenue['values'][1]
            yr3 = yearly_revenue['values'][2]
            
            # Yearly growth should be approximately 43% (1.03^12 = 1.43)
            # but we allow for seasonal variations
            yr1_to_yr2_growth = (yr2 / yr1) - 1
            yr2_to_yr3_growth = (yr3 / yr2) - 1
            
            # Should be roughly around 1.03^12 = 1.43 (43% growth)
            # We allow a wide delta due to seasonal effects
            expected_annual_growth = (1.03 ** 12) - 1
            self.assertAlmostEqual(yr1_to_yr2_growth, expected_annual_growth, delta=0.1)
            self.assertAlmostEqual(yr2_to_yr3_growth, expected_annual_growth, delta=0.1)
    
    def test_year_over_year_calculation(self):
        """Test Year-over-Year (YoY) calculation accuracy"""
        # Create monthly data with exact 1-year separation for clear comparison
        dates = pd.date_range(start='2020-01-01', end='2022-12-31', freq='M')
        
        # Create a DataFrame with specific YoY patterns
        # Year 1: 100,110,120,130,140,150,160,170,180,190,200,210
        # Year 2: 200,220,240,260,280,300,320,340,360,380,400,420 (100% growth)
        # Year 3: 400,440,480,520,560,600,640,680,720,760,800,840 (100% growth)
        
        values = []
        for year in range(3):
            base = 100 * (2 ** year)  # 100, 200, 400
            for month in range(12):
                values.append(base + (month * 10 * (2 ** year)))
        
        df = pd.DataFrame({
            'date': dates,
            'value': values
        })
        
        # Calculate aggregations and analysis
        aggs = self.analyzer.prepare_timescale_aggregations(df, 'date', ['value'])
        pop_analysis = self.analyzer.calculate_period_over_period_analysis(aggs, ['value'])
        
        # Check yearly calculation
        yearly_value = pop_analysis['yearly']['value']
        
        # First year: average of year 1 values
        # Second year: average of year 2 values (should be 100% more than year 1)
        # Third year: average of year 3 values (should be 100% more than year 2)
        if len(yearly_value['pct_changes']) >= 3:
            self.assertAlmostEqual(yearly_value['pct_changes'][1], 100.0, delta=1.0)
            self.assertAlmostEqual(yearly_value['pct_changes'][2], 100.0, delta=1.0)
    
    def test_financial_ratios(self):
        """Test that financial ratios are calculated correctly"""
        # Create a dataset with revenue, costs, and profit margin
        dates = pd.date_range(start='2020-01-01', end='2022-12-31', freq='M')
        
        # Create predictable pattern
        revenue = [1000 + (i * 50) for i in range(len(dates))]
        costs = [800 + (i * 30) for i in range(len(dates))]
        
        df = pd.DataFrame({
            'date': dates,
            'revenue': revenue,
            'costs': costs
        })
        
        # Calculate profit and profit margin
        df['profit'] = df['revenue'] - df['costs']
        df['profit_margin'] = df['profit'] / df['revenue'] * 100
        
        # Calculate aggregations and analysis
        aggs = self.analyzer.prepare_timescale_aggregations(
            df, 'date', ['revenue', 'costs', 'profit', 'profit_margin']
        )
        
        pop_analysis = self.analyzer.calculate_period_over_period_analysis(
            aggs, ['revenue', 'costs', 'profit', 'profit_margin']
        )
        
        # Check profit calculation
        monthly_profit = pop_analysis['monthly']['profit']
        monthly_revenue = pop_analysis['monthly']['revenue']
        monthly_costs = pop_analysis['monthly']['costs']
        
        for i in range(len(monthly_profit['values'])):
            expected_profit = monthly_revenue['values'][i] - monthly_costs['values'][i]
            actual_profit = monthly_profit['values'][i]
            self.assertAlmostEqual(actual_profit, expected_profit, delta=0.1)
        
        # Check profit margin calculation
        monthly_margin = pop_analysis['monthly']['profit_margin']
        
        for i in range(len(monthly_margin['values'])):
            expected_margin = (monthly_profit['values'][i] / monthly_revenue['values'][i]) * 100
            actual_margin = monthly_margin['values'][i]
            self.assertAlmostEqual(actual_margin, expected_margin, delta=0.1)
        
        # Check that profit margin improves over time
        # (since revenue grows faster than costs in our model)
        first_margin = monthly_margin['values'][0]
        last_margin = monthly_margin['values'][-1]
        self.assertGreater(last_margin, first_margin)

if __name__ == "__main__":
    unittest.main()
