"""
VariancePro Sales Budget Actuals Test

This script specifically tests the TimescaleAnalyzer with the sales_budget_actuals.csv file
to diagnose and fix the date column detection issue.
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime

# Add parent directory to path to import from app.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the TimescaleAnalyzer class from app.py
from app import TimescaleAnalyzer
from utils.test_logger import TestResultLogger

def test_sales_budget_actuals_file():
    """Test the TimescaleAnalyzer with the sales_budget_actuals.csv file"""
    
    # Initialize the test logger
    logger = TestResultLogger()
    logger.start_test_log("sales_budget_actuals_test")
    
    # Initialize the analyzer
    analyzer = TimescaleAnalyzer()
    
    # File path
    file_path = 'sales_budget_actuals.csv'
    full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), file_path)
    
    # Check if file exists
    if not os.path.exists(full_path):
        logger.log_message(f"File not found: {full_path}")
        logger.finish_test_log(False)
        return logger.current_log_path
    
    # Log test start
    logger.log_message(f"Testing TimescaleAnalyzer with {file_path}")
    logger.log_message(f"File path: {full_path}")
    
    try:
        # Load the file
        df = pd.read_csv(full_path)
        logger.log_message(f"Successfully loaded file with {len(df)} rows and {len(df.columns)} columns")
        
        # Log column information
        logger.log_section("Column Information")
        for col in df.columns:
            dtype = str(df[col].dtype)
            sample_values = str(df[col].head(3).tolist())
            logger.log_message(f"- {col}: {dtype}, Sample: {sample_values}")
        
        # Examine the 'period_end' column specifically
        logger.log_section("Period End Column Analysis")
        if 'period_end' in df.columns:
            logger.log_message("'period_end' column found in the dataset")
            logger.log_message(f"Data type: {df['period_end'].dtype}")
            logger.log_message(f"Sample values: {df['period_end'].head(10).tolist()}")
            
            # Try to convert to datetime
            try:
                df['period_end'] = pd.to_datetime(df['period_end'])
                logger.log_message("Successfully converted 'period_end' to datetime")
                logger.log_message(f"New data type: {df['period_end'].dtype}")
                logger.log_message(f"Date range: {df['period_end'].min()} to {df['period_end'].max()}")
            except Exception as e:
                logger.log_message(f"Failed to convert 'period_end' to datetime: {str(e)}")
        else:
            logger.log_message("'period_end' column NOT found in the dataset")
            logger.log_message(f"Available columns: {df.columns.tolist()}")
        
        # Log the first few rows of the dataset
        logger.log_section("Dataset Sample")
        logger.log_dataframe(df.head(10), "First 10 rows")
        
        # Test the analyzer
        logger.log_section("TimescaleAnalyzer Test")
        logger.log_message("Running generate_timescale_analysis...")
        
        # Run the analysis
        analysis_result = analyzer.generate_timescale_analysis(df)
        
        # Check if the analysis failed due to no date column
        if "No date column found" in analysis_result:
            logger.log_message("❌ FAILED: TimescaleAnalyzer reported 'No date column found'")
            logger.log_message("Analysis Result:")
            logger.log_message(analysis_result)
            
            # Test manual detection
            logger.log_section("Manual Date Detection")
            date_cols = []
            for col in df.columns:
                try:
                    pd.to_datetime(df[col])
                    date_cols.append(col)
                    logger.log_message(f"- {col}: Successfully converted to datetime")
                except:
                    if any(keyword in col.lower() for keyword in ['date', 'time', 'period', 'year', 'month']):
                        logger.log_message(f"- {col}: Name suggests date but conversion failed")
            
            if date_cols:
                logger.log_message(f"Found {len(date_cols)} date columns: {date_cols}")
            else:
                logger.log_message("No date columns found through manual testing")
                
            # Try a custom fix - convert period_end if it exists
            if 'period_end' in df.columns:
                logger.log_section("Attempting Fix")
                try:
                    # Force conversion of period_end
                    df['period_end_datetime'] = pd.to_datetime(df['period_end'], errors='coerce')
                    logger.log_message("Created 'period_end_datetime' column")
                    logger.log_message(f"Non-null values: {df['period_end_datetime'].count()}/{len(df)}")
                    
                    # Try analysis again with fixed dataframe
                    logger.log_message("Running analysis with fixed dataframe...")
                    fixed_analysis = analyzer.generate_timescale_analysis(df)
                    
                    if "No date column found" in fixed_analysis:
                        logger.log_message("❌ Fix FAILED: Still cannot detect date column")
                    else:
                        logger.log_message("✅ Fix SUCCEEDED: Date column now detected")
                        logger.log_message("First 500 characters of analysis:")
                        logger.log_message(fixed_analysis[:500] + "...")
                except Exception as e:
                    logger.log_message(f"Error during fix attempt: {str(e)}")
        else:
            logger.log_message("✅ SUCCESS: TimescaleAnalyzer detected date column")
            logger.log_message("First 500 characters of analysis:")
            logger.log_message(analysis_result[:500] + "...")
        
    except Exception as e:
        logger.log_message(f"Error during test: {str(e)}")
        logger.log_exception(e)
        logger.finish_test_log(False)
        return logger.current_log_path
    
    # Log test completion
    logger.finish_test_log()
    return logger.current_log_path

if __name__ == "__main__":
    log_path = test_sales_budget_actuals_file()
    print(f"Test completed. Results saved to: {log_path}")
