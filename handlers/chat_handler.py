"""
Chat Handler for VariancePro v2.0

This module handles all chat message processing including:
- User message validation and processing
- Natural language query routing
- Response generation and formatting
- Top/Bottom query handling
- NL2SQL integration

Extracted from app_v2.py to follow modular design principles.
"""

import re
from datetime import datetime
from typing import List, Dict, Tuple, Optional, Any

from handlers.timestamp_handler import TimestampHandler


class ChatHandler:
    """
    Handles chat message processing and response generation.
    
    This class encapsulates all chat-related functionality to keep
    the main application code clean and focused.
    """
    
    def __init__(self, app_core):
        """
        Initialize the chat handler.
        
        Args:
            app_core: Reference to the main application core for data access
        """
        self.app_core = app_core
        self.timestamp_handler = TimestampHandler()
    
    def process_message(self, message: str, history: List[Dict]) -> Tuple[List[Dict], str]:
        """
        Process a chat message and generate a response.
        
        Args:
            message (str): The user's input message
            history (List[Dict]): The chat history
            
        Returns:
            Tuple[List[Dict], str]: Updated history and empty string for input clearing
        """
        if not message.strip():
            return history, ""
        
        # Generate timestamp for browser local time
        current_timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Add user message with timestamp
        user_message = {
            "role": "user", 
            "content": self.timestamp_handler.add_timestamp_to_message(message, current_timestamp)
        }
        history.append(user_message)
        
        # Process the message and generate response
        response = self._generate_response(message)
        
        # Add assistant response with timestamp
        assistant_message = {
            "role": "assistant", 
            "content": self.timestamp_handler.add_timestamp_to_message(response, current_timestamp)
        }
        history.append(assistant_message)
        
        return history, ""
    
    def _generate_response(self, message: str) -> str:
        """
        Generate a response based on the user message.
        
        Args:
            message (str): The user's input message
            
        Returns:
            str: The generated response
        """
        # Check if data is loaded
        if not self.app_core.has_data():
            return "Please upload a CSV file first to start analyzing your data."
        
        # Route the message to appropriate handler
        message_lower = message.lower()
        
        if self._is_top_bottom_query(message):
            return self._handle_top_bottom_query(message)
        elif "summary" in message_lower:
            return self._generate_summary_response()
        elif "help" in message_lower:
            return self._generate_help_response()
        elif self.app_core.nl2sql_engine and self.app_core.is_ollama_available():
            # Use NL2SQL for complex queries
            return self._handle_nl2sql_query(message)
        else:
            return f"I understand you asked: '{message}'. I can help analyze your data! Try asking for a 'summary' or use the quick action buttons."
    
    def _is_top_bottom_query(self, message: str) -> bool:
        """
        Check if the message is asking for top/bottom analysis.
        
        Args:
            message (str): The user's input message
            
        Returns:
            bool: True if this is a top/bottom query, False otherwise
        """
        message_lower = message.lower()
        top_bottom_indicators = [
            'top 5', 'top 10', 'bottom 5', 'bottom 10',
            'highest', 'lowest', 'best', 'worst', 'largest', 'smallest'
        ]
        return any(indicator in message_lower for indicator in top_bottom_indicators)
    
    def _handle_top_bottom_query(self, message: str) -> str:
        """
        Handle top/bottom queries using base analyzer.
        
        Args:
            message (str): The user's input message
            
        Returns:
            str: The analysis response
        """
        try:
            from analyzers.base_analyzer import BaseAnalyzer
            
            # Create a temporary base analyzer instance
            base_analyzer = BaseAnalyzer()
            
            # Parse the query to extract N and direction
            message_lower = message.lower()
            
            # Determine direction and N
            if any(word in message_lower for word in ['top', 'highest', 'best', 'largest']):
                direction = 'top'
            else:
                direction = 'bottom'
            
            # Extract number
            numbers = re.findall(r'\d+', message)
            n = int(numbers[0]) if numbers else 5
            
            # Get current data
            current_data, _ = self.app_core.get_current_data()
            
            # Get numeric columns for analysis
            numeric_columns = current_data.select_dtypes(include=['number']).columns.tolist()
            
            if not numeric_columns:
                return "⚠️ **Top/Bottom Analysis**: No numeric columns found in your data."
            
            # Use the first numeric column
            value_col = numeric_columns[0]
            
            # Perform analysis
            if direction == 'top':
                result = base_analyzer.perform_top_n_analysis(
                    data=current_data,
                    value_column=value_col,
                    n=n
                )
            else:
                result = base_analyzer.perform_bottom_n_analysis(
                    data=current_data,
                    value_column=value_col,
                    n=n
                )
            
            return f"🔍 **{direction.title()} {n} Analysis**\n\n{result}"
            
        except Exception as e:
            return f"❌ **Top/Bottom Analysis Error**: {str(e)}"
    
    def _generate_summary_response(self) -> str:
        """
        Generate a summary response for the current data.
        
        Returns:
            str: Summary response
        """
        current_data, data_summary = self.app_core.get_current_data()
        
        if data_summary:
            return f"📊 **Data Summary**\n\n{data_summary}"
        else:
            # Generate basic summary if no cached summary
            row_count = len(current_data)
            col_count = len(current_data.columns)
            columns = ', '.join(current_data.columns[:5])
            if len(current_data.columns) > 5:
                columns += "..."
            
            return f"""📊 **Data Summary**

**Overview**: {row_count:,} rows × {col_count} columns

**Columns**: {columns}

💡 **Tip**: Ask me specific questions about your data or use the quick analysis buttons!"""
    
    def _generate_help_response(self) -> str:
        """
        Generate a help response with available commands.
        
        Returns:
            str: Help response
        """
        return """🆘 **VariancePro Help**

**What I can do:**
• 📊 **Data Summary** - Get overview of your dataset
• 📈 **Trend Analysis** - Analyze time-series patterns
• 🔝 **Top/Bottom Analysis** - Find highest/lowest values
• 💬 **Natural Language Queries** - Ask me questions about your data

**Example questions:**
• "Show me the top 10 sales"
• "What are the trends in revenue?"
• "Summarize the data"
• "Compare actual vs planned values"

**Quick Actions:** Use the buttons below the chat for instant analysis!

💡 **Variance Analysis**: I can compare "actual vs planned", "budget vs sales", and similar metrics across different time periods."""
    
    def _handle_nl2sql_query(self, message: str) -> str:
        """
        Handle complex queries using NL2SQL engine.
        
        Args:
            message (str): The user's input message
            
        Returns:
            str: The analysis response
        """
        try:
            current_data, _ = self.app_core.get_current_data()
            
            # Use the NL2SQL engine to process the query
            result = self.app_core.nl2sql_engine.process_query(
                query=message,
                data=current_data
            )
            
            return f"🔍 **Analysis Results**\n\n{result}"
            
        except Exception as e:
            return f"❌ **Query Processing Error**: {str(e)}"
