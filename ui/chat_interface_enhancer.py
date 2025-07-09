"""
Chat Interface Enhancer for Quant Commander
Integrates text overflow handling with existing chat functionality
"""

from typing import Dict, Any, Optional
from ai.llm_interpreter import LLMResponse
from ui.text_overflow_handler import ChatResponseFormatter


class ChatInterfaceEnhancer:
    """
    Enhances chat interface with advanced text handling capabilities
    Integrates with existing LLM interpreter to provide better user experience
    """
    
    def __init__(self, character_threshold: int = 150):
        """
        Initialize chat interface enhancer
        
        Args:
            character_threshold: Character limit before text truncation
        """
        self.response_formatter = ChatResponseFormatter(character_threshold)
        self.session_active = False
    
    def enhance_llm_response(self, llm_response: LLMResponse) -> Dict[str, Any]:
        """
        Enhance LLM response with text overflow handling and improved formatting
        
        Args:
            llm_response: Response from LLM interpreter
            
        Returns:
            Enhanced response dictionary with formatted content
        """
        if not llm_response.success:
            # For error responses, return as-is with basic formatting
            return {
                'content': llm_response.content,
                'formatted_content': self._format_error_response(llm_response),
                'success': False,
                'error': llm_response.error,
                'metadata': llm_response.metadata
            }
        
        # Process successful response with text overflow handling
        formatted_content = self.response_formatter.format_chat_response(
            llm_response.content
        )
        
        return {
            'content': llm_response.content,  # Original content
            'formatted_content': formatted_content,  # HTML formatted with overflow handling
            'success': True,
            'metadata': {
                **(llm_response.metadata or {}),
                'formatted': True,
                'truncated': len(llm_response.content) > 150,
                'character_count': len(llm_response.content)
            },
            'processing_time': llm_response.processing_time
        }
    
    def _format_error_response(self, llm_response: LLMResponse) -> str:
        """
        Format error responses with appropriate styling
        
        Args:
            llm_response: Failed LLM response
            
        Returns:
            Formatted HTML for error display
        """
        error_message = llm_response.error or "An unknown error occurred"
        
        return f"""
        <div class="error-response">
            <div class="error-icon">⚠️</div>
            <div class="error-content">
                <h4>Analysis Unavailable</h4>
                <p>{error_message}</p>
                <div class="error-suggestions">
                    <strong>Suggestions:</strong>
                    <ul>
                        <li>Check if the LLM service is running</li>
                        <li>Verify your query is clear and specific</li>
                        <li>Try simplifying your request</li>
                    </ul>
                </div>
            </div>
        </div>
        
        <style>
        .error-response {{
            display: flex;
            align-items: flex-start;
            background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
            border: 1px solid #f87171;
            border-radius: 8px;
            padding: 16px;
            margin: 10px 0;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }}
        
        .error-icon {{
            font-size: 24px;
            margin-right: 12px;
            margin-top: 2px;
        }}
        
        .error-content h4 {{
            color: #dc2626;
            margin: 0 0 8px 0;
            font-size: 16px;
            font-weight: 600;
        }}
        
        .error-content p {{
            color: #7f1d1d;
            margin: 0 0 12px 0;
            line-height: 1.5;
        }}
        
        .error-suggestions {{
            color: #7f1d1d;
            font-size: 14px;
        }}
        
        .error-suggestions ul {{
            margin: 8px 0 0 0;
            padding-left: 20px;
        }}
        
        .error-suggestions li {{
            margin: 4px 0;
        }}
        </style>
        """
    
    def start_new_session(self) -> None:
        """
        Start a new chat session
        Resets response counter for clean ID generation
        """
        self.response_formatter.reset_counter()
        self.session_active = True
    
    def end_session(self) -> None:
        """End current chat session"""
        self.session_active = False
    
    def get_session_status(self) -> Dict[str, Any]:
        """
        Get current session status
        
        Returns:
            Session status information
        """
        return {
            'active': self.session_active,
            'response_count': self.response_formatter.response_counter,
            'character_threshold': self.response_formatter.overflow_handler.character_threshold
        }


# Integration helper function for easy use in existing code
def enhance_chat_response(llm_response: LLMResponse, 
                         character_threshold: int = 150) -> Dict[str, Any]:
    """
    Convenience function to enhance a single LLM response
    
    Args:
        llm_response: Response from LLM interpreter
        character_threshold: Character limit for truncation
        
    Returns:
        Enhanced response with formatting
    """
    enhancer = ChatInterfaceEnhancer(character_threshold)
    return enhancer.enhance_llm_response(llm_response)
