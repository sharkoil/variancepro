"""
Test file specifically for the new ContributionAnalyzer implementation
"""

import unittest
import pandas as pd
import numpy as np
from app import ContributionAnalyzer

class TestContributionAnalyzer(unittest.TestCase):
    """Test the ContributionAnalyzer implementation"""
    
    def setUp(self):
        """Set up test data"""
        self.analyzer = ContributionAnalyzer()
        
        # Create test data similar to the Medium article example
        self.test_data = pd.DataFrame({
            'Product': ['Product_A', 'Product_B', 'Product_C', 'Product_D', 'Product_E',
                       'Product_F', 'Product_G', 'Product_H', 'Product_I', 'Product_J'],
            'Sales': [6500, 5200, 4100, 3800, 3600, 3400, 3200, 3100, 3050, 3000]
        })
        
        # Test data with time dimension
        self.time_data = pd.DataFrame({
            'Date': pd.date_range('2024-01-01', periods=12, freq='M'),
            'Product': ['Product_A'] * 12,
            'Sales': [1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100]
        })
    
    def test_perform_contribution_analysis_pandas(self):
        """Test the main pandas-based contribution analysis method"""
        result_df, summary, fig = self.analyzer.perform_contribution_analysis_pandas(
            self.test_data, 'Product', 'Sales'
        )
        
        # Check result structure
        self.assertIsInstance(result_df, pd.DataFrame)
        self.assertIsInstance(summary, dict)
        self.assertIsNotNone(fig)
        
        # Check required columns in result
        required_columns = ['Product', 'Sales', 'cumulative_sum', 'contribution', 
                          'individual_contribution', 'is_key_contributor', 'rank']
        for col in required_columns:
            self.assertIn(col, result_df.columns)
        
        # Check data is sorted correctly (descending by Sales)
        self.assertTrue(result_df['Sales'].is_monotonic_decreasing)
        
        # Check cumulative contribution reaches 1.0
        self.assertAlmostEqual(result_df['contribution'].iloc[-1], 1.0, places=2)
        
        # Check individual contributions sum to 1.0
        self.assertAlmostEqual(result_df['individual_contribution'].sum(), 1.0, places=2)
        
        # Check ranking
        self.assertEqual(result_df['rank'].tolist(), list(range(1, len(result_df) + 1)))
        
        print(f"✅ Basic contribution analysis test passed")
        print(f"   Key contributors: {summary['key_contributors_count']}/{summary['total_categories']}")
        print(f"   Key contributors share: {summary['key_contributors_value_share']:.1f}%")
    
    def test_pareto_analysis_method(self):
        """Test the original perform_pareto_analysis method"""
        result_df, fig = self.analyzer.perform_pareto_analysis(
            self.test_data, 'Product', 'Sales'
        )
        
        # Check result structure
        self.assertIsInstance(result_df, pd.DataFrame)
        self.assertIsNotNone(fig)
        
        # Check required columns
        expected_columns = ['Product', 'Sales', 'cumulative_sum', 'cumulative_pct', 
                          'individual_pct', 'is_key_contributor', 'rank']
        for col in expected_columns:
            self.assertIn(col, result_df.columns)
        
        print(f"✅ Pareto analysis method test passed")
    
    def test_time_based_analysis(self):
        """Test time-based contribution analysis"""
        result_df, summary, fig = self.analyzer.perform_contribution_analysis_pandas(
            self.time_data, 'Product', 'Sales', 'Date'
        )
        
        # Should work with time column
        self.assertIsInstance(result_df, pd.DataFrame)
        self.assertIsInstance(summary, dict)
        
        print(f"✅ Time-based analysis test passed")
    
    def test_analyze_time_based_contribution(self):
        """Test the time-based contribution analysis method"""
        # Create extended time data
        extended_data = []
        for month in range(1, 13):
            for product in ['Product_A', 'Product_B', 'Product_C']:
                extended_data.append({
                    'Date': f'2024-{month:02d}-01',
                    'Product': product,
                    'Sales': np.random.randint(1000, 5000)
                })
        
        df = pd.DataFrame(extended_data)
        df['Date'] = pd.to_datetime(df['Date'])
        
        results = self.analyzer.analyze_time_based_contribution(
            df, 'Product', 'Sales', 'Date', periods=3
        )
        
        # Check results structure
        self.assertIsInstance(results, dict)
        self.assertIn('meta_analysis', results)
        
        print(f"✅ Time-based contribution analysis test passed")
        print(f"   Periods analyzed: {results['meta_analysis']['periods_analyzed']}")
    
    def test_summary_generation(self):
        """Test the summary generation functionality"""
        result_df, summary, fig = self.analyzer.perform_contribution_analysis_pandas(
            self.test_data, 'Product', 'Sales'
        )
        
        # Check summary keys
        expected_keys = ['total_categories', 'key_contributors_count', 'key_contributors_percentage',
                        'key_contributors_value_share', 'threshold_used', 'total_value',
                        'key_contributors_list', 'top_contributor', 'insights']
        
        for key in expected_keys:
            self.assertIn(key, summary)
        
        # Check insights are generated
        self.assertIsInstance(summary['insights'], list)
        self.assertGreater(len(summary['insights']), 0)
        
        # Check top contributor structure
        self.assertIn('name', summary['top_contributor'])
        self.assertIn('value', summary['top_contributor'])
        self.assertIn('percentage', summary['top_contributor'])
        
        print(f"✅ Summary generation test passed")
        print(f"   Insights generated: {len(summary['insights'])}")
        for insight in summary['insights']:
            print(f"   - {insight}")
    
    def test_edge_cases(self):
        """Test edge cases and error handling"""
        # Empty dataframe
        empty_df = pd.DataFrame()
        try:
            result_df, summary, fig = self.analyzer.perform_contribution_analysis_pandas(
                empty_df, 'Product', 'Sales'
            )
            print("⚠️  Empty dataframe handled gracefully")
        except Exception as e:
            print(f"⚠️  Empty dataframe raised exception: {str(e)}")
        
        # Single row
        single_row = pd.DataFrame({'Product': ['A'], 'Sales': [100]})
        result_df, summary, fig = self.analyzer.perform_contribution_analysis_pandas(
            single_row, 'Product', 'Sales'
        )
        self.assertEqual(len(result_df), 1)
        self.assertEqual(summary['key_contributors_count'], 1)
        
        print(f"✅ Edge cases test passed")

if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)
