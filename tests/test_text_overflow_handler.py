"""
Unit tests for Text Overflow Handler
Tests text truncation and show more/less functionality
"""

import unittest
from ui.text_overflow_handler import TextOverflowHandler, ChatResponseFormatter


class TestTextOverflowHandler(unittest.TestCase):
    """Test cases for TextOverflowHandler class"""
    
    def setUp(self) -> None:
        """Set up test fixtures"""
        self.handler = TextOverflowHandler(character_threshold=100)
        self.short_text = "This is a short response that should not be truncated."
        self.long_text = (
            "This is a very long response that definitely exceeds the character threshold "
            "and should be truncated with show more/less functionality. "
            "It contains multiple sentences and should demonstrate the text overflow feature "
            "working correctly with proper HTML formatting and JavaScript controls."
        )
    
    def test_short_response_no_truncation(self) -> None:
        """Test that short responses are not truncated"""
        result = self.handler.process_response_for_display(self.short_text, "test_1")
        
        # Should contain the full text
        self.assertIn(self.short_text, result)
        
        # Should not contain show more/less controls
        self.assertNotIn("Show More", result)
        self.assertNotIn("show-more-btn", result)
    
    def test_long_response_gets_truncated(self) -> None:
        """Test that long responses get truncation controls"""
        result = self.handler.process_response_for_display(self.long_text, "test_2")
        
        # Should contain show more/less controls
        self.assertIn("Show More", result)
        self.assertIn("show-more-btn", result)
        self.assertIn("show-less-btn", result)
        
        # Should contain JavaScript functions
        self.assertIn("function showMore", result)
        self.assertIn("function showLess", result)
    
    def test_optimal_truncation_point_at_sentence_end(self) -> None:
        """Test that truncation occurs at optimal points (sentence endings)"""
        text_with_sentences = (
            "First sentence is here. Second sentence continues the thought. "
            "Third sentence should be in the expanded section after truncation point."
        )
        
        truncation_point = self.handler._find_optimal_truncation_point(text_with_sentences)
        
        # Should truncate at a sentence boundary
        truncated_text = text_with_sentences[:truncation_point]
        self.assertTrue(
            truncated_text.endswith('. ') or truncated_text.endswith('! ') or truncated_text.endswith('? ')
        )
    
    def test_clean_response_text_formatting(self) -> None:
        """Test that response text is properly cleaned and formatted"""
        messy_text = """
        
        
        • First bullet point
        - Second bullet point
        * Third bullet point
        
        1.   First numbered item
        2.    Second numbered item
        
        
        """
        
        cleaned = self.handler._clean_response_text(messy_text)
        
        # Should have consistent bullet formatting
        self.assertIn("• First bullet point", cleaned)
        self.assertIn("• Second bullet point", cleaned)
        self.assertIn("• Third bullet point", cleaned)
        
        # Should have consistent numbering
        self.assertIn("1. First numbered item", cleaned)
        self.assertIn("2. Second numbered item", cleaned)
        
        # Should not have excessive whitespace
        self.assertNotIn("\n\n\n", cleaned)
    
    def test_unique_response_ids_generated(self) -> None:
        """Test that unique IDs are generated for each response"""
        result1 = self.handler.process_response_for_display(self.long_text, "test_1")
        result2 = self.handler.process_response_for_display(self.long_text, "test_2")
        
        # Should contain different IDs
        self.assertIn("preview_test_1", result1)
        self.assertIn("preview_test_2", result2)
        
        # IDs should not overlap
        self.assertNotIn("preview_test_2", result1)
        self.assertNotIn("preview_test_1", result2)


class TestChatResponseFormatter(unittest.TestCase):
    """Test cases for ChatResponseFormatter class"""
    
    def setUp(self) -> None:
        """Set up test fixtures"""
        self.formatter = ChatResponseFormatter(character_threshold=150)
    
    def test_format_chat_response_increments_counter(self) -> None:
        """Test that response counter increments for unique IDs"""
        response1 = self.formatter.format_chat_response("Test response 1")
        response2 = self.formatter.format_chat_response("Test response 2")
        
        # Should have different response IDs
        self.assertIn("response_1", response1)
        self.assertIn("response_2", response2)
    
    def test_reset_counter_functionality(self) -> None:
        """Test that counter reset works correctly"""
        # Generate some responses
        self.formatter.format_chat_response("Test 1")
        self.formatter.format_chat_response("Test 2")
        
        # Reset counter
        self.formatter.reset_counter()
        
        # Next response should start from 1 again
        response = self.formatter.format_chat_response("Test after reset")
        self.assertIn("response_1", response)
    
    def test_css_and_javascript_included(self) -> None:
        """Test that CSS and JavaScript are included in long responses"""
        long_response = "A" * 200  # Long enough to trigger truncation
        
        result = self.formatter.format_chat_response(long_response)
        
        # Should include CSS
        self.assertIn("<style>", result)
        self.assertIn(".response-text", result)
        self.assertIn(".text-control-btn", result)
        
        # Should include JavaScript
        self.assertIn("<script>", result)
        self.assertIn("function showMore", result)


class TestTextOverflowHandlerEdgeCases(unittest.TestCase):
    """Test edge cases for TextOverflowHandler"""
    
    def setUp(self) -> None:
        """Set up test fixtures"""
        self.handler = TextOverflowHandler(character_threshold=50)
    
    def test_empty_string_handling(self) -> None:
        """Test handling of empty strings"""
        result = self.handler.process_response_for_display("", "empty_test")
        
        # Should handle gracefully without errors
        self.assertIsInstance(result, str)
        self.assertNotIn("Show More", result)
    
    def test_text_exactly_at_threshold(self) -> None:
        """Test text that is exactly at the character threshold"""
        text_at_threshold = "A" * 50  # Exactly at threshold
        
        result = self.handler.process_response_for_display(text_at_threshold, "threshold_test")
        
        # Should not be truncated (threshold is inclusive)
        self.assertNotIn("Show More", result)
    
    def test_text_one_character_over_threshold(self) -> None:
        """Test text that is just over the threshold"""
        text_over_threshold = "A" * 51  # One character over
        
        result = self.handler.process_response_for_display(text_over_threshold, "over_test")
        
        # Should be truncated
        self.assertIn("Show More", result)
    
    def test_special_characters_handling(self) -> None:
        """Test handling of special characters in text"""
        special_text = (
            "Text with special chars: é, ñ, ü, 中文, 🎉, & < > \" ' "
            "This text contains various special characters that should be handled properly "
            "when creating HTML output without breaking the formatting or JavaScript."
        )
        
        result = self.handler.process_response_for_display(special_text, "special_test")
        
        # Should not break HTML or JavaScript
        self.assertIn("Show More", result)
        self.assertIn("function showMore", result)
        
        # Special characters should be preserved
        self.assertIn("é, ñ, ü", result)


if __name__ == '__main__':
    unittest.main()
