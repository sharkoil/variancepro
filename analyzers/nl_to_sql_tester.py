"""
NL-to-SQL Testing Framework with Strategy Comparison
Allows safe testing of different NL-to-SQL approaches without breaking the app
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import time
import pandas as pd


class NLToSQLStrategy(Enum):
    """Available NL-to-SQL translation strategies"""
    CURRENT = "current"
    STRATEGY_1_LLM_ENHANCED = "strategy_1_llm"
    STRATEGY_2_SEMANTIC_PARSING = "strategy_2_semantic"


@dataclass
class TranslationComparison:
    """Comparison result between different strategies"""
    query: str
    current_sql: str
    current_explanation: str
    strategy_1_sql: str
    strategy_1_explanation: str
    strategy_2_sql: str
    strategy_2_explanation: str
    current_confidence: float
    strategy_1_confidence: float
    strategy_2_confidence: float
    execution_times: Dict[str, float]
    quality_scores: Dict[str, float]
    recommendations: List[str]


class NLToSQLTester:
    """
    Safe testing framework for NL-to-SQL strategies
    Allows evaluation without affecting production queries
    """
    
    def __init__(self, data_df: pd.DataFrame, llm_interpreter=None):
        """
        Initialize tester with data context
        
        Args:
            data_df: DataFrame to test queries against
            llm_interpreter: Optional LLM for strategy 1
        """
        self.data_df = data_df
        self.llm_interpreter = llm_interpreter
        self.schema_info = self._extract_schema_info()
        self.table_name = "test_data"
        
        # Initialize strategies
        self.current_translator = None
        self.strategy_1_translator = None
        self.strategy_2_translator = None
        
        # Test queries for evaluation
        self.test_queries = [
            "Show me sales where region is North",
            "Find records where actual sales > 1000",
            "Get data for Q1 2023",
            "Show top 5 regions by revenue",
            "List products with negative variance",
            "Find sales above budget in December",
            "Show me all transactions greater than 500",
            "Get regions where sales exceed 10000",
            "Find products with variance less than -5%",
            "Show data where date is between Jan and Mar"
        ]
    
    def _extract_schema_info(self) -> Dict[str, Any]:
        """Extract schema information from DataFrame"""
        schema_info = {
            'columns': list(self.data_df.columns),
            'column_types': {col: str(dtype) for col, dtype in self.data_df.dtypes.items()},
            'sample_values': {}
        }
        
        # Get sample values for each column
        for col in self.data_df.columns:
            unique_vals = self.data_df[col].unique()
            schema_info['sample_values'][col] = list(unique_vals[:5])  # First 5 unique values
            
        return schema_info
    
    def initialize_strategies(self, current_translator, strategy_1_translator, strategy_2_translator):
        """
        Initialize all translation strategies
        
        Args:
            current_translator: Existing enhanced translator
            strategy_1_translator: LLM-enhanced translator
            strategy_2_translator: Semantic parsing translator
        """
        self.current_translator = current_translator
        self.strategy_1_translator = strategy_1_translator
        self.strategy_2_translator = strategy_2_translator
        
        # Set schema context for all translators
        for translator in [current_translator, strategy_1_translator, strategy_2_translator]:
            if hasattr(translator, 'set_schema_context'):
                translator.set_schema_context(self.schema_info, self.table_name)
    
    def test_single_query(self, query: str) -> TranslationComparison:
        """
        Test a single query against all strategies
        
        Args:
            query: Natural language query to test
            
        Returns:
            TranslationComparison with results from all strategies
        """
        print(f"Testing query: '{query}'")
        
        # Test current implementation
        start_time = time.time()
        current_result = self.current_translator.translate_to_sql(query)
        current_time = time.time() - start_time
        
        # Test strategy 1 (LLM-enhanced)
        start_time = time.time()
        strategy_1_result = self.strategy_1_translator.translate_to_sql(query)
        strategy_1_time = time.time() - start_time
        
        # Test strategy 2 (Semantic parsing)
        start_time = time.time()
        strategy_2_result = self.strategy_2_translator.translate_to_sql(query)
        strategy_2_time = time.time() - start_time
        
        # Calculate quality scores
        quality_scores = self._calculate_quality_scores(
            query, current_result, strategy_1_result, strategy_2_result
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            current_result, strategy_1_result, strategy_2_result, quality_scores
        )
        
        return TranslationComparison(
            query=query,
            current_sql=current_result.sql_query if current_result.success else "FAILED",
            current_explanation=current_result.explanation if current_result.success else current_result.error_message,
            strategy_1_sql=strategy_1_result.sql_query if strategy_1_result.success else "FAILED",
            strategy_1_explanation=strategy_1_result.explanation if strategy_1_result.success else strategy_1_result.error_message,
            strategy_2_sql=strategy_2_result.sql_query if strategy_2_result.success else "FAILED",
            strategy_2_explanation=strategy_2_result.explanation if strategy_2_result.success else strategy_2_result.error_message,
            current_confidence=current_result.confidence if current_result.success else 0.0,
            strategy_1_confidence=strategy_1_result.confidence if strategy_1_result.success else 0.0,
            strategy_2_confidence=strategy_2_result.confidence if strategy_2_result.success else 0.0,
            execution_times={
                'current': current_time,
                'strategy_1': strategy_1_time,
                'strategy_2': strategy_2_time
            },
            quality_scores=quality_scores,
            recommendations=recommendations
        )
    
    def _calculate_quality_scores(self, query: str, current_result, strategy_1_result, strategy_2_result) -> Dict[str, float]:
        """
        Calculate quality scores for each strategy based on multiple factors
        
        Returns:
            Dictionary with quality scores for each strategy
        """
        scores = {'current': 0.0, 'strategy_1': 0.0, 'strategy_2': 0.0}
        
        results = {
            'current': current_result,
            'strategy_1': strategy_1_result,
            'strategy_2': strategy_2_result
        }
        
        for strategy, result in results.items():
            score = 0.0
            
            if result.success:
                # Base success score
                score += 30.0
                
                # SQL quality indicators
                sql = result.sql_query.upper()
                
                # Check for WHERE clause (key problem with current implementation)
                if 'WHERE' in sql and 'WHERE ' in sql:
                    score += 25.0
                
                # Check for appropriate SELECT (not just SELECT *)
                if 'SELECT *' not in sql:
                    score += 15.0
                
                # Check for aggregations when appropriate
                query_lower = query.lower()
                if any(word in query_lower for word in ['top', 'sum', 'count', 'average', 'max', 'min']):
                    if any(func in sql for func in ['SUM(', 'COUNT(', 'AVG(', 'MAX(', 'MIN(']):
                        score += 15.0
                
                # Check for LIMIT when appropriate
                if 'top' in query_lower or 'first' in query_lower:
                    if 'LIMIT' in sql:
                        score += 10.0
                
                # Confidence bonus
                score += result.confidence * 5.0
                
            scores[strategy] = min(score, 100.0)  # Cap at 100
        
        return scores
    
    def _generate_recommendations(self, current_result, strategy_1_result, strategy_2_result, quality_scores) -> List[str]:
        """Generate recommendations based on comparison results"""
        recommendations = []
        
        # Identify best performing strategy
        best_strategy = max(quality_scores.items(), key=lambda x: x[1])
        
        if best_strategy[0] != 'current':
            recommendations.append(f"Consider switching to {best_strategy[0]} (score: {best_strategy[1]:.1f} vs current: {quality_scores['current']:.1f})")
        
        # Check for specific issues
        if current_result.success and 'SELECT *' in current_result.sql_query:
            recommendations.append("Current implementation uses SELECT * - consider more specific column selection")
        
        if current_result.success and 'WHERE' not in current_result.sql_query.upper():
            recommendations.append("Current implementation missing WHERE clause - likely returning all rows")
        
        if strategy_1_result.confidence > current_result.confidence + 0.2:
            recommendations.append("Strategy 1 (LLM-enhanced) shows significantly higher confidence")
        
        if strategy_2_result.confidence > current_result.confidence + 0.2:
            recommendations.append("Strategy 2 (Semantic parsing) shows significantly higher confidence")
        
        return recommendations
    
    def run_comprehensive_test(self) -> Dict[str, Any]:
        """
        Run comprehensive test across all test queries
        
        Returns:
            Comprehensive test results with summary statistics
        """
        all_results = []
        strategy_wins = {'current': 0, 'strategy_1': 0, 'strategy_2': 0}
        
        print("Running comprehensive NL-to-SQL strategy comparison...")
        print("=" * 60)
        
        for query in self.test_queries:
            result = self.test_single_query(query)
            all_results.append(result)
            
            # Determine winner
            best_strategy = max(result.quality_scores.items(), key=lambda x: x[1])
            strategy_wins[best_strategy[0]] += 1
            
            # Print summary for this query
            print(f"\nQuery: {query}")
            print(f"Scores - Current: {result.quality_scores['current']:.1f}, "
                  f"Strategy 1: {result.quality_scores['strategy_1']:.1f}, "
                  f"Strategy 2: {result.quality_scores['strategy_2']:.1f}")
            if result.recommendations:
                print(f"Recommendations: {'; '.join(result.recommendations)}")
        
        # Calculate summary statistics
        avg_scores = {
            'current': sum(r.quality_scores['current'] for r in all_results) / len(all_results),
            'strategy_1': sum(r.quality_scores['strategy_1'] for r in all_results) / len(all_results),
            'strategy_2': sum(r.quality_scores['strategy_2'] for r in all_results) / len(all_results)
        }
        
        avg_times = {
            'current': sum(r.execution_times['current'] for r in all_results) / len(all_results),
            'strategy_1': sum(r.execution_times['strategy_1'] for r in all_results) / len(all_results),
            'strategy_2': sum(r.execution_times['strategy_2'] for r in all_results) / len(all_results)
        }
        
        print("\n" + "=" * 60)
        print("COMPREHENSIVE TEST RESULTS")
        print("=" * 60)
        print(f"Strategy Wins: Current={strategy_wins['current']}, Strategy 1={strategy_wins['strategy_1']}, Strategy 2={strategy_wins['strategy_2']}")
        print(f"Average Scores: Current={avg_scores['current']:.1f}, Strategy 1={avg_scores['strategy_1']:.1f}, Strategy 2={avg_scores['strategy_2']:.1f}")
        print(f"Average Times: Current={avg_times['current']:.3f}s, Strategy 1={avg_times['strategy_1']:.3f}s, Strategy 2={avg_times['strategy_2']:.3f}s")
        
        return {
            'all_results': all_results,
            'strategy_wins': strategy_wins,
            'average_scores': avg_scores,
            'average_times': avg_times,
            'total_queries': len(all_results)
        }
    
    def get_test_queries(self) -> List[str]:
        """Get list of test queries for manual testing"""
        return self.test_queries.copy()
    
    def add_custom_test_query(self, query: str):
        """Add a custom test query"""
        if query not in self.test_queries:
            self.test_queries.append(query)
