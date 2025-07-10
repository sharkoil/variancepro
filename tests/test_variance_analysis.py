#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Comprehensive test for variance analysis functionality

This test validates that the variance analysis regression has been resolved
and all modular components are working correctly.
"""

import sys
import os
import pandas as pd
import unittest

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestVarianceAnalysis(unittest.TestCase):
    """Test suite for variance analysis functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.test_data = pd.DataFrame({
            'Date': pd.date_range('2023-01-01', periods=6, freq='M'),
            'Actual_Sales': [1000, 1200, 900, 1100, 1300, 1150],
            'Planned_Sales': [950, 1150, 1000, 1050, 1250, 1100],
            'Budget_Revenue': [900, 1100, 950, 1000, 1200, 1050],
            'Actual_Revenue': [950, 1180, 920, 1080, 1280, 1120],
            'Region': ['North', 'South', 'North', 'South', 'North', 'South']
        })
    
    def test_variance_analyzer_import(self):
        """Test that variance analyzer can be imported correctly"""
        try:
            from analyzers.variance_analyzer import QuantAnalyzer
            self.assertTrue(True, "QuantAnalyzer imported successfully")
        except ImportError as e:
            self.fail(f"Failed to import QuantAnalyzer: {e}")
    
    def test_variance_analyzer_initialization(self):
        """Test that variance analyzer can be initialized"""
        from analyzers.variance_analyzer import QuantAnalyzer
        
        analyzer = QuantAnalyzer()
        self.assertIsNotNone(analyzer, "QuantAnalyzer should initialize successfully")
    
    def test_variance_pair_detection(self):
        """Test variance pair detection functionality"""
        from analyzers.variance_analyzer import QuantAnalyzer
        
        analyzer = QuantAnalyzer()
        columns = self.test_data.columns.tolist()
        variance_pairs = analyzer.detect_variance_pairs(columns)
        
        self.assertIsInstance(variance_pairs, list, "Should return a list of variance pairs")
        self.assertGreater(len(variance_pairs), 0, "Should detect at least one variance pair")
        
        # Check structure of first pair
        if variance_pairs:
            first_pair = variance_pairs[0]
            self.assertIn('actual', first_pair, "Pair should have 'actual' key")
            self.assertIn('planned', first_pair, "Pair should have 'planned' key")
    
    def test_comprehensive_variance_analysis(self):
        """Test comprehensive variance analysis functionality"""
        from analyzers.variance_analyzer import QuantAnalyzer
        
        analyzer = QuantAnalyzer()
        columns = self.test_data.columns.tolist()
        variance_pairs = analyzer.detect_variance_pairs(columns)
        
        self.assertGreater(len(variance_pairs), 0, "Need variance pairs for analysis")
        
        pair = variance_pairs[0]
        result = analyzer.comprehensive_variance_analysis(
            self.test_data, pair['actual'], pair['planned']
        )
        
        self.assertIsInstance(result, dict, "Should return analysis results as dict")
        self.assertNotIn('error', result, "Analysis should not contain errors")
    
    def test_variance_handler_import(self):
        """Test that variance handler can be imported correctly"""
        try:
            from handlers.quick_actions.variance_handler import VarianceHandler
            self.assertTrue(True, "VarianceHandler imported successfully")
        except ImportError as e:
            self.fail(f"Failed to import VarianceHandler: {e}")
    
    def test_variance_handler_initialization(self):
        """Test variance handler initialization"""
        from handlers.quick_actions.variance_handler import VarianceHandler
        
        class MockAppCore:
            def __init__(self, data):
                self.data = data
                self.metadata = {"row_count": len(data)}
            
            def get_current_data(self):
                return self.data, self.metadata
            
            def has_data(self):
                return self.data is not None and not self.data.empty
        
        mock_app = MockAppCore(self.test_data)
        handler = VarianceHandler(mock_app)
        
        self.assertIsNotNone(handler, "VarianceHandler should initialize successfully")
    
    def test_variance_handler_execution(self):
        """Test variance handler execution"""
        from handlers.quick_actions.variance_handler import VarianceHandler
        
        class MockAppCore:
            def __init__(self, data):
                self.data = data
                self.metadata = {"row_count": len(data)}
            
            def get_current_data(self):
                return self.data, self.metadata
            
            def has_data(self):
                return self.data is not None and not self.data.empty
        
        mock_app = MockAppCore(self.test_data)
        handler = VarianceHandler(mock_app)
        
        result = handler.handle()
        
        self.assertIsInstance(result, str, "Should return analysis result as string")
        self.assertGreater(len(result), 0, "Result should not be empty")
        self.assertNotIn("Error", result, "Result should not contain errors")
    
    def test_modular_quick_action_handler_integration(self):
        """Test integration with main modular quick action handler"""
        from handlers.quick_action_handler import QuickActionHandler
        
        class MockAppCore:
            def __init__(self, data):
                self.data = data
                self.metadata = {"row_count": len(data)}
                self.timescale_analyzer = None
            
            def get_current_data(self):
                return self.data, self.metadata
            
            def has_data(self):
                return self.data is not None and not self.data.empty
        
        mock_app = MockAppCore(self.test_data)
        handler = QuickActionHandler(mock_app)
        
        # Test that variance handler is properly initialized
        self.assertIsNotNone(handler.variance_handler, "Variance handler should be initialized")
        
        # Test variance action routing
        result = handler._route_action("variance")
        self.assertIsInstance(result, str, "Should return variance analysis result")
        self.assertGreater(len(result), 0, "Result should not be empty")


class TestVarianceRegression(unittest.TestCase):
    """Specific test for variance analysis regression"""
    
    def test_no_variance_regression(self):
        """Test that variance analysis works as expected (no regression)"""
        print("\n🔍 Testing Variance Analysis Regression...")
        
        # Test import path fix
        try:
            from analyzers.variance_analyzer import QuantAnalyzer
            print("   ✅ Variance analyzer import fixed")
        except ImportError as e:
            self.fail(f"Variance analyzer import failed: {e}")
        
        # Test functionality
        analyzer = QuantAnalyzer()
        
        test_data = pd.DataFrame({
            'Actual_Sales': [1000, 1200, 900],
            'Planned_Sales': [950, 1150, 1000],
            'Date': pd.date_range('2023-01-01', periods=3, freq='M')
        })
        
        pairs = analyzer.detect_variance_pairs(test_data.columns.tolist())
        self.assertGreater(len(pairs), 0, "Should detect variance pairs")
        
        result = analyzer.comprehensive_variance_analysis(
            test_data, pairs[0]['actual'], pairs[0]['planned']
        )
        self.assertNotIn('error', result, "Analysis should not contain errors")
        
        print("   ✅ Variance analysis functionality confirmed")
        print("   ✅ Regression resolved!")


def run_variance_tests():
    """Run all variance analysis tests"""
    print("🧪 Running Variance Analysis Tests")
    print("=" * 50)
    
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add all test cases
    suite.addTest(unittest.makeSuite(TestVarianceAnalysis))
    suite.addTest(unittest.makeSuite(TestVarianceRegression))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    if result.wasSuccessful():
        print("\n🎉 All variance analysis tests passed!")
        print("✅ Variance analysis regression resolved!")
        return True
    else:
        print(f"\n❌ {len(result.failures)} test(s) failed")
        print(f"❌ {len(result.errors)} error(s) occurred")
        return False


if __name__ == "__main__":
    success = run_variance_tests()
    sys.exit(0 if success else 1)
