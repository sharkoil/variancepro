"""
VariancePro Date Column Detection Test

This script specifically tests the date column detection functionality in the TimescaleAnalyzer 
and logs detailed results for review. It's designed to help identify and fix issues with 
date column detection in various file formats.
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime
import traceback

# Add parent directory to path to import from app.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the TimescaleAnalyzer class from app.py
from app import TimescaleAnalyzer
from utils.test_logger import TestResultLogger

def test_date_column_detection():
    """Test date column detection across different CSV files and date column names"""
    
    # Initialize the test logger
    logger = TestResultLogger()
    logger.start_test_log("date_column_detection")
    
    # Initialize the analyzer
    analyzer = TimescaleAnalyzer()
    
    # List of sample files to test
    sample_files = [
        'sales_budget_actuals.csv',
        'sample_financial_data.csv',
        'sample_data/sales_budget_actuals.csv',
        'sample_data/sample_stock_data.csv',
        'sample_data/comprehensive_sales_data.csv'
    ]
    
    # Log test start
    logger.log_message(f"Testing date column detection on {len(sample_files)} sample files")
    logger.log_message(f"Current directory: {os.getcwd()}")
    
    # Test each file
    for file_path in sample_files:
        logger.log_section(f"Testing file: {file_path}")
        
        try:
            # Check if file exists
            full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), file_path)
            if not os.path.exists(full_path):
                logger.log_message(f"File not found: {full_path}")
                continue
            
            # Load the file
            df = pd.read_csv(full_path)
            logger.log_message(f"Successfully loaded file with {len(df)} rows and {len(df.columns)} columns")
            
            # Log column names and types
            column_info = []
            for col in df.columns:
                dtype = str(df[col].dtype)
                sample_values = str(df[col].head(3).tolist())
                column_info.append(f"- {col}: {dtype}, Sample: {sample_values}")
            
            logger.log_message("Columns in the dataset:")
            for info in column_info:
                logger.log_message(info)
            
            # Try to detect date columns
            logger.log_message("\nChecking for date columns:")
            
            # Get all columns that contain date-like strings
            date_like_cols = []
            for col in df.columns:
                try:
                    # Try to convert to datetime
                    pd.to_datetime(df[col].head(5))
                    date_like_cols.append(col)
                    logger.log_message(f"- {col}: Successfully converted to datetime")
                except:
                    # Check if column name contains date-related keywords
                    if any(keyword in col.lower() for keyword in ['date', 'time', 'period', 'year', 'month', 'day']):
                        logger.log_message(f"- {col}: Name suggests date but conversion failed")
            
            # Log detected date columns
            if date_like_cols:
                logger.log_message(f"\nDetected {len(date_like_cols)} potential date columns: {date_like_cols}")
            else:
                logger.log_message("\nNo date columns detected through conversion testing")
            
            # Test the analyzer's built-in date column detection
            # Call a separate function to detect date columns from the analyzer
            logger.log_section(f"Testing TimescaleAnalyzer on {file_path}")
            
            # Run the full analysis
            analysis_result = analyzer.generate_timescale_analysis(df)
            
            # Check for the error message
            if "No date column found" in analysis_result:
                logger.log_message("❌ FAILED: TimescaleAnalyzer could not detect date column")
                logger.log_message("Analysis Result:")
                logger.log_message(analysis_result)
                
                # Log this as a test failure
                logger.log_test_result(f"Date detection in {file_path}", False, 
                                     "TimescaleAnalyzer failed to detect date column")
            else:
                logger.log_message("✅ SUCCESS: TimescaleAnalyzer detected date column")
                logger.log_message("First 500 characters of analysis:")
                logger.log_message(analysis_result[:500] + "...")
                
                # Log this as a test success
                logger.log_test_result(f"Date detection in {file_path}", True, 
                                     "TimescaleAnalyzer successfully detected date column")
            
        except Exception as e:
            logger.log_message(f"Error processing file {file_path}: {str(e)}")
            logger.log_exception(e)
    
    # Log test completion
    logger.finish_test_log()
    
    return logger.current_log_path

def generate_date_columns_test_file():
    """Generate a test file with various date column formats for testing"""
    
    # Create a dataset with different date column names and formats
    num_rows = 100
    start_date = datetime(2020, 1, 1)
    
    # Create date ranges
    dates = [start_date + pd.Timedelta(days=i) for i in range(num_rows)]
    
    # Create the dataframe with different date column naming conventions
    df = pd.DataFrame({
        'date': dates,
        'Date': dates,
        'DATE': dates,
        'transaction_date': dates,
        'TransactionDate': dates,
        'date_of_transaction': dates,
        'time': dates,
        'timestamp': dates,
        'period': dates,
        'period_end': dates,
        'periodEnd': dates,
        'PERIOD_END_DATE': dates,
        'year_month': [d.strftime('%Y-%m') for d in dates],
        'fiscal_period': [f"FY{d.year}P{d.month}" for d in dates],
        'year': [d.year for d in dates],
        'month': [d.month for d in dates],
        'day': [d.day for d in dates],
        'quarter': [f"Q{(d.month-1)//3 + 1}" for d in dates],
        
        # Add some numeric columns
        'sales': np.random.normal(1000, 100, size=num_rows),
        'costs': np.random.normal(700, 50, size=num_rows),
        'profit': np.random.normal(300, 30, size=num_rows),
        
        # Add some categorical columns
        'region': np.random.choice(['North', 'South', 'East', 'West'], size=num_rows),
        'product': np.random.choice(['Product A', 'Product B', 'Product C'], size=num_rows)
    })
    
    # Save the test file
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                             'sample_data', 'date_column_test.csv')
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Save the file
    df.to_csv(output_path, index=False)
    
    return output_path

def run_all_tests():
    """Run all date detection tests and create a summary report"""
    
    # Generate the test file
    test_file_path = generate_date_columns_test_file()
    print(f"Generated test file: {test_file_path}")
    
    # Run the date column detection test
    log_path = test_date_column_detection()
    print(f"Test completed. Results saved to: {log_path}")
    
    return log_path

if __name__ == "__main__":
    run_all_tests()
