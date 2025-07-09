"""
Unit tests for Query Validators

This module tests the parameter validation functionality to ensure
that extracted parameters are properly validated before tool execution.

Author: AI Assistant
Date: July 2025
Phase: Enhanced Query Analysis
"""

import unittest

# Add the parent directory to the path to import our modules
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from validators.query_validators import (
    TopBottomValidator, VarianceValidator, SummaryValidator, TrendsValidator,
    ValidationResult, get_validator
)


class TestValidationResult(unittest.TestCase):
    """Test suite for ValidationResult class."""
    
    def test_validation_result_initialization(self):
        """Test ValidationResult initialization."""
        # Test valid result
        result = ValidationResult(is_valid=True)
        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.errors), 0)
        
        # Test invalid result with errors
        result = ValidationResult(is_valid=False, errors=["Error 1", "Error 2"])
        self.assertFalse(result.is_valid)
        self.assertEqual(len(result.errors), 2)
    
    def test_add_error_functionality(self):
        """Test adding errors to ValidationResult."""
        result = ValidationResult(is_valid=True)
        
        # Add error should set is_valid to False
        result.add_error("Test error")
        self.assertFalse(result.is_valid)
        self.assertEqual(len(result.errors), 1)
        self.assertEqual(result.errors[0], "Test error")
        
        # Add multiple errors
        result.add_error("Second error")
        self.assertEqual(len(result.errors), 2)


class TestTopBottomValidator(unittest.TestCase):
    """Test suite for TopBottomValidator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.validator = TopBottomValidator()
    
    def test_validator_initialization(self):
        """Test TopBottomValidator initialization."""
        self.assertIn('direction', self.validator.required_fields)
        self.assertIn('count', self.validator.optional_fields)
        self.assertIn('sort_column', self.validator.optional_fields)
    
    def test_valid_top_bottom_parameters(self):
        """Test validation of valid top/bottom parameters."""
        valid_params = {
            'direction': 'top',
            'count': 10,
            'sort_column': 'revenue',
            'time_period': 'monthly',
            'aggregation_method': 'sum',
            'grouping_columns': ['category', 'region']
        }
        
        result = self.validator.validate_parameters(valid_params)
        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.errors), 0)
    
    def test_missing_required_field(self):
        """Test validation with missing required field."""
        invalid_params = {
            'count': 10,
            'sort_column': 'revenue'
        }
        
        result = self.validator.validate_parameters(invalid_params)
        self.assertFalse(result.is_valid)
        self.assertIn("Missing required field: direction", result.errors)
    
    def test_invalid_direction_value(self):
        """Test validation with invalid direction value."""
        invalid_params = {
            'direction': 'middle',  # Invalid value
            'count': 10
        }
        
        result = self.validator.validate_parameters(invalid_params)
        self.assertFalse(result.is_valid)
        self.assertIn("must be one of", result.errors[0])
    
    def test_invalid_count_value(self):
        """Test validation with invalid count value."""
        # Test negative count
        invalid_params = {
            'direction': 'top',
            'count': -5
        }
        
        result = self.validator.validate_parameters(invalid_params)
        self.assertFalse(result.is_valid)
        self.assertIn("positive integer", result.errors[0])
        
        # Test count exceeding limit
        invalid_params = {
            'direction': 'top',
            'count': 1500  # Exceeds limit
        }
        
        result = self.validator.validate_parameters(invalid_params)
        self.assertFalse(result.is_valid)
        self.assertIn("cannot exceed 1000", result.errors[0])
    
    def test_invalid_time_period(self):
        """Test validation with invalid time period."""
        invalid_params = {
            'direction': 'top',
            'time_period': 'invalid_period'
        }
        
        result = self.validator.validate_parameters(invalid_params)
        self.assertFalse(result.is_valid)
        self.assertIn("Invalid time_period", result.errors[0])
    
    def test_invalid_aggregation_method(self):
        """Test validation with invalid aggregation method."""
        invalid_params = {
            'direction': 'top',
            'aggregation_method': 'invalid_method'
        }
        
        result = self.validator.validate_parameters(invalid_params)
        self.assertFalse(result.is_valid)
        self.assertIn("aggregation_method", result.errors[0])
    
    def test_invalid_grouping_columns(self):
        """Test validation with invalid grouping columns."""
        # Test non-list grouping_columns
        invalid_params = {
            'direction': 'top',
            'grouping_columns': 'not_a_list'
        }
        
        result = self.validator.validate_parameters(invalid_params)
        self.assertFalse(result.is_valid)
        self.assertIn("must be a list", result.errors[0])
        
        # Test non-string items in list
        invalid_params = {
            'direction': 'top',
            'grouping_columns': ['valid_string', 123]
        }
        
        result = self.validator.validate_parameters(invalid_params)
        self.assertFalse(result.is_valid)
        self.assertIn("must be strings", result.errors[0])
        
        # Test too many columns
        invalid_params = {
            'direction': 'top',
            'grouping_columns': [f'col_{i}' for i in range(15)]  # Too many
        }
        
        result = self.validator.validate_parameters(invalid_params)
        self.assertFalse(result.is_valid)
        self.assertIn("cannot have more than 10", result.errors[0])


class TestVarianceValidator(unittest.TestCase):
    """Test suite for VarianceValidator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.validator = VarianceValidator()
    
    def test_validator_initialization(self):
        """Test VarianceValidator initialization."""
        self.assertEqual(len(self.validator.required_fields), 0)  # No required fields
        self.assertIn('actual_column', self.validator.optional_fields)
        self.assertIn('budget_column', self.validator.optional_fields)
        self.assertIn('variance_type', self.validator.optional_fields)
    
    def test_valid_variance_parameters(self):
        """Test validation of valid variance parameters."""
        valid_params = {
            'actual_column': 'actual_sales',
            'budget_column': 'budget_sales',
            'variance_type': 'percentage',
            'time_period': 'monthly',
            'periods': 12,
            'grouping_columns': ['region', 'product'],
            'threshold': 0.05
        }
        
        result = self.validator.validate_parameters(valid_params)
        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.errors), 0)
    
    def test_invalid_variance_type(self):
        """Test validation with invalid variance type."""
        invalid_params = {
            'variance_type': 'invalid_type'
        }
        
        result = self.validator.validate_parameters(invalid_params)
        self.assertFalse(result.is_valid)
        self.assertIn("must be one of", result.errors[0])
    
    def test_invalid_periods_value(self):
        """Test validation with invalid periods value."""
        # Test negative periods
        invalid_params = {
            'periods': -5
        }
        
        result = self.validator.validate_parameters(invalid_params)
        self.assertFalse(result.is_valid)
        self.assertIn("positive integer", result.errors[0])
        
        # Test periods exceeding limit
        invalid_params = {
            'periods': 150  # Exceeds limit
        }
        
        result = self.validator.validate_parameters(invalid_params)
        self.assertFalse(result.is_valid)
        self.assertIn("cannot exceed 120", result.errors[0])
    
    def test_invalid_threshold_value(self):
        """Test validation with invalid threshold value."""
        # Test negative threshold
        invalid_params = {
            'threshold': -0.1
        }
        
        result = self.validator.validate_parameters(invalid_params)
        self.assertFalse(result.is_valid)
        self.assertIn("cannot be negative", result.errors[0])
        
        # Test non-numeric threshold
        invalid_params = {
            'threshold': 'not_a_number'
        }
        
        result = self.validator.validate_parameters(invalid_params)
        self.assertFalse(result.is_valid)
        self.assertIn("must be a number", result.errors[0])


class TestSummaryValidator(unittest.TestCase):
    """Test suite for SummaryValidator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.validator = SummaryValidator()
    
    def test_validator_initialization(self):
        """Test SummaryValidator initialization."""
        self.assertEqual(len(self.validator.required_fields), 0)  # No required fields
        self.assertIn('focus_columns', self.validator.optional_fields)
        self.assertIn('detail_level', self.validator.optional_fields)
    
    def test_valid_summary_parameters(self):
        """Test validation of valid summary parameters."""
        valid_params = {
            'focus_columns': ['revenue', 'cost', 'profit'],
            'include_stats': True,
            'include_trends': False,
            'detail_level': 'detailed'
        }
        
        result = self.validator.validate_parameters(valid_params)
        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.errors), 0)
    
    def test_invalid_detail_level(self):
        """Test validation with invalid detail level."""
        invalid_params = {
            'detail_level': 'invalid_level'
        }
        
        result = self.validator.validate_parameters(invalid_params)
        self.assertFalse(result.is_valid)
        self.assertIn("detail_level", result.errors[0])
    
    def test_invalid_boolean_fields(self):
        """Test validation with invalid boolean fields."""
        invalid_params = {
            'include_stats': 'not_boolean',
            'include_trends': 'also_not_boolean'
        }
        
        result = self.validator.validate_parameters(invalid_params)
        self.assertFalse(result.is_valid)
        self.assertIn("must be a boolean", result.errors[0])
        self.assertIn("must be a boolean", result.errors[1])
    
    def test_too_many_focus_columns(self):
        """Test validation with too many focus columns."""
        invalid_params = {
            'focus_columns': [f'col_{i}' for i in range(25)]  # Too many
        }
        
        result = self.validator.validate_parameters(invalid_params)
        self.assertFalse(result.is_valid)
        self.assertIn("cannot have more than 20", result.errors[0])


class TestTrendsValidator(unittest.TestCase):
    """Test suite for TrendsValidator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.validator = TrendsValidator()
    
    def test_validator_initialization(self):
        """Test TrendsValidator initialization."""
        self.assertEqual(len(self.validator.required_fields), 0)  # No required fields
        self.assertIn('focus_columns', self.validator.optional_fields)
        self.assertIn('trend_type', self.validator.optional_fields)
    
    def test_valid_trends_parameters(self):
        """Test validation of valid trends parameters."""
        valid_params = {
            'focus_columns': ['revenue', 'growth'],
            'time_period': 'monthly',
            'periods': 24,
            'trend_type': 'linear',
            'smoothing': True
        }
        
        result = self.validator.validate_parameters(valid_params)
        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.errors), 0)
    
    def test_invalid_trend_type(self):
        """Test validation with invalid trend type."""
        invalid_params = {
            'trend_type': 'invalid_trend'
        }
        
        result = self.validator.validate_parameters(invalid_params)
        self.assertFalse(result.is_valid)
        self.assertIn("trend_type", result.errors[0])
    
    def test_invalid_smoothing_value(self):
        """Test validation with invalid smoothing value."""
        invalid_params = {
            'smoothing': 'not_boolean'
        }
        
        result = self.validator.validate_parameters(invalid_params)
        self.assertFalse(result.is_valid)
        self.assertIn("must be a boolean", result.errors[0])


class TestValidatorFactory(unittest.TestCase):
    """Test suite for validator factory function."""
    
    def test_get_validator_function(self):
        """Test get_validator function returns correct validators."""
        # Test top_bottom validator
        validator = get_validator('top_bottom')
        self.assertIsInstance(validator, TopBottomValidator)
        
        # Test variance validator
        validator = get_validator('variance')
        self.assertIsInstance(validator, VarianceValidator)
        
        # Test summary validator
        validator = get_validator('summary')
        self.assertIsInstance(validator, SummaryValidator)
        
        # Test trends validator
        validator = get_validator('trends')
        self.assertIsInstance(validator, TrendsValidator)
        
        # Test unknown validator returns BaseValidator
        validator = get_validator('unknown_type')
        self.assertEqual(type(validator).__name__, 'BaseValidator')


if __name__ == '__main__':
    unittest.main()
