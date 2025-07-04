"""
Function Registry for Gemma 3 Function Calling
Defines available functions for VariancePro analyzers

This module provides function definitions that map to existing analyzer capabilities,
enabling Gemma 3 to understand and call appropriate analysis functions.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class FunctionDefinition:
    """Definition of a callable function for Gemma 3"""
    name: str
    description: str
    parameters: Dict[str, Any]
    analyzer_type: str
    confidence_boost: float = 0.1


class FunctionRegistry:
    """
    Registry of available functions for Gemma 3 function calling
    Maps natural language intents to VariancePro analyzer capabilities
    """
    
    def __init__(self):
        """Initialize the function registry with predefined functions"""
        self._functions = {}
        self._build_function_definitions()
    
    def _build_function_definitions(self):
        """Build comprehensive function definitions for all analyzers"""
        
        # Time-based variance analysis functions
        self._functions["analyze_time_variance"] = FunctionDefinition(
            name="analyze_time_variance",
            description="Analyze budget vs actual variance for specific time periods like months, quarters, or fiscal years",
            parameters={
                "type": "object",
                "properties": {
                    "time_period": {
                        "type": "string",
                        "description": "Time period to analyze (e.g., 'July', 'Q2', 'January 2023')"
                    },
                    "metric": {
                        "type": "string", 
                        "description": "Budget metric to analyze (budget_sales, budget_cogs, budget_marketing, etc.)",
                        "enum": ["budget_sales", "budget_cogs", "budget_marketing", "budget_labor", "budget_overhead"]
                    },
                    "dimension": {
                        "type": "string",
                        "description": "Dimension to group by (region, product_line, channel, customer_segment)",
                        "enum": ["region", "product_line", "channel", "customer_segment"]
                    }
                },
                "required": ["time_period", "metric"]
            },
            analyzer_type="variance_analysis",
            confidence_boost=0.15
        )
        
        # Contribution analysis functions
        self._functions["analyze_contribution"] = FunctionDefinition(
            name="analyze_contribution",
            description="Perform Pareto/contribution analysis to identify top contributors (80/20 analysis)",
            parameters={
                "type": "object",
                "properties": {
                    "metric": {
                        "type": "string",
                        "description": "Metric to analyze for contributions",
                        "enum": ["actual_sales", "budget_sales", "sales_variance", "customer_satisfaction"]
                    },
                    "dimension": {
                        "type": "string",
                        "description": "Dimension to analyze contributions by",
                        "enum": ["region", "product_line", "channel", "customer_segment", "sales_rep"]
                    },
                    "top_n": {
                        "type": "integer",
                        "description": "Number of top contributors to identify",
                        "default": 10
                    }
                },
                "required": ["metric", "dimension"]
            },
            analyzer_type="contribution_analysis",
            confidence_boost=0.12
        )
        
        # Financial variance analysis
        self._functions["analyze_financial_variance"] = FunctionDefinition(
            name="analyze_financial_variance",
            description="Analyze financial variances between actual and budget performance",
            parameters={
                "type": "object",
                "properties": {
                    "variance_type": {
                        "type": "string",
                        "description": "Type of variance to analyze",
                        "enum": ["sales_variance", "price_variance", "volume_variance", "cost_variance"]
                    },
                    "filter_condition": {
                        "type": "string",
                        "description": "Filter condition (negative, positive, above_threshold, below_threshold)"
                    },
                    "threshold_value": {
                        "type": "number",
                        "description": "Threshold value for filtering (when using above/below threshold)"
                    },
                    "group_by": {
                        "type": "string",
                        "description": "Dimension to group results by",
                        "enum": ["region", "product_line", "channel", "customer_segment"]
                    }
                },
                "required": ["variance_type"]
            },
            analyzer_type="variance_analysis",
            confidence_boost=0.11
        )
        
        # Top/Bottom N analysis
        self._functions["analyze_top_performers"] = FunctionDefinition(
            name="analyze_top_performers",
            description="Find top N performers by specified metrics",
            parameters={
                "type": "object",
                "properties": {
                    "metric": {
                        "type": "string",
                        "description": "Metric to rank by",
                        "enum": ["actual_sales", "budget_sales", "customer_satisfaction", "discount_pct"]
                    },
                    "dimension": {
                        "type": "string", 
                        "description": "Dimension to rank",
                        "enum": ["region", "product_line", "channel", "customer_segment", "sales_rep"]
                    },
                    "count": {
                        "type": "integer",
                        "description": "Number of top performers to return",
                        "default": 5
                    },
                    "aggregation": {
                        "type": "string",
                        "description": "Aggregation method for the metric",
                        "enum": ["SUM", "AVG", "MAX", "MIN", "COUNT"],
                        "default": "SUM"
                    }
                },
                "required": ["metric", "dimension"]
            },
            analyzer_type="top_n_analysis",
            confidence_boost=0.13
        )
        
        # Complex SQL queries for flexible data analysis
        self._functions["execute_flexible_query"] = FunctionDefinition(
            name="execute_flexible_query",
            description="Execute flexible data queries with custom filtering, grouping, and aggregation",
            parameters={
                "type": "object",
                "properties": {
                    "select_columns": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Columns to select in the query"
                    },
                    "aggregations": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "function": {"type": "string", "enum": ["SUM", "AVG", "COUNT", "MIN", "MAX"]},
                                "column": {"type": "string"}
                            }
                        },
                        "description": "Aggregation functions to apply"
                    },
                    "filters": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "column": {"type": "string"},
                                "operator": {"type": "string", "enum": [">", "<", "=", ">=", "<=", "!="]},
                                "value": {"type": "string"}
                            }
                        },
                        "description": "Filter conditions to apply"
                    },
                    "group_by": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Columns to group by"
                    },
                    "order_by": {
                        "type": "object",
                        "properties": {
                            "column": {"type": "string"},
                            "direction": {"type": "string", "enum": ["ASC", "DESC"]}
                        },
                        "description": "Ordering specification"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return"
                    }
                },
                "required": []
            },
            analyzer_type="sql_query",
            confidence_boost=0.08
        )
        
        # Time series trend analysis
        self._functions["analyze_trends"] = FunctionDefinition(
            name="analyze_trends",
            description="Analyze trends over time for financial metrics",
            parameters={
                "type": "object",
                "properties": {
                    "metric": {
                        "type": "string",
                        "description": "Metric to analyze trends for",
                        "enum": ["actual_sales", "budget_sales", "sales_variance", "customer_satisfaction"]
                    },
                    "time_granularity": {
                        "type": "string",
                        "description": "Time granularity for trend analysis",
                        "enum": ["daily", "weekly", "monthly", "quarterly"],
                        "default": "monthly"
                    },
                    "dimension": {
                        "type": "string",
                        "description": "Optional dimension to segment trends by",
                        "enum": ["region", "product_line", "channel", "customer_segment"]
                    },
                    "trend_type": {
                        "type": "string",
                        "description": "Type of trend analysis",
                        "enum": ["growth", "seasonality", "variance_trends", "ttm_analysis"],
                        "default": "growth"
                    }
                },
                "required": ["metric"]
            },
            analyzer_type="trend_analysis",
            confidence_boost=0.10
        )
    
    def get_function_definitions(self) -> List[Dict[str, Any]]:
        """
        Get all function definitions in Gemma 3 format
        
        Returns:
            List of function definitions formatted for Gemma 3
        """
        return [
            {
                "name": func_def.name,
                "description": func_def.description,
                "parameters": func_def.parameters
            }
            for func_def in self._functions.values()
        ]
    
    def get_function_by_name(self, name: str) -> Optional[FunctionDefinition]:
        """
        Get function definition by name
        
        Args:
            name: Function name
            
        Returns:
            FunctionDefinition if found, None otherwise
        """
        return self._functions.get(name)
    
    def get_functions_for_analyzer_type(self, analyzer_type: str) -> List[FunctionDefinition]:
        """
        Get all functions for a specific analyzer type
        
        Args:
            analyzer_type: Type of analyzer
            
        Returns:
            List of function definitions for the analyzer type
        """
        return [
            func_def for func_def in self._functions.values()
            if func_def.analyzer_type == analyzer_type
        ]
    
    def suggest_functions_for_query(self, query: str) -> List[FunctionDefinition]:
        """
        Suggest appropriate functions based on query content
        
        Args:
            query: Natural language query
            
        Returns:
            List of potentially relevant function definitions
        """
        query_lower = query.lower()
        suggestions = []
        
        # Time-based query detection
        time_keywords = ['january', 'february', 'march', 'april', 'may', 'june',
                        'july', 'august', 'september', 'october', 'november', 'december',
                        'q1', 'q2', 'q3', 'q4', 'quarter', 'month', 'year']
        
        if any(keyword in query_lower for keyword in time_keywords):
            if 'budget' in query_lower:
                suggestions.append(self._functions["analyze_time_variance"])
        
        # Contribution analysis detection
        contribution_keywords = ['contribution', 'pareto', '80/20', 'top contributors']
        if any(keyword in query_lower for keyword in contribution_keywords):
            suggestions.append(self._functions["analyze_contribution"])
        
        # Variance analysis detection
        variance_keywords = ['variance', 'actual vs budget', 'budget vs actual', 'negative variance']
        if any(keyword in query_lower for keyword in variance_keywords):
            suggestions.append(self._functions["analyze_financial_variance"])
        
        # Top N analysis detection
        top_keywords = ['top', 'best', 'highest', 'maximum', 'bottom', 'worst', 'lowest']
        if any(keyword in query_lower for keyword in top_keywords):
            suggestions.append(self._functions["analyze_top_performers"])
        
        # Trend analysis detection
        trend_keywords = ['trend', 'over time', 'growth', 'seasonality', 'ttm']
        if any(keyword in query_lower for keyword in trend_keywords):
            suggestions.append(self._functions["analyze_trends"])
        
        # Default to flexible query for complex queries
        if len(suggestions) == 0 or any(word in query_lower for word in ['show', 'list', 'find', 'count']):
            suggestions.append(self._functions["execute_flexible_query"])
        
        return suggestions
    
    def validate_function_call(self, function_name: str, parameters: Dict[str, Any]) -> tuple[bool, str]:
        """
        Validate a function call against its definition
        
        Args:
            function_name: Name of the function to call
            parameters: Parameters for the function call
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        func_def = self.get_function_by_name(function_name)
        if not func_def:
            return False, f"Unknown function: {function_name}"
        
        # Check required parameters
        required_params = func_def.parameters.get("required", [])
        for param in required_params:
            if param not in parameters:
                return False, f"Missing required parameter: {param}"
        
        # Validate parameter types and enums
        properties = func_def.parameters.get("properties", {})
        for param_name, param_value in parameters.items():
            if param_name not in properties:
                return False, f"Unknown parameter: {param_name}"
            
            param_def = properties[param_name]
            
            # Check enum values
            if "enum" in param_def and param_value not in param_def["enum"]:
                return False, f"Invalid value for {param_name}: {param_value}. Must be one of {param_def['enum']}"
        
        return True, "Valid function call"


# Global registry instance
function_registry = FunctionRegistry()
