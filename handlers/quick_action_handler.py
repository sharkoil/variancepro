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
        
        if data_summary:
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
    
    def _generate_top_bottom_commentary(self, result_data: pd.DataFrame, direction: str, n: int, 
                                      value_col: str, full_data: pd.DataFrame, 
                                      category_col: Optional[str] = None) -> str:
        """
        Generate LLM commentary for top/bottom N analysis results.
        
        Args:
            result_data (pd.DataFrame): The top/bottom N results
            direction (str): 'top' or 'bottom'
            n (int): Number of results
            value_col (str): The value column being analyzed
            full_data (pd.DataFrame): The complete dataset
            category_col (str, optional): Category column if grouping was used
            
        Returns:
            str: LLM-generated commentary or fallback analysis
        """
        try:
            # Check if LLM is available
            if not self.app_core.is_ollama_available():
                return self._generate_fallback_commentary(result_data, direction, n, value_col, full_data, category_col)
            
            # Prepare context for LLM
            total_records = len(full_data)
            total_value = full_data[value_col].sum()
            avg_value = full_data[value_col].mean()
            
            # Create data summary for LLM
            data_summary = []
            for idx, (_, row) in enumerate(result_data.iterrows(), 1):
                if category_col:
                    data_summary.append(f"{idx}. {row[category_col]}: ${row[value_col]:,.2f}")
                else:
                    data_summary.append(f"{idx}. ${row[value_col]:,.2f}")
            
            # Calculate percentage of total for top item
            top_percentage = (result_data.iloc[0][value_col] / total_value * 100) if total_value > 0 else 0
            
            prompt = f"""
As a financial analyst, provide insightful commentary on this {direction} {n} analysis:

DATASET CONTEXT:
- Total records: {total_records:,}
- Column analyzed: {value_col}
- Total value: ${total_value:,.2f}
- Average value: ${avg_value:,.2f}
- Analysis type: {direction.title()} {n} performers

{direction.upper()} {n} RESULTS:
{chr(10).join(data_summary)}

KEY METRICS:
- Top performer represents {top_percentage:.1f}% of total value
- Range: ${result_data.iloc[-1][value_col]:,.2f} to ${result_data.iloc[0][value_col]:,.2f}

Please provide:
1. What these results reveal about performance distribution
2. Business implications of the {direction} performers
3. Potential areas for investigation or action
4. Any notable patterns or outliers

Keep response under 150 words and focus on actionable business insights.
"""
            
            # Get LLM response
            llm_response = self.app_core.call_ollama(prompt)
            
            return f"""### 🤖 **AI Commentary**
{llm_response}"""
            
        except Exception as e:
            return self._generate_fallback_commentary(result_data, direction, n, value_col, full_data, category_col)
    
    def _generate_fallback_commentary(self, result_data: pd.DataFrame, direction: str, n: int,
                                    value_col: str, full_data: pd.DataFrame,
                                    category_col: Optional[str] = None) -> str:
        """
        Generate fallback commentary when LLM is not available.
        
        Args:
            result_data (pd.DataFrame): The analysis results
            direction (str): 'top' or 'bottom'  
            n (int): Number of results
            value_col (str): The value column
            full_data (pd.DataFrame): Complete dataset
            category_col (str, optional): Category column
            
        Returns:
            str: Statistical commentary
        """
        try:
            total_value = full_data[value_col].sum()
            avg_value = full_data[value_col].mean()
            
            # Calculate key metrics
            top_value = result_data.iloc[0][value_col]
            top_percentage = (top_value / total_value * 100) if total_value > 0 else 0
            
            # Range analysis
            value_range = result_data.iloc[0][value_col] - result_data.iloc[-1][value_col]
            range_percentage = (value_range / avg_value * 100) if avg_value > 0 else 0
            
            commentary_lines = [
                "### 📊 **Statistical Analysis**",
                f"• **{direction.title()} performer** represents **{top_percentage:.1f}%** of total value",
                f"• **Performance range** spans **${value_range:,.2f}** ({range_percentage:.1f}% of average)",
                f"• **{direction.title()} {n}** collectively account for **{(result_data[value_col].sum() / total_value * 100):.1f}%** of total"
            ]
            
            # Add insights based on distribution
            if top_percentage > 20:
                commentary_lines.append(f"• **High concentration**: Top performer dominates the dataset")
            elif top_percentage < 5:
                commentary_lines.append(f"• **Even distribution**: Performance is relatively balanced")
            
            if range_percentage > 100:
                commentary_lines.append(f"• **High variability**: Significant performance gaps identified")
            
            return "\n".join(commentary_lines)
            
        except Exception as e:
            return f"### 📊 **Analysis Summary**\n• {direction.title()} {n} analysis completed\n• Statistical commentary unavailable: {str(e)}"

    def _generate_enhanced_top_bottom_analysis(self, result_data, direction: str, n: int, 
                                             value_col: str, full_data, category_col: str, 
                                             total_sum: float) -> str:
        """
        Generate comprehensive analysis with LLM commentary, variance analysis, and RAG enhancement.
        
        Args:
            result_data: The top/bottom N results
            direction: 'top' or 'bottom'
            n: Number of results
            value_col: The numeric column being analyzed
            full_data: The complete dataset
            category_col: The categorical column for grouping
            total_sum: Total sum of all values
            
        Returns:
            str: Comprehensive analysis with LLM commentary and RAG enhancement
        """
        try:
            # Basic statistical analysis
            result_values = result_data[value_col].values
            stats = {
                'mean': result_values.mean(),
                'median': np.median(result_values),
                'std': result_values.std(),
                'min': result_values.min(),
                'max': result_values.max(),
                'range': result_values.max() - result_values.min()
            }
            
            # Variance analysis across timeframes if date column exists
            variance_analysis = self._perform_multi_timeframe_analysis(full_data, value_col, category_col)
            
            # Generate base LLM commentary
            base_llm_commentary = self._generate_llm_commentary_for_top_bottom(
                result_data, direction, n, value_col, category_col, stats, total_sum, variance_analysis
            )
            
            # Enhance with RAG if available
            enhanced_commentary = base_llm_commentary
            if self.rag_manager and self.rag_analyzer and self.rag_manager.has_documents():
                try:
                    print(f"🔍 Enhancing {direction} {n} analysis with RAG context...")
                    
                    # Prepare top performers data for RAG context
                    top_performers = []
                    for _, row in result_data.iterrows():
                        percentage = (row[value_col] / total_sum) * 100 if total_sum > 0 else 0
                        top_performers.append(f"{row[category_col]}: ${row[value_col]:,.2f} ({percentage:.1f}%)")
                    
                    # Create analysis context for RAG enhancement
                    analysis_context = f"""
{direction.title()} {n} Analysis Results:
- Category: {category_col}
- Metric: {value_col}
- Performers: {'; '.join(top_performers)}
- Mean: ${stats['mean']:,.2f}
- Range: ${stats['range']:,.2f}
- Standard Deviation: ${stats['std']:,.2f}
"""
                    
                    analysis_data = {
                        'top_performers': top_performers,
                        'stats': stats,
                        'variance_analysis': variance_analysis,
                        'base_commentary': base_llm_commentary
                    }
                    
                    # Enhance with RAG
                    enhanced_result = self.rag_analyzer.enhance_top_n_analysis(
                        top_n_data=analysis_data,
                        analysis_context=analysis_context,
                        direction=direction,
                        n=n
                    )
                    
                    if enhanced_result.get('success'):
                        print(f"✅ RAG-enhanced {direction} {n} analysis generated with {enhanced_result.get('documents_used', 0)} document(s)")
                        
                        # Log the prompt being used for validation
                        if 'prompt_used' in enhanced_result:
                            print("📝 PROMPT USED FOR RAG ENHANCEMENT:")
                            print("=" * 50)
                            print(enhanced_result['prompt_used'])
                            print("=" * 50)
                        
                        enhanced_commentary = f"""{base_llm_commentary}

### 🔍 **RAG-Enhanced Insights**
{enhanced_result['enhanced_analysis']}

---
**RAG Enhancement**: Analysis enhanced with {enhanced_result.get('documents_used', 0)} document(s)"""
                    else:
                        print(f"⚠️ RAG enhancement failed: {enhanced_result.get('error', 'Unknown error')}")
                        
                except Exception as e:
                    print(f"❌ RAG enhancement error: {str(e)}")
            
            # Format comprehensive response
            analysis_lines = [
                "### 📊 **Statistical Summary**",
                f"• **Mean**: ${stats['mean']:,.2f}",
                f"• **Median**: ${stats['median']:,.2f}",
                f"• **Range**: ${stats['range']:,.2f} (${stats['min']:,.2f} to ${stats['max']:,.2f})",
                f"• **Standard Deviation**: ${stats['std']:,.2f}",
                ""
            ]
            
            # Add variance analysis if available
            if variance_analysis:
                analysis_lines.extend([
                    "### 📈 **Multi-Timeframe Variance Analysis**",
                    variance_analysis,
                    ""
                ])
            
            # Add enhanced LLM commentary
            analysis_lines.extend([
                "### 🤖 **AI Analysis & Insights**",
                enhanced_commentary
            ])
            
            return "\n".join(analysis_lines)
            
        except Exception as e:
            return f"### 📊 **Enhanced Analysis**\n• Analysis completed for {direction} {n} results\n• Error in detailed analysis: {str(e)}"
    
    def _generate_enhanced_numeric_analysis(self, result_data, direction: str, n: int, 
                                          value_col: str, full_data) -> str:
        """
        Generate enhanced analysis for numeric-only data without categorical grouping, with RAG enhancement.
        
        Args:
            result_data: The top/bottom N results
            direction: 'top' or 'bottom'
            n: Number of results
            value_col: The numeric column being analyzed
            full_data: The complete dataset
            
        Returns:
            str: Enhanced analysis with insights and RAG enhancement
        """
        try:
            # Format results with more detail
            result_text = ""
            result_values = result_data[value_col].values
            
            for idx, (_, row) in enumerate(result_data.head(n).iterrows(), 1):
                # Calculate percentile rank
                percentile = (full_data[value_col] <= row[value_col]).mean() * 100
                result_text += f"• **#{idx}**: ${row[value_col]:,.2f} ({percentile:.1f}th percentile)\n"
            
            # Statistical analysis
            stats = {
                'mean': result_values.mean(),
                'median': np.median(result_values),
                'std': result_values.std() if len(result_values) > 1 else 0,
                'range': result_values.max() - result_values.min() if len(result_values) > 1 else 0
            }
            
            # Variance analysis
            variance_analysis = self._perform_numeric_variance_analysis(full_data, value_col)
            
            # Generate base LLM commentary
            base_llm_commentary = self._generate_llm_commentary_for_numeric(
                result_data, direction, n, value_col, stats, variance_analysis
            )
            
            # Enhance with RAG if available
            enhanced_commentary = base_llm_commentary
            if self.rag_manager and self.rag_analyzer and self.rag_manager.has_documents():
                try:
                    print(f"🔍 Enhancing numeric {direction} {n} analysis with RAG context...")
                    
                    values_list = [f"${val:,.2f}" for val in result_data[value_col].values]
                    
                    # Create analysis context for RAG enhancement
                    analysis_context = f"""
Numeric {direction.title()} {n} Analysis:
- Column: {value_col}
- Values: {', '.join(values_list)}
- Mean: ${stats['mean']:,.2f}
- Range: ${stats['range']:,.2f}
- Standard Deviation: ${stats['std']:,.2f}
"""
                    
                    analysis_data = {
                        'values': values_list,
                        'stats': stats,
                        'variance_analysis': variance_analysis,
                        'base_commentary': base_llm_commentary
                    }
                    
                    # Enhance with RAG
                    enhanced_result = self.rag_analyzer.enhance_top_n_analysis(
                        top_n_data=analysis_data,
                        analysis_context=analysis_context,
                        direction=direction,
                        n=n
                    )
                    
                    if enhanced_result.get('success'):
                        print(f"✅ RAG-enhanced numeric {direction} {n} analysis generated with {enhanced_result.get('documents_used', 0)} document(s)")
                        
                        # Log the prompt being used for validation
                        if 'prompt_used' in enhanced_result:
                            print("📝 PROMPT USED FOR RAG ENHANCEMENT:")
                            print("=" * 50)
                            print(enhanced_result['prompt_used'])
                            print("=" * 50)
                        
                        enhanced_commentary = f"""{base_llm_commentary}

### 🔍 **RAG-Enhanced Insights**
{enhanced_result['enhanced_analysis']}

---
**RAG Enhancement**: Analysis enhanced with {enhanced_result.get('documents_used', 0)} document(s)"""
                    else:
                        print(f"⚠️ RAG enhancement failed: {enhanced_result.get('error', 'Unknown error')}")
                        
                except Exception as e:
                    print(f"❌ RAG enhancement error: {str(e)}")
            
            analysis_lines = [
                result_text,
                "### 📊 **Statistical Analysis**",
                f"• **{direction.title()} {n} Mean**: ${stats['mean']:,.2f}",
                f"• **{direction.title()} {n} Range**: ${stats['range']:,.2f}",
                f"• **Standard Deviation**: ${stats['std']:,.2f}",
                ""
            ]
            
            if variance_analysis:
                analysis_lines.extend([
                    "### 📈 **Variance Analysis**",
                    variance_analysis,
                    ""
                ])
            
            analysis_lines.extend([
                "### 🤖 **AI Insights**",
                enhanced_commentary
            ])
            
            return "\n".join(analysis_lines)
            
        except Exception as e:
            return f"### 📊 **Analysis Results**\n{result_text}\n• Detailed analysis error: {str(e)}"
    
    def _perform_multi_timeframe_analysis(self, data, value_col: str, category_col: str) -> str:
        """
        Perform variance analysis across multiple timeframes (daily, weekly, monthly, quarterly, yearly).
        
        Args:
            data: The dataset
            value_col: The numeric column
            category_col: The categorical column
            
        Returns:
            str: Multi-timeframe variance analysis
        """
        try:
            # Look for date columns
            date_columns = self._detect_date_columns(data)
            
            if not date_columns:
                return "• No date columns detected for timeframe analysis"
            
            import pandas as pd
            date_col = date_columns[0]
            
            # Convert to datetime
            data_with_dates = data.copy()
            data_with_dates[date_col] = pd.to_datetime(data_with_dates[date_col], errors='coerce')
            
            # Remove rows with invalid dates
            data_with_dates = data_with_dates.dropna(subset=[date_col])
            
            if len(data_with_dates) == 0:
                return "• Date column could not be parsed for timeframe analysis"
            
            analysis_results = []
            
            # Determine available timeframes based on data span
            date_range = data_with_dates[date_col].max() - data_with_dates[date_col].min()
            
            if date_range.days >= 365:  # Yearly analysis
                yearly_analysis = self._analyze_timeframe(data_with_dates, date_col, value_col, category_col, 'Y')
                if yearly_analysis:
                    analysis_results.append(f"**Yearly**: {yearly_analysis}")
            
            if date_range.days >= 90:  # Quarterly analysis
                quarterly_analysis = self._analyze_timeframe(data_with_dates, date_col, value_col, category_col, 'Q')
                if quarterly_analysis:
                    analysis_results.append(f"**Quarterly**: {quarterly_analysis}")
            
            if date_range.days >= 30:  # Monthly analysis
                monthly_analysis = self._analyze_timeframe(data_with_dates, date_col, value_col, category_col, 'M')
                if monthly_analysis:
                    analysis_results.append(f"**Monthly**: {monthly_analysis}")
            
            if date_range.days >= 7:  # Weekly analysis
                weekly_analysis = self._analyze_timeframe(data_with_dates, date_col, value_col, category_col, 'W')
                if weekly_analysis:
                    analysis_results.append(f"**Weekly**: {weekly_analysis}")
            
            if date_range.days >= 1:  # Daily analysis
                daily_analysis = self._analyze_timeframe(data_with_dates, date_col, value_col, category_col, 'D')
                if daily_analysis:
                    analysis_results.append(f"**Daily**: {daily_analysis}")
            
            return "\n• ".join(analysis_results) if analysis_results else "• No significant timeframe patterns detected"
            
        except Exception as e:
            return f"• Multi-timeframe analysis error: {str(e)}"
    
    def _analyze_timeframe(self, data, date_col: str, value_col: str, category_col: str, freq: str) -> str:
        """
        Analyze variance for a specific timeframe.
        
        Args:
            data: Dataset with date column
            date_col: Date column name
            value_col: Value column name
            category_col: Category column name
            freq: Frequency code ('D', 'W', 'M', 'Q', 'Y')
            
        Returns:
            str: Timeframe-specific variance analysis
        """
        try:
            import pandas as pd
            
            # Group by timeframe
            data['period'] = data[date_col].dt.to_period(freq)
            
            # Calculate variance across periods
            period_stats = data.groupby('period')[value_col].agg(['sum', 'mean', 'std']).reset_index()
            period_stats = period_stats.dropna()
            
            if len(period_stats) < 2:
                return ""
            
            # Calculate variance metrics
            period_variance = period_stats['sum'].var()
            mean_variance = period_stats['sum'].mean()
            cv = (period_stats['sum'].std() / mean_variance) * 100 if mean_variance != 0 else 0
            
            return f"CV: {cv:.1f}%, Variance: ${period_variance:,.0f}"
            
        except Exception as e:
            return f"Analysis error: {str(e)}"
    
    def _perform_numeric_variance_analysis(self, data, value_col: str) -> str:
        """
        Perform variance analysis for numeric-only data.
        
        Args:
            data: The dataset
            value_col: The numeric column
            
        Returns:
            str: Numeric variance analysis
        """
        try:
            import numpy as np
            
            values = data[value_col].values
            
            # Basic variance metrics
            variance = np.var(values)
            std_dev = np.std(values)
            mean_val = np.mean(values)
            cv = (std_dev / mean_val) * 100 if mean_val != 0 else 0
            
            # Distribution analysis
            q1 = np.percentile(values, 25)
            q3 = np.percentile(values, 75)
            iqr = q3 - q1
            
            analysis_lines = [
                f"• **Coefficient of Variation**: {cv:.1f}%",
                f"• **Variance**: ${variance:,.0f}",
                f"• **IQR**: ${iqr:,.2f} (${q1:,.2f} to ${q3:,.2f})"
            ]
            
            # Outlier detection
            outlier_threshold = 1.5 * iqr
            outliers = len(values[(values < q1 - outlier_threshold) | (values > q3 + outlier_threshold)])
            if outliers > 0:
                analysis_lines.append(f"• **Outliers Detected**: {outliers} values ({(outliers/len(values)*100):.1f}%)")
            
            return "\n".join(analysis_lines)
            
        except Exception as e:
            return f"• Variance analysis error: {str(e)}"
    
    def _generate_llm_commentary_for_top_bottom(self, result_data, direction: str, n: int, 
                                              value_col: str, category_col: str, stats: dict, 
                                              total_sum: float, variance_analysis: str) -> str:
        """
        Generate LLM commentary for top/bottom analysis with categorical data.
        
        Args:
            result_data: Analysis results
            direction: 'top' or 'bottom'
            n: Number of results
            value_col: Value column name
            category_col: Category column name
            stats: Statistical metrics
            total_sum: Total sum of values
            variance_analysis: Variance analysis results
            
        Returns:
            str: LLM-generated commentary
        """
        try:
            if not self.app_core.is_ollama_available():
                return self._generate_fallback_commentary(result_data, direction, n, value_col, stats)
            
            # Prepare data for LLM
            top_performers = []
            for _, row in result_data.iterrows():
                percentage = (row[value_col] / total_sum) * 100 if total_sum > 0 else 0
                top_performers.append(f"{row[category_col]}: ${row[value_col]:,.2f} ({percentage:.1f}%)")
            
            prompt = f"""
You are a financial analyst reviewing {direction} {n} performance data. Provide insights and business recommendations.

DATA ANALYSIS:
- Category: {category_col}
- Metric: {value_col}
- {direction.title()} {n} performers: {'; '.join(top_performers)}

STATISTICAL SUMMARY:
- Mean of {direction} {n}: ${stats['mean']:,.2f}
- Range: ${stats['range']:,.2f}
- Standard Deviation: ${stats['std']:,.2f}

VARIANCE ANALYSIS:
{variance_analysis}

Please provide:
1. Key insights about the {direction} performers
2. Business implications of these results
3. Potential causes for the performance patterns
4. Actionable recommendations for improvement
5. Any concerning trends or outliers

Keep the response concise but insightful, focusing on practical business value.
"""
            
            return self.app_core.call_ollama(prompt)
            
        except Exception as e:
            return f"LLM commentary unavailable: {str(e)}"
    
    def _generate_llm_commentary_for_numeric(self, result_data, direction: str, n: int, 
                                           value_col: str, stats: dict, variance_analysis: str) -> str:
        """
        Generate LLM commentary for numeric-only analysis.
        
        Args:
            result_data: Analysis results
            direction: 'top' or 'bottom'
            n: Number of results
            value_col: Value column name
            stats: Statistical metrics
            variance_analysis: Variance analysis results
            
        Returns:
            str: LLM-generated commentary
        """
        try:
            if not self.app_core.is_ollama_available():
                return f"• {direction.title()} {n} values show significant variation\n• Range spans ${stats['range']:,.2f}\n• Consider investigating extreme values"
            
            values_list = [f"${val:,.2f}" for val in result_data[value_col].values]
            
            prompt = f"""
You are analyzing {direction} {n} values from a financial dataset.

DATA:
- Column: {value_col}
- {direction.title()} {n} values: {', '.join(values_list)}
- Mean: ${stats['mean']:,.2f}
- Range: ${stats['range']:,.2f}
- Standard Deviation: ${stats['std']:,.2f}

VARIANCE ANALYSIS:
{variance_analysis}

Provide concise insights about:
1. What these {direction} values indicate
2. Potential business implications
3. Whether the variation is concerning
4. Recommended next steps for analysis

Keep response under 150 words, focus on actionable insights.
"""
            
            return self.app_core.call_ollama(prompt)
            
        except Exception as e:
            return f"• {direction.title()} {n} analysis completed\n• LLM insights unavailable: {str(e)}"
    
    def _generate_fallback_commentary(self, result_data, direction: str, n: int, 
                                    value_col: str, stats: dict) -> str:
        """
        Generate fallback commentary when LLM is not available.
        
        Args:
            result_data: Analysis results
            direction: 'top' or 'bottom'
            n: Number of results
            value_col: Value column name
            stats: Statistical metrics
            
        Returns:
            str: Statistical fallback commentary
        """
        commentary_lines = [
            f"• **Performance Range**: The {direction} {n} values span ${stats['range']:,.2f}",
            f"• **Average Performance**: ${stats['mean']:,.2f} mean for {direction} performers"
        ]
        
        # Add insights based on standard deviation
        cv = (stats['std'] / stats['mean']) * 100 if stats['mean'] != 0 else 0
        
        if cv > 30:
            commentary_lines.append(f"• **High Variability**: {cv:.1f}% coefficient of variation indicates significant performance differences")
        elif cv < 10:
            commentary_lines.append(f"• **Consistent Performance**: {cv:.1f}% coefficient of variation shows relatively stable results")
        else:
            commentary_lines.append(f"• **Moderate Variability**: {cv:.1f}% coefficient of variation indicates normal performance spread")
        
        return "\n".join(commentary_lines)
