"""
NL2SQL Function Caller for VariancePro
Uses Gemma3 function calling for robust SQL generation
"""

import json
import pandas as pd
import requests
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass


@dataclass
class QueryResult:
    """Result of a query execution"""
    success: bool
    data: Optional[pd.DataFrame]
    sql_query: str
    explanation: str
    row_count: int
    error_message: Optional[str] = None


class NL2SQLFunctionCaller:
    """
    Handles natural language to SQL conversion using Gemma3 function calling
    """
    
    def __init__(self, ollama_url: str = "http://localhost:11434", model_name: str = "gemma3:latest"):
        """Initialize the function caller"""
        self.ollama_url = ollama_url
        self.model_name = model_name
        self.current_schema = None
        self.current_data = None
        
        # Define function schema for Gemma3
        self.function_schema = {
            "name": "generate_data_query",
            "description": "Generate a structured query to analyze CSV data based on natural language input",
            "parameters": {
                "type": "object",
                "properties": {
                    "intent": {
                        "type": "string",
                        "enum": ["select", "filter", "aggregate", "sort", "top_n", "bottom_n"],
                        "description": "The main intent of the query"
                    },
                    "columns": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Column names to include in the query"
                    },
                    "conditions": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "column": {"type": "string"},
                                "operator": {"type": "string", "enum": ["=", ">", "<", ">=", "<=", "!=", "LIKE", "BETWEEN", "IN"]},
                                "value": {"type": "string"},
                                "value_type": {"type": "string", "enum": ["string", "number", "date"]}
                            }
                        },
                        "description": "WHERE clause conditions"
                    },
                    "aggregations": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "function": {"type": "string", "enum": ["SUM", "COUNT", "AVG", "MAX", "MIN"]},
                                "column": {"type": "string"}
                            }
                        },
                        "description": "Aggregation functions to apply"
                    },
                    "group_by": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Columns to group by"
                    },
                    "order_by": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "column": {"type": "string"},
                                "direction": {"type": "string", "enum": ["ASC", "DESC"]}
                            }
                        },
                        "description": "Columns to sort by"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of rows to return"
                    }
                },
                "required": ["intent", "columns"]
            }
        }
    
    def set_data_context(self, data: pd.DataFrame, schema_info: Dict) -> None:
        """Set the current data and schema context"""
        self.current_data = data
        self.current_schema = schema_info
    
    def parse_natural_language_query(self, query: str) -> QueryResult:
        """
        Parse natural language query using Gemma3 function calling
        
        Args:
            query: Natural language query string
            
        Returns:
            QueryResult with parsed query and execution results
        """
        if self.current_data is None:
            return QueryResult(
                success=False,
                data=None,
                sql_query="",
                explanation="No data context available",
                row_count=0,
                error_message="Please upload CSV data first"
            )
        
        try:
            # Create context prompt for Gemma3
            context_prompt = self._build_context_prompt(query)
            
            # Call Gemma3 with function calling
            function_call_result = self._call_gemma3_with_functions(context_prompt)
            
            if not function_call_result["success"]:
                return QueryResult(
                    success=False,
                    data=None,
                    sql_query="",
                    explanation="Failed to parse query",
                    row_count=0,
                    error_message=function_call_result["error"]
                )
            
            # Execute the structured query
            query_params = function_call_result["function_args"]
            result = self._execute_structured_query(query_params)
            
            return result
            
        except Exception as e:
            return QueryResult(
                success=False,
                data=None,
                sql_query="",
                explanation="Query parsing failed",
                row_count=0,
                error_message=str(e)
            )
    
    def _build_context_prompt(self, query: str) -> str:
        """Build context prompt with schema information"""
        columns_info = []
        for col, dtype in self.current_schema.get('column_types', {}).items():
            sample_values = self.current_schema.get('sample_data', {}).get(col, [])[:3]
            columns_info.append(f"- {col} ({dtype}): {sample_values}")
        
        return f"""
You are a SQL query generator. Based on the user's natural language query, generate a structured query using the provided function.

DATASET SCHEMA:
{chr(10).join(columns_info)}

TOTAL ROWS: {len(self.current_data):,}

USER QUERY: "{query}"

Please analyze the query and call the generate_data_query function with appropriate parameters.
Focus on understanding the intent and mapping column names correctly.
"""
    
    def _call_gemma3_with_functions(self, prompt: str) -> Dict[str, Any]:
        """Call Gemma3 with function calling support"""
        try:
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "functions": [self.function_schema],
                "function_call": "auto",
                "stream": False
            }
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Check if function was called
                if "function_call" in result:
                    return {
                        "success": True,
                        "function_args": json.loads(result["function_call"]["arguments"]),
                        "function_name": result["function_call"]["name"]
                    }
                else:
                    # Fallback: try to parse response as JSON
                    try:
                        parsed = json.loads(result.get("response", "{}"))
                        return {"success": True, "function_args": parsed, "function_name": "generate_data_query"}
                    except:
                        return {"success": False, "error": "No function call in response"}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _execute_structured_query(self, params: Dict[str, Any]) -> QueryResult:
        """Execute structured query on pandas DataFrame"""
        try:
            df = self.current_data.copy()
            
            # Apply filters (WHERE conditions)
            if "conditions" in params and params["conditions"]:
                df = self._apply_conditions(df, params["conditions"])
            
            # Apply aggregations and grouping
            if "aggregations" in params and params["aggregations"]:
                df = self._apply_aggregations(df, params["aggregations"], params.get("group_by", []))
            else:
                # Select specific columns if specified
                if "columns" in params and params["columns"]:
                    available_cols = [col for col in params["columns"] if col in df.columns]
                    if available_cols:
                        df = df[available_cols]
            
            # Apply sorting
            if "order_by" in params and params["order_by"]:
                df = self._apply_sorting(df, params["order_by"])
            
            # Apply limit
            if "limit" in params and params["limit"]:
                df = df.head(params["limit"])
            
            # Generate SQL explanation
            sql_explanation = self._generate_sql_explanation(params)
            
            return QueryResult(
                success=True,
                data=df,
                sql_query=sql_explanation,
                explanation=f"Executed {params.get('intent', 'query')} operation",
                row_count=len(df)
            )
            
        except Exception as e:
            return QueryResult(
                success=False,
                data=None,
                sql_query="",
                explanation="Query execution failed",
                row_count=0,
                error_message=str(e)
            )
    
    def _apply_conditions(self, df: pd.DataFrame, conditions: List[Dict]) -> pd.DataFrame:
        """Apply WHERE conditions to DataFrame"""
        for condition in conditions:
            col = condition.get("column")
            op = condition.get("operator")
            val = condition.get("value")
            val_type = condition.get("value_type", "string")
            
            if col not in df.columns:
                continue
            
            # Convert value to appropriate type
            if val_type == "number":
                try:
                    val = float(val)
                except:
                    continue
            elif val_type == "date":
                try:
                    val = pd.to_datetime(val)
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                except:
                    continue
            
            # Apply condition
            if op == "=":
                df = df[df[col] == val]
            elif op == ">":
                df = df[df[col] > val]
            elif op == "<":
                df = df[df[col] < val]
            elif op == ">=":
                df = df[df[col] >= val]
            elif op == "<=":
                df = df[df[col] <= val]
            elif op == "!=":
                df = df[df[col] != val]
            elif op == "LIKE":
                df = df[df[col].astype(str).str.contains(str(val), case=False, na=False)]
        
        return df
    
    def _apply_aggregations(self, df: pd.DataFrame, aggregations: List[Dict], group_by: List[str]) -> pd.DataFrame:
        """Apply aggregation functions"""
        if group_by:
            # Group by specified columns
            grouped = df.groupby(group_by)
            
            agg_dict = {}
            for agg in aggregations:
                func = agg.get("function", "COUNT").lower()
                col = agg.get("column")
                
                if col in df.columns:
                    agg_dict[col] = func
            
            if agg_dict:
                result = grouped.agg(agg_dict).reset_index()
                return result
        
        # No grouping - apply aggregations to entire dataset
        result_data = {}
        for col in group_by:
            if col in df.columns:
                result_data[col] = ["Total"]
        
        for agg in aggregations:
            func = agg.get("function", "COUNT").lower()
            col = agg.get("column")
            
            if col in df.columns:
                if func == "sum":
                    result_data[f"{func}_{col}"] = [df[col].sum()]
                elif func == "count":
                    result_data[f"{func}_{col}"] = [df[col].count()]
                elif func == "avg":
                    result_data[f"{func}_{col}"] = [df[col].mean()]
                elif func == "max":
                    result_data[f"{func}_{col}"] = [df[col].max()]
                elif func == "min":
                    result_data[f"{func}_{col}"] = [df[col].min()]
        
        return pd.DataFrame(result_data)
    
    def _apply_sorting(self, df: pd.DataFrame, order_by: List[Dict]) -> pd.DataFrame:
        """Apply sorting to DataFrame"""
        sort_columns = []
        sort_ascending = []
        
        for sort_spec in order_by:
            col = sort_spec.get("column")
            direction = sort_spec.get("direction", "ASC")
            
            if col in df.columns:
                sort_columns.append(col)
                sort_ascending.append(direction.upper() == "ASC")
        
        if sort_columns:
            df = df.sort_values(sort_columns, ascending=sort_ascending)
        
        return df
    
    def _generate_sql_explanation(self, params: Dict[str, Any]) -> str:
        """Generate SQL-like explanation of the query"""
        sql_parts = []
        
        # SELECT clause
        if params.get("aggregations"):
            select_parts = []
            for agg in params["aggregations"]:
                func = agg.get("function", "COUNT")
                col = agg.get("column", "*")
                select_parts.append(f"{func}({col})")
            
            if params.get("group_by"):
                select_parts = params["group_by"] + select_parts
            
            sql_parts.append(f"SELECT {', '.join(select_parts)}")
        else:
            columns = params.get("columns", ["*"])
            sql_parts.append(f"SELECT {', '.join(columns)}")
        
        sql_parts.append("FROM data")
        
        # WHERE clause
        if params.get("conditions"):
            where_parts = []
            for cond in params["conditions"]:
                col = cond.get("column")
                op = cond.get("operator")
                val = cond.get("value")
                where_parts.append(f"{col} {op} '{val}'")
            sql_parts.append(f"WHERE {' AND '.join(where_parts)}")
        
        # GROUP BY clause
        if params.get("group_by"):
            sql_parts.append(f"GROUP BY {', '.join(params['group_by'])}")
        
        # ORDER BY clause
        if params.get("order_by"):
            order_parts = []
            for order in params["order_by"]:
                col = order.get("column")
                direction = order.get("direction", "ASC")
                order_parts.append(f"{col} {direction}")
            sql_parts.append(f"ORDER BY {', '.join(order_parts)}")
        
        # LIMIT clause
        if params.get("limit"):
            sql_parts.append(f"LIMIT {params['limit']}")
        
        return " ".join(sql_parts)
