"""
Run tests for deepseek-coder:6.7b integration with VariancePro

This script executes all tests that verify the correct integration with
the deepseek-coder:6.7b model for professional financial analysis.
"""

import unittest
import os
import sys

def run_tests():
    """Run all deepseek-coder integration tests"""
    print("🧪 Running DeepSeek Coder Integration Tests")
    print("=" * 50)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test modules
    test_modules = [
        'test_deepseek_integration',
        'test_aria_deepseek_integration'
    ]
    
    for test_module in test_modules:
        try:
            # Load the tests from module
            module_tests = loader.loadTestsFromName(test_module)
            suite.addTests(module_tests)
            print(f"✅ Loaded tests from {test_module}")
        except Exception as e:
            print(f"❌ Failed to load {test_module}: {str(e)}")
    
    # Run the tests
    print("\n📝 Test Results:")
    print("=" * 50)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n📊 Test Summary:")
    print(f"- Tests Run: {result.testsRun}")
    print(f"- Failures: {len(result.failures)}")
    print(f"- Errors: {len(result.errors)}")
    print(f"- Skipped: {len(result.skipped)}")
    
    # Print failures details if any
    if result.failures:
        print("\n❌ Test Failures:")
        for i, (test, traceback) in enumerate(result.failures, 1):
            print(f"\nFailure {i}: {test}")
            print("-" * 50)
            print(traceback)
    
    # Print errors details if any
    if result.errors:
        print("\n⚠️ Test Errors:")
        for i, (test, traceback) in enumerate(result.errors, 1):
            print(f"\nError {i}: {test}")
            print("-" * 50)
            print(traceback)
            
    return len(result.failures) == 0 and len(result.errors) == 0

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
