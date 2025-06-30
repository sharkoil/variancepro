"""
VariancePro Timescale Analysis Test Suite

This script runs the comprehensive test suite for the TimescaleAnalyzer
and generates detailed test reports with timestamps.
"""

import os
import sys
import subprocess
import datetime
import traceback

def run_test_script(script_name, description):
    """Run a test script and return result"""
    print(f"\n{'=' * 70}")
    print(f"Running: {script_name} - {description}")
    print(f"{'-' * 70}")
    
    try:
        # Run the script
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=True,
            text=True
        )
        
        # Check if the script ran successfully
        if result.returncode == 0:
            print(f"✅ SUCCESS: {script_name}")
            if "Test completed" in result.stdout:
                print(result.stdout.split("Test completed")[1].strip())
            else:
                print(result.stdout[-200:] if result.stdout else "No output")
        else:
            print(f"❌ FAILED: {script_name}")
            print(f"Error: {result.stderr}")
        
        return result.returncode == 0, result.stdout, result.stderr
    
    except Exception as e:
        print(f"❌ ERROR: Failed to run {script_name}: {str(e)}")
        traceback.print_exc()
        return False, "", str(e)

def generate_summary_report(test_results):
    """Generate a consolidated summary report"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = os.path.join("test_logs", f"summary_report_{timestamp}.txt")
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    
    with open(report_path, 'w') as f:
        f.write(f"===== VariancePro Test Suite Summary Report =====\n")
        f.write(f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"System: {os.name}\n")
        f.write("=" * 60 + "\n\n")
        
        # Write summary
        f.write(f"Tests Run: {len(test_results)}\n")
        successful = sum(1 for result in test_results if result['success'])
        f.write(f"Successful: {successful}\n")
        f.write(f"Failed: {len(test_results) - successful}\n\n")
        
        # Write individual test results
        f.write("Test Details:\n")
        f.write("-" * 60 + "\n")
        
        for result in test_results:
            status = "✅ PASS" if result['success'] else "❌ FAIL"
            f.write(f"{status}: {result['name']} - {result['description']}\n")
            if 'log_path' in result and result['log_path']:
                f.write(f"   Log: {result['log_path']}\n")
            f.write("\n")
    
    return report_path

def run_all_tests():
    """Run all TimescaleAnalyzer tests and generate reports"""
    start_time = datetime.datetime.now()
    print(f"Starting test suite: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Define test scripts to run
    test_scripts = [
        {"name": "test_sales_budget_actuals.py", 
         "description": "Tests the sales_budget_actuals.csv file specifically"},
        {"name": "test_date_detection.py", 
         "description": "Tests date column detection across different files"},
        {"name": "test_timescale_analyzer_unit.py", 
         "description": "Unit tests for TimescaleAnalyzer"},
        {"name": "test_timescale_analyzer_edge_cases.py", 
         "description": "Edge case tests for TimescaleAnalyzer"},
        {"name": "test_financial_accuracy.py", 
         "description": "Financial accuracy tests"}
    ]
    
    # Run each test script
    test_results = []
    for script in test_scripts:
        success, stdout, stderr = run_test_script(script["name"], script["description"])
        
        # Extract log path from output if available
        log_path = None
        if "Results saved to:" in stdout:
            log_path = stdout.split("Results saved to:")[1].strip()
        
        test_results.append({
            "name": script["name"],
            "description": script["description"],
            "success": success,
            "log_path": log_path
        })
    
    # Generate summary report
    summary_path = generate_summary_report(test_results)
    
    # Calculate time taken
    end_time = datetime.datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print(f"\n{'=' * 70}")
    print(f"Test Suite Completed")
    print(f"Time taken: {duration:.2f} seconds")
    print(f"Summary report: {summary_path}")
    print(f"{'=' * 70}")
    
    return summary_path

if __name__ == "__main__":
    run_all_tests()
