"""
Function Call Parser for Gemma 3 Function Calling
Parses and validates function call responses from Gemma 3

This module handles the parsing of function call responses from Gemma 3,
validates them against function definitions, and prepares them for execution.
"""

import json
import re
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass

from ai.function_registry import function_registry


@dataclass
class ParsedFunctionCall:
    """Parsed function call with validation status"""
    function_name: str
    parameters: Dict[str, Any]
    is_valid: bool
    error_message: str = ""
    confidence: float = 0.0
    analyzer_type: str = ""


class FunctionCallParser:
    """
    Parser for Gemma 3 function call responses
    Handles both Python-style and JSON-style function call formats
    """
    
    def __init__(self):
        """Initialize the function call parser"""
        self.registry = function_registry
    
    def parse_function_call_response(self, response: str) -> List[ParsedFunctionCall]:
        """
        Parse function call response from Gemma 3
        
        Args:
            response: Raw response from Gemma 3 containing function calls
            
        Returns:
            List of parsed function calls
        """
        function_calls = []
        
        # Try different parsing strategies
        calls = self._extract_function_calls(response)
        
        for call in calls:
            parsed_call = self._parse_single_call(call)
            if parsed_call:
                function_calls.append(parsed_call)
        
        return function_calls
    
    def _extract_function_calls(self, response: str) -> List[str]:
        """
        Extract function call strings from response
        Handles both Python-style and JSON-style formats
        
        Args:
            response: Raw response text
            
        Returns:
            List of function call strings
        """
        calls = []
        
        # Pattern 1: Python-style function calls
        # Example: [analyze_time_variance(time_period="July", metric="budget_sales")]
        python_pattern = r'\[([a-zA-Z_][a-zA-Z0-9_]*\([^)]*\))\]'
        python_matches = re.findall(python_pattern, response)
        calls.extend(python_matches)
        
        # Pattern 2: JSON-style function calls
        # Example: {"name": "analyze_time_variance", "parameters": {"time_period": "July", "metric": "budget_sales"}}
        json_pattern = r'\{[^}]*"name"[^}]*"parameters"[^}]*\}'
        json_matches = re.findall(json_pattern, response, re.DOTALL)
        calls.extend(json_matches)
        
        # Pattern 3: Simple bracket notation
        # Example: [function_name(param1=value1, param2=value2)]
        bracket_pattern = r'\[([^]]+)\]'
        if not calls:  # Only try this if others failed
            bracket_matches = re.findall(bracket_pattern, response)
            for match in bracket_matches:
                if '(' in match and ')' in match:
                    calls.append(match)
        
        return calls
    
    def _parse_single_call(self, call_str: str) -> Optional[ParsedFunctionCall]:
        """
        Parse a single function call string
        
        Args:
            call_str: Function call string
            
        Returns:
            ParsedFunctionCall if successful, None otherwise
        """
        try:
            # Try JSON format first
            if call_str.strip().startswith('{'):
                return self._parse_json_call(call_str)
            
            # Try Python format
            return self._parse_python_call(call_str)
            
        except Exception as e:
            print(f"[PARSER] Error parsing function call '{call_str}': {str(e)}")
            return None
    
    def _parse_json_call(self, call_str: str) -> Optional[ParsedFunctionCall]:
        """
        Parse JSON-style function call
        
        Args:
            call_str: JSON function call string
            
        Returns:
            ParsedFunctionCall if successful, None otherwise
        """
        try:
            call_data = json.loads(call_str)
            function_name = call_data.get("name", "")
            parameters = call_data.get("parameters", {})
            
            return self._create_parsed_call(function_name, parameters)
            
        except json.JSONDecodeError as e:
            print(f"[PARSER] JSON parsing error: {str(e)}")
            return None
    
    def _parse_python_call(self, call_str: str) -> Optional[ParsedFunctionCall]:
        """
        Parse Python-style function call
        
        Args:
            call_str: Python function call string
            
        Returns:
            ParsedFunctionCall if successful, None otherwise
        """
        try:
            # Extract function name
            func_match = re.match(r'([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', call_str)
            if not func_match:
                return None
            
            function_name = func_match.group(1)
            
            # Extract parameters
            params_str = call_str[func_match.end():-1]  # Remove function name and parentheses
            parameters = self._parse_python_parameters(params_str)
            
            return self._create_parsed_call(function_name, parameters)
            
        except Exception as e:
            print(f"[PARSER] Python parsing error: {str(e)}")
            return None
    
    def _parse_python_parameters(self, params_str: str) -> Dict[str, Any]:
        """
        Parse Python-style parameters
        
        Args:
            params_str: Parameter string (e.g., 'param1="value1", param2=123')
            
        Returns:
            Dictionary of parameters
        """
        parameters = {}
        
        if not params_str.strip():
            return parameters
        
        # Split parameters by comma, but respect quoted strings
        param_parts = []
        current_part = ""
        in_quotes = False
        quote_char = None
        
        for char in params_str:
            if char in ['"', "'"] and not in_quotes:
                in_quotes = True
                quote_char = char
                current_part += char
            elif char == quote_char and in_quotes:
                in_quotes = False
                quote_char = None
                current_part += char
            elif char == ',' and not in_quotes:
                param_parts.append(current_part.strip())
                current_part = ""
            else:
                current_part += char
        
        if current_part.strip():
            param_parts.append(current_part.strip())
        
        # Parse each parameter
        for part in param_parts:
            if '=' not in part:
                continue
                
            key, value = part.split('=', 1)
            key = key.strip()
            value = value.strip()
            
            # Parse value
            parameters[key] = self._parse_parameter_value(value)
        
        return parameters
    
    def _parse_parameter_value(self, value_str: str) -> Any:
        """
        Parse parameter value from string
        
        Args:
            value_str: Value string
            
        Returns:
            Parsed value (string, int, float, bool, etc.)
        """
        value_str = value_str.strip()
        
        # Handle quoted strings
        if (value_str.startswith('"') and value_str.endswith('"')) or \
           (value_str.startswith("'") and value_str.endswith("'")):
            return value_str[1:-1]
        
        # Handle numbers
        try:
            if '.' in value_str:
                return float(value_str)
            return int(value_str)
        except ValueError:
            pass
        
        # Handle booleans
        if value_str.lower() == 'true':
            return True
        if value_str.lower() == 'false':
            return False
        
        # Handle null/none
        if value_str.lower() in ['null', 'none']:
            return None
        
        # Default to string
        return value_str
    
    def _create_parsed_call(self, function_name: str, parameters: Dict[str, Any]) -> ParsedFunctionCall:
        """
        Create and validate a ParsedFunctionCall
        
        Args:
            function_name: Name of the function
            parameters: Function parameters
            
        Returns:
            ValidatedFunctionCall with validation results
        """
        # Get function definition
        func_def = self.registry.get_function_by_name(function_name)
        
        if not func_def:
            return ParsedFunctionCall(
                function_name=function_name,
                parameters=parameters,
                is_valid=False,
                error_message=f"Unknown function: {function_name}",
                confidence=0.0
            )
        
        # Validate the call
        is_valid, error_message = self.registry.validate_function_call(function_name, parameters)
        
        # Calculate confidence based on parameter completeness
        confidence = self._calculate_confidence(func_def, parameters, is_valid)
        
        return ParsedFunctionCall(
            function_name=function_name,
            parameters=parameters,
            is_valid=is_valid,
            error_message=error_message,
            confidence=confidence,
            analyzer_type=func_def.analyzer_type
        )
    
    def _calculate_confidence(self, func_def, parameters: Dict[str, Any], is_valid: bool) -> float:
        """
        Calculate confidence score for the function call
        
        Args:
            func_def: Function definition
            parameters: Provided parameters
            is_valid: Whether the call is valid
            
        Returns:
            Confidence score (0.0 to 1.0)
        """
        if not is_valid:
            return 0.0
        
        base_confidence = func_def.confidence_boost
        
        # Check parameter completeness
        all_params = list(func_def.parameters.get("properties", {}).keys())
        required_params = func_def.parameters.get("required", [])
        provided_params = list(parameters.keys())
        
        # Boost for having all required parameters
        if all(param in provided_params for param in required_params):
            base_confidence += 0.2
        
        # Boost for having optional parameters
        optional_provided = len([p for p in provided_params if p not in required_params])
        if optional_provided > 0:
            base_confidence += min(0.1, optional_provided * 0.05)
        
        return min(1.0, base_confidence)
    
    def format_function_calls_for_execution(self, parsed_calls: List[ParsedFunctionCall]) -> List[Dict[str, Any]]:
        """
        Format parsed function calls for execution by analyzers
        
        Args:
            parsed_calls: List of parsed function calls
            
        Returns:
            List of execution-ready function call dictionaries
        """
        execution_calls = []
        
        for call in parsed_calls:
            if call.is_valid:
                execution_calls.append({
                    "function_name": call.function_name,
                    "analyzer_type": call.analyzer_type,
                    "parameters": call.parameters,
                    "confidence": call.confidence
                })
        
        return execution_calls
    
    def get_best_function_call(self, parsed_calls: List[ParsedFunctionCall]) -> Optional[ParsedFunctionCall]:
        """
        Get the best (highest confidence) valid function call
        
        Args:
            parsed_calls: List of parsed function calls
            
        Returns:
            Best function call or None if no valid calls
        """
        valid_calls = [call for call in parsed_calls if call.is_valid]
        
        if not valid_calls:
            return None
        
        return max(valid_calls, key=lambda call: call.confidence)


# Global parser instance
function_call_parser = FunctionCallParser()
