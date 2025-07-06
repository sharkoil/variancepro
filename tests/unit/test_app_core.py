"""
Unit tests for the AppCore module
Tests core application functionality including initialization, state management, and component coordination
"""

import unittest
from unittest.mock import Mock, patch
import uuid

from core.app_core import AppCore


class TestAppCore(unittest.TestCase):
    """Test cases for the AppCore class"""
    
    def setUp(self):
        """Set up test fixtures before each test method"""
        # Mock external dependencies to isolate unit tests
        with patch('core.app_core.OllamaConnector'), \
             patch('core.app_core.Settings'), \
             patch('core.app_core.TimescaleAnalyzer'), \
             patch('core.app_core.NL2SQLFunctionCaller'):
            self.app_core = AppCore()
    
    def test_initialization(self):
        """Test that AppCore initializes correctly with all required components"""
        # Check that session ID is generated
        self.assertIsInstance(self.app_core.session_id, str)
        self.assertEqual(len(self.app_core.session_id), 8)
        
        # Check initial state
        self.assertIsNone(self.app_core.current_data)
        self.assertIsNone(self.app_core.data_summary)
        self.assertEqual(self.app_core.gradio_status, "Running")
    
    def test_session_id_uniqueness(self):
        """Test that each AppCore instance gets a unique session ID"""
        with patch('core.app_core.OllamaConnector'), \
             patch('core.app_core.Settings'), \
             patch('core.app_core.TimescaleAnalyzer'), \
             patch('core.app_core.NL2SQLFunctionCaller'):
            app_core_2 = AppCore()
        
        self.assertNotEqual(self.app_core.session_id, app_core_2.session_id)
    
    def test_set_current_data(self):
        """Test setting current data and summary"""
        test_data = "test_data"
        test_summary = {"test": "summary"}
        
        self.app_core.set_current_data(test_data, test_summary)
        
        self.assertEqual(self.app_core.current_data, test_data)
        self.assertEqual(self.app_core.data_summary, test_summary)
    
    def test_get_current_data(self):
        """Test getting current data and summary"""
        test_data = "test_data"
        test_summary = {"test": "summary"}
        
        self.app_core.set_current_data(test_data, test_summary)
        data, summary = self.app_core.get_current_data()
        
        self.assertEqual(data, test_data)
        self.assertEqual(summary, test_summary)
    
    def test_has_data(self):
        """Test data availability checking"""
        # Initially no data
        self.assertFalse(self.app_core.has_data())
        
        # After setting data
        self.app_core.set_current_data("test_data")
        self.assertTrue(self.app_core.has_data())
    
    def test_clear_data(self):
        """Test clearing current data"""
        self.app_core.set_current_data("test_data", {"test": "summary"})
        self.assertTrue(self.app_core.has_data())
        
        self.app_core.clear_data()
        
        self.assertFalse(self.app_core.has_data())
        self.assertIsNone(self.app_core.current_data)
        self.assertIsNone(self.app_core.data_summary)
    
    def test_get_session_info(self):
        """Test session information retrieval"""
        session_info = self.app_core.get_session_info()
        
        self.assertIsInstance(session_info, dict)
        self.assertIn('session_id', session_info)
        self.assertIn('ollama_status', session_info)
        self.assertIn('gradio_status', session_info)
        self.assertIn('has_data', session_info)
        self.assertIn('timestamp', session_info)


if __name__ == '__main__':
    unittest.main()
