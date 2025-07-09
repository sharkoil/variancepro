"""
Chat Handler for Quant Commander v2.0

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
        elif "search document" in message_lower or "find in document" in message_lower:
            return self._handle_document_search(message)
        elif self.app_core.nl2sql_engine and self.app_core.is_ollama_available():
            # Use NL2SQL for complex queries
            return self._handle_nl2sql_query(message)
        else:
            return f"I understand you asked: '{message}'. I can help analyze your data! Try asking for a 'summary', use the quick action buttons, or if you have documents uploaded, your question will be enhanced with document insights automatically."
    
    def _is_top_bottom_query(self, message: str) -> bool:
        """
        Check if the message is asking for top/bottom analysis.
        
        Args:
            message (str): The user's input message
            
        Returns:
            bool: True if this is a top/bottom query, False otherwise
        """
        message_lower = message.lower().strip()
        
        # More robust pattern matching for top/bottom queries
        import re
        
        # Pattern 1: "top N" or "bottom N" where N is a number
        pattern1 = r'\b(top|bottom)\s+(\d+)\b'
        if re.search(pattern1, message_lower):
            return True
            
        # Pattern 2: "top N by column" or "bottom N by column"
        pattern2 = r'\b(top|bottom)\s+(\d+)\s+by\s+\w+'
        if re.search(pattern2, message_lower):
            return True
            
        # Pattern 3: Common phrases that indicate top/bottom analysis
        top_bottom_phrases = [
            'show me top', 'show me bottom', 'give me top', 'give me bottom',
            'what are the top', 'what are the bottom', 'find top', 'find bottom',
            'highest values', 'lowest values', 'best performing', 'worst performing',
            'largest values', 'smallest values'
        ]
        
        for phrase in top_bottom_phrases:
            if phrase in message_lower:
                return True
                
        # Pattern 4: Single words that might indicate top/bottom (be more careful)
        single_indicators = ['highest', 'lowest', 'best', 'worst', 'largest', 'smallest']
        for indicator in single_indicators:
            if f' {indicator} ' in f' {message_lower} ':  # Whole word match
                return True
                
        return False
    
    def _handle_top_bottom_query(self, message: str) -> str:
        """
        Handle top/bottom queries by delegating to QuickActionHandler.
        
        Args:
            message (str): The user's input message
            
        Returns:
            str: The analysis response
        """
        try:
            # Import QuickActionHandler to avoid circular imports
            from handlers.quick_action_handler import QuickActionHandler
            
            # Create a temporary handler instance
            quick_handler = QuickActionHandler(self.app_core)
            
            # Parse the message to create appropriate action
            message_lower = message.lower().strip()
            
            # Use regex to extract number, direction, and column if specified
            import re
            
            # Pattern for "top N by column" or "bottom N by column"
            pattern_with_column = r'\b(top|bottom)\s+(\d+)\s+by\s+(\w+)'
            match_with_column = re.search(pattern_with_column, message_lower)
            
            if match_with_column:
                direction = match_with_column.group(1)
                n = int(match_with_column.group(2))
                column = match_with_column.group(3)
                action = f"{direction} {n} by {column}"
            else:
                # Pattern for "top N" or "bottom N" without column
                pattern_simple = r'\b(top|bottom)\s+(\d+)'
                match_simple = re.search(pattern_simple, message_lower)
                
                if match_simple:
                    direction = match_simple.group(1)
                    n = int(match_simple.group(2))
                    action = f"{direction} {n}"
                else:
                    # Fallback: determine direction from keywords
                    numbers = re.findall(r'\d+', message)
                    n = int(numbers[0]) if numbers else 5
                    
                    if any(word in message_lower for word in ['top', 'highest', 'best', 'largest']):
                        action = f"top {n}"
                    else:
                        action = f"bottom {n}"
            
            print(f"[DEBUG] Parsed action: '{action}' from message: '{message}'")
            
            # Use the quick action handler's top/bottom method
            result = quick_handler._handle_top_bottom_action(action)
            
            return result
            
        except Exception as e:
            print(f"[DEBUG] Error in top/bottom query handler: {e}")
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
        return """🆘 **Quant Commander Help**

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
    
    def _handle_document_search(self, message: str) -> str:
        """
        Handle document search queries within chat.
        
        Args:
            message (str): The user's search query
            
        Returns:
            str: Search results or error message
        """
        try:
            # Extract search terms from the message
            # Remove common search prefixes to get actual search terms
            search_prefixes = ["search document for", "find in document", "search for", "find"]
            search_query = message.lower()
            
            for prefix in search_prefixes:
                if prefix in search_query:
                    search_query = search_query.replace(prefix, "").strip()
                    break
            
            if not search_query:
                return "Please specify what you'd like to search for in the documents."
            
            # Access RAG manager through app_core if available
            if hasattr(self.app_core, 'rag_manager') and self.app_core.rag_manager:
                results = self.app_core.rag_manager.retrieve_relevant_chunks(search_query, max_chunks=3)
                
                if not results:
                    return f"No relevant content found for '{search_query}' in uploaded documents."
                
                formatted_results = [f"🔍 **Document Search Results for '{search_query}':**\n"]
                
                for i, chunk in enumerate(results, 1):
                    formatted_results.append(
                        f"**Result {i}:**\n"
                        f"📄 Document: {chunk.get('document_name', 'Unknown')}\n"
                        f"📝 Content: {chunk.get('content', '')[:300]}...\n"
                    )
                
                return "\n".join(formatted_results)
            else:
                return "📚 Document search is not available. Please make sure documents are uploaded and RAG is enabled."
                
        except Exception as e:
            return f"❌ Error searching documents: {str(e)}"
