#!/usr/bin/env python3
"""
Test Runner for Enhanced Query Analysis Components

This script runs all tests for the new LLM-powered query analysis system
including query analyzer, validators, and integration tests.

Author: AI Assistant
Date: July 2025
Phase: Enhanced Query Analysis
"""

import sys
import os
import unittest
from io import StringIO
import traceback

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_query_analyzer_tests():
    """Run the query analyzer tests"""
    print("=" * 60)
    print("🧪 QUERY ANALYZER TESTS")
    print("=" * 60)
    
    try:
        # Import and run the test
        from tests.test_query_analyzer import TestQueryAnalyzer
        
        # Create test suite
        suite = unittest.TestLoader().loadTestsFromTestCase(TestQueryAnalyzer)
        
        # Run tests
        stream = StringIO()
        runner = unittest.TextTestRunner(stream=stream, verbosity=2)
        result = runner.run(suite)
        
        # Print results
        output = stream.getvalue()
        print(output)
        
        if result.wasSuccessful():
            print(f"\n✅ All {result.testsRun} Query Analyzer tests: PASSED")
            return True
        else:
            print(f"\n❌ {len(result.failures)} failures, {len(result.errors)} errors")
            return False
            
    except Exception as e:
        print(f"\n❌ Query Analyzer tests failed: {e}")
        traceback.print_exc()
        return False

def run_query_validator_tests():
    """Run the query validator tests"""
    print("\n" + "=" * 60)
    print("🧪 QUERY VALIDATOR TESTS")
    print("=" * 60)
    
    try:
        # Import test classes
        from tests.test_query_validators import (
            TestValidationResult, TestTopBottomValidator, TestVarianceValidator,
            TestSummaryValidator, TestTrendsValidator, TestValidatorFactory
        )
        
        # Create test suite
        test_classes = [
            TestValidationResult, TestTopBottomValidator, TestVarianceValidator,
            TestSummaryValidator, TestTrendsValidator, TestValidatorFactory
        ]
        
        suite = unittest.TestSuite()
        for test_class in test_classes:
            suite.addTest(unittest.TestLoader().loadTestsFromTestCase(test_class))
        
        # Run tests
        stream = StringIO()
        runner = unittest.TextTestRunner(stream=stream, verbosity=2)
        result = runner.run(suite)
        
        # Print results
        output = stream.getvalue()
        print(output)
        
        if result.wasSuccessful():
            print(f"\n✅ All {result.testsRun} Query Validator tests: PASSED")
            return True
        else:
            print(f"\n❌ {len(result.failures)} failures, {len(result.errors)} errors")
            return False
            
    except Exception as e:
        print(f"\n❌ Query Validator tests failed: {e}")
        traceback.print_exc()
        return False

def run_simple_integration_test():
    """Run a simple integration test"""
    print("\n" + "=" * 60)
    print("🧪 SIMPLE INTEGRATION TEST")
    print("=" * 60)
    
    try:
        # Test the components working together
        from analyzers.query_analyzer import QueryAnalyzer, QueryType
        from validators.query_validators import get_validator
        from unittest.mock import Mock
        
        # Create mock LLM
        mock_llm = Mock()
        mock_llm.interpret.side_effect = Exception("Force pattern matching")
        
        # Create analyzer
        analyzer = QueryAnalyzer(llm_interpreter=mock_llm)
        
        # Test top/bottom query
        result = analyzer.analyze_query("Show me top 5 products by revenue monthly")
        print(f"📊 Query: 'Show me top 5 products by revenue monthly'")
        print(f"   Type: {result.query_type}")
        print(f"   Parameters: {result.parameters}")
        print(f"   Confidence: {result.confidence}")
        
        # Validate parameters
        validator = get_validator(result.query_type.value)
        validation_result = validator.validate_parameters(result.parameters)
        print(f"   Validation: {'✅ PASSED' if validation_result.is_valid else '❌ FAILED'}")
        
        if not validation_result.is_valid:
            print(f"   Errors: {validation_result.errors}")
        
        # Test variance query
        result2 = analyzer.analyze_query("Show me quarterly variance in budget vs actual")
        print(f"\n📊 Query: 'Show me quarterly variance in budget vs actual'")
        print(f"   Type: {result2.query_type}")
        print(f"   Parameters: {result2.parameters}")
        print(f"   Confidence: {result2.confidence}")
        
        # Validate parameters
        validator2 = get_validator(result2.query_type.value)
        validation_result2 = validator2.validate_parameters(result2.parameters)
        print(f"   Validation: {'✅ PASSED' if validation_result2.is_valid else '❌ FAILED'}")
        
        if not validation_result2.is_valid:
            print(f"   Errors: {validation_result2.errors}")
        
        success = validation_result.is_valid and validation_result2.is_valid
        print(f"\n{'✅ Integration test: PASSED' if success else '❌ Integration test: FAILED'}")
        
        return success
        
    except Exception as e:
        print(f"\n❌ Integration test failed: {e}")
        traceback.print_exc()
        return False

def run_all_enhanced_query_tests():
    """Run all enhanced query analysis tests"""
    print("🚀 Starting Enhanced Query Analysis Test Suite")
    print("📅 Date: July 2025")
    print("🎯 Phase: Enhanced Query Analysis Foundation")
    print("")
    
    # Track results
    results = []
    
    # Run query analyzer tests
    analyzer_success = run_query_analyzer_tests()
    results.append(("Query Analyzer", analyzer_success))
    
    # Run query validator tests
    validator_success = run_query_validator_tests()
    results.append(("Query Validators", validator_success))
    
    # Run integration test
    integration_success = run_simple_integration_test()
    results.append(("Integration Test", integration_success))
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 ENHANCED QUERY ANALYSIS TEST RESULTS")
    print("=" * 60)
    
    all_passed = True
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_name}: {status}")
        if not success:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL ENHANCED QUERY ANALYSIS TESTS PASSED!")
        print("🚀 LLM-powered query understanding is working correctly")
        print("📈 Foundation ready for tool executor integration")
    else:
        print("❌ SOME TESTS FAILED")
        print("🔧 Please review the failures above")
        print("📋 Fix issues before proceeding to tool integration")
    
    print("=" * 60)
    
    return all_passed

if __name__ == "__main__":
    try:
        success = run_all_enhanced_query_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Test suite interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Test runner failed: {e}")
        traceback.print_exc()
        sys.exit(1)
