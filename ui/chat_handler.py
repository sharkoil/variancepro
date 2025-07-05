"""
Chat Handler for VariancePro
Handles all chat response logic and query processing
"""

import re
import json
from typing import List, Dict, Tuple, Optional, Any
from datetime import datetime

from ai.llm_interpreter import LLMInterpreter
from ai.narrative_generator import NarrativeGenerator
from analyzers.query_router import QueryRouter
from utils.session_manager import SessionManager


class ChatHandler:
    """
    Handles chat interactions, query processing, and AI response generation
    Integrates with session management for timestamped responses
    """
    
    def __init__(self, app_instance):
        """
        Initialize chat handler with reference to main app
        
        Args:
            app_instance: Reference to the main QuantCommanderApp instance
        """
        self.app = app_instance
        self.session_manager = SessionManager()
        
    def chat_response(self, message: str, history: List[Dict]) -> Tuple[List[Dict], str]:
        """
        Enhanced chat response with AI-powered analysis and timestamps
        
        Args:
            message: User's message
            history: Chat history
            
        Returns:
            Tuple of (updated_history, empty_string)
        """
        if not message.strip():
            return history, ""
        
        try:
            # Check if data is loaded
            if self.app.current_data is None:
                response = "⚠️ **No data loaded**. Please upload a CSV file first to start analysis."
                # Add timestamp to response
                timestamped_response = self.session_manager.add_timestamp_to_message(response)
                
                history.append({"role": "user", "content": message})
                history.append({"role": "assistant", "content": timestamped_response})
                return history, ""
            
            # Analyze the user's query to determine intent
            response = self._process_user_query(message.lower().strip())
            
            # Add timestamp to response
            timestamped_response = self.session_manager.add_timestamp_to_message(response)
            
            # Add to history
            history.append({"role": "user", "content": message})
            history.append({"role": "assistant", "content": timestamped_response})
            
            return history, ""
            
        except Exception as e:
            error_response = f"❌ **Error processing request**: {str(e)}"
            timestamped_error = self.session_manager.add_timestamp_to_message(error_response)
            
            history.append({"role": "user", "content": message})
            history.append({"role": "assistant", "content": timestamped_error})
            return history, ""
    
    def _process_user_query(self, query: str) -> str:
        """Process user query using intelligent routing with SQL support"""
        try:
            # First, use our new intelligent query router
            if self.app.current_data is not None:
                route_result = self.app.query_router.route_query(
                    query=query,
                    data=self.app.current_data,
                    column_info=self.app.csv_loader.column_info,
                    column_suggestions=self.app.column_suggestions
                )
                
                print(f"[DEBUG] Query router result: {route_result}")
                
                # Route to appropriate analyzer based on the result
                if route_result.analyzer_type == "sql":
                    return self.app.analysis_handlers._handle_sql_query(query, route_result)
                elif route_result.analyzer_type == "contribution":
                    return self.app.analysis_handlers._perform_contribution_analysis(query)
                elif route_result.analyzer_type == "variance":
                    return self.app.analysis_handlers._perform_variance_analysis(query)
                elif route_result.analyzer_type == "trend":
                    return self.app.analysis_handlers._perform_trend_analysis(query)
                elif route_result.analyzer_type == "data_overview":
                    return self.app.analysis_handlers._generate_data_overview()
                elif route_result.analyzer_type == "general":
                    return self._generate_ai_response(query)
            
            # Use AI for intelligent intent classification if available
            if self.app.llm_interpreter.is_available:
                ai_result = self._classify_user_intent(query)
                if ai_result:
                    return ai_result
            
            # Fallback to keyword-based routing
            return self._fallback_keyword_routing(query)
            
        except Exception as e:
            print(f"[DEBUG] Error in query processing: {str(e)}")
            return f"❌ **Query Processing Error**: {str(e)}"
    
    def _classify_user_intent(self, query: str) -> Optional[str]:
        """Use LLM to classify user intent and route to appropriate analysis"""
        try:
            # Build context about available analysis types based on data
            available_analyses = []
            suggestions = self.app.column_suggestions
            
            if suggestions.get('category_columns') and suggestions.get('value_columns'):
                available_analyses.append("contribution_analysis")
            
            if suggestions.get('budget_vs_actual'):
                available_analyses.append("variance_analysis")
            
            if self.app.csv_loader.column_info.get('date_columns'):
                available_analyses.append("trend_analysis")
            
            # Always available
            available_analyses.extend(["data_overview", "general_question"])
            
            # Create intent classification prompt
            intent_prompt = f"""
You are an AI assistant that classifies user queries about financial data analysis.

AVAILABLE ANALYSIS TYPES:
{', '.join(available_analyses)}, sql_query

USER QUERY: "{query}"

DATASET CONTEXT:
- Rows: {len(self.app.current_data):,}
- Columns: {list(self.app.current_data.columns)}
- Available columns: {dict(self.app.csv_loader.column_info)}

CLASSIFICATION RULES:
1. sql_query: Direct SQL queries (starting with SELECT) or complex data questions requiring custom queries, aggregations, filtering, or calculations not covered by other analysis types
2. contribution_analysis: Questions about top performers, pareto analysis, biggest contributors, 80/20 rule, ranking, market share
3. variance_analysis: Questions about budget vs actual, variances, over/under budget, performance vs target
4. trend_analysis: Questions about trends, time series, growth, patterns over time, seasonal analysis, forecasting
5. top_n_analysis: Questions asking for top N, best N, highest N, largest N, most N (e.g., "top 10 products", "best 5 states")
6. bottom_n_analysis: Questions asking for bottom N, worst N, lowest N, smallest N, least N (e.g., "bottom 5 performers", "worst 3 regions")
7. data_overview: Questions asking for summary, overview, description of the data, capabilities, what can be analyzed
8. general_question: All other questions that need contextual answers about the data

PRIORITIZE sql_query for:
- Complex filtering ("show me products with sales > 1000")
- Custom calculations ("calculate profit margin by product")
- Multiple conditions ("products in Q1 with revenue above average")
- Aggregations not covered by other types ("average sales by region and quarter")

RESPOND WITH ONLY ONE WORD - THE CLASSIFICATION TYPE (e.g., "sql_query" or "contribution_analysis")
"""
            
            # Query the LLM for intent classification
            print(f"[DEBUG] Classifying intent for query: {query}")
            ai_response = self.app.llm_interpreter.query_llm(intent_prompt, {})
            
            if not ai_response.success:
                print(f"[DEBUG] Intent classification failed: {ai_response.error}")
                return None
            
            # Parse the classification result
            classification = ai_response.content.strip().lower()
            print(f"[DEBUG] LLM classified intent as: {classification}")
            
            # Route to appropriate analysis based on classification
            if classification == "sql_query":
                print("[DEBUG] Routing to SQL query")
                return self.app.analysis_handlers._handle_sql_query(query, None)
            
            elif classification == "contribution_analysis":
                if "contribution_analysis" in available_analyses:
                    print("[DEBUG] Routing to contribution analysis")
                    return self.app.analysis_handlers._perform_contribution_analysis(query)
                else:
                    return "⚠️ **Contribution analysis not available** - Missing required category and value columns"
            
            elif classification == "variance_analysis":
                if "variance_analysis" in available_analyses:
                    print("[DEBUG] Routing to variance analysis")
                    return self.app.analysis_handlers._perform_variance_analysis(query)
                else:
                    return "⚠️ **Variance analysis not available** - Missing required budget/actual columns"
            
            elif classification == "trend_analysis":
                if "trend_analysis" in available_analyses:
                    print("[DEBUG] Routing to trend analysis")
                    return self.app.analysis_handlers._perform_trend_analysis(query)
                else:
                    return "⚠️ **Trend analysis not available** - Missing required date column"
            
            elif classification == "top_n_analysis":
                print("[DEBUG] Routing to top N analysis")
                return self.app.analysis_handlers._perform_top_n_analysis(query, is_bottom=False)
            
            elif classification == "bottom_n_analysis":
                print("[DEBUG] Routing to bottom N analysis")
                return self.app.analysis_handlers._perform_top_n_analysis(query, is_bottom=True)
            
            elif classification == "data_overview":
                print("[DEBUG] Routing to data overview")
                return self.app.analysis_handlers._generate_data_overview()
            
            elif classification == "general_question":
                print("[DEBUG] Routing to general AI response")
                return self._generate_ai_response(query)
            
            else:
                print(f"[DEBUG] Unrecognized classification: {classification}, using general response")
                return self._generate_ai_response(query)
        
        except Exception as e:
            print(f"[DEBUG] Error in intent classification: {str(e)}")
            return None  # Fall back to keyword matching
    
    def _generate_ai_response(self, query: str) -> str:
        """Generate AI-powered response to general queries with enhanced context"""
        try:
            if not self.app.llm_interpreter.is_available:
                return (
                    "⚠️ **AI Assistant Unavailable**\n\n"
                    "The AI assistant requires Ollama/Gemma3 to be running. "
                    "You can still upload data and use specific analysis commands like:\n"
                    "• 'analyze contribution'\n"
                    "• 'analyze variance'\n"
                    "• 'analyze trends'\n"
                    "• 'summary'\n\n"
                    "Or try uploading data to see available analysis options."
                )
            
            # Build comprehensive context for AI including data samples
            context = {
                'dataset_info': {
                    'rows': len(self.app.current_data),
                    'columns': len(self.app.current_data.columns),
                    'column_names': list(self.app.current_data.columns),
                    'column_types': dict(self.app.csv_loader.column_info),
                    'data_summary': self.app.data_summary,
                    'available_analyses': self._get_available_analyses()
                },
                'sample_data': {
                    'first_few_rows': self.app.current_data.head(3).to_dict('records'),
                    'data_range': {
                        col: {
                            'min': self.app.current_data[col].min() if self.app.current_data[col].dtype in ['int64', 'float64'] else None,
                            'max': self.app.current_data[col].max() if self.app.current_data[col].dtype in ['int64', 'float64'] else None,
                            'unique_count': self.app.current_data[col].nunique()
                        } for col in self.app.current_data.columns[:5]
                    }
                }
            }
            
            # Enhanced prompt for contextual understanding
            enhanced_prompt = f"""
You are Aria Sterling, a professional financial analyst AI assistant. You have access to a dataset and should provide insightful, actionable responses.

USER QUESTION: "{query}"

DATASET CONTEXT:
- {len(self.app.current_data):,} rows × {len(self.app.current_data.columns)} columns
- Columns: {', '.join(self.app.current_data.columns)}
- Available analyses: {', '.join(self._get_available_analyses())}

RESPONSE GUIDELINES:
1. Provide specific, actionable insights based on the actual data structure
2. Reference specific columns and data patterns when relevant
3. Suggest appropriate analyses if the user's question could be answered with a specific analysis type
4. Be conversational but professional
5. If asking about specific metrics, explain what columns contain that information
6. Always relate your response to the actual dataset structure and content

Provide a helpful, contextual response as Aria Sterling.
"""
            
            # Query the AI with enhanced context
            ai_response = self.app.llm_interpreter.query_llm(enhanced_prompt, context)
            
            if ai_response.success:
                return self.app.narrative_generator.format_for_chat(
                    ai_response.content,
                    "💡 AI Assistant Response"
                )
            else:
                return f"❌ **AI Error**: {ai_response.error}"
        
        except Exception as e:
            return f"❌ **AI Processing Error**: {str(e)}"
    
    def _fallback_keyword_routing(self, query: str) -> str:
        """Fallback keyword-based routing when AI is not available"""
        # Check for specific analysis keywords
        if any(word in query for word in ['contribute', 'pareto', '80/20', 'contributor', 'top performer']):
            return self.app.analysis_handlers._perform_contribution_analysis(query)
        
        elif any(word in query for word in ['variance', 'budget', 'actual', 'vs', 'versus', 'performance']):
            return self.app.analysis_handlers._perform_variance_analysis(query)
        
        elif any(word in query for word in ['trend', 'time', 'growth', 'timescale', 'ttm', 'trailing', 'pattern']):
            return self.app.analysis_handlers._perform_trend_analysis(query)
        
        elif any(word in query for word in ['summary', 'overview', 'describe', 'what', 'capabilities']):
            return self.app.analysis_handlers._generate_data_overview()
        
        elif query.strip().lower().startswith('select') or 'show me' in query or 'find' in query:
            return self.app.analysis_handlers._handle_sql_query(query, None)
        
        else:
            return self._generate_ai_response(query)
    
    def _get_available_analyses(self) -> List[str]:
        """Get list of available analysis types based on current dataset"""
        available = []
        suggestions = self.app.column_suggestions
        
        if suggestions.get('category_columns') and suggestions.get('value_columns'):
            available.append("Contribution Analysis (80/20 Pareto)")
        
        if suggestions.get('budget_vs_actual'):
            available.append("Variance Analysis (Budget vs Actual)")
        
        if self.app.csv_loader.column_info.get('date_columns'):
            available.append("Trend Analysis (Time Series & TTM)")
        
        # Top N / Bottom N analysis (always available if we have categorical and numeric data)
        if suggestions.get('category_columns') and (suggestions.get('value_columns') or self.app.csv_loader.column_info.get('numeric_columns')):
            available.append("Top N / Bottom N Analysis")
        
        # Always available
        available.append("Data Overview & Summary")
        
        return available
