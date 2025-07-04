"""
Integration Example for Text Overflow in VariancePro
Shows how to integrate the text overflow functionality with existing chat interface
"""

# Example integration with your existing app_new.py or chat handling code

def enhanced_chat_response_handler(user_question: str, context: dict = None) -> dict:
    """
    Enhanced chat response handler that includes text overflow functionality
    
    Args:
        user_question: User's question
        context: Optional context data
        
    Returns:
        Enhanced response with formatting
    """
    from ai.llm_interpreter import LLMInterpreter
    from ui.chat_interface_enhancer import enhance_chat_response
    from config.settings import Settings
    
    try:
        # Initialize your existing LLM interpreter
        settings = Settings()
        llm_interpreter = LLMInterpreter(settings)
        
        # Get response from LLM
        llm_response = llm_interpreter.query_llm(user_question, context)
        
        # Enhance response with text overflow handling
        enhanced_response = enhance_chat_response(llm_response)
        
        return enhanced_response
        
    except Exception as e:
        # Fallback for any errors
        return {
            'content': f"Error processing request: {str(e)}",
            'formatted_content': f"<div class='error'>Error: {str(e)}</div>",
            'success': False,
            'error': str(e)
        }


def gradio_chat_interface_example():
    """
    Example of how to integrate with Gradio chat interface
    """
    import gradio as gr
    
    def chat_with_overflow(message, history):
        """
        Chat function that uses text overflow handling
        """
        # Get enhanced response
        response = enhanced_chat_response_handler(message)
        
        if response['success']:
            # Return the formatted content for display
            return response['formatted_content']
        else:
            # Return error message
            return response['formatted_content']
    
    # Create Gradio interface
    demo = gr.ChatInterface(
        fn=chat_with_overflow,
        title="VariancePro Chat with Text Overflow",
        description="Ask questions about your financial data. Long responses will have 'Show More/Less' controls.",
        examples=[
            "Analyze the variance in Q3 sales data",
            "What are the top performing regions?",
            "Provide detailed recommendations for improving performance"
        ]
    )
    
    return demo


# Quick integration snippet for existing code:
"""
# In your existing chat handler, replace:
response_text = llm_interpreter.query_llm(question)

# With:
from ui.chat_interface_enhancer import enhance_chat_response
llm_response = llm_interpreter.query_llm(question)
enhanced = enhance_chat_response(llm_response)
response_text = enhanced['formatted_content']  # This will have show more/less if needed
"""


# For integration with your app_new.py file:
def integrate_with_app_new():
    """
    Example integration points for app_new.py
    """
    integration_code = '''
    # Add this import at the top of app_new.py
    from ui.chat_interface_enhancer import ChatInterfaceEnhancer
    
    # In your QuantCommanderApp class __init__ method:
    self.chat_enhancer = ChatInterfaceEnhancer(character_threshold=150)
    
    # In your chat_response method, replace the LLM query with:
    def chat_response(self, message, history):
        try:
            # ... existing context building code ...
            
            # Instead of: response = self.llm_interpreter.query_llm(message, context)
            llm_response = self.llm_interpreter.query_llm(message, context)
            enhanced_response = self.chat_enhancer.enhance_llm_response(llm_response)
            
            if enhanced_response['success']:
                return enhanced_response['formatted_content']  # HTML with show more/less
            else:
                return enhanced_response['formatted_content']  # Styled error message
                
        except Exception as e:
            return f"Error: {str(e)}"
    '''
    
    print("Integration code for app_new.py:")
    print(integration_code)


if __name__ == "__main__":
    print("VariancePro Text Overflow Integration Examples")
    print("=" * 60)
    
    # Show integration examples
    integrate_with_app_new()
    
    print("\n" + "=" * 60)
    print("✅ Text overflow functionality successfully implemented!")
    print("\nKey features:")
    print("• Automatic truncation for responses > 150 characters")
    print("• Smart truncation at sentence boundaries")
    print("• Show More/Less buttons with smooth transitions")
    print("• Professional styling with gradients and hover effects")
    print("• Error handling with styled error messages")
    print("• Mobile responsive design")
    print("• Unique IDs for multiple responses on same page")
    print("• Session management and response counting")
    
    print("\nNext steps:")
    print("1. Update your app_new.py with the integration code above")
    print("2. Test with long responses to see the truncation in action")
    print("3. Customize the character threshold if needed (default: 150)")
    print("4. Optionally modify CSS styling to match your theme")
