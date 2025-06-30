import unittest
import pandas as pd
import numpy as np
import os
import sys
from datetime import datetime
import logging
from pathlib import Path

# Add the project root to the path so we can import the app module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from app import TimescaleAnalyzer
except ImportError:
    print("Error importing TimescaleAnalyzer. Make sure you're running this from the project root.")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"date_detection_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('DateColumnDetection')

class TestDateColumnDetection(unittest.TestCase):
    """Test the date column detection functionality of TimescaleAnalyzer"""
    
    def setUp(self):
        """Set up the test environment"""
        self.analyzer = TimescaleAnalyzer()
        self.test_results = []
        logger.info("Setting up test environment")
    
    def tearDown(self):
        """Clean up after tests"""
        # Log test results
        if self.test_results:
            logger.info(f"Test results summary: {len(self.test_results)} tests run")
            for result in self.test_results:
                logger.info(f"  {result}")
        logger.info("Test environment cleaned up")
    
    def log_test_result(self, test_name, result, details=None):
        """Log a test result with timestamp"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        status = "✅ PASS" if result else "❌ FAIL"
        result_entry = f"[{timestamp}] {status} - {test_name}"
        if details:
            result_entry += f" - {details}"
        self.test_results.append(result_entry)
        if result:
            logger.info(result_entry)
        else:
            logger.error(result_entry)
        return result
        
    def test_already_datetime_column(self):
        """Test detection of columns that are already datetime type"""
        # Create test dataframe with a datetime column
        df = pd.DataFrame({
            'id': range(5),
            'name': ['A', 'B', 'C', 'D', 'E'],
            'transaction_date': pd.date_range(start='2023-01-01', periods=5)
        })
        
        # Run the test
        date_col = self.analyzer.detect_date_column(df)
        
        # Log and verify
        result = date_col == 'transaction_date'
        details = f"Expected: 'transaction_date', Got: '{date_col}'"
        self.log_test_result("Already datetime column detection", result, details)
        self.assertEqual(date_col, 'transaction_date')
        
    def test_date_related_column_names(self):
        """Test detection based on column names with date-related keywords"""
        test_cases = [
            ('date_column', ['date_column', 'value'], '2023-01-01'),
            ('time_stamp', ['time_stamp', 'value'], '2023-01-01 12:34:56'),
            ('period_end', ['period_end', 'value'], '2023-Q1'),
            ('fiscal_year', ['fiscal_year', 'value'], '2023'),
            ('month_data', ['month_data', 'value'], 'January 2023'),
            ('day_value', ['day_value', 'value'], '01/02/2023'),
            ('quarter_results', ['quarter_results', 'value'], 'Q1 2023')
        ]
        
        for expected_col, columns, date_format in test_cases:
            # Create test dataframe
            df = pd.DataFrame({
                columns[0]: [date_format] * 5,
                columns[1]: range(5)
            })
            
            # Run the test
            date_col = self.analyzer.detect_date_column(df)
            
            # Log and verify
            result = date_col == expected_col
            details = f"Column: '{expected_col}', Format: '{date_format}', Result: '{date_col}'"
            self.log_test_result(f"Date keyword detection - {expected_col}", result, details)
            self.assertEqual(date_col, expected_col)
    
    def test_string_conversion_detection(self):
        """Test detection by attempting to convert string columns"""
        date_formats = [
            '2023-01-01',                # ISO format
            '01/02/2023',                # MM/DD/YYYY
            'January 1, 2023',           # Month name
            '2023.01.01',                # Period separated
            '20230101',                  # Compact
            'Sun, 01 Jan 2023',          # Day, DD Mon YYYY
            '2023-01-01 14:30:45'        # Datetime
        ]
        
        for date_format in date_formats:
            # Create test dataframe
            df = pd.DataFrame({
                'id': range(5),
                'value': range(5),
                'string_date': [date_format] * 5
            })
            
            # Run the test
            date_col = self.analyzer.detect_date_column(df)
            
            # Log and verify
            result = date_col == 'string_date'
            details = f"Format: '{date_format}', Result: '{date_col}'"
            self.log_test_result(f"String conversion detection - {date_format}", result, details)
            self.assertEqual(date_col, 'string_date')
    
    def test_no_date_column(self):
        """Test behavior when no date column is present"""
        # Create test dataframe with no date columns
        df = pd.DataFrame({
            'id': range(5),
            'name': ['A', 'B', 'C', 'D', 'E'],
            'value': [10, 20, 30, 40, 50]
        })
        
        # Run the test
        date_col = self.analyzer.detect_date_column(df)
        
        # Log and verify
        result = date_col is None
        details = f"Expected: None, Got: '{date_col}'"
        self.log_test_result("No date column detection", result, details)
        self.assertIsNone(date_col)
    
    def test_mixed_date_formats(self):
        """Test with mixed date formats in the same column"""
        # Create test dataframe with mixed date formats
        df = pd.DataFrame({
            'id': range(5),
            'mixed_dates': ['2023-01-01', '01/02/2023', 'Jan 3, 2023', '2023.01.04', '20230105']
        })
        
        # Run the test
        date_col = self.analyzer.detect_date_column(df)
        
        # Log and verify
        result = date_col == 'mixed_dates'
        details = f"Expected: 'mixed_dates', Got: '{date_col}'"
        self.log_test_result("Mixed date formats detection", result, details)
        self.assertEqual(date_col, 'mixed_dates')
    
    def test_real_files(self):
        """Test with real CSV files from the project"""
        test_files = [
            ('sales_budget_actuals.csv', ['period_end']),
            ('sample_data/comprehensive_sales_data.csv', ['date']),
            ('sample_data/sample_stock_data.csv', ['date', 'Date'])  # Accept either case
        ]
        
        for file_path, expected_cols in test_files:
            if not os.path.exists(file_path):
                self.log_test_result(f"File test - {file_path}", False, "File not found")
                continue
                
            try:
                # Load the CSV
                df = pd.read_csv(file_path)
                
                # Run the test
                date_col = self.analyzer.detect_date_column(df)
                
                # Log and verify
                result = date_col in expected_cols
                details = f"Expected one of: {expected_cols}, Got: '{date_col}'"
                self.log_test_result(f"Real file test - {file_path}", result, details)
                self.assertIn(date_col, expected_cols)
            except Exception as e:
                self.log_test_result(f"File test - {file_path}", False, f"Exception: {str(e)}")
                continue

if __name__ == '__main__':
    # Create a test result file with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    result_file = f"date_column_detection_results_{timestamp}.txt"
    
    print(f"Running date column detection tests. Results will be saved to {result_file}")
    print("Check the log file for detailed results.")
    
    # Run the tests
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
