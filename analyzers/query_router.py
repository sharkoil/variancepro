"""
Query Router for Quant Commander
Intelligently routes queries to appropriate analyzers or SQL engine
"""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class RouteResult:
    """Result object for query routing"""
    analyzer_type: str
    confidence: float = 0.0
    explanation: str = ""
    parameters: Dict = None
    
    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}


class QueryRouter:
    """Routes user queries to the most appropriate analysis method"""
    
    def __init__(self, settings: Dict = None):
        self.settings = settings or {}
        self.llm_interpreter = None
        self.available_analyzers = []
        self.schema_info = {}
        
    def set_llm_interpreter(self, llm_interpreter):
        """Set LLM interpreter for intelligent routing"""
        self.llm_interpreter = llm_interpreter
    
    def set_available_analyzers(self, analyzers: List[str]):
        """Set list of available analyzer types"""
        self.available_analyzers = analyzers
    
    def set_schema_context(self, schema_info: Dict):
        """Set schema context for routing decisions"""
        self.schema_info = schema_info
    
    def route_query(self, query: str, data=None, column_info=None, column_suggestions=None) -> RouteResult:
        """
        Route query to appropriate analyzer
        
        Returns:
            RouteResult with analyzer_type and routing details
            
        analyzer_type can be:
        - 'contribution' (contribution analysis)
        - 'variance' (quantitative analysis) 
        - 'trend' (trend analysis)
        - 'top_n' (top N analysis)
        - 'bottom_n' (bottom N analysis)
        - 'sql' (SQL query)
        - 'overview' (data overview)
        - 'general' (general question)
        """
        try:
            print(f"[ROUTER] Routing query: {query}")
            
            # Store context for routing decisions
            self.current_context = {
                'data': data,
                'column_info': column_info or {},
                'column_suggestions': column_suggestions or {}
            }
            
            # First try rule-based routing (fast and reliable)
            analyzer_type, context = self._rule_based_routing(query)
            
            if analyzer_type != 'unknown':
                print(f"[ROUTER] Rule-based routing: {analyzer_type}")
                confidence = context.get('confidence', 'medium')
                confidence_score = {'high': 0.9, 'medium': 0.7, 'low': 0.5}.get(confidence, 0.7)
                
                return RouteResult(
                    analyzer_type=analyzer_type,
                    confidence=confidence_score,
                    explanation=f"Matched rule-based pattern for {analyzer_type}",
                    parameters=context
                )
            
            # Fall back to LLM-based routing if available
            if self.llm_interpreter and self.llm_interpreter.is_available:
                print("[ROUTER] Using LLM-based routing")
                analyzer_type, context = self._llm_based_routing(query)
                return RouteResult(
                    analyzer_type=analyzer_type,
                    confidence=context.get('confidence', 0.8),
                    explanation="LLM-based routing decision",
                    parameters=context
                )
            
            # Default fallback
            print("[ROUTER] Using default routing")
            analyzer_type, context = self._default_routing(query)
            return RouteResult(
                analyzer_type=analyzer_type,
                confidence=0.5,
                explanation="Default fallback routing",
                parameters=context
            )
            
        except Exception as e:
            print(f"[ROUTER ERROR] Routing failed: {str(e)}")
            return RouteResult(
                analyzer_type='general',
                confidence=0.1,
                explanation=f"Error in routing: {str(e)}",
                parameters={'error': str(e)}
            )
    
    def _rule_based_routing(self, query: str) -> Tuple[str, Dict]:
        """Fast rule-based routing using keywords and patterns"""
        query_lower = query.lower().strip()
        
        # High-confidence patterns for existing analyzers
        
        # Contribution Analysis patterns
        contribution_patterns = [
            r'\b(?:contribution|pareto|80/?20)\b',
            r'\b(?:top contributors?|biggest contributors?)\b',
            r'\b(?:analyze contribution|contribution analysis)\b'
        ]
        
        if any(re.search(pattern, query_lower) for pattern in contribution_patterns):
            return 'contribution', {'confidence': 'high', 'method': 'rule'}
        
        # Variance Analysis patterns
        variance_patterns = [
            r'\b(?:variance|budget vs actual|actual vs budget)\b',
            r'\b(?:analyze variance|quantitative analysis)\b',
            r'\b(?:over budget|under budget|vs budget)\b'
        ]
        
        if any(re.search(pattern, query_lower) for pattern in variance_patterns):
            return 'variance', {'confidence': 'high', 'method': 'rule'}
        
        # Trend Analysis patterns
        trend_patterns = [
            r'\b(?:trend|trends|trending|timescale|time series)\b',
            r'\b(?:analyze trend|trend analysis)\b',
            r'\b(?:ttm|trailing|twelve months?)\b',
            r'\b(?:over time|time scale|all periods)\b'
        ]
        
        if any(re.search(pattern, query_lower) for pattern in trend_patterns):
            return 'trend', {'confidence': 'high', 'method': 'rule'}
        
        # Top N Analysis patterns
        top_n_patterns = [
            r'\b(?:top|best|highest|largest|most)\s+\d+\b',
            r'\b(?:top|best|highest|largest|most)\b.*\b(?:performers?|products?|customers?|states?|regions?)\b'
        ]
        
        if any(re.search(pattern, query_lower) for pattern in top_n_patterns):
            return 'top_n', {'confidence': 'high', 'method': 'rule'}
        
        # Bottom N Analysis patterns
        bottom_n_patterns = [
            r'\b(?:bottom|worst|lowest|smallest|least)\s+\d+\b',
            r'\b(?:bottom|worst|lowest|smallest|least)\b.*\b(?:performers?|products?|customers?|states?|regions?)\b'
        ]
        
        if any(re.search(pattern, query_lower) for pattern in bottom_n_patterns):
            return 'bottom_n', {'confidence': 'high', 'method': 'rule'}
        
        # Data Overview patterns
        overview_patterns = [
            r'\b(?:summary|overview|describe|what.*data)\b',
            r'\b(?:show.*data|data.*summary)\b'
        ]
        
        if any(re.search(pattern, query_lower) for pattern in overview_patterns):
            return 'overview', {'confidence': 'high', 'method': 'rule'}
        
        # SQL Query patterns (flexible data queries)
        sql_patterns = [
            r'\bselect\s+',  # Direct SQL
            r'\b(?:show|give|list|find)\s+(?:me\s+)?(?:all\s+)?.*\b(?:where|with|having)\b',
            r'\b(?:how many|count of|total|sum of|average)\b',
            r'\b(?:filter|select)\b',
            r'\b(?:group by|by)\b.*\b(?:product|customer|region|state|category)\b',
            r'\b(?:products?|customers?|regions?|states?)\s+(?:where|with|having)\b'
        ]
        
        if any(re.search(pattern, query_lower) for pattern in sql_patterns):
            # Check if it's not already caught by specialized analyzers
            if not any(word in query_lower for word in ['contribution', 'variance', 'trend', 'pareto']):
                return 'sql', {'confidence': 'medium', 'method': 'rule'}
        
        return 'unknown', {'confidence': 'none', 'method': 'rule'}
    
    def _llm_based_routing(self, query: str) -> Tuple[str, Dict]:
        """Use LLM for intelligent query routing with function calling"""
        try:
            available_types = [
                'contribution_analysis',
                'variance_analysis', 
                'trend_analysis',
                'top_n_analysis',
                'bottom_n_analysis',
                'sql_query',
                'data_overview',
                'general_question'
            ]
            
            # Enhanced prompt for Gemma3 with clear instructions
            prompt = f"""
You are a query routing specialist for a financial analysis system. Classify the user's query into the most appropriate analysis type.

AVAILABLE ANALYSIS TYPES:
1. contribution_analysis - 80/20 Pareto analysis, top contributors, market share analysis
2. variance_analysis - Budget vs actual comparison, performance gaps
3. trend_analysis - Time series analysis, growth trends, seasonal patterns, TTM analysis
4. top_n_analysis - Top N rankings (top 5, top 10, best performers)
5. bottom_n_analysis - Bottom N rankings (worst performers, lowest values)
6. sql_query - Flexible data queries (show all, count, filter, custom aggregations)
7. data_overview - Dataset summary, capabilities, what can be analyzed
8. general_question - General conversation, help, or unclear requests

USER QUERY: "{query}"

DATASET CONTEXT:
- Available columns: {list(self.schema_info.get('columns', []))}
- Numeric columns: {self.schema_info.get('numeric_columns', [])}
- Categorical columns: {self.schema_info.get('categorical_columns', [])}

CLASSIFICATION RULES:
- If query asks for "contribution" or "pareto" → contribution_analysis
- If query mentions "budget vs actual" or "variance" → variance_analysis  
- If query asks for "trends" or "over time" → trend_analysis
- If query asks for "top N" or "best" → top_n_analysis
- If query asks for "bottom N" or "worst" → bottom_n_analysis
- If query is a flexible data question → sql_query
- If query asks for data summary → data_overview
- Otherwise → general_question

RESPOND WITH ONLY THE ANALYSIS TYPE (one word from the list above):
"""
            
            response = self.llm_interpreter.query_llm(prompt, {})
            
            if response.success:
                classification = response.content.strip().lower()
                print(f"[ROUTER] LLM classified as: {classification}")
                
                # Validate classification
                if classification in available_types:
                    return classification, {'confidence': 'high', 'method': 'llm'}
                else:
                    print(f"[ROUTER] Invalid LLM classification: {classification}")
                    return self._default_routing(query)
            else:
                print(f"[ROUTER] LLM routing failed: {response.error}")
                return self._default_routing(query)
                
        except Exception as e:
            print(f"[ROUTER] LLM routing error: {str(e)}")
            return self._default_routing(query)
    
    def _default_routing(self, query: str) -> Tuple[str, Dict]:
        """Default routing when other methods fail"""
        query_lower = query.lower().strip()
        
        # Simple keyword fallbacks
        if 'top' in query_lower or 'best' in query_lower:
            return 'top_n', {'confidence': 'low', 'method': 'default'}
        elif 'summary' in query_lower or 'overview' in query_lower:
            return 'overview', {'confidence': 'low', 'method': 'default'}
        elif any(word in query_lower for word in ['show', 'list', 'find', 'count', 'total']):
            return 'sql', {'confidence': 'low', 'method': 'default'}
        else:
            return 'general', {'confidence': 'low', 'method': 'default'}
    
    def get_routing_explanation(self, query: str, analyzer_type: str, context: Dict) -> str:
        """Get explanation of why query was routed to specific analyzer"""
        confidence = context.get('confidence', 'unknown')
        method = context.get('method', 'unknown')
        
        explanations = {
            'contribution_analysis': "Detected request for 80/20 Pareto analysis or contribution analysis",
            'variance_analysis': "Detected request for budget vs actual quantitative analysis",
            'trend_analysis': "Detected request for time-series or trend analysis",
            'top_n_analysis': "Detected request for top N ranking analysis",
            'bottom_n_analysis': "Detected request for bottom N ranking analysis",
            'sql_query': "Detected flexible data query that can be handled with SQL",
            'data_overview': "Detected request for data summary or overview",
            'general_question': "General question or unclear request"
        }
        
        explanation = explanations.get(analyzer_type, f"Routed to {analyzer_type}")
        return f"{explanation} (confidence: {confidence}, method: {method})"
