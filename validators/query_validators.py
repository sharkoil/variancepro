"""
Query Parameter Validators for Quant Commander

This module provides validation classes for different query types to ensure
that extracted parameters are valid and consistent before tool execution.

Author: AI Assistant
Date: July 2025
Phase: Enhanced Query Analysis
"""

from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum


class ValidationResult:
    """
    Result of parameter validation containing validation status and errors.
    """
    
    def __init__(self, is_valid: bool, errors: Optional[List[str]] = None):
        """
        Initialize validation result.
        
        Args:
            is_valid: Whether validation passed
            errors: List of validation error messages
        """
        self.is_valid = is_valid
        self.errors = errors or []
    
    def add_error(self, error: str) -> None:
        """
        Add a validation error.
        
        Args:
            error: Error message to add
        """
        self.errors.append(error)
        self.is_valid = False


class BaseValidator:
    """
    Base class for all parameter validators.
    
    Provides common validation utilities and structure for specific validators.
    """
    
    def __init__(self):
        """Initialize base validator."""
        self.required_fields: List[str] = []
        self.optional_fields: List[str] = []
    
    def validate_parameters(self, params: Dict[str, Any]) -> ValidationResult:
        """
        Validate parameters for this query type.
        
        Args:
            params: Parameters dictionary to validate
            
        Returns:
            ValidationResult with validation status and errors
        """
        result = ValidationResult(is_valid=True)
        
        # Check required fields
        for field in self.required_fields:
            if field not in params:
                result.add_error(f"Missing required field: {field}")
        
        # Validate field types and values
        self._validate_field_types(params, result)
        self._validate_field_values(params, result)
        
        return result
    
    def _validate_field_types(self, params: Dict[str, Any], result: ValidationResult) -> None:
        """
        Validate field types. Override in subclasses.
        
        Args:
            params: Parameters to validate
            result: ValidationResult to update
        """
        pass
    
    def _validate_field_values(self, params: Dict[str, Any], result: ValidationResult) -> None:
        """
        Validate field values. Override in subclasses.
        
        Args:
            params: Parameters to validate
            result: ValidationResult to update
        """
        pass
    
    def _validate_time_period(self, time_period: str, result: ValidationResult) -> None:
        """
        Validate time period value.
        
        Args:
            time_period: Time period string to validate
            result: ValidationResult to update
        """
        valid_periods = ['daily', 'weekly', 'monthly', 'quarterly', 'yearly']
        if time_period not in valid_periods:
            result.add_error(f"Invalid time_period '{time_period}'. Must be one of: {valid_periods}")
    
    def _validate_positive_integer(self, value: Any, field_name: str, result: ValidationResult) -> None:
        """
        Validate that a value is a positive integer.
        
        Args:
            value: Value to validate
            field_name: Name of the field being validated
            result: ValidationResult to update
        """
        if not isinstance(value, int):
            result.add_error(f"Field '{field_name}' must be an integer")
        elif value <= 0:
            result.add_error(f"Field '{field_name}' must be a positive integer")
    
    def _validate_string_choice(self, value: Any, field_name: str, choices: List[str], result: ValidationResult) -> None:
        """
        Validate that a value is one of the allowed string choices.
        
        Args:
            value: Value to validate
            field_name: Name of the field being validated
            choices: List of allowed choices
            result: ValidationResult to update
        """
        if not isinstance(value, str):
            result.add_error(f"Field '{field_name}' must be a string")
        elif value not in choices:
            result.add_error(f"Field '{field_name}' must be one of: {choices}")


class TopBottomValidator(BaseValidator):
    """
    Validator for top/bottom query parameters.
    
    Validates parameters for top N and bottom N analysis queries including
    direction, count, sorting, and time aggregation parameters.
    """
    
    def __init__(self):
        """Initialize top/bottom validator."""
        super().__init__()
        self.required_fields = ['direction']
        self.optional_fields = [
            'count', 'sort_column', 'time_period', 'aggregation_method',
            'grouping_columns', 'filter_column', 'filter_value'
        ]
    
    def _validate_field_types(self, params: Dict[str, Any], result: ValidationResult) -> None:
        """
        Validate field types for top/bottom parameters.
        
        Args:
            params: Parameters to validate
            result: ValidationResult to update
        """
        # Validate direction
        if 'direction' in params:
            if not isinstance(params['direction'], str):
                result.add_error("Field 'direction' must be a string")
        
        # Validate count
        if 'count' in params:
            if not isinstance(params['count'], int):
                result.add_error("Field 'count' must be an integer")
        
        # Validate sort_column
        if 'sort_column' in params:
            if not isinstance(params['sort_column'], str):
                result.add_error("Field 'sort_column' must be a string")
        
        # Validate time_period
        if 'time_period' in params:
            if not isinstance(params['time_period'], str):
                result.add_error("Field 'time_period' must be a string")
        
        # Validate aggregation_method
        if 'aggregation_method' in params:
            if not isinstance(params['aggregation_method'], str):
                result.add_error("Field 'aggregation_method' must be a string")
        
        # Validate grouping_columns
        if 'grouping_columns' in params:
            if not isinstance(params['grouping_columns'], list):
                result.add_error("Field 'grouping_columns' must be a list")
            elif not all(isinstance(col, str) for col in params['grouping_columns']):
                result.add_error("All items in 'grouping_columns' must be strings")
    
    def _validate_field_values(self, params: Dict[str, Any], result: ValidationResult) -> None:
        """
        Validate field values for top/bottom parameters.
        
        Args:
            params: Parameters to validate
            result: ValidationResult to update
        """
        # Validate direction value
        if 'direction' in params:
            self._validate_string_choice(
                params['direction'], 'direction', ['top', 'bottom'], result
            )
        
        # Validate count value
        if 'count' in params:
            self._validate_positive_integer(params['count'], 'count', result)
            if isinstance(params['count'], int) and params['count'] > 1000:
                result.add_error("Field 'count' cannot exceed 1000")
        
        # Validate time_period value
        if 'time_period' in params:
            self._validate_time_period(params['time_period'], result)
        
        # Validate aggregation_method value
        if 'aggregation_method' in params:
            valid_methods = ['sum', 'avg', 'mean', 'max', 'min', 'count']
            self._validate_string_choice(
                params['aggregation_method'], 'aggregation_method', valid_methods, result
            )
        
        # Validate grouping_columns length
        if 'grouping_columns' in params:
            if len(params['grouping_columns']) > 10:
                result.add_error("Field 'grouping_columns' cannot have more than 10 columns")


class VarianceValidator(BaseValidator):
    """
    Validator for variance query parameters.
    
    Validates parameters for variance analysis queries including actual/budget
    columns, variance type, time periods, and grouping parameters.
    """
    
    def __init__(self):
        """Initialize variance validator."""
        super().__init__()
        self.required_fields = []  # No strictly required fields for variance
        self.optional_fields = [
            'actual_column', 'budget_column', 'variance_type', 'time_period',
            'periods', 'grouping_columns', 'threshold'
        ]
    
    def _validate_field_types(self, params: Dict[str, Any], result: ValidationResult) -> None:
        """
        Validate field types for variance parameters.
        
        Args:
            params: Parameters to validate
            result: ValidationResult to update
        """
        # Validate column names
        for field in ['actual_column', 'budget_column']:
            if field in params:
                if not isinstance(params[field], str):
                    result.add_error(f"Field '{field}' must be a string")
        
        # Validate variance_type
        if 'variance_type' in params:
            if not isinstance(params['variance_type'], str):
                result.add_error("Field 'variance_type' must be a string")
        
        # Validate time_period
        if 'time_period' in params:
            if not isinstance(params['time_period'], str):
                result.add_error("Field 'time_period' must be a string")
        
        # Validate periods
        if 'periods' in params:
            if not isinstance(params['periods'], int):
                result.add_error("Field 'periods' must be an integer")
        
        # Validate grouping_columns
        if 'grouping_columns' in params:
            if not isinstance(params['grouping_columns'], list):
                result.add_error("Field 'grouping_columns' must be a list")
            elif not all(isinstance(col, str) for col in params['grouping_columns']):
                result.add_error("All items in 'grouping_columns' must be strings")
        
        # Validate threshold
        if 'threshold' in params:
            if not isinstance(params['threshold'], (int, float)):
                result.add_error("Field 'threshold' must be a number")
    
    def _validate_field_values(self, params: Dict[str, Any], result: ValidationResult) -> None:
        """
        Validate field values for variance parameters.
        
        Args:
            params: Parameters to validate
            result: ValidationResult to update
        """
        # Validate variance_type value
        if 'variance_type' in params:
            valid_types = ['absolute', 'percentage', 'both']
            self._validate_string_choice(
                params['variance_type'], 'variance_type', valid_types, result
            )
        
        # Validate time_period value
        if 'time_period' in params:
            self._validate_time_period(params['time_period'], result)
        
        # Validate periods value
        if 'periods' in params:
            self._validate_positive_integer(params['periods'], 'periods', result)
            if isinstance(params['periods'], int) and params['periods'] > 120:
                result.add_error("Field 'periods' cannot exceed 120")
        
        # Validate threshold value
        if 'threshold' in params:
            if isinstance(params['threshold'], (int, float)):
                if params['threshold'] < 0:
                    result.add_error("Field 'threshold' cannot be negative")
        
        # Validate grouping_columns length
        if 'grouping_columns' in params:
            if len(params['grouping_columns']) > 10:
                result.add_error("Field 'grouping_columns' cannot have more than 10 columns")


class SummaryValidator(BaseValidator):
    """
    Validator for summary query parameters.
    
    Validates parameters for summary analysis queries including focus columns
    and analysis depth parameters.
    """
    
    def __init__(self):
        """Initialize summary validator."""
        super().__init__()
        self.required_fields = []  # No required fields for summary
        self.optional_fields = [
            'focus_columns', 'include_stats', 'include_trends', 'detail_level'
        ]
    
    def _validate_field_types(self, params: Dict[str, Any], result: ValidationResult) -> None:
        """
        Validate field types for summary parameters.
        
        Args:
            params: Parameters to validate
            result: ValidationResult to update
        """
        # Validate focus_columns
        if 'focus_columns' in params:
            if not isinstance(params['focus_columns'], list):
                result.add_error("Field 'focus_columns' must be a list")
            elif not all(isinstance(col, str) for col in params['focus_columns']):
                result.add_error("All items in 'focus_columns' must be strings")
        
        # Validate boolean fields
        for field in ['include_stats', 'include_trends']:
            if field in params:
                if not isinstance(params[field], bool):
                    result.add_error(f"Field '{field}' must be a boolean")
        
        # Validate detail_level
        if 'detail_level' in params:
            if not isinstance(params['detail_level'], str):
                result.add_error("Field 'detail_level' must be a string")
    
    def _validate_field_values(self, params: Dict[str, Any], result: ValidationResult) -> None:
        """
        Validate field values for summary parameters.
        
        Args:
            params: Parameters to validate
            result: ValidationResult to update
        """
        # Validate detail_level value
        if 'detail_level' in params:
            valid_levels = ['basic', 'detailed', 'comprehensive']
            self._validate_string_choice(
                params['detail_level'], 'detail_level', valid_levels, result
            )
        
        # Validate focus_columns length
        if 'focus_columns' in params:
            if len(params['focus_columns']) > 20:
                result.add_error("Field 'focus_columns' cannot have more than 20 columns")


class TrendsValidator(BaseValidator):
    """
    Validator for trends query parameters.
    
    Validates parameters for trend analysis queries including time periods,
    focus columns, and trend analysis parameters.
    """
    
    def __init__(self):
        """Initialize trends validator."""
        super().__init__()
        self.required_fields = []  # No required fields for trends
        self.optional_fields = [
            'focus_columns', 'time_period', 'periods', 'trend_type', 'smoothing'
        ]
    
    def _validate_field_types(self, params: Dict[str, Any], result: ValidationResult) -> None:
        """
        Validate field types for trends parameters.
        
        Args:
            params: Parameters to validate
            result: ValidationResult to update
        """
        # Validate focus_columns
        if 'focus_columns' in params:
            if not isinstance(params['focus_columns'], list):
                result.add_error("Field 'focus_columns' must be a list")
            elif not all(isinstance(col, str) for col in params['focus_columns']):
                result.add_error("All items in 'focus_columns' must be strings")
        
        # Validate time_period
        if 'time_period' in params:
            if not isinstance(params['time_period'], str):
                result.add_error("Field 'time_period' must be a string")
        
        # Validate periods
        if 'periods' in params:
            if not isinstance(params['periods'], int):
                result.add_error("Field 'periods' must be an integer")
        
        # Validate trend_type
        if 'trend_type' in params:
            if not isinstance(params['trend_type'], str):
                result.add_error("Field 'trend_type' must be a string")
        
        # Validate smoothing
        if 'smoothing' in params:
            if not isinstance(params['smoothing'], bool):
                result.add_error("Field 'smoothing' must be a boolean")
    
    def _validate_field_values(self, params: Dict[str, Any], result: ValidationResult) -> None:
        """
        Validate field values for trends parameters.
        
        Args:
            params: Parameters to validate
            result: ValidationResult to update
        """
        # Validate time_period value
        if 'time_period' in params:
            self._validate_time_period(params['time_period'], result)
        
        # Validate periods value
        if 'periods' in params:
            self._validate_positive_integer(params['periods'], 'periods', result)
            if isinstance(params['periods'], int) and params['periods'] > 120:
                result.add_error("Field 'periods' cannot exceed 120")
        
        # Validate trend_type value
        if 'trend_type' in params:
            valid_types = ['linear', 'exponential', 'seasonal', 'auto']
            self._validate_string_choice(
                params['trend_type'], 'trend_type', valid_types, result
            )
        
        # Validate focus_columns length
        if 'focus_columns' in params:
            if len(params['focus_columns']) > 10:
                result.add_error("Field 'focus_columns' cannot have more than 10 columns")


def get_validator(query_type: str) -> BaseValidator:
    """
    Get the appropriate validator for a query type.
    
    Args:
        query_type: Type of query to validate
        
    Returns:
        Appropriate validator instance
    """
    validators = {
        'top_bottom': TopBottomValidator,
        'variance': VarianceValidator,
        'summary': SummaryValidator,
        'trends': TrendsValidator
    }
    
    validator_class = validators.get(query_type, BaseValidator)
    return validator_class()
