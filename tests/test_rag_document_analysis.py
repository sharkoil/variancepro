#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test RAG document analysis functionality

This test validates that document upload triggers proper LLM analysis
similar to CSV upload behavior.
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestRAGDocumentAnalysis(unittest.TestCase):
    """Test suite for RAG document analysis functionality"""
    
    def setUp(self):
        """Set up test environment"""
        # Mock the app_v2 dependencies that might not be available
        self.mock_rag_manager = Mock()
        self.mock_rag_analyzer = Mock()
        self.mock_app_core = Mock()
        
        # Mock successful document upload
        self.successful_uploads = [
            ("/path/to/doc1.pdf", "financial_report.pdf", 5),
            ("/path/to/doc2.txt", "market_analysis.txt", 3)
        ]
    
    def test_document_upload_triggers_analysis(self):
        """Test that document upload triggers LLM analysis"""
        print("\n🧪 Testing Document Upload Analysis Trigger...")
        
        try:
            from app_v2 import QuantCommanderV2
            
            # Create app instance with mocked dependencies
            app = QuantCommanderV2()
            app.rag_manager = self.mock_rag_manager
            app.rag_analyzer = self.mock_rag_analyzer
            
            # Mock the dependencies
            self.mock_rag_manager.has_documents.return_value = True
            app.is_ollama_available = Mock(return_value=True)
            app.call_ollama = Mock(return_value="This is a test financial analysis response")
            
            # Test the RAG analysis trigger
            result = app._trigger_rag_analysis_on_document_upload(self.successful_uploads)
            
            # Verify analysis was triggered
            self.assertIsNotNone(result, "Should return analysis result")
            self.assertIn("Financial Document Analysis", result, "Should contain financial analysis")
            self.assertIn("financial", result.lower(), "Should have finance focus")
            
            # Verify Ollama was called
            app.call_ollama.assert_called_once()
            call_args = app.call_ollama.call_args[0][0]  # Get the prompt
            self.assertIn("finance", call_args.lower(), "Prompt should mention finance")
            
            print("   ✅ Document upload triggers LLM analysis")
            
        except ImportError as e:
            self.skipTest(f"App dependencies not available: {e}")
    
    def test_document_upload_integration(self):
        """Test full document upload integration"""
        print("\n🧪 Testing Document Upload Integration...")
        
        try:
            from app_v2 import QuantCommanderV2
            
            # Create app instance
            app = QuantCommanderV2()
            app.rag_manager = self.mock_rag_manager
            app.rag_analyzer = self.mock_rag_analyzer
            
            # Mock file upload success
            self.mock_rag_manager.upload_document.return_value = {
                'status': 'success',
                'document_info': {'filename': 'test_doc.pdf'},
                'chunks_created': 5
            }
            self.mock_rag_manager.has_documents.return_value = True
            
            # Mock LLM availability and response
            app.is_ollama_available = Mock(return_value=True)
            app.call_ollama = Mock(return_value="Test financial document analysis")
            
            # Test upload_documents method
            mock_files = ["/path/to/test_doc.pdf"]
            history = []
            
            status, updated_history = app.upload_documents(mock_files, history)
            
            # Verify upload status
            self.assertIn("✅", status, "Should show success status")
            
            # Verify history was updated with analysis
            self.assertGreater(len(updated_history), len(history), "History should be updated")
            
            # Check that analysis was added to history
            analysis_found = False
            for message in updated_history:
                if "Financial Document Analysis" in message.get('content', ''):
                    analysis_found = True
                    break
            
            self.assertTrue(analysis_found, "Analysis should be added to chat history")
            
            print("   ✅ Document upload integration works correctly")
            
        except ImportError as e:
            self.skipTest(f"App dependencies not available: {e}")
    
    def test_finance_persona_in_analysis(self):
        """Test that analysis uses finance persona as requested"""
        print("\n🧪 Testing Finance Persona in Analysis...")
        
        try:
            from app_v2 import QuantCommanderV2
            
            app = QuantCommanderV2()
            app.rag_manager = self.mock_rag_manager
            app.rag_analyzer = self.mock_rag_analyzer
            
            # Mock dependencies
            self.mock_rag_manager.has_documents.return_value = True
            app.is_ollama_available = Mock(return_value=True)
            
            # Capture the prompt sent to LLM
            captured_prompt = None
            def capture_prompt(prompt):
                nonlocal captured_prompt
                captured_prompt = prompt
                return "Mock financial analysis"
            
            app.call_ollama = Mock(side_effect=capture_prompt)
            
            # Trigger analysis
            result = app._trigger_rag_analysis_on_document_upload(self.successful_uploads)
            
            # Verify finance persona is used in prompt
            self.assertIsNotNone(captured_prompt, "Prompt should be captured")
            self.assertIn("finance expert", captured_prompt.lower(), "Should use finance expert persona")
            self.assertIn("financial", captured_prompt.lower(), "Should focus on financial analysis")
            
            # Verify result mentions financial context
            self.assertIn("Financial Document Analysis", result, "Result should mention financial analysis")
            
            print("   ✅ Finance persona is properly used in analysis")
            
        except ImportError as e:
            self.skipTest(f"App dependencies not available: {e}")
    
    def test_fallback_when_llm_unavailable(self):
        """Test fallback behavior when LLM is not available"""
        print("\n🧪 Testing Fallback When LLM Unavailable...")
        
        try:
            from app_v2 import QuantCommanderV2
            
            app = QuantCommanderV2()
            app.rag_manager = self.mock_rag_manager
            app.rag_analyzer = self.mock_rag_analyzer
            
            # Mock LLM unavailable
            self.mock_rag_manager.has_documents.return_value = True
            app.is_ollama_available = Mock(return_value=False)
            
            # Trigger analysis
            result = app._trigger_rag_analysis_on_document_upload(self.successful_uploads)
            
            # Verify fallback message is returned
            self.assertIsNotNone(result, "Should return fallback message")
            self.assertIn("Financial Documents Ready", result, "Should use fallback with financial focus")
            self.assertIn("financial", result.lower(), "Fallback should still mention financial context")
            
            print("   ✅ Fallback behavior works with financial focus")
            
        except ImportError as e:
            self.skipTest(f"App dependencies not available: {e}")


def run_rag_analysis_tests():
    """Run all RAG document analysis tests"""
    print("🧪 Running RAG Document Analysis Tests")
    print("=" * 50)
    
    # Create test suite
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestRAGDocumentAnalysis))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    if result.wasSuccessful():
        print("\n🎉 All RAG document analysis tests passed!")
        print("✅ Document upload now triggers proper LLM analysis")
        print("✅ Finance persona is used correctly")
        print("✅ Similar behavior to CSV upload achieved")
        return True
    else:
        print(f"\n❌ {len(result.failures)} test(s) failed")
        print(f"❌ {len(result.errors)} error(s) occurred")
        return False


if __name__ == "__main__":
    success = run_rag_analysis_tests()
    sys.exit(0 if success else 1)
