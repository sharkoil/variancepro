"""
Function Registry for VariancePro Gemma 3 Function Calling
Defines available functions for the LLM to call.
"""

from typing import Dict, List, Any

class FunctionRegistry:
    """Registry of available functions for LLM function calling."""
    
    def __init__(self):
        self.functions = self._define_functions()
    
    def _define_functions(self) -> List[Dict[str, Any]]:
        """Defines all available functions for financial analysis."""
        return [
            {
                "name": "analyze_time_variance",
                "description": "Analyze budget vs actual variance for specific time periods like months, quarters, or years.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "time_period": {
                            "type": "string",
                            "description": "Time period to analyze (e.g., 'July', 'Q1', '2023')"
                        },
                        "metric": {
                            "type": "string", 
                            "description": "Metric to analyze (e.g., 'budget_sales', 'actual_sales', 'variance')"
                        }
                    },
                    "required": ["time_period", "metric"]
                }
            },
            {
                "name": "generate_sql_query",
                "description": "Generate a SQL query for a flexible data question when other functions do not match.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query_intent": {
                            "type": "string",
                            "description": "A natural language description of what the SQL query should accomplish."
                        }
                    },
                    "required": ["query_intent"]
                }
            }
        ]
    
    def get_all_functions(self) -> List[Dict[str, Any]]:
        """Returns all available functions."""
        return self.functions

# Create a global instance for easy access
function_registry = FunctionRegistry()
