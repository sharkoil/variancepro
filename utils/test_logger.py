"""
Test Logger Utility for VariancePro

This module provides utilities for logging test results to a file with timestamps
for review and audit purposes. It's particularly useful for financial analysis
tests where maintaining proof of calculation accuracy is important.
"""

import os
import datetime
import traceback
import json
import pandas as pd
import numpy as np

class TestResultLogger:
    """Logger for capturing and storing test results in timestamped files"""
    
    def __init__(self, log_dir="test_logs"):
        """Initialize the test logger with a directory for logs"""
        self.log_dir = log_dir
        self.current_test_name = None
        self.current_log_path = None
        self.ensure_log_dir()
    
    def ensure_log_dir(self):
        """Ensure the log directory exists"""
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
    
    def start_test_log(self, test_name):
        """Start a new test log file with timestamp"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{test_name}_{timestamp}.txt"
        self.current_log_path = os.path.join(self.log_dir, filename)
        self.current_test_name = test_name
        
        # Create the log file with header
        with open(self.current_log_path, 'w', encoding='utf-8') as f:
            f.write(f"===== VariancePro Test Results: {test_name} =====\n")
            f.write(f"Started: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"System: {os.name}\n")
            f.write("=" * 60 + "\n\n")
        
        return self.current_log_path
    
    def log_message(self, message):
        """Log a simple message to the current test log"""
        if not self.current_log_path:
            raise ValueError("No test log started. Call start_test_log first.")
        
        with open(self.current_log_path, 'a', encoding='utf-8') as f:
            f.write(f"{message}\n")
    
    def log_section(self, section_name):
        """Log a section header to the current test log"""
        if not self.current_log_path:
            raise ValueError("No test log started. Call start_test_log first.")
        
        with open(self.current_log_path, 'a', encoding='utf-8') as f:
            f.write(f"\n\n----- {section_name} -----\n")
    
    def log_dataframe(self, df, description="DataFrame"):
        """Log a pandas DataFrame to the current test log"""
        if not self.current_log_path:
            raise ValueError("No test log started. Call start_test_log first.")
        
        with open(self.current_log_path, 'a', encoding='utf-8') as f:
            f.write(f"\n{description} (Shape: {df.shape}):\n")
            f.write(df.to_string(max_rows=20) + "\n")
            
            # Add statistical summary for numeric columns
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                f.write("\nNumeric Statistics:\n")
                f.write(df[numeric_cols].describe().to_string() + "\n")
    
    def log_dict(self, data_dict, description="Dictionary"):
        """Log a dictionary to the current test log"""
        if not self.current_log_path:
            raise ValueError("No test log started. Call start_test_log first.")
        
        with open(self.current_log_path, 'a', encoding='utf-8') as f:
            f.write(f"\n{description}:\n")
            json_str = json.dumps(data_dict, indent=2, default=str)
            f.write(json_str + "\n")
    
    def log_test_result(self, test_name, passed, details=None):
        """Log a test result with pass/fail status"""
        if not self.current_log_path:
            raise ValueError("No test log started. Call start_test_log first.")
        
        status = "PASSED" if passed else "FAILED"
        
        with open(self.current_log_path, 'a', encoding='utf-8') as f:
            f.write(f"\nTEST: {test_name} - {status}\n")
            if details:
                f.write(f"Details: {details}\n")
    
    def log_exception(self, exception):
        """Log an exception with traceback"""
        if not self.current_log_path:
            raise ValueError("No test log started. Call start_test_log first.")
        
        with open(self.current_log_path, 'a', encoding='utf-8') as f:
            f.write("\nEXCEPTION OCCURRED:\n")
            f.write(str(exception) + "\n")
            f.write(traceback.format_exc() + "\n")
    
    def log_comparison(self, expected, actual, description="Comparison"):
        """Log a comparison between expected and actual values"""
        if not self.current_log_path:
            raise ValueError("No test log started. Call start_test_log first.")
        
        with open(self.current_log_path, 'a', encoding='utf-8') as f:
            f.write(f"\n{description}:\n")
            f.write(f"Expected: {expected}\n")
            f.write(f"Actual  : {actual}\n")
            
            # Calculate difference for numeric values
            try:
                if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
                    diff = actual - expected
                    pct_diff = (diff / expected) * 100 if expected != 0 else float('inf')
                    f.write(f"Diff    : {diff} ({pct_diff:.2f}%)\n")
            except:
                pass
    
    def finish_test_log(self, success=True):
        """Finish the current test log with summary"""
        if not self.current_log_path:
            raise ValueError("No test log started. Call start_test_log first.")
        
        status = "SUCCESSFUL" if success else "FAILED"
        
        with open(self.current_log_path, 'a', encoding='utf-8') as f:
            f.write(f"\n\n===== Test {self.current_test_name} {status} =====\n")
            f.write(f"Completed: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n")
        
        return self.current_log_path


# Simple logger for quick one-off logs
def log_result(test_name, data, directory="test_logs"):
    """Quick function to log a test result without creating a logger instance"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if not os.path.exists(directory):
        os.makedirs(directory)
        
    filename = f"{test_name}_{timestamp}.txt"
    filepath = os.path.join(directory, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"===== VariancePro Test Result: {test_name} =====\n")
        f.write(f"Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 60 + "\n\n")
        
        if isinstance(data, pd.DataFrame):
            f.write(f"DataFrame (Shape: {data.shape}):\n")
            f.write(data.to_string() + "\n")
        elif isinstance(data, dict):
            f.write("Dictionary:\n")
            json_str = json.dumps(data, indent=2, default=str)
            f.write(json_str + "\n")
        else:
            f.write(str(data) + "\n")
    
    return filepath
