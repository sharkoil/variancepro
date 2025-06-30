"""
VariancePro TimescaleAnalyzer Unit Tests

Comprehensive test suite for the TimescaleAnalyzer class to ensure accurate 
period-over-period financial analysis.

In a regulated financial environment, accuracy is critical. These tests verify:
1. Time granularity detection
2. Proper period aggregation
3. Accurate period-over-period calculations
4. Insight generation validity
5. Error handling and edge cases
"""

import unittest
import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import re
from utils.test_logger import TestResultLogger

# Add parent directory to path to import from app.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the TimescaleAnalyzer class from app.py
from app import TimescaleAnalyzer

class TestTimescaleAnalyzer(unittest.TestCase):
    """Unit test suite for TimescaleAnalyzer class"""
    
    def setUp(self):
        """Setup test environment before each test"""
        self.analyzer = TimescaleAnalyzer()
        self.logger = TestResultLogger()
        
        # Create sample datasets for testing
        self.daily_df = self._create_daily_sample_data()
        self.weekly_df = self._create_weekly_sample_data()
        self.monthly_df = self._create_monthly_sample_data()
        self.quarterly_df = self._create_quarterly_sample_data()
        self.yearly_df = self._create_yearly_sample_data()
        
        # Edge cases
        self.single_row_df = pd.DataFrame({
            'date': [datetime(2023, 1, 1)],
            'value': [100]
        })
        
        self.no_date_df = pd.DataFrame({
            'col1': [1, 2, 3],
            'col2': [4, 5, 6]
        })
        
        self.empty_df = pd.DataFrame()
    
    def _create_daily_sample_data(self):
        """Create daily sample data for testing"""
        dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
        df = pd.DataFrame({
            'date': dates,
            'revenue': np.random.normal(1000, 100, size=len(dates)) * (1 + 0.0002 * np.arange(len(dates))),
            'costs': np.random.normal(700, 50, size=len(dates)) * (1 + 0.0001 * np.arange(len(dates))),
            'customers': np.random.normal(500, 50, size=len(dates))} 
        )
        
        # Add some seasonal patterns
        for i, date in enumerate(dates):
            # Q4 boost
            if date.month in [10, 11, 12]:
                df.loc[i, 'revenue'] *= 1.2
            # Month-end effect
            if date.day >= 28:
                df.loc[i, 'revenue'] *= 1.1
        
        # Calculate profit
        df['profit'] = df['revenue'] - df['costs']
        
        # Add categorical columns
        df['region'] = np.random.choice(['North', 'South', 'East', 'West'], size=len(dates))
        df['product'] = np.random.choice(['Product A', 'Product B', 'Product C'], size=len(dates))
        
        return df
    
    def _create_weekly_sample_data(self):
        """Create weekly sample data for testing"""
        dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='W')
        df = pd.DataFrame({
            'date': dates,
            'revenue': np.random.normal(7000, 700, size=len(dates)) * (1 + 0.003 * np.arange(len(dates))),
            'costs': np.random.normal(4900, 350, size=len(dates)) * (1 + 0.002 * np.arange(len(dates))),
            'customers': np.random.normal(3500, 350, size=len(dates))}
        )
        
        # Calculate profit
        df['profit'] = df['revenue'] - df['costs']
        
        # Add categorical columns
        df['region'] = np.random.choice(['North', 'South', 'East', 'West'], size=len(dates))
        df['product'] = np.random.choice(['Product A', 'Product B', 'Product C'], size=len(dates))
        
        return df
    
    def _create_monthly_sample_data(self):
        """Create monthly sample data for testing"""
        dates = pd.date_range(start='2021-01-01', end='2023-12-31', freq='M')
        df = pd.DataFrame({
            'date': dates,
            'revenue': np.random.normal(30000, 3000, size=len(dates)) * (1 + 0.01 * np.arange(len(dates))),
            'costs': np.random.normal(21000, 1500, size=len(dates)) * (1 + 0.008 * np.arange(len(dates))),
            'customers': np.random.normal(15000, 1500, size=len(dates))}
        )
        
        # Calculate profit
        df['profit'] = df['revenue'] - df['costs']
        
        # Add categorical columns
        df['region'] = np.random.choice(['North', 'South', 'East', 'West'], size=len(dates))
        df['product'] = np.random.choice(['Product A', 'Product B', 'Product C'], size=len(dates))
        
        return df
    
    def _create_quarterly_sample_data(self):
        """Create quarterly sample data for testing"""
        dates = pd.date_range(start='2021-01-01', end='2023-12-31', freq='Q')
        df = pd.DataFrame({
            'date': dates,
            'revenue': np.random.normal(90000, 9000, size=len(dates)) * (1 + 0.03 * np.arange(len(dates))),
            'costs': np.random.normal(63000, 4500, size=len(dates)) * (1 + 0.025 * np.arange(len(dates))),
            'customers': np.random.normal(45000, 4500, size=len(dates))}
        )
        
        # Calculate profit
        df['profit'] = df['revenue'] - df['costs']
        
        # Add categorical columns
        df['region'] = np.random.choice(['North', 'South', 'East', 'West'], size=len(dates))
        df['product'] = np.random.choice(['Product A', 'Product B', 'Product C'], size=len(dates))
        
        return df
    
    def _create_yearly_sample_data(self):
        """Create yearly sample data for testing"""
        dates = pd.date_range(start='2010-01-01', end='2023-12-31', freq='Y')
        df = pd.DataFrame({
            'date': dates,
            'revenue': np.random.normal(360000, 36000, size=len(dates)) * (1 + 0.05 * np.arange(len(dates))),
            'costs': np.random.normal(252000, 18000, size=len(dates)) * (1 + 0.04 * np.arange(len(dates))),
            'customers': np.random.normal(180000, 18000, size=len(dates))}
        )
        
        # Calculate profit
        df['profit'] = df['revenue'] - df['costs']
        
        # Add categorical columns
        df['region'] = np.random.choice(['North', 'South', 'East', 'West'], size=len(dates))
        df['product'] = np.random.choice(['Product A', 'Product B', 'Product C'], size=len(dates))
        
        return df
    
    # Test time granularity detection
    def test_detect_time_granularity(self):
        """Test time granularity detection for different time series"""
        # Start log for this test
        self.logger.start_test_log("detect_time_granularity")
        self.logger.log_message("Testing time granularity detection for different time series")
        
        # Test daily data
        granularity = self.analyzer.detect_time_granularity(self.daily_df, 'date')
        self.assertEqual(granularity, 'daily')
        self.logger.log_comparison('daily', granularity, "Daily data detection")
        
        # Test weekly data
        granularity = self.analyzer.detect_time_granularity(self.weekly_df, 'date')
        self.assertEqual(granularity, 'weekly')
        self.logger.log_comparison('weekly', granularity, "Weekly data detection")
        
        # Test monthly data
        granularity = self.analyzer.detect_time_granularity(self.monthly_df, 'date')
        self.assertEqual(granularity, 'monthly')
        self.logger.log_comparison('monthly', granularity, "Monthly data detection")
        
        # Test quarterly data
        granularity = self.analyzer.detect_time_granularity(self.quarterly_df, 'date')
        self.assertEqual(granularity, 'quarterly')
        self.logger.log_comparison('quarterly', granularity, "Quarterly data detection")
        
        # Test yearly data
        granularity = self.analyzer.detect_time_granularity(self.yearly_df, 'date')
        self.assertEqual(granularity, 'yearly')
        self.logger.log_comparison('yearly', granularity, "Yearly data detection")
        
        # Test invalid date column
        granularity = self.analyzer.detect_time_granularity(self.daily_df, 'invalid_column')
        self.assertEqual(granularity, 'unknown')
        self.logger.log_comparison('unknown', granularity, "Invalid column detection")
        
        # Test single row data
        granularity = self.analyzer.detect_time_granularity(self.single_row_df, 'date')
        self.assertEqual(granularity, 'daily')
        self.logger.log_comparison('daily', granularity, "Single row data detection")
        
        # Test no date column
        granularity = self.analyzer.detect_time_granularity(self.no_date_df, 'date')
        self.assertEqual(granularity, 'unknown')
        self.logger.log_comparison('unknown', granularity, "No date column detection")
        
        # Finish log
        self.logger.finish_test_log()
    
    # Test timescale aggregations
    def test_prepare_timescale_aggregations(self):
        """Test preparation of aggregations at different time scales"""
        # Test with daily data
        daily_aggs = self.analyzer.prepare_timescale_aggregations(
            self.daily_df, 'date', ['revenue', 'costs', 'profit']
        )
        
        # Check that we have all time scales
        self.assertIn('weekly', daily_aggs)
        self.assertIn('monthly', daily_aggs)
        self.assertIn('quarterly', daily_aggs)
        self.assertIn('yearly', daily_aggs)
        
        # Check that each scale has data and periods
        for scale in ['weekly', 'monthly', 'quarterly', 'yearly']:
            self.assertIn('data', daily_aggs[scale])
            self.assertIn('periods', daily_aggs[scale])
            self.assertTrue(len(daily_aggs[scale]['periods']) > 0)
        
        # Test with monthly data
        monthly_aggs = self.analyzer.prepare_timescale_aggregations(
            self.monthly_df, 'date', ['revenue', 'costs', 'profit']
        )
        
        # Check that quarterly aggregation has correct number of periods
        # 36 months should give us 12 quarters
        self.assertEqual(len(monthly_aggs['quarterly']['periods']), 12)
        
        # Test with invalid column
        empty_aggs = self.analyzer.prepare_timescale_aggregations(
            self.daily_df, 'invalid_column', ['revenue', 'costs', 'profit']
        )
        self.assertEqual(empty_aggs, {})
        
        # Test with empty dataframe
        empty_df_aggs = self.analyzer.prepare_timescale_aggregations(
            self.empty_df, 'date', ['revenue', 'costs', 'profit']
        )
        self.assertEqual(empty_df_aggs, {})
        
        # Test with no value columns specified (should use numeric columns)
        auto_value_aggs = self.analyzer.prepare_timescale_aggregations(
            self.daily_df, 'date', []
        )
        # Check that it automatically used numeric columns
        for scale in ['weekly', 'monthly', 'quarterly', 'yearly']:
            self.assertIn('revenue', auto_value_aggs[scale]['data'].columns)
            self.assertIn('costs', auto_value_aggs[scale]['data'].columns)
            self.assertIn('profit', auto_value_aggs[scale]['data'].columns)
    
    # Test period-over-period analysis
    def test_calculate_period_over_period_analysis(self):
        """Test calculation of period-over-period metrics"""
        # First prepare aggregations
        daily_aggs = self.analyzer.prepare_timescale_aggregations(
            self.daily_df, 'date', ['revenue', 'costs', 'profit']
        )
        
        # Calculate POP analysis
        pop_analysis = self.analyzer.calculate_period_over_period_analysis(
            daily_aggs, ['revenue', 'costs', 'profit']
        )
        
        # Check that we have all time scales
        self.assertIn('weekly', pop_analysis)
        self.assertIn('monthly', pop_analysis)
        self.assertIn('quarterly', pop_analysis)
        self.assertIn('yearly', pop_analysis)
        
        # Check metrics for each scale
        for scale in ['weekly', 'monthly', 'quarterly', 'yearly']:
            for metric in ['revenue', 'costs', 'profit']:
                # Check that metric exists
                self.assertIn(metric, pop_analysis[scale])
                
                # Check that it has all required components
                self.assertIn('periods', pop_analysis[scale][metric])
                self.assertIn('values', pop_analysis[scale][metric])
                self.assertIn('abs_changes', pop_analysis[scale][metric])
                self.assertIn('pct_changes', pop_analysis[scale][metric])
                self.assertIn('summary', pop_analysis[scale][metric])
                
                # Check summary statistics
                summary = pop_analysis[scale][metric]['summary']
                self.assertIn('total_periods', summary)
                self.assertIn('positive_periods', summary)
                self.assertIn('negative_periods', summary)
                self.assertIn('avg_pct_change', summary)
                self.assertIn('max_pct_change', summary)
                self.assertIn('min_pct_change', summary)
                self.assertIn('latest_value', summary)
                self.assertIn('latest_change', summary)
                
                # Check logical constraints
                self.assertGreaterEqual(summary['positive_periods'] + summary['negative_periods'], 0)
                self.assertLessEqual(summary['positive_periods'] + summary['negative_periods'], summary['total_periods'])
                
                # Changes array should be one less than values array
                self.assertEqual(len(pop_analysis[scale][metric]['abs_changes']), 
                                len(pop_analysis[scale][metric]['values']) - 1)
                
                # Verify first change is NaN (represented as None in JSON)
                self.assertTrue(pd.isna(pop_analysis[scale][metric]['abs_changes'][0]) or 
                              pop_analysis[scale][metric]['abs_changes'][0] is None)
    
    # Test summary insights generation
    def test_generate_summary_insights(self):
        """Test generation of natural language insights"""
        # First prepare aggregations and POP analysis
        daily_aggs = self.analyzer.prepare_timescale_aggregations(
            self.daily_df, 'date', ['revenue', 'costs', 'profit']
        )
        
        pop_analysis = self.analyzer.calculate_period_over_period_analysis(
            daily_aggs, ['revenue', 'costs', 'profit']
        )
        
        # Generate insights
        insights = self.analyzer._generate_summary_insights(pop_analysis)
        
        # Check that it's a non-empty string
        self.assertIsInstance(insights, str)
        self.assertGreater(len(insights), 0)
        
        # Check for expected section headers
        self.assertIn("# 📊 Automatic Timescale Analysis", insights)
        self.assertIn("## 📅 Year-over-Year", insights)
        self.assertIn("## 📊 Quarter-over-Quarter", insights)
        self.assertIn("## 📆 Month-over-Month", insights)
        self.assertIn("## 📈 Week-over-Week", insights)
        self.assertIn("## 📋 Executive Summary", insights)
        
        # Check for metrics
        for metric in ['Revenue', 'Costs', 'Profit']:
            self.assertIn(metric, insights)
        
        # Check for key phrases
        key_phrases = [
            "trend", "increase", "decrease", 
            "Largest", "Average change"
        ]
        for phrase in key_phrases:
            self.assertIn(phrase, insights)
            
        # Test with empty analysis
        empty_insights = self.analyzer._generate_summary_insights({})
        self.assertIsInstance(empty_insights, str)
        self.assertGreater(len(empty_insights), 0)
    
    # Test full timescale analysis
    def test_generate_timescale_analysis(self):
        """Test the full analysis pipeline"""
        # Start log for this test
        self.logger.start_test_log("generate_timescale_analysis")
        self.logger.log_message("Testing complete timescale analysis pipeline")
        
        # Test with daily data
        self.logger.log_section("Daily Data Analysis")
        self.logger.log_dataframe(self.daily_df.head(), "Daily Data Sample")
        
        daily_analysis = self.analyzer.generate_timescale_analysis(self.daily_df)
        
        # Check that it's a non-empty string
        self.assertIsInstance(daily_analysis, str)
        self.assertGreater(len(daily_analysis), 0)
        
        # Log the analysis result
        self.logger.log_message("Analysis Output:")
        self.logger.log_message(daily_analysis)
        self.logger.log_test_result("Daily Analysis", True, "Analysis completed successfully")
        
        # Test with no date column
        self.logger.log_section("No Date Column Test")
        no_date_analysis = self.analyzer.generate_timescale_analysis(self.no_date_df)
        self.assertIn("No date column found", no_date_analysis)
        self.logger.log_message("Analysis Output:")
        self.logger.log_message(no_date_analysis)
        self.logger.log_test_result("No Date Column", True, "Correctly identified missing date column")
        
        # Test with empty dataframe
        self.logger.log_section("Empty DataFrame Test")
        empty_df_analysis = self.analyzer.generate_timescale_analysis(self.empty_df)
        self.assertIn("No date column found", empty_df_analysis)
        self.logger.log_message("Analysis Output:")
        self.logger.log_message(empty_df_analysis)
        self.logger.log_test_result("Empty DataFrame", True, "Correctly handled empty dataframe")
        
        # Test with single row data
        self.logger.log_section("Single Row Test")
        self.logger.log_dataframe(self.single_row_df, "Single Row Data")
        
        single_row_analysis = self.analyzer.generate_timescale_analysis(self.single_row_df)
        self.assertIsInstance(single_row_analysis, str)
        self.assertGreater(len(single_row_analysis), 0)
        
        self.logger.log_message("Analysis Output:")
        self.logger.log_message(single_row_analysis)
        self.logger.log_test_result("Single Row Analysis", True, "Analysis handled single row case")
        
        # Check numeric formatting in output
        # Numbers should be properly formatted with decimal points
        pattern = r'\d+\.\d+%'  # Pattern for numbers like 10.50%
        self.assertTrue(re.search(pattern, daily_analysis))
        
        # Finish log
        self.logger.finish_test_log()
    
    # Test error handling
    def test_error_handling(self):
        """Test error handling for edge cases"""
        # Test with None dataframe
        try:
            self.analyzer.generate_timescale_analysis(None)
            self.fail("Expected an exception when passing None dataframe")
        except Exception as e:
            # Expected exception
            pass
        
        # Test with invalid date column data
        df_invalid_dates = pd.DataFrame({
            'date': ['invalid', 'not-a-date', 'bad-format'],
            'value': [1, 2, 3]
        })
        
        # Should handle gracefully without crashing
        analysis = self.analyzer.generate_timescale_analysis(df_invalid_dates)
        self.assertIsInstance(analysis, str)

if __name__ == "__main__":
    unittest.main()
