import unittest
import os
import pandas as pd
import sys
import json
import requests
from unittest.mock import MagicMock, patch
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the main app class
from app import SimpleFinancialChat, TimescaleAnalyzer

class TestAriaDeepseekIntegration(unittest.TestCase):
    """Test integration of SimpleFinancialChat with deepseek-coder:6.7b for financial analysis"""
    
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
        
        # Convert data to CSV for file-based tests
        self.csv_data = self.test_data.to_csv(index=False).encode('utf-8')
        
        # Sample user query
        self.test_query = "Analyze the profit margin trends by region"
    
    @patch('requests.get')
    @patch('requests.post')
    def test_initial_analysis_with_deepseek(self, mock_post, mock_get):
        """
        Test that the initial analysis and system prompt for Aria Sterling persona
        are correctly used with deepseek-coder:6.7b
        """
        # Mock the Ollama API responses
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "models": [{"name": "deepseek-coder:6.7b"}]
        }
        
        # Setup mock for post request
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "response": "# Executive Summary\n\n- Profit margins range from 20% to 29.2% across the 5-day period\n- North region shows the highest average profit margin at 28.1%\n- Overall improving trend with day-over-day growth\n\n## Detailed Analysis..."
        }
        
        # Initialize AriaFinancialChat with a mocked Ollama connection
        chat_app = SimpleFinancialChat()
        
        # Generate automatic analysis
        response = chat_app.generate_automatic_analysis_with_aria(self.test_data)
        
        # Verify the Ollama API was called with the right parameters
        mock_post.assert_called_once()
        
        # Extract the call arguments
        args, kwargs = mock_post.call_args
        
        # Verify the correct URL and model were used
        self.assertEqual(args[0], "http://localhost:11434/api/generate")
        self.assertEqual(kwargs['json']['model'], "deepseek-coder:6.7b")
        
        # Validate the prompt contains key components of the Aria Sterling persona
        prompt = kwargs['json']['prompt']
        
        # Check for system prompt elements
        self.assertIn("You are **Aria Sterling**, a world-class financial analyst", prompt)
        self.assertIn("Financial Analyst Persona", prompt)
        
        # Check for data context elements
        self.assertIn("DATASET INFORMATION:", prompt)
        
        # Check that the response was passed through correctly
        self.assertEqual(response, mock_post.return_value.json.return_value["response"])
    
    @patch('requests.get')
    @patch('requests.post')
    def test_analyze_data_integration(self, mock_post, mock_get):
        """Test the analyze_data method integrates with deepseek-coder correctly"""
        # Mock the Ollama API responses
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "models": [{"name": "deepseek-coder:6.7b"}]
        }
        
        # Setup mock for post request
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "response": "## Financial Analysis\n\nProfit margin trends by region show significant variations. North region has the highest average margin at 28.1%, followed by West at 26.9%, South at 29.2%, and East at 21.7%.\n\n## Data Patterns & Insights\n\nThere is a positive correlation between Revenue and Profit across all regions..."
        }
        
        # Initialize SimpleFinancialChat
        chat_app = SimpleFinancialChat()
        
        # Call analyze_data with our test CSV data
        response, status = chat_app.analyze_data(self.csv_data, self.test_query)
        
        # Verify the Ollama API was called
        mock_post.assert_called_once()
        
        # Extract the call arguments
        args, kwargs = mock_post.call_args
        
        # Verify the prompt contains the user question
        prompt = kwargs['json']['prompt']
        self.assertIn(f"USER QUESTION: {self.test_query}", prompt)
        
        # Verify Aria Sterling system prompt is included
        self.assertIn("You are **Aria Sterling**", prompt)
        
        # Check configuration parameters
        self.assertEqual(kwargs['json']['options']['temperature'], 0.3)
        self.assertTrue(kwargs['json']['options']['num_ctx'] >= 4096)  # Should have large context
        
        # Verify the response matches what the mock returned
        self.assertEqual(response, mock_post.return_value.json.return_value["response"])
        
        # Verify the status indicates success
        self.assertIn("✅ Aria Sterling Analysis", status)
    
    @patch('requests.get')
    def test_check_ollama_connection(self, mock_get):
        """Test that check_ollama_connection correctly identifies deepseek-coder:6.7b"""
        # Mock case 1: deepseek-coder:6.7b is available
        mock_response_1 = MagicMock()
        mock_response_1.status_code = 200
        mock_response_1.json.return_value = {
            "models": [
                {"name": "llama3"},
                {"name": "deepseek-coder:6.7b"},
                {"name": "phi3"}
            ]
        }
        mock_get.return_value = mock_response_1
        
        chat_app = SimpleFinancialChat()
        result = chat_app.check_ollama_connection()
        
        # Should find deepseek-coder:6.7b
        self.assertTrue(result)
        self.assertEqual(chat_app.model_name, "deepseek-coder:6.7b")
        
        # Mock case 2: deepseek-coder:6.7b is not available, but other models are
        mock_response_2 = MagicMock()
        mock_response_2.status_code = 200
        mock_response_2.json.return_value = {
            "models": [
                {"name": "llama3"},
                {"name": "phi3"}
            ]
        }
        mock_get.return_value = mock_response_2
        
        chat_app = SimpleFinancialChat()
        result = chat_app.check_ollama_connection()
        
        # Should find a fallback model
        self.assertTrue(result)
        self.assertIn(chat_app.model_name, ["llama3", "phi3"])
        
        # Mock case 3: No models available
        mock_response_3 = MagicMock()
        mock_response_3.status_code = 200
        mock_response_3.json.return_value = {"models": []}
        mock_get.return_value = mock_response_3
        
        chat_app = SimpleFinancialChat()
        result = chat_app.check_ollama_connection()
        
        # Should return False when no models
        self.assertFalse(result)
        
        # Mock case 4: Ollama not running
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection refused")
        
        chat_app = SimpleFinancialChat()
        result = chat_app.check_ollama_connection()
        
        # Should return False when Ollama not running
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()
