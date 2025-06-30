"""
VariancePro Test Runner

Executes all test suites for the VariancePro application and generates a comprehensive report.
This provides a simple way to run all tests and ensure the application is functioning correctly.
"""

import unittest
import sys
import os
import time
from datetime import datetime

# Define test files to run
test_files = [
    'test_timescale_analyzer_unit.py',
    'test_timescale_analyzer_integration.py',
    'test_financial_accuracy.py',
    'test_timescale_analyzer_edge_cases.py'
]

def run_tests():
    """Run all test suites and generate report"""
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Add to path to ensure imports work
    sys.path.append(current_dir)
    
    # Create test suite
    full_suite = unittest.TestSuite()
    
    # Add all test files
    for test_file in test_files:
        try:
            # Convert filename to module name
            module_name = os.path.splitext(test_file)[0]
            
            # Import the module
            module = __import__(module_name)
            
            # Load tests from the module
            suite = unittest.defaultTestLoader.loadTestsFromModule(module)
            full_suite.addTest(suite)
            
            print(f"Added tests from {test_file}")
        except Exception as e:
            print(f"Error loading tests from {test_file}: {str(e)}")
    
    # Try to use HTML test runner if available, otherwise use text runner
    try:
        # First try the HTMLTestRunner package if installed
        try:
            from HtmlTestRunner import HTMLTestRunner
            
            # Create HTML report file
            report_dir = os.path.join(current_dir, 'test_reports')
            os.makedirs(report_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            report_file = os.path.join(report_dir, f'test_report_{timestamp}.html')
            
            runner = HTMLTestRunner(
                output=report_dir,
                report_name=f'test_report_{timestamp}',
                combine_reports=True,
                report_title='VariancePro Test Report'
            )
            result = runner.run(full_suite)
            
            print(f"\nHTML Test Report generated: {os.path.join(report_dir, f'test_report_{timestamp}.html')}")
            return result
            
        except ImportError:
            # Fall back to unittest.TextTestRunner
            print("\nRunning tests with text runner (HTML reports not available)")
            print("To enable HTML reports, run: pip install html-testRunner")
            runner = unittest.TextTestRunner(verbosity=2)
            return runner.run(full_suite)
            
    except Exception as e:
        print(f"Error setting up test runner: {str(e)}")
        # Final fallback to simple test runner
        runner = unittest.TextTestRunner(verbosity=2)
        return runner.run(full_suite)

if __name__ == "__main__":
    start_time = time.time()
    print("=" * 70)
    print(f"VariancePro Test Runner - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    result = run_tests()
    
    # Calculate time taken
    end_time = time.time()
    time_taken = end_time - start_time
    
    # Print summary
    print("\n" + "=" * 70)
    print(f"Test Summary:")
    print(f"Time taken: {time_taken:.2f} seconds")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    # Print detailed error information if there are failures
    if result.failures or result.errors:
        print("\nTest Failures and Errors:")
        
        for failure in result.failures:
            test_case, traceback = failure
            print(f"\n--- FAILURE: {test_case} ---")
            print(traceback)
        
        for error in result.errors:
            test_case, traceback = error
            print(f"\n--- ERROR: {test_case} ---")
            print(traceback)
    
    print("=" * 70)
    
    # Exit with appropriate code
    sys.exit(len(result.failures) + len(result.errors))
