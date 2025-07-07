"""
Quick Action Handler for VariancePro v2.0

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
        
        print(f"🔧 QuickActionHandler initialized with RAG: {self.rag_manager is not None}")
    
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
        elif "top" in action_lower or "bottom" in action_lower:
            return self._handle_top_bottom_action(action)
        else:
            return f"🔍 **{action.title()} Analysis**\n\nThis feature is being implemented. You can ask questions about your data in the chat!"
    
    def _handle_summary_action(self) -> str:
        """
        Handle summary quick action with RAG enhancement.
        
        Returns:
            str: Summary analysis response with RAG context if available
        """
        current_data, data_summary = self.app_core.get_current_data()
        
        # Generate a human-readable summary from the data
        if data_summary and isinstance(data_summary, dict):
            # Convert the data_summary dict to a readable format
            base_summary = self._format_data_summary_dict(data_summary, current_data)
        elif isinstance(data_summary, str):
            # If it's already a string, use it directly
            base_summary = f"📊 **Data Summary**\n\n{data_summary}"
        else:
            # Generate basic summary if no cached summary
            row_count = len(current_data)
            col_count = len(current_data.columns)
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
                    
                    return f"""{base_summary}

{enhanced_result['enhanced_analysis']}

---
🔍 **RAG Enhancement**: Analysis enhanced with {enhanced_result.get('documents_used', 0)} document(s)"""
                else:
                    print(f"⚠️ RAG enhancement failed: {enhanced_result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                print(f"❌ RAG enhancement error: {str(e)}")
        
        return base_summary
    
    def _handle_trends_action(self) -> str:
        """
        Handle trends quick action with RAG enhancement.
        
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
                            
                            return f"""{base_analysis}

{enhanced_result['enhanced_analysis']}

---
🔍 **RAG Enhancement**: Analysis enhanced with {enhanced_result.get('documents_used', 0)} document(s)"""
                        else:
                            print(f"⚠️ RAG enhancement failed: {enhanced_result.get('error', 'Unknown error')}")
                            
                    except Exception as e:
                        print(f"❌ RAG enhancement error: {str(e)}")
                
                return base_analysis
            else:
                return f"❌ **Trends Analysis Failed**: {self.app_core.timescale_analyzer.status}"
                
        except Exception as e:
            return f"❌ **Trends Analysis Error**: {str(e)}"
    
    def _handle_variance_action(self) -> str:
        """
        Handle variance analysis quick action with RAG enhancement.
        
        Returns:
            str: Variance analysis response with RAG context if available
        """
        try:
            current_data, _ = self.app_core.get_current_data()
            
            # Import the variance analyzer
            from analyzers.variance_analyzer import VarianceAnalyzer
            
            variance_analyzer = VarianceAnalyzer()
            
            # Try to detect common variance comparison patterns
            columns = current_data.columns.tolist()
            
            # Look for common variance column patterns
            variance_pairs = variance_analyzer.detect_variance_pairs(columns)
            
            if not variance_pairs:
                return """⚠️ **Variance Analysis**: No obvious variance comparison pairs detected.

**Expected column patterns:**
• Actual vs Planned (e.g., 'Actual Sales', 'Planned Sales')
• Budget vs Actual (e.g., 'Budget', 'Actual')
• Budget vs Sales (e.g., 'Budget Revenue', 'Sales Revenue')

**Available columns**: """ + ", ".join(columns[:10]) + ("..." if len(columns) > 10 else "") + """

💡 **Tip**: Ask me specific questions like "compare actual vs planned" or manually specify columns for variance analysis."""
            
            # Perform variance analysis on the first detected pair
            first_pair = variance_pairs[0]
            
            # Get date columns for time-based analysis
            date_columns = self._detect_date_columns(current_data)
            date_col = date_columns[0] if date_columns else None
            
            # Use comprehensive variance analysis
            result = variance_analyzer.comprehensive_variance_analysis(
                data=current_data,
                actual_col=first_pair['actual'],
                planned_col=first_pair['planned'],
                date_col=date_col
            )
            
            if 'error' in result:
                return f"❌ **Variance Analysis Error**: {result['error']}"
            
            # Format the comprehensive analysis
            base_analysis = variance_analyzer.format_comprehensive_analysis(result)
            
            # Enhance with RAG if available
            if self.rag_manager and self.rag_analyzer and self.rag_manager.has_documents():
                try:
                    print("🔍 Enhancing variance analysis with RAG context...")
                    
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
                        print(f"✅ RAG-enhanced variance analysis generated with {enhanced_result.get('documents_used', 0)} document(s)")
                        
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
    
    def _handle_top_bottom_action(self, action: str) -> str:
        """
        Handle top/bottom N analysis actions.
        
        Args:
            action (str): The action (top5, bottom10, etc.)
            
        Returns:
            str: Analysis response
        """
        try:
            current_data, _ = self.app_core.get_current_data()
            
            # Parse the action to get N and direction
            action_lower = action.lower()
            
            if "top" in action_lower:
                direction = "top"
                if "5" in action_lower:
                    n = 5
                elif "10" in action_lower:
                    n = 10
                else:
                    n = 5  # default
            elif "bottom" in action_lower:
                direction = "bottom"
                if "5" in action_lower:
                    n = 5
                elif "10" in action_lower:
                    n = 10
                else:
                    n = 5  # default
            else:
                return f"❌ **Analysis Error**: Unrecognized action '{action}'"
            
            # Get numeric columns for analysis
            numeric_columns = current_data.select_dtypes(include=['number']).columns.tolist()
            
            if not numeric_columns:
                return f"⚠️ **{direction.title()} {n} Analysis**: No numeric columns found in your data."
            
            # Get categorical columns for grouping
            categorical_columns = current_data.select_dtypes(include=['object']).columns.tolist()
            
            # Use the first numeric column for values
            value_col = numeric_columns[0]
            
            # Use the first categorical column for categories (if available)
            if categorical_columns:
                category_col = categorical_columns[0]
                
                # Group by category and sum values
                grouped_data = current_data.groupby(category_col)[value_col].sum().reset_index()
                
                # Sort and get top/bottom N
                if direction == "top":
                    result_data = grouped_data.nlargest(n, value_col)
                else:
                    result_data = grouped_data.nsmallest(n, value_col)
                    
                # Format results with more detail
                result_text = ""
                total_sum = grouped_data[value_col].sum()
                
                for idx, (_, row) in enumerate(result_data.iterrows(), 1):
                    percentage = (row[value_col] / total_sum) * 100 if total_sum > 0 else 0
                    result_text += f"• **#{idx} {row[category_col]}**: ${row[value_col]:,.2f} ({percentage:.1f}% of total)\n"
                
                # Generate comprehensive analysis with LLM commentary
                analysis_result = self._generate_enhanced_top_bottom_analysis(
                    result_data, direction, n, value_col, current_data, category_col, total_sum
                )
                
                return f"""🔍 **{direction.title()} {n} Analysis by {category_col}**

{result_text}

{analysis_result}"""
            
            else:
                # No categorical columns, just sort by the numeric column
                if direction == "top":
                    result_data = current_data.nlargest(n, value_col)
                else:
                    result_data = current_data.nsmallest(n, value_col)
                
                # Create enhanced analysis for non-categorical data
                analysis_result = self._generate_enhanced_numeric_analysis(
                    result_data, direction, n, value_col, current_data
                )
                
                return f"""🔍 **{direction.title()} {n} Analysis**

{analysis_result}"""
                
        except Exception as e:
            return f"❌ **{action.title()} Analysis Error**: {str(e)}"
    
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
                "• Use variance analysis for performance gaps",
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
