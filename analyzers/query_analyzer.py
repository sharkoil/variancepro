"""
Query Analysis Service for Quant Commander

This module provides LLM-powered query analysis to understand user intents
and convert natural language queries into structured JSON parameters.

This replaces the brittle regex-based approach with intelligent query understanding
that can handle complex natural language requests.

Author: AI Assistant
Date: July 2025
Phase: Enhanced Query Analysis
"""

import json
import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

from ai.llm_interpreter import LLMInterpreter
from config.settings import get_settings


class QueryType(Enum):
    """Enumeration of supported query types for structured analysis."""
    TOP_BOTTOM = "top_bottom"
    VARIANCE = "variance"
    SUMMARY = "summary"
    TRENDS = "trends"
    FORECAST = "forecast"
    GENERAL = "general"
    UNKNOWN = "unknown"


@dataclass
class QueryAnalysisResult:
    """
    Structured result from query analysis containing the detected query type
    and extracted parameters in a validated format.
    """
    query_type: QueryType
    parameters: Dict[str, Any]
    confidence: float
    raw_query: str
    validation_errors: List[str]


class QueryAnalyzer:
    """
    LLM-powered query analyzer that understands natural language queries
    and converts them into structured JSON parameters for tool execution.
    
    This service replaces regex-based parsing with intelligent understanding
    of user intent, supporting complex queries with time aggregation and
    sophisticated parameter extraction.
    """
    
    def __init__(self, llm_interpreter: Optional[LLMInterpreter] = None):
        """
        Initialize the query analyzer with LLM interpreter.
        
        Args:
            llm_interpreter: LLM interpreter instance for query understanding
        """
        self.settings = get_settings()
        self.llm_interpreter = llm_interpreter or LLMInterpreter(self.settings)
        
        # Define query detection patterns as fallback
        self.query_patterns = {
            QueryType.TOP_BOTTOM: [
                r'(top|bottom)\s*(\d+)?',
                r'(highest|lowest|best|worst)\s*(\d+)?',
                r'(largest|smallest)\s*(\d+)?'
            ],
            QueryType.VARIANCE: [
                r'variance|deviation|difference|gap',
                r'actual\s*vs\s*budget|budget\s*vs\s*actual',
                r'compare.*budget|budget.*compare'
            ],
            QueryType.SUMMARY: [
                r'summary|overview|describe|explain',
                r'what.*data|tell.*about|analyze'
            ],
            QueryType.TRENDS: [
                r'trend|pattern|over\s*time|timeline',
                r'seasonal|monthly|quarterly|yearly'
            ]
        }
    
    def analyze_query(self, user_query: str) -> QueryAnalysisResult:
        """
        Analyze a user query and return structured parameters.
        
        This method uses LLM to understand the query intent and extract
        parameters, falling back to pattern matching if LLM fails.
        
        Args:
            user_query: Natural language query from user
            
        Returns:
            QueryAnalysisResult with detected type and parameters
        """
        # Clean and normalize the query
        normalized_query = self._normalize_query(user_query)
        
        # Try LLM-based analysis first
        try:
            llm_result = self._analyze_with_llm(normalized_query)
            if llm_result.confidence > 0.7:
                return llm_result
        except Exception as e:
            print(f"⚠️ LLM analysis failed: {e}")
        
        # Fall back to pattern-based analysis
        return self._analyze_with_patterns(normalized_query)
    
    def _normalize_query(self, query: str) -> str:
        """
        Clean and normalize user query for better analysis.
        
        Args:
            query: Raw user query
            
        Returns:
            Normalized query string
        """
        # Convert to lowercase for consistent processing
        normalized = query.lower().strip()
        
        # Remove extra whitespace
        normalized = re.sub(r'\s+', ' ', normalized)
        
        # Remove common filler words that don't affect meaning
        filler_words = ['please', 'can you', 'could you', 'would you']
        for filler in filler_words:
            normalized = normalized.replace(filler, '')
        
        return normalized.strip()
    
    def _analyze_with_llm(self, query: str) -> QueryAnalysisResult:
        """
        Use LLM to analyze query and extract structured parameters.
        
        Args:
            query: Normalized user query
            
        Returns:
            QueryAnalysisResult from LLM analysis
        """
        # Create LLM prompt for query analysis
        prompt = self._create_analysis_prompt(query)
        
        # Get LLM response
        response = self.llm_interpreter.interpret(prompt)
        
        # Parse JSON response
        try:
            result_data = json.loads(response)
            return self._create_result_from_llm(query, result_data)
        except json.JSONDecodeError:
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                result_data = json.loads(json_match.group())
                return self._create_result_from_llm(query, result_data)
            else:
                raise ValueError("No valid JSON in LLM response")
    
    def _create_analysis_prompt(self, query: str) -> str:
        """
        Create a structured prompt for LLM query analysis.
        
        Args:
            query: User query to analyze
            
        Returns:
            Formatted prompt for LLM
        """
        return f"""
Analyze this user query and return a structured JSON response:

Query: "{query}"

Detect the query type and extract parameters. Return JSON in this format:

{{
  "query_type": "top_bottom|variance|summary|trends|forecast|general",
  "confidence": 0.0-1.0,
  "parameters": {{
    // For top_bottom:
    "direction": "top|bottom",
    "count": number,
    "sort_column": "column_name",
    "time_period": "daily|weekly|monthly|quarterly|yearly",
    "aggregation_method": "sum|avg|max|min|count",
    "grouping_columns": ["col1", "col2"],
    
    // For variance:
    "actual_column": "column_name",
    "budget_column": "column_name", 
    "variance_type": "absolute|percentage",
    "time_period": "daily|weekly|monthly|quarterly|yearly",
    "periods": number,
    "grouping_columns": ["col1", "col2"],
    
    // For summary/trends/forecast:
    "focus_columns": ["col1", "col2"],
    "time_period": "daily|weekly|monthly|quarterly|yearly",
    "periods": number
  }}
}}

Examples:
- "Show me top 5 products by revenue this month" → top_bottom with monthly aggregation
- "Compare actual vs budget sales by quarter" → variance with quarterly periods
- "What's the variance in costs over the last 6 months" → variance with monthly periods
- "Give me a summary of the data" → summary
"""
    
    def _create_result_from_llm(self, query: str, llm_data: Dict) -> QueryAnalysisResult:
        """
        Create QueryAnalysisResult from LLM response data.
        
        Args:
            query: Original user query
            llm_data: Parsed JSON from LLM
            
        Returns:
            Structured QueryAnalysisResult
        """
        # Extract query type
        query_type_str = llm_data.get('query_type', 'unknown')
        query_type = QueryType(query_type_str) if query_type_str in [q.value for q in QueryType] else QueryType.UNKNOWN
        
        # Extract parameters and confidence
        parameters = llm_data.get('parameters', {})
        confidence = llm_data.get('confidence', 0.0)
        
        # Validate parameters
        validation_errors = self._validate_parameters(query_type, parameters)
        
        return QueryAnalysisResult(
            query_type=query_type,
            parameters=parameters,
            confidence=confidence,
            raw_query=query,
            validation_errors=validation_errors
        )
    
    def _analyze_with_patterns(self, query: str) -> QueryAnalysisResult:
        """
        Fallback pattern-based analysis when LLM fails.
        
        Args:
            query: Normalized user query
            
        Returns:
            QueryAnalysisResult from pattern matching
        """
        # Try to match query patterns
        for query_type, patterns in self.query_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query, re.IGNORECASE):
                    parameters = self._extract_parameters_from_pattern(query, query_type, pattern)
                    return QueryAnalysisResult(
                        query_type=query_type,
                        parameters=parameters,
                        confidence=0.6,  # Lower confidence for pattern matching
                        raw_query=query,
                        validation_errors=[]
                    )
        
        # Default to general query if no pattern matches
        return QueryAnalysisResult(
            query_type=QueryType.GENERAL,
            parameters={},
            confidence=0.3,
            raw_query=query,
            validation_errors=[]
        )
    
    def _extract_parameters_from_pattern(self, query: str, query_type: QueryType, pattern: str) -> Dict[str, Any]:
        """
        Extract parameters from query using pattern matching.
        
        Args:
            query: User query
            query_type: Detected query type
            pattern: Regex pattern that matched
            
        Returns:
            Extracted parameters dictionary
        """
        parameters = {}
        
        if query_type == QueryType.TOP_BOTTOM:
            # Extract direction (top/bottom)
            if re.search(r'(top|highest|best|largest)', query):
                parameters['direction'] = 'top'
            else:
                parameters['direction'] = 'bottom'
            
            # Extract count
            count_match = re.search(r'(\d+)', query)
            parameters['count'] = int(count_match.group(1)) if count_match else 10
            
            # Try to detect time period
            if re.search(r'(month|monthly)', query):
                parameters['time_period'] = 'monthly'
            elif re.search(r'(quarter|quarterly)', query):
                parameters['time_period'] = 'quarterly'
            elif re.search(r'(year|yearly|annual)', query):
                parameters['time_period'] = 'yearly'
            elif re.search(r'(week|weekly)', query):
                parameters['time_period'] = 'weekly'
            elif re.search(r'(day|daily)', query):
                parameters['time_period'] = 'daily'
            else:
                parameters['time_period'] = 'daily'
        
        elif query_type == QueryType.VARIANCE:
            # Default variance parameters
            parameters['variance_type'] = 'percentage'
            parameters['periods'] = 12
            
            # Try to detect time period
            if re.search(r'(month|monthly)', query):
                parameters['time_period'] = 'monthly'
            elif re.search(r'(quarter|quarterly)', query):
                parameters['time_period'] = 'quarterly'
            elif re.search(r'(year|yearly|annual)', query):
                parameters['time_period'] = 'yearly'
            elif re.search(r'(week|weekly)', query):
                parameters['time_period'] = 'weekly'
            elif re.search(r'(day|daily)', query):
                parameters['time_period'] = 'daily'
            else:
                parameters['time_period'] = 'monthly'
            
            # Try to detect specific columns
            if re.search(r'actual', query):
                parameters['actual_column'] = 'actual'
            if re.search(r'budget', query):
                parameters['budget_column'] = 'budget'
        
        return parameters
    
    def _validate_parameters(self, query_type: QueryType, parameters: Dict[str, Any]) -> List[str]:
        """
        Validate extracted parameters for the given query type.
        
        Args:
            query_type: Type of query being validated
            parameters: Parameters to validate
            
        Returns:
            List of validation error messages
        """
        errors = []
        
        if query_type == QueryType.TOP_BOTTOM:
            # Validate required parameters
            if 'direction' not in parameters:
                errors.append("Missing required parameter: direction")
            elif parameters['direction'] not in ['top', 'bottom']:
                errors.append("Invalid direction: must be 'top' or 'bottom'")
            
            if 'count' in parameters:
                if not isinstance(parameters['count'], int) or parameters['count'] <= 0:
                    errors.append("Invalid count: must be positive integer")
            
            if 'time_period' in parameters:
                valid_periods = ['daily', 'weekly', 'monthly', 'quarterly', 'yearly']
                if parameters['time_period'] not in valid_periods:
                    errors.append(f"Invalid time_period: must be one of {valid_periods}")
        
        elif query_type == QueryType.VARIANCE:
            # Validate variance parameters
            if 'variance_type' in parameters:
                if parameters['variance_type'] not in ['absolute', 'percentage']:
                    errors.append("Invalid variance_type: must be 'absolute' or 'percentage'")
            
            if 'periods' in parameters:
                if not isinstance(parameters['periods'], int) or parameters['periods'] <= 0:
                    errors.append("Invalid periods: must be positive integer")
        
        return errors
    
    def detect_query_type(self, query: str) -> QueryType:
        """
        Quick detection of query type without full analysis.
        
        Args:
            query: User query
            
        Returns:
            Detected QueryType
        """
        result = self.analyze_query(query)
        return result.query_type
    
    def parse_top_bottom_query(self, query: str) -> Dict[str, Any]:
        """
        Parse a top/bottom query and return parameters.
        
        Args:
            query: User query expected to be top/bottom type
            
        Returns:
            Dictionary of top/bottom parameters
        """
        result = self.analyze_query(query)
        if result.query_type == QueryType.TOP_BOTTOM:
            return result.parameters
        else:
            # Force interpretation as top/bottom
            return self._extract_parameters_from_pattern(query, QueryType.TOP_BOTTOM, "")
    
    def parse_variance_query(self, query: str) -> Dict[str, Any]:
        """
        Parse a variance query and return parameters.
        
        Args:
            query: User query expected to be variance type
            
        Returns:
            Dictionary of variance parameters
        """
        result = self.analyze_query(query)
        if result.query_type == QueryType.VARIANCE:
            return result.parameters
        else:
            # Force interpretation as variance
            return self._extract_parameters_from_pattern(query, QueryType.VARIANCE, "")
    
    def validate_json_structure(self, json_data: Dict[str, Any]) -> bool:
        """
        Validate the structure of JSON parameters.
        
        Args:
            json_data: JSON data to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Check if required fields exist
        if 'query_type' not in json_data:
            return False
        
        if 'parameters' not in json_data:
            return False
        
        # Validate query type
        query_type_str = json_data['query_type']
        if query_type_str not in [q.value for q in QueryType]:
            return False
        
        # Additional validation can be added here
        return True
