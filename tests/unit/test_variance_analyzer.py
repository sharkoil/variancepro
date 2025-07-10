"""
Unit tests for the QuantAnalyzer module
Tests quantitative analysis functionality including pair detection and calculations
"""

import unittest
import pandas as pd
import numpy as np

from analyzers.variance_analyzer import QuantAnalyzer


class TestQuantAnalyzer(unittest.TestCase):
    """Test cases for the QuantAnalyzer class"""
    
    def setUp(self):
        """Set up test fixtures before each test method"""
        self.analyzer = QuantAnalyzer()
        
        # Create sample data for testing
        self.sample_data = pd.DataFrame({
            'Actual Sales': [1000, 1200, 900, 1100],
            'Planned Sales': [950, 1150, 1000, 1050],
            'Budget Revenue': [900, 1100, 950, 1000],
            'Forecast Sales': [980, 1180, 980, 1080],
            'Month': ['Jan', 'Feb', 'Mar', 'Apr'],
            'Region': ['North', 'South', 'East', 'West']
        })
    
    def test_initialization(self):
        """Test that QuantAnalyzer initializes correctly"""
        self.assertIsNone(self.analyzer.analysis_results)
        self.assertIsInstance(self.analyzer.variance_types, dict)
        self.assertIn('actual_vs_planned', self.analyzer.variance_types)
    
    def test_detect_variance_columns(self):
        """Test detection of variance-related columns"""
        detected = self.analyzer.detect_variance_columns(self.sample_data)
        
        self.assertIsInstance(detected, dict)
        self.assertIn('actual', detected)
        self.assertIn('planned', detected)
        self.assertIn('sales', detected)
        
        # Should detect actual sales column
        self.assertIn('Actual Sales', detected['actual'])
        
        # Should detect planned sales column  
        self.assertIn('Planned Sales', detected['planned'])
    
    def test_detect_variance_pairs(self):
        """Test detection of variance comparison pairs"""
        columns = self.sample_data.columns.tolist()
        pairs = self.analyzer.detect_variance_pairs(columns)
        
        self.assertIsInstance(pairs, list)
        self.assertGreater(len(pairs), 0)
        
        # Each pair should have required keys
        for pair in pairs:
            self.assertIn('actual', pair)
            self.assertIn('planned', pair)
            self.assertIn('type', pair)
    
    def test_calculate_variance_basic(self):
        """Test basic variance calculation"""
        result = self.analyzer.calculate_variance(
            data=self.sample_data,
            actual_col='Actual Sales',
            planned_col='Planned Sales'
        )
        
        self.assertIsInstance(result, str)
        self.assertIn('Actual Sales', result)
        self.assertIn('Planned Sales', result)
        self.assertIn('Variance', result)
    
    def test_calculate_variance_invalid_columns(self):
        """Test variance calculation with invalid column names"""
        result = self.analyzer.calculate_variance(
            data=self.sample_data,
            actual_col='Invalid Column',
            planned_col='Planned Sales'
        )
        
        self.assertIn('Error', result)
        self.assertIn('not found', result)
    
    def test_calculate_variance_zero_planned(self):
        """Test variance calculation when planned values are zero"""
        # Create data with zero planned values
        zero_data = pd.DataFrame({
            'Actual': [100, 200],
            'Planned': [0, 0]
        })
        
        result = self.analyzer.calculate_variance(
            data=zero_data,
            actual_col='Actual',
            planned_col='Planned'
        )
        
        # Should handle division by zero gracefully
        self.assertIsInstance(result, str)
        self.assertIn('Actual', result)
    
    def test_suggest_variance_analysis(self):
        """Test quantitative analysis suggestions"""
        suggestions = self.analyzer.suggest_variance_analysis(self.sample_data)
        
        self.assertIsInstance(suggestions, list)
        self.assertGreater(len(suggestions), 0)
        
        # Should suggest actual vs planned analysis
        actual_vs_planned_found = any('Actual vs Planned' in suggestion for suggestion in suggestions)
        self.assertTrue(actual_vs_planned_found)
    
    def test_format_variance_report_no_results(self):
        """Test formatting when no analysis results are available"""
        report = self.analyzer.format_variance_report()
        
        self.assertIsInstance(report, str)
        self.assertIn('No quantitative analysis results', report)


class TestQuantAnalyzerIntegration(unittest.TestCase):
    """Integration tests for QuantAnalyzer with realistic data"""
    
    def setUp(self):
        """Set up integration test fixtures"""
        self.analyzer = QuantAnalyzer()
        
        # Create realistic financial data
        self.financial_data = pd.DataFrame({
            'Date': pd.date_range('2024-01-01', periods=12, freq='M'),
            'Actual Revenue': [95000, 102000, 88000, 115000, 108000, 125000,
                              130000, 118000, 135000, 142000, 128000, 155000],
            'Budget Revenue': [90000, 100000, 95000, 110000, 105000, 120000,
                              125000, 115000, 130000, 140000, 125000, 150000],
            'Sales Target': [92000, 98000, 92000, 108000, 103000, 118000,
                            123000, 113000, 128000, 138000, 123000, 148000],
            'Department': ['Sales', 'Sales', 'Marketing', 'Sales', 'Marketing', 'Sales',
                          'Sales', 'Marketing', 'Sales', 'Sales', 'Marketing', 'Sales']
        })
    
    def test_realistic_variance_analysis(self):
        """Test quantitative analysis with realistic financial data"""
        pairs = self.analyzer.detect_variance_pairs(self.financial_data.columns.tolist())
        
        # Should detect revenue comparisons
        revenue_pairs = [p for p in pairs if 'Revenue' in p['actual'] or 'Revenue' in p['planned']]
        self.assertGreater(len(revenue_pairs), 0)
        
        # Test calculation with realistic data
        if revenue_pairs:
            result = self.analyzer.calculate_variance(
                data=self.financial_data,
                actual_col='Actual Revenue',
                planned_col='Budget Revenue'
            )
            
            self.assertIn('Revenue', result)
            self.assertIn('$', result)  # Should include currency formatting


if __name__ == '__main__':
    unittest.main()
