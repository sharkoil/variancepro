#!/usr/bin/env python3
"""
Phase 3A Cache Integration Test Runner

This script runs all Phase 3A cache integration tests to verify
the performance foundation is working correctly.

Author: AI Assistant
Date: July 2025
Phase: 3A - Performance Foundation
"""

import sys
import os
import unittest
from io import StringIO
import traceback

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_simple_cache_test():
    """Run the simple cache integration test"""
    print("=" * 60)
    print("🧪 PHASE 3A - SIMPLE CACHE INTEGRATION TEST")
    print("=" * 60)
    
    try:
        # Import and run the simple test
        from test_cache_simple import test_basic_cache_integration
        
        success = test_basic_cache_integration()
        if success:
            print("\n✅ Simple cache integration test: PASSED")
            return True
        else:
            print("\n❌ Simple cache integration test: FAILED")
            return False
    except Exception as e:
        print(f"\n❌ Simple cache integration test failed: {e}")
        traceback.print_exc()
        return False

def run_comprehensive_cache_tests():
    """Run the comprehensive cache integration tests"""
    print("\n" + "=" * 60)
    print("🧪 PHASE 3A - COMPREHENSIVE CACHE INTEGRATION TESTS")
    print("=" * 60)
    
    try:
        # Import the test class
        from tests.test_phase3a_cache_integration import TestPhase3ACacheIntegration
        
        # Create a test suite
        suite = unittest.TestLoader().loadTestsFromTestCase(TestPhase3ACacheIntegration)
        
        # Create a test runner with detailed output
        stream = StringIO()
        runner = unittest.TextTestRunner(stream=stream, verbosity=2)
        
        # Run the tests
        result = runner.run(suite)
        
        # Print the results
        output = stream.getvalue()
        print(output)
        
        if result.wasSuccessful():
            print(f"\n✅ All {result.testsRun} comprehensive tests: PASSED")
            return True
        else:
            print(f"\n❌ {len(result.failures)} failures, {len(result.errors)} errors out of {result.testsRun} tests")
            
            # Print failure details
            for test, traceback_str in result.failures:
                print(f"\n❌ FAILURE: {test}")
                print(traceback_str)
            
            for test, traceback_str in result.errors:
                print(f"\n❌ ERROR: {test}")
                print(traceback_str)
            
            return False
            
    except Exception as e:
        print(f"\n❌ Comprehensive cache integration tests failed: {e}")
        traceback.print_exc()
        return False

def run_all_phase3a_tests():
    """Run all Phase 3A tests and provide summary"""
    print("🚀 Starting Phase 3A Cache Integration Test Suite")
    print("📅 Date: July 2025")
    print("🎯 Phase: 3A - Performance Foundation")
    print("")
    
    # Track results
    results = []
    
    # Run simple test
    simple_success = run_simple_cache_test()
    results.append(("Simple Cache Integration", simple_success))
    
    # Run comprehensive tests
    comprehensive_success = run_comprehensive_cache_tests()
    results.append(("Comprehensive Cache Integration", comprehensive_success))
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 PHASE 3A TEST RESULTS SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_name}: {status}")
        if not success:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL PHASE 3A TESTS PASSED!")
        print("🚀 Cache integration is working correctly")
        print("📈 Performance foundation is ready for Phase 3B")
    else:
        print("❌ SOME PHASE 3A TESTS FAILED")
        print("🔧 Please review the failures above")
        print("📋 Fix issues before proceeding to Phase 3B")
    
    print("=" * 60)
    
    return all_passed

if __name__ == "__main__":
    try:
        success = run_all_phase3a_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Test suite interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Test runner failed: {e}")
        traceback.print_exc()
        sys.exit(1)
