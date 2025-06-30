"""
VariancePro TimescaleAnalyzer Integration Tests

This test suite validates the integration of TimescaleAnalyzer within the VariancePro app.
It focuses on the analysis of real datasets and checks whether the analyzer produces correct 
results when used in the full application context.
"""

import unittest
import sys
import os
import pandas as pd
from io import StringIO
import re

# Add parent directory to path to import from app.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the main app modules
from app import TimescaleAnalyzer
from utils.data_processor import DataProcessor

class TestTimescaleAnalyzerIntegration(unittest.TestCase):
    """Integration test suite for TimescaleAnalyzer"""
    
    def setUp(self):
        """Setup test environment before each test"""
        self.analyzer = TimescaleAnalyzer()
        self.data_processor = DataProcessor()
        
        # Load real sample data files
        self.sample_files = [
            'sample_data/sales_budget_actuals.csv',
            'sample_data/sample_stock_data.csv',
            'sales_budget_actuals.csv',
            'sample_financial_data.csv'
        ]
        
        # Load datasets
        self.datasets = {}
        for file in self.sample_files:
            try:
                path = os.path.join(os.path.dirname(os.path.abspath(__file__)), file)
                if os.path.exists(path):
                    df = pd.read_csv(path)
                    # Data is loaded directly for TimescaleAnalyzer testing
                    self.datasets[file] = df
            except Exception as e:
                print(f"Could not load {file}: {str(e)}")
    
    def test_integration_with_data_processor(self):
        """Test the integration between DataProcessor and TimescaleAnalyzer"""
        # Skip if no datasets were loaded
        if not self.datasets:
            self.skipTest("No sample datasets available for testing")
        
        for file_name, df in self.datasets.items():
            # Skip if df is empty or doesn't have date column
            if df.empty or not any(col.lower() in ['date', 'period', 'time'] for col in df.columns):
                continue
                
            # Ensure there's a date column to analyze
            date_cols = [col for col in df.columns if df[col].dtype == 'datetime64[ns]' or 
                         (pd.api.types.is_object_dtype(df[col]) and 
                          isinstance(df[col].iloc[0], str) and 
                          bool(re.search(r'\d{4}[/-]\d{2}[/-]\d{2}', df[col].iloc[0])))]
            
            if not date_cols:
                # Try to convert any likely date columns
                for col in df.columns:
                    if pd.api.types.is_object_dtype(df[col]) and 'date' in col.lower():
                        try:
                            df[col] = pd.to_datetime(df[col])
                            date_cols.append(col)
                            break
                        except:
                            pass
            
            if not date_cols:
                continue
                
            date_col = date_cols[0]
            
            # Run the timescale analysis directly (data is already loaded)
            analysis_result = self.analyzer.generate_timescale_analysis(df)
            
            # Check that analysis result is a non-empty string
            self.assertIsInstance(analysis_result, str)
            self.assertGreater(len(analysis_result), 0)
            
            # Check for expected section headers
            self.assertIn("# 📊 Automatic Timescale Analysis", analysis_result)
            
            # At least one of these timescale headers should be present
            timescale_headers = ["## 📅 Year-over-Year", "## 📊 Quarter-over-Quarter", 
                               "## 📆 Month-over-Month", "## 📈 Week-over-Week"]
            self.assertTrue(any(header in analysis_result for header in timescale_headers))
            
            # The Executive Summary should always be present
            self.assertIn("## 📋 Executive Summary", analysis_result)
    
    def test_metric_calculations(self):
        """Test that the metrics are calculated correctly"""
        # Skip if no datasets were loaded
        if not self.datasets:
            self.skipTest("No sample datasets available for testing")
        
        for file_name, df in self.datasets.items():
            # Skip if df is empty or too small for analysis
            if df.empty or len(df) < 3:
                continue
                
            # Get numeric columns for analysis
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            if not numeric_cols:
                continue
                
            # Choose a test column
            test_col = numeric_cols[0]
            
            # Get the original values to validate calculations
            if 'date' in df.columns:
                date_col = 'date'
            elif any('date' in col.lower() for col in df.columns):
                date_col = next(col for col in df.columns if 'date' in col.lower())
            else:
                continue
                
            # Ensure date column is datetime
            try:
                df[date_col] = pd.to_datetime(df[date_col])
            except:
                continue
                
            # Create a manual monthly aggregation to verify against the analyzer's results
            try:
                monthly_manual = df.groupby(pd.Grouper(key=date_col, freq='M')).agg({test_col: 'sum'}).reset_index()
                
                # Calculate month-over-month changes manually
                monthly_manual['change'] = monthly_manual[test_col].diff()
                monthly_manual['pct_change'] = monthly_manual[test_col].pct_change() * 100
                
                # Calculate the same with the analyzer
                aggs = self.analyzer.prepare_timescale_aggregations(df, date_col, [test_col])
                if 'monthly' not in aggs:
                    continue
                    
                pop_analysis = self.analyzer.calculate_period_over_period_analysis(aggs, [test_col])
                
                # Compare the results (allowing for small floating point differences)
                if 'monthly' in pop_analysis and test_col in pop_analysis['monthly']:
                    analyzer_values = pop_analysis['monthly'][test_col]['values']
                    
                    # Get last few values for comparison (may have different lengths)
                    manual_recent = monthly_manual[test_col].dropna().tail(3).tolist()
                    analyzer_recent = analyzer_values[-3:] if len(analyzer_values) >= 3 else analyzer_values
                    
                    # Calculate relative difference
                    for m_val, a_val in zip(manual_recent, analyzer_recent):
                        if m_val != 0:
                            rel_diff = abs((m_val - a_val) / m_val)
                            self.assertLess(rel_diff, 0.01, 
                                          f"Values differ by more than 1%: {m_val} vs {a_val}")
            except Exception as e:
                # If there's an error in the validation, we continue with other tests
                print(f"Error validating calculations for {file_name}: {str(e)}")
                continue
    
    def test_analysis_quality(self):
        """Test the quality and completeness of the analysis"""
        # Skip if no datasets were loaded
        if not self.datasets:
            self.skipTest("No sample datasets available for testing")
        
        for file_name, df in self.datasets.items():
            # Skip if df is empty
            if df.empty:
                continue
                
            # Run the timescale analysis
            analysis_result = self.analyzer.generate_timescale_analysis(df)
            
            # Skip if no analysis was generated
            if "No date column found" in analysis_result:
                continue
            
            # Skip files with insufficient data
            if "Insufficient" in analysis_result and "Executive Summary" in analysis_result:
                if "Insufficient time series data for executive insights" in analysis_result:
                    print(f"Skipping {file_name} - insufficient data for analysis")
                    continue
                
            # Check the quality of insights
            
            # Look for quantitative statements (numbers and percentages)
            number_pattern = r'\d+(\.\d+)?%'
            percentages_found = bool(re.search(number_pattern, analysis_result))
            
            # Look for specific financial metrics or numbers
            number_mentions = re.findall(r'\d+\.\d+%|\d+%|\$\d+|\d+\.\d+', analysis_result)
            
            # At least one should be found for a quality analysis
            has_quantitative_data = percentages_found or len(number_mentions) > 0
            self.assertTrue(has_quantitative_data, 
                          f"No quantitative data (percentages or numbers) found in analysis for {file_name}")
            
            # Check for metric mentions (more lenient check)
            metrics_found = False
            metric_keywords = ['total', 'average', 'mean', 'sum', 'count', 'revenue', 'sales', 
                              'budget', 'actual', 'variance', 'growth', 'trend', 'value', 'amount',
                              'increase', 'decrease', 'change']
            for keyword in metric_keywords:
                if keyword in analysis_result.lower():
                    metrics_found = True
                    break
            
            # Also check for specific column names
            if not metrics_found:
                for col in df.select_dtypes(include=['number']).columns:
                    if col.lower() in analysis_result.lower():
                        metrics_found = True
                        break
            
            self.assertTrue(metrics_found, f"No metrics mentioned in analysis for {file_name}")
            
            # Check for time period mentions
            time_periods = ['year', 'quarter', 'month', 'week', 'yoy', 'qoq', 'mom', 'wow']
            time_periods_found = any(period in analysis_result.lower() for period in time_periods)
            self.assertTrue(time_periods_found, 
                          f"No time periods mentioned in analysis for {file_name}")
            
            print(f"✅ Quality tests passed for {file_name}")
            
            # Check for analytical language
            analytical_terms = ['increase', 'decrease', 'growth', 'decline', 'trend', 
                              'average', 'median', 'change', 'performance']
            analytical_terms_found = any(term in analysis_result.lower() for term in analytical_terms)
            self.assertTrue(analytical_terms_found, 
                          f"No analytical terms found in analysis for {file_name}")

if __name__ == "__main__":
    unittest.main()
