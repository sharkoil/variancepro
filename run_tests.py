#!/usr/bin/env python3
"""
VariancePro Test Runner
Organized test execution for the cleaned up codebase
"""

import os
import sys
import subprocess
from pathlib import Path

def run_test_category(category_name: str, test_files: list) -> bool:
    """Run a category of tests and report results"""
    print(f"\n🧪 Running {category_name} Tests")
    print("=" * 50)
    
    success_count = 0
    total_count = len(test_files)
    
    for test_file in test_files:
        test_path = Path("tests") / test_file
        if test_path.exists():
            print(f"  ▶️ {test_file}... ", end="")
            try:
                result = subprocess.run([sys.executable, str(test_path)], 
                                      capture_output=True, text=True, timeout=60)
                if result.returncode == 0:
                    print("✅ PASSED")
                    success_count += 1
                else:
                    print("❌ FAILED")
                    if result.stderr:
                        print(f"    Error: {result.stderr.strip()}")
            except subprocess.TimeoutExpired:
                print("⏰ TIMEOUT")
            except Exception as e:
                print(f"💥 ERROR: {e}")
        else:
            print(f"  ⚠️ {test_file} not found")
    
    print(f"\n📊 {category_name} Results: {success_count}/{total_count} passed")
    return success_count == total_count

def main():
    """Run organized test suite"""
    print("🚀 VariancePro Test Suite")
    print("=" * 50)
    
    # Test categories
    test_categories = {
        "Core Configuration": [
            "test_config.py"
        ],
        "Data Processing": [
            "test_csv_loader.py",
            "test_csv_simple.py"
        ],
        "Financial Analysis": [
            "test_financial_analyzer.py", 
            "test_financial_quick.py",
            "test_fixed_analyzers.py"
        ],
        "AI Components": [
            "test_ai_core.py",
            "test_ai_simple.py"
        ],
        "SQL Integration": [
            "test_sql_integration.py",
            "test_enhanced_nl_to_sql.py"
        ],
        "News Analysis": [
            "test_news_analyzer_v2.py"
        ],
        "Integration Tests": [
            "test_interface.py",
            "test_quick.py"
        ]
    }
    
    overall_success = True
    
    for category, test_files in test_categories.items():
        category_success = run_test_category(category, test_files)
        overall_success = overall_success and category_success
    
    print("\n" + "=" * 50)
    if overall_success:
        print("🎉 All test categories passed!")
        return 0
    else:
        print("⚠️ Some tests failed. Check output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
