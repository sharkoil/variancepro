"""
Integration tests for VariancePro v2.0 refactored application
Tests full workflow functionality including file upload, chat processing, and variance analysis
"""

import unittest
import pandas as pd
import tempfile
import os
from unittest.mock import Mock, patch

from app_v2 import VarianceProApp


class TestVarianceProIntegration(unittest.TestCase):
    """Integration tests for the complete VariancePro application"""
    
    def setUp(self):
        """Set up integration test fixtures"""
        # Mock external dependencies for consistent testing
        with patch('core.ollama_connector.requests.get') as mock_get:
            # Mock successful Ollama connection
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'models': [{'name': 'gemma3:latest'}]
            }
            mock_get.return_value = mock_response
            
            self.app = VarianceProApp()
        
        # Create sample CSV data for testing
        self.sample_data = pd.DataFrame({
            'Date': pd.date_range('2024-01-01', periods=6, freq='M'),
            'Actual Sales': [10000, 12000, 9000, 11000, 13000, 15000],
            'Planned Sales': [9500, 11500, 10000, 10500, 12500, 14500],
            'Budget': [9000, 11000, 9500, 10000, 12000, 14000],
            'Region': ['North', 'South', 'East', 'West', 'North', 'South']
        })
        
        # Create temporary CSV file
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        self.sample_data.to_csv(self.temp_file.name, index=False)
        self.temp_file.close()
    
    def tearDown(self):
        """Clean up after tests"""
        # Remove temporary file
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_app_initialization(self):
        """Test that the application initializes with all components"""
        self.assertIsNotNone(self.app.app_core)
        self.assertIsNotNone(self.app.file_handler)
        self.assertIsNotNone(self.app.chat_handler)
        self.assertIsNotNone(self.app.quick_action_handler)
        self.assertIsNotNone(self.app.variance_analyzer)
    
    def test_file_upload_workflow(self):
        """Test complete file upload and processing workflow"""
        # Mock file object
        mock_file = Mock()
        mock_file.name = self.temp_file.name
        
        # Test upload
        history = []
        status, updated_history = self.app.upload_csv(mock_file, history)
        
        # Verify upload success
        self.assertIn('Upload Successful', status)
        self.assertGreater(len(updated_history), 0)
        
        # Verify data is loaded in app core
        self.assertTrue(self.app.app_core.has_data())
        
        data, summary = self.app.app_core.get_current_data()
        self.assertIsInstance(data, pd.DataFrame)
        self.assertEqual(len(data), 6)  # Should have 6 rows
    
    def test_chat_response_workflow(self):
        """Test chat message processing workflow"""
        # First upload data
        mock_file = Mock()
        mock_file.name = self.temp_file.name
        
        history = []
        self.app.upload_csv(mock_file, history)
        
        # Test chat response with summary request
        updated_history, input_clear = self.app.chat_response("show me a summary", history)
        
        self.assertIsInstance(updated_history, list)
        self.assertEqual(input_clear, "")  # Input should be cleared
        
        # Should have added user and assistant messages
        user_messages = [msg for msg in updated_history if msg['role'] == 'user']
        assistant_messages = [msg for msg in updated_history if msg['role'] == 'assistant']
        
        self.assertGreater(len(user_messages), 0)
        self.assertGreater(len(assistant_messages), 0)
    
    def test_quick_action_workflow(self):
        """Test quick action button processing workflow"""
        # Upload data first
        mock_file = Mock()
        mock_file.name = self.temp_file.name
        
        history = []
        self.app.upload_csv(mock_file, history)
        
        # Test summary quick action
        updated_history = self.app.quick_action("summary", history)
        
        self.assertIsInstance(updated_history, list)
        
        # Should have summary response
        last_message = updated_history[-1]
        self.assertEqual(last_message['role'], 'assistant')
        self.assertIn('Summary', last_message['content'])
    
    def test_variance_analysis_workflow(self):
        """Test variance analysis through quick action"""
        # Upload data first
        mock_file = Mock()
        mock_file.name = self.temp_file.name
        
        history = []
        self.app.upload_csv(mock_file, history)
        
        # Test variance quick action
        updated_history = self.app.quick_action("variance", history)
        
        self.assertIsInstance(updated_history, list)
        
        # Should have variance analysis response
        last_message = updated_history[-1]
        self.assertEqual(last_message['role'], 'assistant')
        # Should contain variance analysis or pair detection info
        content = last_message['content']
        self.assertTrue(
            'Variance' in content or 'comparison' in content or 'pairs' in content
        )
    
    def test_top_bottom_analysis_workflow(self):
        """Test top/bottom analysis through quick actions"""
        # Upload data first
        mock_file = Mock()
        mock_file.name = self.temp_file.name
        
        history = []
        self.app.upload_csv(mock_file, history)
        
        # Test top 5 analysis
        updated_history = self.app.quick_action("top 5", history)
        
        self.assertIsInstance(updated_history, list)
        
        # Should have analysis response
        last_message = updated_history[-1]
        self.assertEqual(last_message['role'], 'assistant')
        self.assertIn('Top 5', last_message['content'])
    
    def test_interface_creation(self):
        """Test that the Gradio interface can be created"""
        interface = self.app.create_interface()
        
        # Should return a Gradio Blocks object
        self.assertIsNotNone(interface)
        # Basic check that it has the expected type
        self.assertTrue(hasattr(interface, 'launch'))
    
    def test_error_handling_invalid_file(self):
        """Test error handling with invalid file upload"""
        # Test with None file
        history = []
        status, updated_history = self.app.upload_csv(None, history)
        
        self.assertIn('select a CSV file', status)
        
        # Test with non-existent file
        mock_file = Mock()
        mock_file.name = 'non_existent_file.csv'
        
        status, updated_history = self.app.upload_csv(mock_file, history)
        self.assertIn('Failed', status)
    
    def test_chat_without_data(self):
        """Test chat response when no data is uploaded"""
        history = []
        updated_history, input_clear = self.app.chat_response("show me data", history)
        
        # Should get a message about uploading data first
        last_message = updated_history[-1]
        self.assertIn('upload a CSV file', last_message['content'])
    
    def test_session_persistence(self):
        """Test that session information persists throughout workflow"""
        initial_session_id = self.app.app_core.session_id
        
        # Upload file
        mock_file = Mock()
        mock_file.name = self.temp_file.name
        
        history = []
        self.app.upload_csv(mock_file, history)
        
        # Session ID should remain the same
        self.assertEqual(self.app.app_core.session_id, initial_session_id)
        
        # Process chat message
        self.app.chat_response("test message", history)
        
        # Session ID should still be the same
        self.assertEqual(self.app.app_core.session_id, initial_session_id)


class TestVarianceAnalysisIntegration(unittest.TestCase):
    """Integration tests specifically for variance analysis features"""
    
    def setUp(self):
        """Set up variance analysis integration tests"""
        with patch('core.ollama_connector.requests.get') as mock_get:
            # Mock successful Ollama connection
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'models': [{'name': 'gemma3:latest'}]
            }
            mock_get.return_value = mock_response
            
            self.app = VarianceProApp()
        
        # Create variance-specific test data
        self.variance_data = pd.DataFrame({
            'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            'Actual Revenue': [50000, 52000, 48000, 55000, 58000, 60000],
            'Planned Revenue': [48000, 50000, 50000, 53000, 56000, 58000],
            'Budget Expenses': [30000, 31000, 29000, 33000, 35000, 36000],
            'Actual Expenses': [32000, 30500, 31000, 34500, 36500, 37000],
            'Sales Target': [45000, 47000, 47000, 50000, 53000, 55000]
        })
        
        # Create temporary CSV file
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        self.variance_data.to_csv(self.temp_file.name, index=False)
        self.temp_file.close()
    
    def tearDown(self):
        """Clean up after tests"""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_variance_pair_detection_integration(self):
        """Test that variance pairs are properly detected in uploaded data"""
        # Upload variance data
        mock_file = Mock()
        mock_file.name = self.temp_file.name
        
        history = []
        self.app.upload_csv(mock_file, history)
        
        # Get the data and test variance pair detection
        data, _ = self.app.app_core.get_current_data()
        pairs = self.app.variance_analyzer.detect_variance_pairs(data.columns.tolist())
        
        # Should detect multiple variance pairs
        self.assertGreater(len(pairs), 0)
        
        # Should find revenue comparison
        revenue_pairs = [p for p in pairs if 'Revenue' in p['actual'] or 'Revenue' in p['planned']]
        self.assertGreater(len(revenue_pairs), 0)
    
    def test_variance_analysis_through_chat(self):
        """Test variance analysis triggered through chat interface"""
        # Upload data
        mock_file = Mock()
        mock_file.name = self.temp_file.name
        
        history = []
        self.app.upload_csv(mock_file, history)
        
        # Request variance analysis through chat
        updated_history, _ = self.app.chat_response("compare actual vs planned revenue", history)
        
        # Should process the variance request
        self.assertIsInstance(updated_history, list)
        
        # Look for variance-related content in responses
        assistant_messages = [msg for msg in updated_history if msg['role'] == 'assistant']
        variance_responses = [msg for msg in assistant_messages if 'variance' in msg['content'].lower()]
        
        # Should have at least some mention of variance or comparison
        self.assertGreater(len(assistant_messages), 0)


if __name__ == '__main__':
    # Run integration tests
    unittest.main(verbosity=2)
