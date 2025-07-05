"""
Analysis Handlers for VariancePro
Contains all analysis method implementations
"""

import re
import json
from typing import List, Dict, Optional, Any

from analyzers.base_analyzer import AnalysisFormatter


class AnalysisHandlers:
    """
    Handles all analysis operations including contribution, variance, trend, and SQL queries
    Modular design allows for easy extension and maintenance
    """
    
    def __init__(self, app_instance):
        """
        Initialize analysis handlers with reference to main app
        
        Args:
            app_instance: Reference to the main QuantCommanderApp instance
        """
        self.app = app_instance
    
    def _perform_contribution_analysis(self, query: str) -> str:
        """Perform contribution analysis"""
        try:
            # Get suggested columns for analysis
            suggestions = self.app.column_suggestions
            category_cols = suggestions.get('category_columns', [])
            value_cols = suggestions.get('value_columns', [])
            
            if not category_cols or not value_cols:
                return "⚠️ **Contribution analysis requires both category and value columns**. Upload data with products/categories and sales/revenue columns."
            
            # Use first suggested columns as defaults
            category_col = category_cols[0]
            value_col = value_cols[0]
            
            # Analyze contribution using the contributor analyzer
            results = self.app.contributor_analyzer.analyze(
                data=self.app.current_data,
                category_column=category_col,
                value_column=value_col
            )
            
            # Generate AI narrative if available
            if self.app.llm_interpreter.is_available:
                context = {
                    'analysis_type': 'contribution',
                    'category_column': category_col,
                    'value_column': value_col,
                    'results_summary': results
                }
                ai_response = self.app.llm_interpreter.query_llm(
                    "Provide insights on this contribution analysis", context
                )
                
                if ai_response.success:
                    ai_insights = self.app.narrative_generator.format_for_chat(
                        ai_response.content, 
                        "💡 AI Insights"
                    )
                    return f"{self.app.contributor_analyzer.format_for_chat()}\n\n{ai_insights}"
            
            # Return formatted results
            return self.app.contributor_analyzer.format_for_chat()
            
        except Exception as e:
            return f"❌ **Contribution Analysis Error**: {str(e)}"
    
    def _perform_variance_analysis(self, query: str) -> str:
        """Perform variance analysis"""
        try:
            # Get suggested columns for variance analysis
            suggestions = self.app.column_suggestions
            budget_actual_pairs = suggestions.get('budget_vs_actual', [])
            
            if not budget_actual_pairs:
                return "⚠️ **Variance analysis requires Budget and Actual columns**. Upload data with budget/plan and actual/result columns."
            
            # Use first suggested pair
            budget_col, actual_col = budget_actual_pairs[0]
            category_cols = suggestions.get('category_columns', [])
            category_col = category_cols[0] if category_cols else None
            
            # Perform variance analysis using the financial analyzer
            results = self.app.financial_analyzer.analyze(
                data=self.app.current_data,
                budget_col=budget_col,
                actual_col=actual_col,
                category_col=category_col,
                analysis_type="variance"
            )
            
            # Generate AI narrative if available
            if self.app.llm_interpreter.is_available:
                context = {
                    'analysis_type': 'variance',
                    'budget_column': budget_col,
                    'actual_column': actual_col,
                    'category_column': category_col,
                    'results_summary': results
                }
                ai_response = self.app.llm_interpreter.query_llm(
                    "Provide insights on this variance analysis", context
                )
                
                if ai_response.success:
                    ai_insights = self.app.narrative_generator.format_for_chat(
                        ai_response.content, 
                        "💡 AI Insights"
                    )
                    return f"{self.app.financial_analyzer.format_for_chat()}\n\n{ai_insights}"
            
            # Return formatted results
            return self.app.financial_analyzer.format_for_chat()
            
        except Exception as e:
            return f"❌ **Variance Analysis Error**: {str(e)}"
    
    def _perform_trend_analysis(self, query: str) -> str:
        """Perform trend analysis"""
        try:
            # Get suggested columns for trend analysis
            date_cols = self.app.csv_loader.column_info.get('date_columns', [])
            value_cols = self.app.column_suggestions.get('value_columns', [])
            category_cols = self.app.column_suggestions.get('category_columns', [])
            
            if not date_cols:
                return "⚠️ **Trend analysis requires a date column**. Upload data with Date, Month, Quarter, or Year columns."
            
            if not value_cols:
                return "⚠️ **Trend analysis requires numeric value columns**. Upload data with sales, revenue, or other numeric metrics."
            
            # Use first suggested columns
            date_col = date_cols[0]
            value_col = value_cols[0]
            category_col = category_cols[0] if category_cols else None
            
            # Determine analysis type based on query
            if any(word in query for word in ['ttm', 'trailing', 'twelve']):
                analysis_type = "ttm"
            else:
                analysis_type = "timescale"
            
            # Perform analysis with FinancialAnalyzer
            results = self.app.financial_analyzer.analyze(
                data=self.app.current_data,
                date_col=date_col,
                value_col=value_col,
                category_col=category_col,
                analysis_type=analysis_type
            )
            
            # Generate AI narrative if available
            if self.app.llm_interpreter.is_available:
                context = {
                    'analysis_type': 'trend',
                    'date_column': date_col,
                    'value_column': value_col,
                    'category_column': category_col,
                    'results_summary': results
                }
                ai_response = self.app.llm_interpreter.query_llm(
                    "Provide insights on this trend analysis", context
                )
                
                if ai_response.success:
                    ai_insights = self.app.narrative_generator.format_for_chat(
                        ai_response.content, 
                        "💡 AI Insights"
                    )
                    return f"{self.app.financial_analyzer.format_for_chat()}\n\n{ai_insights}"
            
            # Return formatted results
            return self.app.financial_analyzer.format_for_chat()
            
        except Exception as e:
            return f"❌ **Trend Analysis Error**: {str(e)}"
    
    def _generate_data_overview(self) -> str:
        """Generate comprehensive data overview"""
        try:
            overview_parts = [
                "📊 **COMPREHENSIVE DATA OVERVIEW**",
                "",
                self.app.data_summary,
                "",
                "🎯 **Analysis Capabilities Detected:**"
            ]
            
            # Add capabilities based on available columns
            suggestions = self.app.column_suggestions
            
            if suggestions.get('category_columns') and suggestions.get('value_columns'):
                overview_parts.append("✅ **Contribution Analysis** (80/20 Pareto) - Available")
            
            if suggestions.get('budget_vs_actual'):
                overview_parts.append("✅ **Variance Analysis** (Budget vs Actual) - Available")
            
            if self.app.csv_loader.column_info.get('date_columns'):
                overview_parts.append("✅ **Trend Analysis** (Time Series & TTM) - Available")
            
            # Add data quality information
            quality = self.app.csv_loader.data_quality
            if quality.get('missing_data'):
                overview_parts.append("")
                overview_parts.append("⚠️ **Data Quality Notes:**")
                overview_parts.append(f"• Missing data detected: {quality['missing_data']}")
            
            # Generate AI summary if available
            if self.app.llm_interpreter.is_available:
                context = {
                    'data_summary': self.app.data_summary,
                    'columns': list(self.app.current_data.columns),
                    'shape': self.app.current_data.shape,
                    'column_suggestions': suggestions
                }
                ai_response = self.app.llm_interpreter.query_llm(
                    "Provide a strategic overview of this dataset and its analysis potential", context
                )
                
                if ai_response.success:
                    overview_parts.append("")
                    overview_parts.append("🧠 **AI Strategic Analysis:**")
                    overview_parts.append(ai_response.content)
            
            return "\n".join(overview_parts)
            
        except Exception as e:
            return f"❌ **Overview Generation Error**: {str(e)}"
    
    def _perform_top_n_analysis(self, query: str, is_bottom: bool = False) -> str:
        """Perform Top N or Bottom N analysis using LLM to understand parameters"""
        try:
            # Use LLM to extract analysis parameters from the query
            if not self.app.llm_interpreter.is_available:
                return (
                    "⚠️ **Top/Bottom N Analysis Requires AI**\n\n"
                    "This analysis type requires the AI assistant to understand your query parameters. "
                    "Please ensure Ollama/Gemma3 is running.\n\n"
                    "Alternative: Use specific commands like 'analyze contribution' for similar insights."
                )
            
            # Get available columns for analysis
            suggestions = self.app.column_suggestions
            category_cols = suggestions.get('category_columns', [])
            value_cols = suggestions.get('value_columns', [])
            numeric_cols = self.app.csv_loader.column_info.get('numeric_columns', [])
            
            # Create parameter extraction prompt
            direction = "bottom" if is_bottom else "top"
            param_prompt = f"""
You are analyzing a user query to extract parameters for {direction} N analysis on financial data.

USER QUERY: "{query}"

AVAILABLE COLUMNS IN DATASET:
- Category/Grouping columns: {category_cols}
- Value/Numeric columns: {value_cols}
- All numeric columns: {numeric_cols}
- All available columns: {list(self.app.current_data.columns)}

TASK: Extract these 3 parameters from the user query:

1. N (number): How many items to show (look for numbers like "5", "10", "top 3", etc. Default: 10)
2. GROUP_BY_COLUMN: What to group/rank by (Product, State, Category, etc. - must be from available columns)
3. VALUE_COLUMN: What metric to measure/sort by (Budget, Actual, Sales, Revenue, etc. - must be numeric)

EXTRACTION RULES:
- If user doesn't specify N, use 10
- If user doesn't specify group_by_column, use the first category column: {category_cols[0] if category_cols else 'Product'}
- If user doesn't specify value_column, use the first value column: {value_cols[0] if value_cols else numeric_cols[0] if numeric_cols else 'Actual'}
- Column names must EXACTLY match available columns (case sensitive)

EXAMPLES:
- "top 5 products by sales" → n=5, group_by_column="Product", value_column="Sales"  
- "bottom 10 states" → n=10, group_by_column="State", value_column=<best numeric column>
- "worst performers" → n=10, group_by_column=<best category column>, value_column=<best numeric column>

RESPOND ONLY WITH VALID JSON (no explanation):
{{
    "n": <number>,
    "group_by_column": "<exact_column_name>",
    "value_column": "<exact_column_name>"
}}
"""
            
            # Extract parameters using LLM
            print(f"[DEBUG] Extracting {direction} N parameters from query: '{query}'")
            param_response = self.app.llm_interpreter.query_llm(param_prompt, {})
            
            if not param_response.success:
                return f"❌ **Parameter Extraction Error**: {param_response.error}"
            
            # Parse the JSON response with better error handling
            try:
                print(f"[DEBUG] Raw LLM response: {param_response.content}")
                
                # Clean up the response (remove any extra text)
                response_text = param_response.content.strip()
                
                # Find JSON content (look for {...})
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}') + 1
                
                if start_idx == -1 or end_idx == 0:
                    raise ValueError("No JSON found in response")
                
                json_text = response_text[start_idx:end_idx]
                print(f"[DEBUG] Extracted JSON: {json_text}")
                
                params = json.loads(json_text)
                
                n = params.get('n', 10)
                group_by_col = params.get('group_by_column')
                value_col = params.get('value_column')
                
                print(f"[DEBUG] Parsed parameters - N: {n}, Group: {group_by_col}, Value: {value_col}")
                
                # Validate and fix parameters
                if not isinstance(n, int) or n <= 0:
                    n = 10
                
                # Validate group_by_column exists
                if not group_by_col or group_by_col not in self.app.current_data.columns:
                    if category_cols:
                        group_by_col = category_cols[0]
                        print(f"[DEBUG] Using fallback group column: {group_by_col}")
                    else:
                        return "⚠️ **No suitable grouping column found in data**"
                
                # Validate value_column exists and is numeric
                if not value_col or value_col not in self.app.current_data.columns:
                    if value_cols:
                        value_col = value_cols[0]
                        print(f"[DEBUG] Using fallback value column: {value_col}")
                    elif numeric_cols:
                        value_col = numeric_cols[0]
                        print(f"[DEBUG] Using fallback numeric column: {value_col}")
                    else:
                        return "⚠️ **No suitable numeric column found in data**"
                
                print(f"[DEBUG] Final parameters - N: {n}, Group: {group_by_col}, Value: {value_col}")
                
            except (json.JSONDecodeError, ValueError, KeyError) as e:
                print(f"[DEBUG] JSON parsing failed: {e}")
                print(f"[DEBUG] Raw response was: {param_response.content}")
                
                # Fallback to intelligent defaults
                n = 10
                
                # Extract number from query if possible
                numbers = re.findall(r'\b(\d+)\b', query)
                if numbers:
                    try:
                        n = int(numbers[0])
                        if n > 100:  # Reasonable limit
                            n = 10
                    except ValueError:
                        n = 10
                
                # Use first available columns as fallback
                group_by_col = category_cols[0] if category_cols else None
                value_col = value_cols[0] if value_cols else (numeric_cols[0] if numeric_cols else None)
                
                if not group_by_col or not value_col:
                    return "⚠️ **Cannot determine analysis parameters** - Please specify columns explicitly"
                
                print(f"[DEBUG] Using fallback parameters - N: {n}, Group: {group_by_col}, Value: {value_col}")
            
            # Validate columns exist
            if not group_by_col or group_by_col not in self.app.current_data.columns:
                return (
                    f"⚠️ **Invalid Group Column**: '{group_by_col}' not found.\n\n"
                    f"Available columns: {', '.join(self.app.current_data.columns)}"
                )
            
            if not value_col or value_col not in self.app.current_data.columns:
                return (
                    f"⚠️ **Invalid Value Column**: '{value_col}' not found.\n\n"
                    f"Available numeric columns: {', '.join(numeric_cols)}"
                )
            
            # Perform the Top/Bottom N analysis
            try:
                # Group by the specified column and aggregate the value column
                if self.app.current_data[value_col].dtype not in ['int64', 'float64']:
                    return f"⚠️ **Non-numeric Value Column**: '{value_col}' must be numeric for ranking analysis."
                
                # Aggregate data
                grouped = self.app.current_data.groupby(group_by_col)[value_col].agg(['sum', 'mean', 'count']).reset_index()
                grouped.columns = [group_by_col, f'{value_col}_Total', f'{value_col}_Average', 'Record_Count']
                
                # Sort and get top/bottom N
                ascending = is_bottom  # Bottom N = ascending sort
                sorted_data = grouped.sort_values(f'{value_col}_Total', ascending=ascending).head(n)
                
                # Format results using AnalysisFormatter
                formatter = AnalysisFormatter()
                
                direction_text = "Bottom" if is_bottom else "Top"
                
                # Create summary section
                explanation = f"Analysis of the {direction_text.lower()} {n} {group_by_col} items ranked by {value_col} totals."
                assumptions = [
                    f"Ranking based on total {value_col} values per {group_by_col}",
                    f"Data aggregated by {group_by_col} grouping",
                    f"Showing {direction_text.lower()} {n} performers",
                    "Includes total, average, and record count for each item"
                ]
                
                formatted_output = formatter.create_summary_section(
                    f"{direction_text} {n} Analysis",
                    explanation,
                    assumptions
                )
                
                # Create metrics grid for high-level stats
                total_sum = sorted_data[f'{value_col}_Total'].sum()
                overall_sum = grouped[f'{value_col}_Total'].sum()
                percentage = (total_sum / overall_sum * 100) if overall_sum > 0 else 0
                
                summary_metrics = {
                    f"{direction_text}_{n}_Items": len(sorted_data),
                    "Total_Value": formatter.format_currency(total_sum),
                    "Percentage_of_Total": formatter.format_percentage(percentage / 100),
                    "Average_per_Item": formatter.format_currency(total_sum/len(sorted_data))
                }
                
                formatted_output += "\n\n" + formatter.create_metrics_grid(
                    summary_metrics, 
                    f"{direction_text} {n} Summary"
                )
                
                # Create detailed results table
                formatted_output += f"\n\n🎯 **{direction_text.upper()} {n} {group_by_col.upper()} BY {value_col.upper()}:**\n"
                
                table_data = []
                for idx, row in sorted_data.iterrows():
                    rank = len(sorted_data) - sorted_data.index.get_loc(idx) if is_bottom else sorted_data.index.get_loc(idx) + 1
                    
                    table_data.append({
                        "Rank": rank,
                        group_by_col: row[group_by_col],
                        f"Total_{value_col}": formatter.format_currency(row[f'{value_col}_Total']),
                        f"Avg_{value_col}": formatter.format_currency(row[f'{value_col}_Average']),
                        "Records": f"{row['Record_Count']:,}",
                        "% of Total": formatter.format_percentage((row[f'{value_col}_Total'] / overall_sum) if overall_sum > 0 else 0)
                    })
                
                headers = ["Rank", group_by_col, f"Total_{value_col}", f"Avg_{value_col}", "Records", "% of Total"]
                formatted_output += "\n" + formatter.create_banded_table(table_data, headers, max_rows=n+2)
                
                # Add insights section
                insights = [
                    f"{direction_text} {n} {group_by_col} represent {percentage:.1f}% of total {value_col}",
                    f"Combined value: {formatter.format_currency(total_sum)}",
                    f"Average performance per {group_by_col}: {formatter.format_currency(total_sum/len(sorted_data))}",
                    f"Distribution shows {'concentration' if percentage > 50 else 'dispersion'} in the {'worst' if is_bottom else 'best'} performers"
                ]
                
                recommendations = [
                    f"Focus on {'improving' if is_bottom else 'maintaining'} the {'underperforming' if is_bottom else 'top-performing'} {group_by_col}",
                    f"Analyze what makes the {'worst' if is_bottom else 'best'} performers different",
                    f"Consider {'intervention strategies' if is_bottom else 'scaling best practices'} for these {group_by_col}",
                    f"Monitor changes in this {direction_text.lower()} {n} ranking over time"
                ]
                
                formatted_output += "\n\n" + formatter.create_insights_section(insights, recommendations)
                
                results_text = formatted_output
                
                # Generate AI insights if available
                if self.app.llm_interpreter.is_available:
                    context = {
                        'analysis_type': f'{direction}_n_analysis',
                        'parameters': {
                            'n': n,
                            'group_by_column': group_by_col,
                            'value_column': value_col,
                            'direction': direction
                        },
                        'results': sorted_data.to_dict('records'),
                        'summary_stats': {
                            'percentage_of_total': percentage,
                            'combined_value': total_sum,
                            'average_per_item': total_sum/len(sorted_data)
                        }
                    }
                    
                    insight_prompt = f"Provide business insights on this {direction} {n} analysis of {group_by_col} by {value_col}"
                    ai_response = self.app.llm_interpreter.query_llm(insight_prompt, context)
                    
                    if ai_response.success:
                        ai_insights = self.app.narrative_generator.format_for_chat(
                            ai_response.content,
                            f"AI Insights - {direction_text} {n} Analysis"
                        )
                        results_text += "\n\n" + ai_insights
                
                return results_text
                
            except Exception as e:
                return f"❌ **Analysis Execution Error**: {str(e)}"
                
        except Exception as e:
            return f"❌ **Top/Bottom N Analysis Error**: {str(e)}"
    
    def _handle_sql_query(self, query: str, route_result=None) -> str:
        """Handle SQL queries using NL-to-SQL translation and execution"""
        try:
            # Ensure data is loaded into SQL engine
            if self.app.current_data is None:
                return "⚠️ **No data available for SQL queries**. Please upload a CSV file first."
            
            # Load data into SQL engine if not already done or if connection is invalid
            if (not hasattr(self.app, '_sql_data_loaded') or not self.app._sql_data_loaded or 
                not self.app.sql_engine.is_connection_valid()):
                
                print("[DEBUG] Loading/reloading data into SQL engine...")
                success = self.app.sql_engine.load_dataframe_to_sql(self.app.current_data, table_name="data")
                if success:
                    self.app._sql_data_loaded = True
                    print("[DEBUG] Data loaded into SQL engine successfully")
                else:
                    return "❌ **SQL Setup Error**: Failed to load data into SQL engine. Please try again."
            
            # Check if this is already a SQL query or needs translation
            if query.strip().lower().startswith('select'):
                # Direct SQL query
                print(f"[DEBUG] Executing direct SQL: {query}")
                result = self.app.sql_engine.execute_query(query)
                
                # Handle threading issues by retrying with fresh connection
                if not result.success and "thread" in result.error_message.lower():
                    print("[DEBUG] Threading issue detected, refreshing connection...")
                    if self.app.sql_engine.refresh_connection(self.app.current_data):
                        result = self.app.sql_engine.execute_query(query)
                    
            else:
                # Natural language query - translate to SQL
                print(f"[DEBUG] Translating NL to SQL: {query}")
                
                # Get schema context
                schema_context = {
                    'table_name': 'data',
                    'columns': list(self.app.current_data.columns),
                    'sample_data': self.app.current_data.head(3).to_dict('records'),
                    'column_info': self.app.csv_loader.column_info
                }
                
                # Translate to SQL
                sql_result = self.app.nl_to_sql.translate_to_sql(query, schema_context)
                
                if not sql_result.success:
                    return f"❌ **SQL Translation Error**: {sql_result.error_message}"
                
                print(f"[DEBUG] Generated SQL: {sql_result.sql_query}")
                
                # Execute the translated SQL
                result = self.app.sql_engine.execute_query(sql_result.sql_query)
                
                # Handle threading issues by retrying with fresh connection
                if not result.success and "thread" in result.error_message.lower():
                    print("[DEBUG] Threading issue detected in NL query, refreshing connection...")
                    if self.app.sql_engine.refresh_connection(self.app.current_data):
                        result = self.app.sql_engine.execute_query(sql_result.sql_query)
            
            # Format and return results
            if result.success:
                if result.data is not None and len(result.data) > 0:
                    # For translated queries, we need both the original and generated SQL
                    if query.strip().lower().startswith('select'):
                        # Direct SQL query
                        formatted_results = self.app.sql_engine.format_sql_results(result.data, query, query)
                    else:
                        # NL query that was translated
                        formatted_results = self.app.sql_engine.format_sql_results(result.data, sql_result.sql_query, query)
                    
                    # Add AI insights if available
                    if self.app.llm_interpreter.is_available and len(result.data) <= 100:
                        try:
                            ai_response = self.app.llm_interpreter.query_llm(
                                f"Provide insights on these SQL query results for: {query}",
                                {
                                    'query': query,
                                    'results': result.data[:20],  # Limit context size
                                    'row_count': len(result.data)
                                }
                            )
                            
                            if ai_response.success:
                                ai_insights = self.app.narrative_generator.format_for_chat(
                                    ai_response.content, 
                                    "💡 AI Insights"
                                )
                                return f"{formatted_results}\n\n{ai_insights}"
                        except Exception as e:
                            print(f"[DEBUG] AI insights error: {e}")
                    
                    return formatted_results
                else:
                    return "✅ **Query executed successfully** but returned no results."
            else:
                return f"❌ **SQL Execution Error**: {result.error_message}"
                
        except Exception as e:
            print(f"[DEBUG] SQL handling error: {str(e)}")
            return f"❌ **SQL Query Error**: {str(e)}"
