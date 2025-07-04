"""
Text Overflow Handler for VariancePro Chat Interface
Implements show more/less functionality for long responses
"""

from typing import Tuple, Optional
import re


class TextOverflowHandler:
    """
    Handles text truncation and expansion for chat responses
    Provides show more/less functionality for responses longer than specified threshold
    """
    
    def __init__(self, character_threshold: int = 150):
        """
        Initialize text overflow handler
        
        Args:
            character_threshold: Maximum characters before truncation (default: 150)
        """
        self.character_threshold = character_threshold
        self.show_more_text = "Show More..."
        self.show_less_text = "Show Less"
    
    def process_response_for_display(self, response_text: str, response_id: str) -> str:
        """
        Process response text and add show more/less functionality if needed
        
        Args:
            response_text: The full response text from LLM
            response_id: Unique identifier for this response
            
        Returns:
            HTML string with truncation and show more/less controls
        """
        # Clean and prepare the response text
        cleaned_text = self._clean_response_text(response_text)
        
        # Check if truncation is needed
        if len(cleaned_text) <= self.character_threshold:
            return self._format_short_response(cleaned_text)
        
        # Create truncated version with show more/less functionality
        return self._create_expandable_response(cleaned_text, response_id)
    
    def _clean_response_text(self, text: str) -> str:
        """
        Clean and format response text for display
        
        Args:
            text: Raw response text
            
        Returns:
            Cleaned text ready for display
        """
        # Remove excessive whitespace while preserving paragraph structure
        cleaned = re.sub(r'\n\s*\n\s*\n+', '\n\n', text.strip())
        
        # Ensure bullet points are properly formatted
        cleaned = re.sub(r'^\s*[•\-\*]\s*', '• ', cleaned, flags=re.MULTILINE)
        
        # Ensure numbered lists are properly formatted
        cleaned = re.sub(r'^\s*(\d+)\.\s*', r'\1. ', cleaned, flags=re.MULTILINE)
        
        return cleaned
    
    def _format_short_response(self, text: str) -> str:
        """
        Format short response that doesn't need truncation
        
        Args:
            text: Response text
            
        Returns:
            Formatted HTML for short response
        """
        # Convert newlines to HTML breaks and preserve formatting
        formatted_text = text.replace('\n', '<br>')
        
        return f"""
        <div class="response-text short-response">
            {formatted_text}
        </div>
        """
    
    def _create_expandable_response(self, full_text: str, response_id: str) -> str:
        """
        Create expandable response with show more/less functionality
        
        Args:
            full_text: Complete response text
            response_id: Unique identifier for this response
            
        Returns:
            HTML string with expandable functionality
        """
        # Find good truncation point (preferably at sentence or paragraph end)
        truncation_point = self._find_optimal_truncation_point(full_text)
        
        # Split text into preview and full content
        preview_text = full_text[:truncation_point].strip()
        
        # Convert to HTML format
        preview_html = preview_text.replace('\n', '<br>')
        full_html = full_text.replace('\n', '<br>')
        
        # Generate unique IDs for this response
        preview_id = f"preview_{response_id}"
        full_id = f"full_{response_id}"
        show_more_id = f"show_more_{response_id}"
        show_less_id = f"show_less_{response_id}"
        
        return f"""
        <div class="response-text expandable-response">
            <div id="{preview_id}" class="text-preview">
                {preview_html}
                <span class="truncation-indicator">...</span>
            </div>
            
            <div id="{full_id}" class="text-full" style="display: none;">
                {full_html}
            </div>
            
            <div class="text-controls">
                <button id="{show_more_id}" class="text-control-btn show-more-btn" 
                        onclick="showMore('{preview_id}', '{full_id}', '{show_more_id}', '{show_less_id}')">
                    {self.show_more_text}
                </button>
                
                <button id="{show_less_id}" class="text-control-btn show-less-btn" 
                        onclick="showLess('{preview_id}', '{full_id}', '{show_more_id}', '{show_less_id}')" 
                        style="display: none;">
                    {self.show_less_text}
                </button>
            </div>
        </div>
        
        {self._get_javascript_functions()}
        {self._get_css_styles()}
        """
    
    def _find_optimal_truncation_point(self, text: str) -> int:
        """
        Find the best point to truncate text for readability
        
        Args:
            text: Full text to truncate
            
        Returns:
            Character position for optimal truncation
        """
        # Start with the threshold as base point
        base_point = self.character_threshold
        
        # Look for sentence endings near the threshold
        sentence_endings = ['. ', '! ', '? ']
        best_point = base_point
        
        # Search within 50 characters before and after threshold for sentence end
        search_start = max(0, base_point - 50)
        search_end = min(len(text), base_point + 50)
        search_text = text[search_start:search_end]
        
        for ending in sentence_endings:
            pos = search_text.rfind(ending)
            if pos != -1:
                absolute_pos = search_start + pos + len(ending)
                if search_start <= absolute_pos <= search_end:
                    best_point = absolute_pos
                    break
        
        # If no sentence ending found, look for paragraph breaks
        if best_point == base_point:
            paragraph_break = text.rfind('\n\n', search_start, search_end)
            if paragraph_break != -1:
                best_point = paragraph_break + 2
        
        # If still no good point, look for any line break
        if best_point == base_point:
            line_break = text.rfind('\n', search_start, search_end)
            if line_break != -1:
                best_point = line_break + 1
        
        # Ensure we don't exceed text length
        return min(best_point, len(text))
    
    def _get_javascript_functions(self) -> str:
        """
        Get JavaScript functions for show more/less functionality
        
        Returns:
            JavaScript code as string
        """
        return """
        <script>
        function showMore(previewId, fullId, showMoreId, showLessId) {
            // Hide preview and show more button
            document.getElementById(previewId).style.display = 'none';
            document.getElementById(showMoreId).style.display = 'none';
            
            // Show full text and show less button
            document.getElementById(fullId).style.display = 'block';
            document.getElementById(showLessId).style.display = 'inline-block';
        }
        
        function showLess(previewId, fullId, showMoreId, showLessId) {
            // Hide full text and show less button
            document.getElementById(fullId).style.display = 'none';
            document.getElementById(showLessId).style.display = 'none';
            
            // Show preview and show more button
            document.getElementById(previewId).style.display = 'block';
            document.getElementById(showMoreId).style.display = 'inline-block';
        }
        </script>
        """
    
    def _get_css_styles(self) -> str:
        """
        Get CSS styles for text overflow functionality
        
        Returns:
            CSS styles as string
        """
        return """
        <style>
        .response-text {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            margin: 10px 0;
        }
        
        .expandable-response {
            position: relative;
        }
        
        .text-preview, .text-full {
            margin-bottom: 8px;
        }
        
        .truncation-indicator {
            color: #666;
            font-style: italic;
            margin-left: 4px;
        }
        
        .text-controls {
            margin-top: 8px;
        }
        
        .text-control-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 6px 12px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 12px;
            font-weight: 500;
            transition: all 0.3s ease;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .text-control-btn:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
            background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
        }
        
        .text-control-btn:active {
            transform: translateY(0);
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .show-more-btn::after {
            content: " ▼";
            font-size: 10px;
            margin-left: 4px;
        }
        
        .show-less-btn::after {
            content: " ▲";
            font-size: 10px;
            margin-left: 4px;
        }
        
        /* Mobile responsiveness */
        @media (max-width: 768px) {
            .text-control-btn {
                padding: 8px 16px;
                font-size: 14px;
            }
        }
        </style>
        """


class ChatResponseFormatter:
    """
    Main formatter for chat responses that integrates text overflow handling
    """
    
    def __init__(self, character_threshold: int = 150):
        """
        Initialize chat response formatter
        
        Args:
            character_threshold: Character limit before showing truncation
        """
        self.overflow_handler = TextOverflowHandler(character_threshold)
        self.response_counter = 0  # For generating unique IDs
    
    def format_chat_response(self, response_content: str) -> str:
        """
        Format response for display in chat interface
        
        Args:
            response_content: Raw response content from LLM
            
        Returns:
            Formatted HTML for chat display
        """
        # Generate unique response ID
        self.response_counter += 1
        response_id = f"response_{self.response_counter}"
        
        # Process response with overflow handling
        formatted_response = self.overflow_handler.process_response_for_display(
            response_content, 
            response_id
        )
        
        return formatted_response
    
    def reset_counter(self) -> None:
        """Reset the response counter (useful for new chat sessions)"""
        self.response_counter = 0
