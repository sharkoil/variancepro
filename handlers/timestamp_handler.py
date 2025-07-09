"""
Timestamp Handler for Quant Commander v2.0

This module provides timestamp functionality for chat messages.
It formats timestamps consistently across all message types and
provides browser-local-time formatting.

Extracted from app_v2.py to follow modular design principles.
"""

from datetime import datetime
from typing import Dict, Any


class TimestampHandler:
    """
    Handles timestamp formatting and application for chat messages.
    
    This class provides consistent timestamp formatting across the application,
    ensuring all messages have proper temporal context for users.
    """
    
    def __init__(self, format_string: str = "%H:%M:%S"):
        """
        Initialize the timestamp handler.
        
        Args:
            format_string (str): The format string for timestamp display (default: HH:MM:SS)
        """
        self.format_string = format_string
    
    def get_current_timestamp(self) -> str:
        """
        Get the current timestamp formatted for display.
        
        Returns:
            str: Current timestamp in the configured format (e.g., "14:30:25")
        """
        return datetime.now().strftime(self.format_string)
    
    def add_timestamp_to_message(self, message: str, timestamp: str = None) -> str:
        """
        Add a timestamp to a chat message in a subtle, professional format.
        
        The timestamp is added as a styled HTML span element that appears
        before the message content with subtle gray styling.
        
        Args:
            message (str): The original message content
            timestamp (str, optional): Custom timestamp. If None, uses current time
            
        Returns:
            str: Message with timestamp prefix in format: "[HH:MM:SS] message content"
        """
        # Use provided timestamp or generate current one
        if timestamp is None:
            timestamp = self.get_current_timestamp()
        
        # Create styled timestamp prefix with subtle appearance
        timestamp_prefix = (
            f"<span style='color: #888; font-size: 0.85em; opacity: 0.7;'>"
            f"[{timestamp}]"
            f"</span> "
        )
        
        return timestamp_prefix + message
    
    def add_timestamp_to_chat_message(self, role: str, content: str, timestamp: str = None) -> Dict[str, str]:
        """
        Create a timestamped chat message dictionary.
        
        This is a convenience method that creates the standard chat message
        format used throughout the application with timestamp included.
        
        Args:
            role (str): The role of the message sender ("user" or "assistant")
            content (str): The message content
            timestamp (str, optional): Custom timestamp. If None, uses current time
            
        Returns:
            Dict[str, str]: Chat message dictionary with timestamped content
                Format: {"role": role, "content": "[timestamp] content"}
        """
        timestamped_content = self.add_timestamp_to_message(content, timestamp)
        
        return {
            "role": role,
            "content": timestamped_content
        }
    
    def extract_timestamp_from_message(self, message: str) -> tuple[str, str]:
        """
        Extract timestamp from a timestamped message.
        
        This method can parse messages that were previously timestamped
        to separate the timestamp from the actual content.
        
        Args:
            message (str): A timestamped message string
            
        Returns:
            tuple[str, str]: (timestamp, original_message) or (None, message) if no timestamp found
        """
        # Look for timestamp pattern in HTML span
        import re
        
        pattern = r'<span[^>]*>\[([^\]]+)\]</span>\s*(.*)'
        match = re.match(pattern, message)
        
        if match:
            timestamp = match.group(1)
            original_message = match.group(2)
            return timestamp, original_message
        else:
            # No timestamp found, return original message
            return None, message
    
    def update_format(self, new_format: str) -> None:
        """
        Update the timestamp format string.
        
        This allows dynamic changing of timestamp format if needed.
        
        Args:
            new_format (str): New format string (e.g., "%Y-%m-%d %H:%M:%S" for date and time)
        """
        self.format_string = new_format
