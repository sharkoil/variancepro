"""
Integration tests for Chat Interface Enhancement
Tests integration with existing LLM interpreter and response processing
"""

import unittest
from unittest.mock import Mock, patch
from ai.llm_interpreter import LLMResponse, LLMInterpreter
from ui.chat_interface_enhancer import ChatInterfaceEnhancer, enhance_chat_response


class TestChatInterfaceIntegration(unittest.TestCase):
    """Integration tests for chat interface enhancement"""
    
    def setUp(self) -> None:
        """Set up test fixtures"""
        self.enhancer = ChatInterfaceEnhancer(character_threshold=100)
        
        # Mock successful LLM response (short)
        self.short_success_response = LLMResponse(
            content="This is a short response.",
            success=True,
            metadata={'model': 'gemma3:latest', 'eval_count': 50},
            processing_time=1.2
        )
        
        # Mock successful LLM response (long)
        self.long_success_response = LLMResponse(
            content=(
                "This is a very long response that exceeds the character threshold "
                "and should trigger the text overflow functionality with show more and less buttons. "
                "It includes detailed analysis with multiple bullet points and recommendations. "
                "The response should be properly formatted with HTML and include JavaScript controls."
            ),
            success=True,
            metadata={'model': 'gemma3:latest', 'eval_count': 150},
            processing_time=2.5
        )
        
        # Mock error response
        self.error_response = LLMResponse(
            content="",
            success=False,
            error="LLM service unavailable",
            processing_time=0.1
        )
    
    def test_enhance_short_successful_response(self) -> None:
        """Test enhancement of short successful response"""
        result = self.enhancer.enhance_llm_response(self.short_success_response)
        
        # Should preserve original content
        self.assertEqual(result['content'], self.short_success_response.content)
        
        # Should be marked as successful
        self.assertTrue(result['success'])
        
        # Should not be truncated
        self.assertFalse(result['metadata']['truncated'])
        
        # Should have formatted content
        self.assertIn('formatted_content', result)
        self.assertIn('response-text', result['formatted_content'])
    
    def test_enhance_long_successful_response(self) -> None:
        """Test enhancement of long successful response"""
        result = self.enhancer.enhance_llm_response(self.long_success_response)
        
        # Should preserve original content
        self.assertEqual(result['content'], self.long_success_response.content)
        
        # Should be marked as successful
        self.assertTrue(result['success'])
        
        # Should be marked as truncated
        self.assertTrue(result['metadata']['truncated'])
        
        # Should include show more/less functionality
        self.assertIn('Show More', result['formatted_content'])
        self.assertIn('show-more-btn', result['formatted_content'])
    
    def test_enhance_error_response(self) -> None:
        """Test enhancement of error response"""
        result = self.enhancer.enhance_llm_response(self.error_response)
        
        # Should preserve error state
        self.assertFalse(result['success'])
        self.assertEqual(result['error'], self.error_response.error)
        
        # Should have formatted error content
        self.assertIn('error-response', result['formatted_content'])
        self.assertIn('Analysis Unavailable', result['formatted_content'])
        self.assertIn('Suggestions:', result['formatted_content'])
    
    def test_session_management(self) -> None:
        """Test session start/end functionality"""
        # Start new session
        self.enhancer.start_new_session()
        
        status = self.enhancer.get_session_status()
        self.assertTrue(status['active'])
        self.assertEqual(status['response_count'], 0)
        
        # Process some responses
        self.enhancer.enhance_llm_response(self.short_success_response)
        self.enhancer.enhance_llm_response(self.long_success_response)
        
        status = self.enhancer.get_session_status()
        self.assertEqual(status['response_count'], 2)
        
        # End session
        self.enhancer.end_session()
        
        status = self.enhancer.get_session_status()
        self.assertFalse(status['active'])
    
    def test_convenience_function(self) -> None:
        """Test the convenience function for single response enhancement"""
        result = enhance_chat_response(self.long_success_response, character_threshold=50)
        
        # Should work the same as the class method
        self.assertTrue(result['success'])
        self.assertTrue(result['metadata']['truncated'])
        self.assertIn('Show More', result['formatted_content'])
    
    def test_metadata_preservation_and_enhancement(self) -> None:
        """Test that original metadata is preserved and enhanced"""
        result = self.enhancer.enhance_llm_response(self.long_success_response)
        
        # Should preserve original metadata
        self.assertEqual(result['metadata']['model'], 'gemma3:latest')
        self.assertEqual(result['metadata']['eval_count'], 150)
        
        # Should add enhancement metadata
        self.assertTrue(result['metadata']['formatted'])
        self.assertIn('character_count', result['metadata'])
        self.assertIn('truncated', result['metadata'])
    
    def test_processing_time_preservation(self) -> None:
        """Test that processing time is preserved"""
        result = self.enhancer.enhance_llm_response(self.long_success_response)
        
        # Should preserve original processing time
        self.assertEqual(result['processing_time'], 2.5)


class TestLLMInterpreterIntegration(unittest.TestCase):
    """Test integration with LLMInterpreter class"""
    
    @patch('requests.get')
    @patch('requests.post')
    def test_query_llm_with_formatting_method(self, mock_post, mock_get) -> None:
        """Test the new query_llm_with_formatting method"""
        # Mock settings
        mock_settings = Mock()
        mock_settings.get_ollama_config.return_value = {
            'host': 'http://localhost:11434',
            'timeout': 30,
            'options': {'temperature': 0.7, 'num_predict': 512}
        }
        mock_settings.llm_model = 'gemma3:latest'
        
        # Mock connection test response
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            'models': [{'name': 'gemma3:latest'}]
        }
        
        # Mock LLM response for long text
        long_response_text = "A" * 200  # Long response
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            'response': long_response_text,
            'eval_count': 100,
            'eval_duration': 1000
        }
        
        # Create interpreter and test
        interpreter = LLMInterpreter(mock_settings)
        result = interpreter.query_llm_with_formatting("Test question")
        
        # Should have enhanced formatting for long response
        self.assertTrue(result['success'])
        self.assertIn('formatted_content', result)
        self.assertTrue(result['metadata']['truncated'])
        
        # Should contain show more/less controls
        if 'Show More' in result['formatted_content']:
            self.assertIn('show-more-btn', result['formatted_content'])


class TestRealWorldScenarios(unittest.TestCase):
    """Test real-world usage scenarios"""
    
    def setUp(self) -> None:
        """Set up test fixtures"""
        self.enhancer = ChatInterfaceEnhancer()
    
    def test_financial_analysis_response(self) -> None:
        """Test enhancement of typical financial analysis response"""
        financial_response = LLMResponse(
            content=(
                "Based on the variance analysis of your Q3 sales data, here are the key findings:\n\n"
                "• Revenue exceeded budget by 12.5% ($125,000 over target)\n"
                "• Top performing regions: North (18% over), West (15% over), South (8% over)\n"
                "• Product line analysis shows Software licenses driving 60% of the variance\n"
                "• Customer satisfaction scores averaged 4.2/5.0 across all regions\n\n"
                "Recommendations:\n"
                "• Increase Q4 sales targets by 8-10% based on current momentum\n"
                "• Replicate North region's strategies in underperforming East region\n"
                "• Consider expanding software license promotions company-wide\n"
                "• Monitor satisfaction metrics closely as sales volume increases"
            ),
            success=True,
            metadata={'model': 'gemma3:latest'},
            processing_time=3.1
        )
        
        result = self.enhancer.enhance_llm_response(financial_response)
        
        # Should be enhanced properly
        self.assertTrue(result['success'])
        self.assertTrue(result['metadata']['truncated'])
        
        # Should preserve business formatting
        self.assertIn('• Revenue exceeded', result['formatted_content'])
        self.assertIn('Recommendations:', result['formatted_content'])
    
    def test_multiple_responses_in_conversation(self) -> None:
        """Test multiple responses in a conversation flow"""
        self.enhancer.start_new_session()
        
        responses = []
        
        # First response (question about data)
        response1 = LLMResponse(
            content="I can help analyze your sales data. What specific metrics would you like to examine?",
            success=True
        )
        enhanced1 = self.enhancer.enhance_llm_response(response1)
        responses.append(enhanced1)
        
        # Second response (detailed analysis)
        response2 = LLMResponse(
            content=(
                "Detailed variance analysis shows significant regional differences in performance. "
                "The North region is outperforming all others with 18% variance above budget. "
                "This is primarily driven by enterprise software sales which increased 45% over the quarter. "
                "In contrast, the East region is underperforming by 8% due to supply chain delays affecting product delivery. "
                "Customer acquisition costs have decreased by 12% overall, indicating improved marketing efficiency. "
                "The customer satisfaction trend shows consistent improvement across all touchpoints."
            ),
            success=True
        )
        enhanced2 = self.enhancer.enhance_llm_response(response2)
        responses.append(enhanced2)
        
        # Verify both responses are properly enhanced
        self.assertEqual(len(responses), 2)
        
        # First response should not be truncated
        self.assertFalse(responses[0]['metadata']['truncated'])
        
        # Second response should be truncated
        self.assertTrue(responses[1]['metadata']['truncated'])
        
        # Should have unique response IDs
        self.assertIn('response_1', responses[0]['formatted_content'])
        self.assertIn('response_2', responses[1]['formatted_content'])


if __name__ == '__main__':
    unittest.main()
