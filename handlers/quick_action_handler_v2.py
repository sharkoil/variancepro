"""
Quick Action Handler for VariancePro v2.0 - Refactored

This module coordinates quick action button functionality by delegating
to specialized handlers. Following modular design principles.

Handles:
- Action routing and coordination
- Response formatting
- Chat history management

Delegates specific analysis to specialized handlers to maintain small file size.
"""

import pandas as pd
from datetime import datetime
from typing import List, Dict

from handlers.timestamp_handler import TimestampHandler
from handlers.summary_analysis_handler import SummaryAnalysisHandler
from handlers.top_bottom_analysis_handler import TopBottomAnalysisHandler
from handlers.data_utils import DataUtils


class QuickActionHandler:
    """
    Coordinates quick action button processing by delegating to specialized handlers.
    
    This class focuses on routing and coordination rather than implementing
    specific analysis logic, keeping it small and focused.
    """
    
    def __init__(self, app_core, rag_manager=None, rag_analyzer=None):
        """
        Initialize the quick action handler and its delegates.
        
        Args:
            app_core: Reference to the main application core for data access
            rag_manager: RAG Document Manager for document context (optional)
            rag_analyzer: RAG Enhanced Analyzer for enhanced analysis (optional)
        """
        self.app_core = app_core
        self.timestamp_handler = TimestampHandler()
        self.rag_manager = rag_manager
        self.rag_analyzer = rag_analyzer
        
        # Initialize specialized handlers
        self.summary_handler = SummaryAnalysisHandler(app_core, rag_manager, rag_analyzer)
        self.top_bottom_handler = TopBottomAnalysisHandler(app_core)
        
        print(f"🔧 QuickActionHandler initialized with RAG: {self.rag_manager is not None}")
    
    def handle_action(self, action: str, history: List[Dict]) -> List[Dict]:
        """
        Handle quick action button clicks by delegating to appropriate handlers.
        
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
        Route the action to the appropriate specialized handler.
        
        Args:
            action (str): The action to perform
            
        Returns:
            str: The analysis response
        """
        action_lower = action.lower()
        
        if action_lower == "summary":
            return self.summary_handler.handle_summary_analysis()
        elif action_lower == "trends":
            return self._handle_trends_action()
        elif action_lower == "variance":
            return self._handle_variance_action()
        elif "top" in action_lower or "bottom" in action_lower:
            return self.top_bottom_handler.handle_top_bottom_analysis(action)
        else:
            return f"🔍 **{action.title()} Analysis**\n\nThis feature is being implemented. You can ask questions about your data in the chat!"
    
    def _handle_trends_action(self) -> str:
        """
        Handle trends analysis - kept here as it uses timescale_analyzer from app_core.
        
        Returns:
            str: Trends analysis response with RAG context if available
        """
        if self.app_core.timescale_analyzer is None:
            return "⚠️ **Trends Analysis**: Timescale analyzer not available. Please check the system configuration."
        
        try:
            current_data, _ = self.app_core.get_current_data()
            
            # Detect date columns for trends analysis
            date_columns = DataUtils.detect_date_columns(current_data)
            
            if not date_columns:
                return "⚠️ **Trends Analysis**: No date columns detected in your data. Trends analysis requires time-based data."
            
            # Get numeric columns
            numeric_columns = DataUtils.get_numeric_columns(current_data)
            
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
                    return self._enhance_trends_with_rag(base_analysis, current_data, date_columns, numeric_columns)
                
                return base_analysis
            else:
                return f"❌ **Trends Analysis Failed**: {self.app_core.timescale_analyzer.status}"
                
        except Exception as e:
            return f"❌ **Trends Analysis Error**: {str(e)}"
    
    def _handle_variance_action(self) -> str:
        """
        Handle variance analysis - kept here as it uses variance_analyzer.
        
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
                return self._generate_variance_help_message(columns)
            
            # Perform variance analysis on the first detected pair
            first_pair = variance_pairs[0]
            
            # Get date columns for time-based analysis
            date_columns = DataUtils.detect_date_columns(current_data)
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
                enhanced_analysis = self._enhance_variance_with_rag(base_analysis, first_pair, date_col, current_data, variance_pairs)
                return f"""{enhanced_analysis}

💡 **Additional Pairs Available**: {len(variance_pairs) - 1} more variance comparison opportunities detected."""
            else:
                return f"""{base_analysis}

💡 **Additional Pairs Available**: {len(variance_pairs) - 1} more variance comparison opportunities detected."""
            
        except Exception as e:
            return f"❌ **Variance Analysis Error**: {str(e)}"
    
    def _generate_variance_help_message(self, columns: List[str]) -> str:
        """Generate help message when no variance pairs are detected."""
        return """⚠️ **Variance Analysis**: No obvious variance comparison pairs detected.

**Expected column patterns:**
• Actual vs Planned (e.g., 'Actual Sales', 'Planned Sales')
• Budget vs Actual (e.g., 'Budget', 'Actual')
• Budget vs Sales (e.g., 'Budget Revenue', 'Sales Revenue')

**Available columns**: """ + ", ".join(columns[:10]) + ("..." if len(columns) > 10 else "") + """

💡 **Tip**: Ask me specific questions like "compare actual vs planned" or manually specify columns for variance analysis."""
    
    def _enhance_trends_with_rag(self, base_analysis: str, current_data: pd.DataFrame, 
                                date_columns: List[str], numeric_columns: List[str]) -> str:
        """Enhance trends analysis with RAG context."""
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
    
    def _enhance_variance_with_rag(self, base_analysis: str, first_pair: dict, date_col: str, 
                                  current_data: pd.DataFrame, variance_pairs: List[dict]) -> str:
        """Enhance variance analysis with RAG context."""
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
                
                return f"""{base_analysis}

{enhanced_result['enhanced_analysis']}

---
🔍 **RAG Enhancement**: Analysis enhanced with {enhanced_result.get('documents_used', 0)} document(s)"""
            else:
                print(f"⚠️ RAG enhancement failed: {enhanced_result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ RAG enhancement error: {str(e)}")
        
        return base_analysis
