"""
Quick Action Handler for Quant Commander v2.0

This module handles all quick action button functionality including:
- Summary analysis
- Trends analysis
- Top/Bottom N analysis
- Action routing and processing
- Response formatting

Extracted from app_v2.py to follow modular design principles.
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import List, Dict, Any, Optional

from handlers.timestamp_handler import TimestampHandler
from analyzers.forecast_analyzer import ForecastingAnalyzer
from utils.cache_manager import get_cache_manager
from utils.performance_monitor import get_performance_monitor, performance_monitor


class QuickActionHandler:
    """
    Handles quick action button processing and analysis.
    
    This class encapsulates all quick action functionality to keep
    the main application code clean and focused.
    """
    
    def __init__(self, app_core, rag_manager=None, rag_analyzer=None):
        """
        Initialize the quick action handler.
        
        Args:
            app_core: Reference to the main application core for data access
            rag_manager: RAG Document Manager for document context (optional)
            rag_analyzer: RAG Enhanced Analyzer for enhanced analysis (optional)
        """
        self.app_core = app_core
        self.timestamp_handler = TimestampHandler()
        self.rag_manager = rag_manager
        self.rag_analyzer = rag_analyzer
        
        # Initialize Phase 3A components: caching and performance monitoring
        self.cache_manager = get_cache_manager()
        self.performance_monitor = get_performance_monitor()
        
        # Initialize Phase 3B components: forecasting analyzer
        self.forecasting_analyzer = ForecastingAnalyzer(confidence_level=0.95)
        
        print(f"🔧 QuickActionHandler initialized with RAG: {self.rag_manager is not None}")
        print(f"🔧 Phase 3A components initialized: Cache & Performance monitoring")
        print(f"🔧 Phase 3B components initialized: Forecasting analyzer")
    
    def handle_action(self, action: str, history: List[Dict]) -> List[Dict]:
        """
        Handle quick action button clicks by creating a proper user-assistant interaction.
        
        Args:
            action (str): The action to perform (summary, trends, top5, etc.)
            history (List[Dict]): The current chat history
            
        Returns:
            List[Dict]: Updated chat history with the action and response
        """
        print(f"[DEBUG] Quick action triggered: {action}")
        
        # Generate timestamp for browser local time
        current_timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Create a user message for the action
        user_message = f"Please provide {action} analysis"
        
        # Add timestamped user message to history
        timestamped_user_message = {
            "role": "user", 
            "content": self.timestamp_handler.add_timestamp_to_message(user_message, current_timestamp)
        }
        history.append(timestamped_user_message)
        
        # Check if data is available
        if not self.app_core.has_data():
            response = "⚠️ **Please upload a CSV file first** to use quick analysis features."
        else:
            # Route to appropriate action handler
            response = self._route_action(action)
        
        # Add the timestamped assistant response to chat history
        timestamped_assistant_message = {
            "role": "assistant", 
            "content": self.timestamp_handler.add_timestamp_to_message(response, current_timestamp)
        }
        history.append(timestamped_assistant_message)
        return history
    
    def _route_action(self, action: str) -> str:
        """
        Route the action to the appropriate handler.
        
        Args:
            action (str): The action to perform
            
        Returns:
            str: The analysis response
        """
        action_lower = action.lower()
        
        if action_lower == "summary":
            return self._handle_summary_action()
        elif action_lower == "trends":
            return self._handle_trends_action()
        elif action_lower == "variance":
            return self._handle_variance_action()
        elif action_lower == "forecast":
            return self._handle_forecast_action()
        elif "top" in action_lower or "bottom" in action_lower:
            return self._handle_top_bottom_action(action)
        else:
            return f"🔍 **{action.title()} Analysis**\n\nThis feature is being implemented. You can ask questions about your data in the chat!"
    
    def invalidate_cache_for_data_change(self):
        """
        Invalidate cache when data changes (e.g., new CSV uploaded).
        
        This method should be called whenever the underlying data changes
        to ensure cache consistency and prevent stale results.
        """
        try:
            current_data, _ = self.app_core.get_current_data()
            if current_data is not None:
                self.cache_manager.invalidate_data_cache(current_data)
                print("🗑️ Cache invalidated due to data change")
        except Exception as e:
            print(f"⚠️ Error invalidating cache: {str(e)}")
    
    def get_cache_stats(self) -> Dict:
        """
        Get cache performance statistics.
        
        Returns:
            Dict: Cache statistics including hit rate, size, etc.
        """
        return self.cache_manager.get_stats()
    
    def get_performance_stats(self) -> Dict:
        """
        Get performance monitoring statistics.
        
        Returns:
            Dict: Performance statistics including response times, etc.
        """
        return self.performance_monitor.get_performance_summary()
    
    @performance_monitor('summary_analysis')
    def _handle_summary_action(self) -> str:
        """
        Handle summary quick action with RAG enhancement and caching.
        
        This method now includes Phase 3A caching to improve performance
        for repeated summary requests on the same data.
        
        Returns:
            str: Summary analysis response with RAG context if available
        """
        # Get data first to check cache - but only once
        try:
            current_data, data_summary = self.app_core.get_current_data()
        except Exception as e:
            return f"❌ **Summary Analysis Error**: Unable to retrieve data - {str(e)}"
        
        # Check cache first for summary analysis
        cache_key_params = {
            'has_rag': self.rag_manager is not None and self.rag_manager.has_documents(),
            'data_summary_type': type(data_summary).__name__
        }
        
        cached_result = self.cache_manager.get(current_data, 'summary', cache_key_params)
        if cached_result is not None:
            return cached_result
        
        # Only calculate these if we didn't get a cache hit
        row_count = len(current_data)
        col_count = len(current_data.columns)
        
        # Generate a human-readable summary from the data
        if data_summary and isinstance(data_summary, dict):
            # Convert the data_summary dict to a readable format
            base_summary = self._format_data_summary_dict(data_summary, current_data)
        elif isinstance(data_summary, str):
            # If it's already a string, use it directly
            base_summary = f"📊 **Data Summary**\n\n{data_summary}"
        else:
            # Generate basic summary if no cached summary
            columns = ', '.join(current_data.columns[:5])
            if len(current_data.columns) > 5:
                columns += "..."
            
            base_summary = f"""📊 **Quick Summary**

**Dataset Overview**: {row_count:,} rows × {col_count} columns

**Columns**: {columns}

**Data Types**: {len(current_data.select_dtypes(include=['number']).columns)} numeric, {len(current_data.select_dtypes(include=['object']).columns)} text

💡 **Next Steps**: Try trends analysis or ask specific questions about your data!"""
        
        # Enhance with RAG if available
        if self.rag_manager and self.rag_analyzer and self.rag_manager.has_documents():
            try:
                print("🔍 Enhancing summary with RAG context...")
                
                # Create analysis context for RAG enhancement
                analysis_context = f"""
Data Summary Analysis:
- Dataset: {row_count:,} rows × {col_count} columns
- Key columns: {', '.join(current_data.columns[:10])}
- Data types: {len(current_data.select_dtypes(include=['number']).columns)} numeric, {len(current_data.select_dtypes(include=['object']).columns)} categorical
"""
                
                # Enhance with RAG
                enhanced_result = self.rag_analyzer.enhance_general_analysis(
                    analysis_data={'summary': base_summary, 'context': analysis_context},
                    analysis_type='summary',
                    query_context="dataset summary and overview analysis"
                )
                
                if enhanced_result.get('success'):
                    print(f"✅ RAG-enhanced summary generated with {enhanced_result.get('documents_used', 0)} document(s)")
                    
                    # Log the prompt being used for validation
                    if 'prompt_used' in enhanced_result:
                        print("📝 PROMPT USED FOR RAG ENHANCEMENT:")
                        print("=" * 50)
                        print(enhanced_result['prompt_used'])
                        print("=" * 50)
                    
                    final_result = f"""{base_summary}

{enhanced_result['enhanced_analysis']}

---
🔍 **RAG Enhancement**: Analysis enhanced with {enhanced_result.get('documents_used', 0)} document(s)"""
                    
                    # Cache the RAG-enhanced result
                    self.cache_manager.put(current_data, 'summary', final_result, cache_key_params)
                    return final_result
                else:
                    print(f"⚠️ RAG enhancement failed: {enhanced_result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                print(f"❌ RAG enhancement error: {str(e)}")
        
        # Cache the base summary result
        self.cache_manager.put(current_data, 'summary', base_summary, cache_key_params)
        return base_summary
    
    @performance_monitor('trends_analysis')
    def _handle_trends_action(self) -> str:
        """
        Handle trends quick action with RAG enhancement and caching.
        
        This method now includes Phase 3A caching to improve performance
        for repeated trends requests on the same data.
        
        Returns:
            str: Trends analysis response with RAG context if available
        """
        if self.app_core.timescale_analyzer is None:
            return "⚠️ **Trends Analysis**: Timescale analyzer not available. Please check the system configuration."
        
        try:
            current_data, _ = self.app_core.get_current_data()
            
            # Detect date columns for trends analysis
            date_columns = self._detect_date_columns(current_data)
            
            if not date_columns:
                return "⚠️ **Trends Analysis**: No date columns detected in your data. Trends analysis requires time-based data."
            
            # Get numeric columns
            numeric_columns = current_data.select_dtypes(include=['number']).columns.tolist()
            
            if not numeric_columns:
                return "⚠️ **Trends Analysis**: No numeric columns found. Trends analysis requires numerical data to analyze."
            
            # Check cache first for trends analysis
            cache_key_params = {
                'has_rag': self.rag_manager is not None and self.rag_manager.has_documents(),
                'date_columns': date_columns,
                'numeric_columns': numeric_columns[:3]  # Only first 3 columns affect analysis
            }
            
            cached_result = self.cache_manager.get(current_data, 'trends', cache_key_params)
            if cached_result is not None:
                return cached_result
            
            # Get numeric columns
            numeric_columns = current_data.select_dtypes(include=['number']).columns.tolist()
            
            if not numeric_columns:
                return "⚠️ **Trends Analysis**: No numeric columns found. Trends analysis requires numerical data to analyze."
            
            # Perform the analysis
            self.app_core.timescale_analyzer.analyze(
                data=current_data,
                date_col=date_columns[0],
                value_cols=numeric_columns[:3]  # Limit to first 3 columns
            )
            
            if self.app_core.timescale_analyzer.status == "completed":
                base_analysis = f"📈 **Trends Analysis**\n\n{self.app_core.timescale_analyzer.format_for_chat()}"
                
                # Enhance with RAG if available
                if self.rag_manager and self.rag_analyzer and self.rag_manager.has_documents():
                    try:
                        print("🔍 Enhancing trends analysis with RAG context...")
                        
                        # Create analysis context for RAG enhancement
                        analysis_context = f"""
Trends Analysis Results:
- Date column: {date_columns[0]}
- Value columns analyzed: {', '.join(numeric_columns[:3])}
- Dataset size: {len(current_data)} records
- Analysis status: {self.app_core.timescale_analyzer.status}
"""
                        
                        # Enhance with RAG
                        enhanced_result = self.rag_analyzer.enhance_trend_analysis(
                            trend_data={'analysis': base_analysis, 'context': analysis_context},
                            analysis_context=analysis_context
                        )
                        
                        if enhanced_result.get('success'):
                            print(f"✅ RAG-enhanced trends analysis generated with {enhanced_result.get('documents_used', 0)} document(s)")
                            
                            # Log the prompt being used for validation
                            if 'prompt_used' in enhanced_result:
                                print("📝 PROMPT USED FOR RAG ENHANCEMENT:")
                                print("=" * 50)
                                print(enhanced_result['prompt_used'])
                                print("=" * 50)
                            
                            final_result = f"""{base_analysis}

{enhanced_result['enhanced_analysis']}

---
🔍 **RAG Enhancement**: Analysis enhanced with {enhanced_result.get('documents_used', 0)} document(s)"""
                            
                            # Cache the RAG-enhanced result
                            self.cache_manager.put(current_data, 'trends', final_result, cache_key_params)
                            return final_result
                        else:
                            print(f"⚠️ RAG enhancement failed: {enhanced_result.get('error', 'Unknown error')}")
                            
                    except Exception as e:
                        print(f"❌ RAG enhancement error: {str(e)}")
                
                # Cache the base analysis result
                self.cache_manager.put(current_data, 'trends', base_analysis, cache_key_params)
                return base_analysis
            else:
                return f"❌ **Trends Analysis Failed**: {self.app_core.timescale_analyzer.status}"
                
        except Exception as e:
            return f"❌ **Trends Analysis Error**: {str(e)}"
    
    @performance_monitor('variance_analysis')
    def _handle_variance_action(self) -> str:
        """
        Handle quantitative analysis quick action with RAG enhancement.
        
        Returns:
            str: Quantitative analysis response with RAG context if available
        """
        try:
            current_data, _ = self.app_core.get_current_data()
            
            # Import the variance analyzer
            from analyzers.quant_analyzer import QuantAnalyzer
            
            quant_analyzer = QuantAnalyzer()
            
            # Try to detect common variance comparison patterns
            columns = current_data.columns.tolist()
            
            # Look for common variance column patterns
            variance_pairs = quant_analyzer.detect_variance_pairs(columns)
            
            if not variance_pairs:
                return """⚠️ **Variance Analysis**: No obvious variance comparison pairs detected.

**Expected column patterns:**
• Actual vs Planned (e.g., 'Actual Sales', 'Planned Sales')
• Budget vs Actual (e.g., 'Budget', 'Actual')
• Budget vs Sales (e.g., 'Budget Revenue', 'Sales Revenue')

**Available columns**: """ + ", ".join(columns[:10]) + ("..." if len(columns) > 10 else "") + """

💡 **Tip**: Ask me specific questions like "compare actual vs planned" or manually specify columns for quantitative analysis."""
            
            # Perform quantitative analysis on the first detected pair
            first_pair = variance_pairs[0]
            
            # Get date columns for time-based analysis
            date_columns = self._detect_date_columns(current_data)
            date_col = date_columns[0] if date_columns else None
            
            # Use comprehensive quantitative analysis
            result = quant_analyzer.comprehensive_variance_analysis(
                data=current_data,
                actual_col=first_pair['actual'],
                planned_col=first_pair['planned'],
                date_col=date_col
            )
            
            if 'error' in result:
                return f"❌ **Variance Analysis Error**: {result['error']}"
            
            # Format the comprehensive analysis
            base_analysis = quant_analyzer.format_comprehensive_analysis(result)
            
            # Enhance with RAG if available
            if self.rag_manager and self.rag_analyzer and self.rag_manager.has_documents():
                try:
                    print("🔍 Enhancing quantitative analysis with RAG context...")
                    
                    # Create analysis context for RAG enhancement
                    analysis_context = f"""
Variance Analysis Results:
- Actual column: {first_pair['actual']}
- Planned column: {first_pair['planned']}
- Date column: {date_col or 'None detected'}
- Dataset size: {len(current_data)} records
- Additional pairs available: {len(variance_pairs) - 1}
"""
                    
                    # Enhance with RAG
                    enhanced_result = self.rag_analyzer.enhance_variance_analysis(
                        variance_data={'analysis': base_analysis, 'context': analysis_context},
                        analysis_context=analysis_context
                    )
                    
                    if enhanced_result.get('success'):
                        print(f"✅ RAG-enhanced quantitative analysis generated with {enhanced_result.get('documents_used', 0)} document(s)")
                        
                        # Log the prompt being used for validation
                        if 'prompt_used' in enhanced_result:
                            print("📝 PROMPT USED FOR RAG ENHANCEMENT:")
                            print("=" * 50)
                            print(enhanced_result['prompt_used'])
                            print("=" * 50)
                        
                        final_analysis = f"""{base_analysis}

{enhanced_result['enhanced_analysis']}

---
🔍 **RAG Enhancement**: Analysis enhanced with {enhanced_result.get('documents_used', 0)} document(s)"""
                    else:
                        print(f"⚠️ RAG enhancement failed: {enhanced_result.get('error', 'Unknown error')}")
                        final_analysis = base_analysis
                        
                except Exception as e:
                    print(f"❌ RAG enhancement error: {str(e)}")
                    final_analysis = base_analysis
            else:
                final_analysis = base_analysis
            
            return f"""{final_analysis}

💡 **Additional Pairs Available**: {len(variance_pairs) - 1} more variance comparison opportunities detected."""
            
        except Exception as e:
            return f"❌ **Variance Analysis Error**: {str(e)}"
    
    @performance_monitor('top_bottom_analysis')
    def _handle_top_bottom_action(self, action: str) -> str:
        """
        Handle top/bottom N quick actions robustly.
        
        This method provides comprehensive error handling and graceful degradation
        for various edge cases including missing columns, invalid data, etc.
        
        Args:
            action (str): The action string (e.g., 'top 5', 'bottom 10', 'top 3 by revenue')
        Returns:
            str: Top/Bottom N analysis response
        """
        import re
        try:
            current_data, _ = self.app_core.get_current_data()
            
            # Validate that we have data
            if current_data is None or current_data.empty:
                return "⚠️ **Top/Bottom N Analysis**: No data available. Please upload a CSV file first."
            
            action_lower = action.lower()
            
            # Extract direction and N (default N=5) with improved parsing
            match = re.search(r'(top|bottom)\s*(\d+)?', action_lower)
            if not match:
                return f"❌ **Top/Bottom N Analysis Error**: Could not parse action '{action}'. Try 'top 5' or 'bottom 10'."
            
            direction = match.group(1)
            n = int(match.group(2)) if match.group(2) else 5
            
            # Validate N is reasonable
            if n <= 0:
                return f"❌ **Top/Bottom N Analysis Error**: N must be positive, got {n}."
            if n > len(current_data):
                n = len(current_data)
                print(f"[DEBUG] N reduced to dataset size: {n}")
            
            # Optionally extract column (e.g., 'by revenue')
            col_match = re.search(r'by ([\w\s]+)', action_lower)
            sort_col = None
            
            if col_match:
                candidate = col_match.group(1).strip()
                # Try to find matching column with fuzzy matching
                for col in current_data.columns:
                    if candidate.lower() in col.lower():
                        sort_col = col
                        break
                
                # If specified column not found, return helpful error
                if not sort_col:
                    available_cols = ', '.join(current_data.columns[:5])
                    if len(current_data.columns) > 5:
                        available_cols += "..."
                    return f"❌ **Column '{candidate}' not found**. Available columns: {available_cols}"
            
            # Default to first numeric column if not specified
            if not sort_col:
                numeric_columns = current_data.select_dtypes(include=['number']).columns.tolist()
                if not numeric_columns:
                    return f"⚠️ **{direction.title()} {n} Analysis**: No numeric columns found in your data. This analysis requires numerical data to sort by."
                sort_col = numeric_columns[0]
                print(f"[DEBUG] Using default numeric column: {sort_col}")
            
            # Validate the selected column has valid data
            if current_data[sort_col].isna().all():
                return f"⚠️ **{direction.title()} {n} Analysis**: Column '{sort_col}' contains only missing values."
            
            # Show all columns for top/bottom N rows
            if direction == "top":
                result_df = current_data.nlargest(n, sort_col)
            else:
                result_df = current_data.nsmallest(n, sort_col)
            
            # Handle case where result is empty
            if result_df.empty:
                return f"⚠️ **{direction.title()} {n} Analysis**: No valid data found for column '{sort_col}'."
            
            # Format as markdown table with error handling
            try:
                result_str = result_df.head(n).to_markdown(index=False)
            except Exception as e:
                # Fallback to string representation if to_markdown fails
                print(f"[DEBUG] to_markdown failed: {e}, using fallback")
                result_str = result_df.head(n).to_string(index=False)
            
            return f"🔍 **{direction.title()} {n} Rows by {sort_col}**\n\n{result_str}\n\n*Tip: You can specify a column, e.g. 'Top 5 by Revenue'.*"
            
        except ImportError as e:
            return f"❌ **Top/Bottom N Analysis Error**: Missing dependency - {str(e)}. Please install required packages."
        except KeyError as e:
            return f"❌ **Top/Bottom N Analysis Error**: Column not found - {str(e)}."
        except ValueError as e:
            return f"❌ **Top/Bottom N Analysis Error**: Invalid data - {str(e)}."
        except Exception as e:
            print(f"[DEBUG] Unexpected error in top/bottom analysis: {e}")
            return f"❌ **Top/Bottom N Analysis Error**: {str(e)}. Please try again or contact support."
    
    @performance_monitor('forecast_analysis')
    def _handle_forecast_action(self) -> str:
        """
        Handle forecast action with caching and performance monitoring.
        
        Returns:
            str: Formatted forecast analysis
        """
        try:
            # Get current data
            current_data, data_summary = self.app_core.get_current_data()
            
            # Check cache first
            cached_result = self.cache_manager.get(current_data, 'forecast_analysis')
            if cached_result:
                return cached_result
            
            # Find the best column for forecasting (prefer numeric columns)
            numeric_columns = current_data.select_dtypes(include=[np.number]).columns
            if len(numeric_columns) == 0:
                return "⚠️ **Forecast Analysis**\n\nNo numeric columns found for forecasting. Please ensure your data contains numeric values."
            
            # Use the first numeric column or look for common patterns
            forecast_column = None
            for col in numeric_columns:
                if any(keyword in col.lower() for keyword in ['revenue', 'sales', 'profit', 'value', 'amount']):
                    forecast_column = col
                    break
            
            if not forecast_column:
                forecast_column = numeric_columns[0]
            
            # Try to find a date column
            date_column = None
            for col in current_data.columns:
                try:
                    pd.to_datetime(current_data[col])
                    date_column = col
                    break
                except:
                    continue
            
            if not date_column:
                return "⚠️ **Forecast Analysis**\n\nNo date column found. Forecasting requires a date column to create time series predictions."
            
            # Generate forecast
            forecast_result = self.forecasting_analyzer.analyze_time_series(
                current_data, 
                target_column=forecast_column, 
                date_column=date_column,
                periods=6  # Default to 6 periods
            )
            
            # Format the result
            formatted_result = self.forecasting_analyzer.format_forecast_for_display(forecast_result)
            
            # Add RAG enhancement if available
            if self.rag_manager and self.rag_manager.has_documents():
                try:
                    rag_enhancement = self.rag_analyzer.enhance_general_analysis(
                        f"Forecast Analysis for {forecast_column}",
                        formatted_result
                    )
                    
                    if rag_enhancement.get('success', False):
                        formatted_result += f"\n\n🎯 **RAG Enhancement**\n{rag_enhancement.get('enhanced_analysis', '')}"
                except Exception as e:
                    print(f"[DEBUG] RAG enhancement failed: {e}")
            
            # Cache the result
            self.cache_manager.put(current_data, 'forecast_analysis', formatted_result)
            
            return formatted_result
            
        except Exception as e:
            print(f"[DEBUG] Forecast analysis error: {e}")
            error_msg = f"⚠️ **Forecast Analysis Error**\n\nAn error occurred while generating the forecast: {str(e)}"
            return error_msg

    # ... existing methods ...
    
    def _detect_date_columns(self, df) -> List[str]:
        """
        Detect potential date columns in the DataFrame.
        
        Args:
            df: The DataFrame to analyze
            
        Returns:
            List[str]: List of potential date column names
        """
        date_columns = []
        
        for col in df.columns:
            col_lower = col.lower()
            # Check for common date column names
            if any(date_word in col_lower for date_word in ['date', 'time', 'day', 'month', 'year']):
                date_columns.append(col)
                continue
            
            # Check if the column can be parsed as dates
            try:
                import pandas as pd
                pd.to_datetime(df[col].dropna().head(10), errors='raise')
                date_columns.append(col)
            except:
                continue
        
        return date_columns
    
    def _format_data_summary_dict(self, data_summary: dict, current_data) -> str:
        """
        Convert data summary dictionary to human-readable format.
        
        Args:
            data_summary: Dictionary containing data analysis results
            current_data: The pandas DataFrame
            
        Returns:
            str: Formatted, human-readable summary
        """
        try:
            # Extract key information from the dictionary
            row_count = data_summary.get('row_count', len(current_data))
            col_count = data_summary.get('column_count', len(current_data.columns))
            columns = data_summary.get('columns', list(current_data.columns))
            basic_stats = data_summary.get('basic_stats', {})
            
            # Start building the summary
            summary_parts = [
                "📊 **Data Summary**",
                "",
                f"**Dataset Overview**: {row_count:,} rows × {col_count} columns",
                ""
            ]
            
            # Add column information
            if columns:
                display_cols = columns[:5]
                if len(columns) > 5:
                    display_cols.append("...")
                summary_parts.append(f"**Columns**: {', '.join(display_cols)}")
                summary_parts.append("")
            
            # Add data types info
            column_types = data_summary.get('column_types', {})
            if column_types:
                numeric_cols = sum(1 for dtype in column_types.values() if 'int' in str(dtype).lower() or 'float' in str(dtype).lower())
                text_cols = sum(1 for dtype in column_types.values() if 'object' in str(dtype).lower())
                summary_parts.append(f"**Data Types**: {numeric_cols} numeric, {text_cols} text")
                summary_parts.append("")
            
            # Add key statistics for numeric columns
            if basic_stats:
                summary_parts.append("**Key Statistics**:")
                for col, stats in list(basic_stats.items())[:3]:  # Show first 3 numeric columns
                    if isinstance(stats, dict) and 'mean' in stats:
                        summary_parts.append(f"• **{col}**: Avg ${stats['mean']:,.0f}, Range ${stats['min']:,.0f}-${stats['max']:,.0f}")
                summary_parts.append("")
            
            # Add data quality insights
            data_quality = data_summary.get('data_quality', {})
            if data_quality:
                null_columns = [col for col, quality in data_quality.items() if quality.get('null_count', 0) > 0]
                if null_columns:
                    summary_parts.append(f"**Data Quality**: {len(null_columns)} columns have missing values")
                else:
                    summary_parts.append("**Data Quality**: No missing values detected")
                summary_parts.append("")
            
            # Add suggested actions
            summary_parts.extend([
                "**Suggested Actions**:",
                "• Try trends analysis for time-based insights",
                "• Use quantitative analysis for performance gaps",
                "• Ask questions like 'show me the top performers'"
            ])
            
            return "\n".join(summary_parts)
            
        except Exception as e:
            print(f"[DEBUG] Error formatting data summary: {e}")
            # Fallback to basic summary
            row_count = len(current_data)
            col_count = len(current_data.columns)
            return f"""📊 **Data Summary**

**Dataset Overview**: {row_count:,} rows × {col_count} columns

**Columns**: {', '.join(current_data.columns[:5])}{"..." if len(current_data.columns) > 5 else ""}

💡 **Note**: Summary formatting issue occurred. You can still analyze your data!"""
