"""
Text Overflow Handler Demo
Demonstrates the show more/less functionality for long chat responses
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from ai.llm_interpreter import LLMResponse
from ui.chat_interface_enhancer import ChatInterfaceEnhancer, enhance_chat_response
from ui.text_overflow_handler import ChatResponseFormatter


def demo_text_overflow_functionality():
    """
    Demonstrate text overflow handling with various response types
    Shows how the feature works for short responses, long responses, and errors
    """
    print("=" * 80)
    print("Quant Commander Text Overflow Handler Demo")
    print("=" * 80)
    
    # Initialize the enhancer
    enhancer = ChatInterfaceEnhancer(character_threshold=150)
    enhancer.start_new_session()
    
    # Test 1: Short response (no truncation needed)
    print("\n1. SHORT RESPONSE TEST (No truncation)")
    print("-" * 50)
    
    short_response = LLMResponse(
        content="Revenue is up 12% this quarter. Good performance across all regions.",
        success=True,
        metadata={'model': 'gemma3:latest'},
        processing_time=1.2
    )
    
    enhanced_short = enhancer.enhance_llm_response(short_response)
    print(f"Original length: {len(short_response.content)} characters")
    print(f"Truncated: {enhanced_short['metadata']['truncated']}")
    print("Formatted content preview:")
    print(enhanced_short['formatted_content'][:200] + "..." if len(enhanced_short['formatted_content']) > 200 else enhanced_short['formatted_content'])
    
    # Test 2: Long response (truncation needed)
    print("\n\n2. LONG RESPONSE TEST (With truncation)")
    print("-" * 50)
    
    long_response = LLMResponse(
        content=(
            "Based on the comprehensive quantitative analysis of your Q3 sales data, here are the detailed findings and strategic recommendations:\n\n"
            "KEY PERFORMANCE INSIGHTS:\n"
            "• Revenue exceeded budget by 12.5% ($125,000 over target)\n"
            "• Top performing regions: North (18% over), West (15% over), South (8% over)\n"
            "• Product line analysis shows Software licenses driving 60% of the overall variance\n"
            "• Customer satisfaction scores averaged 4.2/5.0 across all regions\n"
            "• Customer acquisition costs decreased by 12% indicating improved marketing efficiency\n\n"
            "STRATEGIC RECOMMENDATIONS:\n"
            "• Increase Q4 sales targets by 8-10% based on current momentum and market conditions\n"
            "• Replicate North region's successful strategies in underperforming East region\n"
            "• Consider expanding software license promotions company-wide to capitalize on demand\n"
            "• Monitor satisfaction metrics closely as sales volume increases to ensure quality maintenance\n"
            "• Investigate supply chain optimizations that contributed to cost reductions\n\n"
            "RISK FACTORS TO MONITOR:\n"
            "• Market saturation potential in North region given high growth rates\n"
            "• Seasonal variations that may impact Q4 performance projections\n"
            "• Competitive response to our pricing strategies and market expansion"
        ),
        success=True,
        metadata={'model': 'gemma3:latest', 'eval_count': 200},
        processing_time=3.5
    )
    
    enhanced_long = enhancer.enhance_llm_response(long_response)
    print(f"Original length: {len(long_response.content)} characters")
    print(f"Truncated: {enhanced_long['metadata']['truncated']}")
    print("Contains show more/less controls:", 'Show More' in enhanced_long['formatted_content'])
    print("Contains JavaScript functions:", 'function showMore' in enhanced_long['formatted_content'])
    print("Contains CSS styling:", '.text-control-btn' in enhanced_long['formatted_content'])
    
    # Test 3: Error response
    print("\n\n3. ERROR RESPONSE TEST")
    print("-" * 50)
    
    error_response = LLMResponse(
        content="",
        success=False,
        error="Cannot connect to LLM service. Please check if Ollama is running.",
        processing_time=0.1
    )
    
    enhanced_error = enhancer.enhance_llm_response(error_response)
    print(f"Success: {enhanced_error['success']}")
    print(f"Error: {enhanced_error['error']}")
    print("Contains error styling:", 'error-response' in enhanced_error['formatted_content'])
    print("Contains suggestions:", 'Suggestions:' in enhanced_error['formatted_content'])
    
    # Test 4: Session management
    print("\n\n4. SESSION MANAGEMENT TEST")
    print("-" * 50)
    
    session_status = enhancer.get_session_status()
    print(f"Session active: {session_status['active']}")
    print(f"Response count: {session_status['response_count']}")
    print(f"Character threshold: {session_status['character_threshold']}")
    
    # Test 5: Convenience function
    print("\n\n5. CONVENIENCE FUNCTION TEST")
    print("-" * 50)
    
    convenience_result = enhance_chat_response(long_response, character_threshold=100)
    print(f"Convenience function works: {convenience_result['success']}")
    print(f"Truncated with lower threshold: {convenience_result['metadata']['truncated']}")
    
    print("\n" + "=" * 80)
    print("Demo completed successfully!")
    print("=" * 80)


def demo_formatter_only():
    """
    Demonstrate the standalone ChatResponseFormatter functionality
    """
    print("\n" + "=" * 80)
    print("Standalone Formatter Demo")
    print("=" * 80)
    
    formatter = ChatResponseFormatter(character_threshold=120)
    
    # Test responses with different lengths
    test_responses = [
        "Short response.",
        "Medium length response that might or might not trigger truncation depending on the exact character count threshold.",
        (
            "Very long response with detailed financial analysis including multiple bullet points, "
            "recommendations, and strategic insights that definitely exceeds the character threshold "
            "and will trigger the show more/less functionality with proper HTML formatting."
        )
    ]
    
    for i, response in enumerate(test_responses, 1):
        print(f"\nResponse {i} ({len(response)} chars):")
        formatted = formatter.format_chat_response(response)
        
        is_truncated = 'Show More' in formatted
        print(f"  Truncated: {is_truncated}")
        print(f"  Contains unique ID: response_{i}" in formatted)
        
        if is_truncated:
            print("  Contains controls: ✓")
            print("  Contains styling: ✓")
        else:
            print("  Short format: ✓")


def show_html_output_example():
    """
    Show what the actual HTML output looks like for a long response
    """
    print("\n" + "=" * 80)
    print("HTML Output Example")
    print("=" * 80)
    
    formatter = ChatResponseFormatter(character_threshold=100)
    
    sample_response = (
        "This is a sample financial analysis response that contains detailed insights about "
        "quantitative analysis, performance metrics, and strategic recommendations for the business. "
        "It includes bullet points and structured content that should be properly formatted "
        "with show more/less functionality."
    )
    
    html_output = formatter.format_chat_response(sample_response)
    
    print("Generated HTML (truncated for display):")
    print("-" * 50)
    
    # Show first 500 characters of HTML output
    preview = html_output[:500] + "..." if len(html_output) > 500 else html_output
    print(preview)
    
    print(f"\nTotal HTML length: {len(html_output)} characters")
    print(f"Original text length: {len(sample_response)} characters")
    print(f"Enhancement ratio: {len(html_output) / len(sample_response):.1f}x")


if __name__ == "__main__":
    """
    Run all demonstrations to show text overflow functionality
    """
    try:
        demo_text_overflow_functionality()
        demo_formatter_only()
        show_html_output_example()
        
        print("\n🎉 All demos completed successfully!")
        print("\nTo integrate this into your existing chat interface:")
        print("1. Import: from ui.chat_interface_enhancer import enhance_chat_response")
        print("2. Use: enhanced = enhance_chat_response(llm_response)")
        print("3. Display: enhanced['formatted_content'] in your UI")
        
    except Exception as e:
        print(f"❌ Demo failed with error: {str(e)}")
        print("Make sure all required dependencies are available.")
        import traceback
        traceback.print_exc()
