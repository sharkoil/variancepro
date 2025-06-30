import unittest
import os
import pandas as pd
import sys
import json
from unittest.mock import MagicMock, patch
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the classes we need to test
from utils.llm_handler import LLMHandler, DataContextBuilder
from utils.chat_handler import ChatHandler

class TestDeepseekCoderIntegration(unittest.TestCase):
    """Test integration with deepseek-coder:6.7b for financial analysis"""
    
    def setUp(self):
        """Set up test environment"""
        # Sample data for testing
        self.test_data = pd.DataFrame({
            'Date': ['2025-01-01', '2025-01-02', '2025-01-03', '2025-01-04', '2025-01-05'],
            'Revenue': [1000, 1200, 1150, 1300, 1400],
            'Expenses': [800, 850, 900, 950, 1000],
            'Profit': [200, 350, 250, 350, 400],
            'Region': ['North', 'South', 'East', 'West', 'North']
        })
        self.test_data['Date'] = pd.to_datetime(self.test_data['Date'])
        
        # Sample user query
        self.test_query = "What is the trend in profit margins?"
        
        # Path to the sample file for file-based tests
        self.sample_file_path = "sample_financial_data.csv"
    
    @patch('requests.Session.post')
    @patch('requests.Session.get')
    def test_deepseek_coder_prompt_integration(self, mock_get, mock_post):
        """
        Test that the initial analysis and system prompt are correctly used 
        in a call to deepseek-coder:6.7b to create a professional financial analyst response
        """
        # Mock the API responses
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "models": [{"name": "deepseek-coder:6.7b"}]
        }
        
        # Setup mock for post request with a successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "As a professional financial analyst, I can see that profit margins are improving over time. The trend shows..."}
        mock_post.return_value = mock_response
        
        # Initialize LLMHandler with deepseek-coder model
        llm_handler = LLMHandler(backend="ollama", model_name="deepseek-coder:6.7b")
        
        # Create data context and summary
        data_context_builder = DataContextBuilder()
        data_context, data_summary = data_context_builder.build_context(self.test_data)
        
        # Generate financial response
        response = llm_handler.generate_financial_response(self.test_query, data_context, data_summary)
        
        # Verify the request was made with the correct data
        mock_post.assert_called_once()
        
        # Extract the call arguments
        args, kwargs = mock_post.call_args
        
        # Check that the URL is correct
        self.assertEqual(args[0], "http://localhost:11434/api/generate")
        
        # Validate the prompt includes system prompt and analysis
        payload = kwargs['json']
        self.assertEqual(payload['model'], "deepseek-coder:6.7b")
        
        # Check that the prompt contains key components
        prompt = payload['prompt']
        self.assertIn("You are an expert financial data analyst", prompt)
        self.assertIn("DATASET CONTEXT:", prompt)
        self.assertIn("DATASET SUMMARY:", prompt)
        self.assertIn("USER QUESTION: What is the trend in profit margins?", prompt)
        
        # Verify model-specific configuration is used
        self.assertIn('options', payload)
        self.assertIn('temperature', payload['options'])
        
        # Verify the response came through properly
        self.assertIn("professional financial analyst", response)
        self.assertIn("profit margins are improving", response)
    
    @patch('requests.Session.post')
    @patch('requests.Session.get')
    def test_chat_handler_integration_with_deepseek(self, mock_get, mock_post):
        """Test ChatHandler correctly uses deepseek-coder model through LLMHandler"""
        # Mock the API responses
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "models": [{"name": "deepseek-coder:6.7b"}]
        }
        
        # Setup mock for post request
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "As your financial analyst, I notice that profit margins have increased from 20% to 28.6% over the period..."}
        mock_post.return_value = mock_response
        
        # Initialize ChatHandler and patch the LLMHandler
        with patch('utils.chat_handler.LLMHandler') as mock_llm_handler_class:
            # Create a real LLMHandler but with mocked methods
            llm_handler = LLMHandler(backend="ollama", model_name="deepseek-coder:6.7b")
            
            # Configure mock LLMHandler
            mock_instance = MagicMock()
            mock_instance.is_available.return_value = True
            mock_instance.generate_financial_response.return_value = "As your financial analyst, I notice that profit margins have increased from 20% to 28.6% over the period..."
            mock_llm_handler_class.return_value = mock_instance
            
            # Create ChatHandler with the mocked LLMHandler
            chat_handler = ChatHandler()
            
            # Force the LLM handler to be our mock
            chat_handler.llm_handler = mock_instance
            chat_handler.use_llm = True
            
            # Generate response
            response = chat_handler.generate_response(self.test_query, self.test_data)
            
            # Verify LLMHandler was used to generate a response
            mock_instance.generate_financial_response.assert_called_once()
            
            # Extract call arguments
            args, kwargs = mock_instance.generate_financial_response.call_args
            
            # Verify correct user query was passed
            self.assertEqual(args[0], self.test_query)
            
            # Verify the response includes the AI-enhanced marker
            self.assertIn("AI-Enhanced Analysis", response)
            self.assertIn("profit margins have increased from 20% to 28.6%", response)

if __name__ == '__main__':
    unittest.main()
