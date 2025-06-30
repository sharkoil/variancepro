"""
VariancePro TimescaleAnalyzer Edge Case Tests

This test suite focuses on challenging edge cases to ensure the TimescaleAnalyzer
is robust against unusual data patterns, errors, and exceptional conditions.

Edge cases tested include:
1. Irregular time intervals
2. Missing data and gaps
3. Extreme outliers
4. Mixed data types
5. Very large and very small datasets
6. Negative values
"""

import unittest
import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings

# Add parent directory to path to import from app.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the TimescaleAnalyzer class from app.py
from app import TimescaleAnalyzer

class TestTimescaleAnalyzerEdgeCases(unittest.TestCase):
    """Test suite for TimescaleAnalyzer edge cases"""
    
    def setUp(self):
        """Setup test environment before each test"""
        self.analyzer = TimescaleAnalyzer()
        
        # Create edge case datasets
        self.irregular_intervals_df = self._create_irregular_intervals_dataset()
        self.missing_data_df = self._create_missing_data_dataset()
        self.outliers_df = self._create_outliers_dataset()
        self.mixed_types_df = self._create_mixed_types_dataset()
        self.single_row_df = self._create_single_row_dataset()
        self.very_large_df = self._create_very_large_dataset()
        self.negative_values_df = self._create_negative_values_dataset()
    
    def _create_irregular_intervals_dataset(self):
        """Create dataset with irregular time intervals"""
        # Create irregular date sequence
        dates = []
        date = datetime(2020, 1, 1)
        
        # Add 30 dates with irregular intervals
        for _ in range(30):
            dates.append(date)
            # Random skip between 1 and 15 days
            skip_days = np.random.randint(1, 16)
            date += timedelta(days=skip_days)
        
        # Create values with some trend
        values = [100 + (i * 5) + np.random.normal(0, 10) for i in range(len(dates))]
        
        # Create DataFrame
        df = pd.DataFrame({
            'date': dates,
            'value': values
        })
        
        return df
    
    def _create_missing_data_dataset(self):
        """Create dataset with missing data points"""
        # Create regular date sequence
        dates = pd.date_range(start='2020-01-01', end='2022-12-31', freq='M')
        
        # Create values
        values = [100 + (i * 5) + np.random.normal(0, 10) for i in range(len(dates))]
        
        # Create DataFrame
        df = pd.DataFrame({
            'date': dates,
            'value': values
        })
        
        # Introduce missing values at random positions
        missing_indices = np.random.choice(len(df), size=int(len(df) * 0.3), replace=False)
        df.loc[missing_indices, 'value'] = np.nan
        
        return df
    
    def _create_outliers_dataset(self):
        """Create dataset with extreme outliers"""
        # Create regular date sequence
        dates = pd.date_range(start='2020-01-01', end='2022-12-31', freq='M')
        
        # Create values
        values = [100 + (i * 5) + np.random.normal(0, 10) for i in range(len(dates))]
        
        # Create DataFrame
        df = pd.DataFrame({
            'date': dates,
            'value': values
        })
        
        # Introduce outliers at random positions
        outlier_indices = np.random.choice(len(df), size=3, replace=False)
        df.loc[outlier_indices[0], 'value'] = df['value'].max() * 10  # 10x max
        df.loc[outlier_indices[1], 'value'] = df['value'].min() / 10  # 1/10x min
        df.loc[outlier_indices[2], 'value'] = df['value'].mean() * -5  # -5x mean
        
        return df
    
    def _create_mixed_types_dataset(self):
        """Create dataset with mixed data types"""
        # Create regular date sequence
        dates = pd.date_range(start='2020-01-01', end='2022-12-31', freq='M')
        
        # Create values
        values = [100 + (i * 5) + np.random.normal(0, 10) for i in range(len(dates))]
        
        # Create string values (some that look like numbers)
        str_values = []
        for i in range(len(dates)):
            if i % 5 == 0:
                str_values.append(str(int(values[i])))  # Number as string
            elif i % 5 == 1:
                str_values.append(f"${values[i]:.2f}")  # Currency format
            elif i % 5 == 2:
                str_values.append(f"{values[i]:.2f}%")  # Percentage format
            elif i % 5 == 3:
                str_values.append(f"{values[i]:.2f}K")  # K-format
            else:
                str_values.append("N/A")  # Non-numeric
        
        # Create DataFrame
        df = pd.DataFrame({
            'date': dates,
            'numeric_value': values,
            'string_value': str_values,
            'mixed_value': [values[i] if i % 2 == 0 else str_values[i] for i in range(len(dates))]
        })
        
        return df
    
    def _create_single_row_dataset(self):
        """Create dataset with only one row"""
        return pd.DataFrame({
            'date': [datetime(2023, 1, 1)],
            'value': [100]
        })
    
    def _create_very_large_dataset(self):
        """Create a very large dataset (daily data over many years)"""
        # Daily data over 10 years (this is a reduced version for test performance)
        # In real-world scenarios, this might be much larger
        dates = pd.date_range(start='2010-01-01', end='2022-12-31', freq='D')
        
        # Create values with trend and some noise
        values = [100 + (i * 0.1) + np.random.normal(0, 5) for i in range(len(dates))]
        
        # Create DataFrame
        df = pd.DataFrame({
            'date': dates,
            'value': values
        })
        
        return df
    
    def _create_negative_values_dataset(self):
        """Create dataset with negative values"""
        # Create regular date sequence
        dates = pd.date_range(start='2020-01-01', end='2022-12-31', freq='M')
        
        # Create values that oscillate between positive and negative
        values = []
        for i in range(len(dates)):
            base = 100 + (i * 5)
            if i % 3 == 0:
                values.append(-base)  # Negative
            else:
                values.append(base)  # Positive
        
        # Create DataFrame
        df = pd.DataFrame({
            'date': dates,
            'value': values,
            'always_negative': [-abs(v) for v in values],
            'profit': [v - 150 for v in values]  # Starts negative, might become positive
        })
        
        return df
    
    def test_irregular_intervals(self):
        """Test analyzer with irregular time intervals"""
        # Skip warning about non-fixed frequency
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            
            # Run analysis
            analysis_result = self.analyzer.generate_timescale_analysis(self.irregular_intervals_df)
            
            # Test should not crash
            self.assertIsInstance(analysis_result, str)
            self.assertGreater(len(analysis_result), 0)
            
            # Check aggregations
            aggs = self.analyzer.prepare_timescale_aggregations(
                self.irregular_intervals_df, 'date', ['value']
            )
            
            # At least one time scale should be present
            self.assertGreater(len(aggs), 0)
    
    def test_missing_data(self):
        """Test analyzer with missing data"""
        # Run analysis
        analysis_result = self.analyzer.generate_timescale_analysis(self.missing_data_df)
        
        # Test should not crash
        self.assertIsInstance(analysis_result, str)
        self.assertGreater(len(analysis_result), 0)
        
        # Check aggregations
        aggs = self.analyzer.prepare_timescale_aggregations(
            self.missing_data_df, 'date', ['value']
        )
        
        # All time scales should be present
        self.assertIn('monthly', aggs)
        self.assertIn('quarterly', aggs)
        self.assertIn('yearly', aggs)
        
        # Calculate POP analysis
        pop_analysis = self.analyzer.calculate_period_over_period_analysis(
            aggs, ['value']
        )
        
        # Check that NaN values are handled properly
        for scale in ['monthly', 'quarterly', 'yearly']:
            self.assertIn('value', pop_analysis[scale])
            
            # Values array should not be empty
            self.assertGreater(len(pop_analysis[scale]['value']['values']), 0)
            
            # All values should be finite numbers (no NaN)
            for value in pop_analysis[scale]['value']['values']:
                self.assertFalse(pd.isna(value), "NaN value found in aggregated data")
    
    def test_outliers(self):
        """Test analyzer with extreme outliers"""
        # Run analysis
        analysis_result = self.analyzer.generate_timescale_analysis(self.outliers_df)
        
        # Test should not crash
        self.assertIsInstance(analysis_result, str)
        self.assertGreater(len(analysis_result), 0)
        
        # Check aggregations and POP analysis
        aggs = self.analyzer.prepare_timescale_aggregations(
            self.outliers_df, 'date', ['value']
        )
        
        pop_analysis = self.analyzer.calculate_period_over_period_analysis(
            aggs, ['value']
        )
        
        # Check monthly values - outliers should be included
        monthly_values = pop_analysis['monthly']['value']['values']
        monthly_max = max(monthly_values)
        
        # The max aggregated value should be significantly higher than the median
        monthly_median = np.median(monthly_values)
        self.assertGreater(monthly_max, monthly_median * 5)
    
    def test_mixed_types(self):
        """Test analyzer with mixed data types"""
        # Run analysis
        analysis_result = self.analyzer.generate_timescale_analysis(self.mixed_types_df)
        
        # Test should not crash
        self.assertIsInstance(analysis_result, str)
        self.assertGreater(len(analysis_result), 0)
        
        # Check that only numeric columns are analyzed
        aggs = self.analyzer.prepare_timescale_aggregations(
            self.mixed_types_df, 'date', []  # Auto-detect numeric columns
        )
        
        # Only numeric_value should be in the aggregations
        for scale in ['monthly', 'quarterly', 'yearly']:
            self.assertIn('numeric_value', aggs[scale]['data'].columns)
            self.assertNotIn('string_value', aggs[scale]['data'].columns)
            
            # mixed_value might be included if it was properly converted to numeric
            if 'mixed_value' in aggs[scale]['data'].columns:
                # All values should be finite numbers
                self.assertTrue(aggs[scale]['data']['mixed_value'].notna().all())
    
    def test_single_row(self):
        """Test analyzer with single row dataset"""
        # Run analysis
        analysis_result = self.analyzer.generate_timescale_analysis(self.single_row_df)
        
        # Test should not crash and should return a meaningful message
        self.assertIsInstance(analysis_result, str)
        self.assertGreater(len(analysis_result), 0)
        
        # Should mention that there's not enough data for period-over-period analysis
        self.assertTrue(
            any(phrase in analysis_result.lower() for phrase in 
                ['insufficient data', 'not enough data', 'single data point', 
                 'unable to perform', 'cannot analyze'])
        )
    
    def test_very_large_dataset(self):
        """Test analyzer with very large dataset"""
        # Run analysis
        analysis_result = self.analyzer.generate_timescale_analysis(self.very_large_df)
        
        # Test should not crash
        self.assertIsInstance(analysis_result, str)
        self.assertGreater(len(analysis_result), 0)
        
        # All time scales should be present
        for scale in ['week', 'month', 'quarter', 'year']:
            self.assertIn(scale.lower(), analysis_result.lower())
        
        # Check performance (should handle large datasets efficiently)
        import time
        start_time = time.time()
        
        # Prepare aggregations
        aggs = self.analyzer.prepare_timescale_aggregations(
            self.very_large_df, 'date', ['value']
        )
        
        # Calculate POP analysis
        pop_analysis = self.analyzer.calculate_period_over_period_analysis(
            aggs, ['value']
        )
        
        end_time = time.time()
        
        # Should process quickly (adjust threshold as needed for test environment)
        # This is just a sanity check to catch major performance issues
        processing_time = end_time - start_time
        self.assertLess(processing_time, 5.0, 
                       f"Processing time for large dataset too slow: {processing_time:.2f} seconds")
    
    def test_negative_values(self):
        """Test analyzer with negative values"""
        # Run analysis
        analysis_result = self.analyzer.generate_timescale_analysis(self.negative_values_df)
        
        # Test should not crash
        self.assertIsInstance(analysis_result, str)
        self.assertGreater(len(analysis_result), 0)
        
        # Check aggregations and POP analysis
        aggs = self.analyzer.prepare_timescale_aggregations(
            self.negative_values_df, 'date', ['value', 'always_negative', 'profit']
        )
        
        pop_analysis = self.analyzer.calculate_period_over_period_analysis(
            aggs, ['value', 'always_negative', 'profit']
        )
        
        # Check monthly values
        monthly_values = pop_analysis['monthly']['value']['values']
        monthly_pct_changes = pop_analysis['monthly']['value']['pct_changes']
        
        # Should correctly handle percentage change from negative to positive and vice versa
        # Find transitions from negative to positive or vice versa
        for i in range(1, len(monthly_values)):
            if (monthly_values[i-1] < 0 and monthly_values[i] > 0) or \
               (monthly_values[i-1] > 0 and monthly_values[i] < 0):
                # Just verify there's a percentage change calculated and it's not NaN
                # The exact value depends on how the analyzer handles sign changes
                self.assertFalse(pd.isna(monthly_pct_changes[i]))
        
        # Check always negative values
        always_neg_values = pop_analysis['monthly']['always_negative']['values']
        always_neg_pct_changes = pop_analysis['monthly']['always_negative']['pct_changes']
        
        # All values should be negative
        for value in always_neg_values:
            self.assertLess(value, 0)
        
        # Percentage changes should be calculated correctly for negative values
        for i in range(1, len(always_neg_pct_changes)):
            if not pd.isna(always_neg_pct_changes[i]):
                # If value becomes more negative, change should be negative
                # If value becomes less negative, change should be positive
                v1 = always_neg_values[i-1]
                v2 = always_neg_values[i]
                expected_sign = 1 if abs(v2) < abs(v1) else -1
                actual_sign = 1 if always_neg_pct_changes[i] > 0 else -1
                
                self.assertEqual(actual_sign, expected_sign, 
                               f"Percentage change sign wrong for negative values: {v1} to {v2}")

if __name__ == "__main__":
    unittest.main()
