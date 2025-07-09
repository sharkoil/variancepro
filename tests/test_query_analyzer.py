"""
Unit tests for Query Analyzer

This module tests the LLM-powered query analysis functionality to ensure
accurate query type detection and parameter extraction.

Author: AI Assistant
Date: July 2025
Phase: Enhanced Query Analysis
"""

import unittest
from unittest.mock import Mock, patch
import json

# Add the parent directory to the path to import our modules
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analyzers.query_analyzer import QueryAnalyzer, QueryType, QueryAnalysisResult


class TestQueryAnalyzer(unittest.TestCase):
    """
    Test suite for the QueryAnalyzer class.
    
    Tests both LLM-based analysis and fallback pattern matching
    to ensure robust query understanding.
    """
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create mock LLM interpreter
        self.mock_llm = Mock()
        self.analyzer = QueryAnalyzer(llm_interpreter=self.mock_llm)
    
    def test_query_analyzer_initialization(self):
        """Test that QueryAnalyzer initializes correctly."""
        analyzer = QueryAnalyzer()
        
        # Verify analyzer has required components
        self.assertIsNotNone(analyzer.llm_interpreter)
        self.assertIsNotNone(analyzer.settings)
        self.assertIsNotNone(analyzer.query_patterns)
        
        # Verify query patterns are defined for all major types
        self.assertIn(QueryType.TOP_BOTTOM, analyzer.query_patterns)
        self.assertIn(QueryType.VARIANCE, analyzer.query_patterns)
        self.assertIn(QueryType.SUMMARY, analyzer.query_patterns)
        self.assertIn(QueryType.TRENDS, analyzer.query_patterns)
    
    def test_normalize_query_functionality(self):
        """Test that query normalization works correctly."""
        # Test basic normalization
        normalized = self.analyzer._normalize_query("  SHOW ME   the TOP 5  ")
        self.assertEqual(normalized, "show me the top 5")
        
        # Test filler word removal
        normalized = self.analyzer._normalize_query("Please can you show me top 5")
        self.assertEqual(normalized, "show me top 5")
        
        # Test complex query normalization
        normalized = self.analyzer._normalize_query("Could you please show me the top 10 products by revenue?")
        self.assertEqual(normalized, "show me the top 10 products by revenue?")
    
    def test_llm_analysis_success(self):
        """Test successful LLM-based query analysis."""
        # Mock LLM response
        llm_response = json.dumps({
            "query_type": "top_bottom",
            "confidence": 0.9,
            "parameters": {
                "direction": "top",
                "count": 5,
                "sort_column": "revenue",
                "time_period": "monthly"
            }
        })
        self.mock_llm.interpret.return_value = llm_response
        
        # Test analysis
        result = self.analyzer.analyze_query("Show me top 5 products by revenue this month")
        
        # Verify results
        self.assertEqual(result.query_type, QueryType.TOP_BOTTOM)
        self.assertEqual(result.confidence, 0.9)
        self.assertEqual(result.parameters['direction'], 'top')
        self.assertEqual(result.parameters['count'], 5)
        self.assertEqual(result.parameters['time_period'], 'monthly')
        self.assertEqual(len(result.validation_errors), 0)
    
    def test_llm_analysis_with_partial_json(self):
        """Test LLM analysis when response contains partial JSON."""
        # Mock LLM response with extra text
        llm_response = """
        Here's my analysis:
        {
            "query_type": "variance",
            "confidence": 0.8,
            "parameters": {
                "variance_type": "percentage",
                "time_period": "quarterly"
            }
        }
        Additional explanation here.
        """
        self.mock_llm.interpret.return_value = llm_response
        
        # Test analysis
        result = self.analyzer.analyze_query("Show me variance in sales")
        
        # Verify JSON was extracted correctly
        self.assertEqual(result.query_type, QueryType.VARIANCE)
        self.assertEqual(result.confidence, 0.8)
        self.assertEqual(result.parameters['variance_type'], 'percentage')
    
    def test_pattern_fallback_analysis(self):
        """Test fallback to pattern-based analysis when LLM fails."""
        # Mock LLM to raise exception
        self.mock_llm.interpret.side_effect = Exception("LLM error")
        
        # Test pattern-based analysis
        result = self.analyzer.analyze_query("Show me top 10 products")
        
        # Verify pattern-based results
        self.assertEqual(result.query_type, QueryType.TOP_BOTTOM)
        self.assertEqual(result.confidence, 0.6)  # Lower confidence for pattern matching
        self.assertEqual(result.parameters['direction'], 'top')
        self.assertEqual(result.parameters['count'], 10)
    
    def test_top_bottom_pattern_detection(self):
        """Test pattern-based detection of top/bottom queries."""
        test_cases = [
            ("top 5 products", QueryType.TOP_BOTTOM, "top", 5),
            ("bottom 3 performers", QueryType.TOP_BOTTOM, "bottom", 3),
            ("highest 10 sales", QueryType.TOP_BOTTOM, "top", 10),
            ("lowest revenue", QueryType.TOP_BOTTOM, "bottom", 10),  # default count
            ("best performing products", QueryType.TOP_BOTTOM, "top", 10),
            ("worst 7 categories", QueryType.TOP_BOTTOM, "bottom", 7)
        ]
        
        # Mock LLM to force pattern matching
        self.mock_llm.interpret.side_effect = Exception("Force pattern matching")
        
        for query, expected_type, expected_direction, expected_count in test_cases:
            with self.subTest(query=query):
                result = self.analyzer.analyze_query(query)
                self.assertEqual(result.query_type, expected_type)
                self.assertEqual(result.parameters['direction'], expected_direction)
                self.assertEqual(result.parameters['count'], expected_count)
    
    def test_variance_pattern_detection(self):
        """Test pattern-based detection of variance queries."""
        test_cases = [
            "show me variance in sales",
            "actual vs budget analysis",
            "budget vs actual comparison",
            "what's the difference between actual and budget",
            "compare budget performance"
        ]
        
        # Mock LLM to force pattern matching
        self.mock_llm.interpret.side_effect = Exception("Force pattern matching")
        
        for query in test_cases:
            with self.subTest(query=query):
                result = self.analyzer.analyze_query(query)
                self.assertEqual(result.query_type, QueryType.VARIANCE)
                self.assertEqual(result.parameters['variance_type'], 'percentage')
    
    def test_time_period_detection(self):
        """Test detection of time periods in queries."""
        test_cases = [
            ("top 5 monthly sales", "monthly"),
            ("quarterly variance report", "quarterly"),
            ("yearly performance analysis", "yearly"),
            ("weekly trends", "weekly"),
            ("show me daily data", "daily")
        ]
        
        # Mock LLM to force pattern matching
        self.mock_llm.interpret.side_effect = Exception("Force pattern matching")
        
        for query, expected_period in test_cases:
            with self.subTest(query=query):
                result = self.analyzer.analyze_query(query)
                if 'time_period' in result.parameters:
                    self.assertEqual(result.parameters['time_period'], expected_period)
    
    def test_parameter_validation(self):
        """Test parameter validation for different query types."""
        # Test valid top/bottom parameters
        valid_params = {
            'direction': 'top',
            'count': 5,
            'time_period': 'monthly'
        }
        errors = self.analyzer._validate_parameters(QueryType.TOP_BOTTOM, valid_params)
        self.assertEqual(len(errors), 0)
        
        # Test invalid direction
        invalid_params = {
            'direction': 'middle',  # Invalid
            'count': 5
        }
        errors = self.analyzer._validate_parameters(QueryType.TOP_BOTTOM, invalid_params)
        self.assertGreater(len(errors), 0)
        self.assertIn("Invalid direction", errors[0])
        
        # Test invalid count
        invalid_params = {
            'direction': 'top',
            'count': -5  # Invalid
        }
        errors = self.analyzer._validate_parameters(QueryType.TOP_BOTTOM, invalid_params)
        self.assertGreater(len(errors), 0)
        self.assertIn("Invalid count", errors[0])
    
    def test_variance_parameter_validation(self):
        """Test parameter validation for variance queries."""
        # Test valid variance parameters
        valid_params = {
            'variance_type': 'percentage',
            'periods': 12,
            'time_period': 'monthly'
        }
        errors = self.analyzer._validate_parameters(QueryType.VARIANCE, valid_params)
        self.assertEqual(len(errors), 0)
        
        # Test invalid variance type
        invalid_params = {
            'variance_type': 'invalid_type',
            'periods': 12
        }
        errors = self.analyzer._validate_parameters(QueryType.VARIANCE, invalid_params)
        self.assertGreater(len(errors), 0)
        self.assertIn("Invalid variance_type", errors[0])
    
    def test_json_structure_validation(self):
        """Test JSON structure validation."""
        # Test valid JSON structure
        valid_json = {
            'query_type': 'top_bottom',
            'parameters': {
                'direction': 'top',
                'count': 5
            }
        }
        self.assertTrue(self.analyzer.validate_json_structure(valid_json))
        
        # Test missing query_type
        invalid_json = {
            'parameters': {
                'direction': 'top'
            }
        }
        self.assertFalse(self.analyzer.validate_json_structure(invalid_json))
        
        # Test missing parameters
        invalid_json = {
            'query_type': 'top_bottom'
        }
        self.assertFalse(self.analyzer.validate_json_structure(invalid_json))
        
        # Test invalid query type
        invalid_json = {
            'query_type': 'invalid_type',
            'parameters': {}
        }
        self.assertFalse(self.analyzer.validate_json_structure(invalid_json))
    
    def test_quick_query_type_detection(self):
        """Test quick query type detection without full analysis."""
        # Mock LLM for quick detection
        self.mock_llm.interpret.return_value = json.dumps({
            "query_type": "summary",
            "confidence": 0.9,
            "parameters": {}
        })
        
        query_type = self.analyzer.detect_query_type("Give me a summary of the data")
        self.assertEqual(query_type, QueryType.SUMMARY)
    
    def test_specific_query_parsers(self):
        """Test specific query parsing methods."""
        # Test top/bottom query parsing
        self.mock_llm.interpret.return_value = json.dumps({
            "query_type": "top_bottom",
            "confidence": 0.9,
            "parameters": {
                "direction": "top",
                "count": 5,
                "sort_column": "revenue"
            }
        })
        
        params = self.analyzer.parse_top_bottom_query("Show me top 5 by revenue")
        self.assertEqual(params['direction'], 'top')
        self.assertEqual(params['count'], 5)
        self.assertEqual(params['sort_column'], 'revenue')
        
        # Test variance query parsing
        self.mock_llm.interpret.return_value = json.dumps({
            "query_type": "variance",
            "confidence": 0.9,
            "parameters": {
                "variance_type": "percentage",
                "time_period": "monthly"
            }
        })
        
        params = self.analyzer.parse_variance_query("Show me monthly variance")
        self.assertEqual(params['variance_type'], 'percentage')
        self.assertEqual(params['time_period'], 'monthly')
    
    def test_general_query_fallback(self):
        """Test fallback to general query when no pattern matches."""
        # Mock LLM to force pattern matching
        self.mock_llm.interpret.side_effect = Exception("Force pattern matching")
        
        # Test query that doesn't match any pattern
        result = self.analyzer.analyze_query("What is the meaning of life?")
        self.assertEqual(result.query_type, QueryType.GENERAL)
        self.assertEqual(result.confidence, 0.3)  # Low confidence for general queries


if __name__ == '__main__':
    unittest.main()
