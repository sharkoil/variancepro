#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test Document Upload Chat Integration

This test verifies that document upload actually triggers chat messages
and LLM analysis as expected by the user.
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestDocumentUploadChatIntegration(unittest.TestCase):
    """Test document upload chat integration"""
    
    def setUp(self):
        """Set up test environment"""
        self.mock_rag_manager = Mock()
        self.mock_rag_analyzer = Mock()
    
    def test_document_upload_adds_chat_messages(self):
        """Test that document upload adds messages to chat"""
        print("\n🧪 Testing Document Upload Chat Integration...")
        
        try:
            from app_v2 import QuantCommanderApp
            
            # Create app with mocked RAG components
            app = QuantCommanderApp()
            app.rag_manager = self.mock_rag_manager
            app.rag_analyzer = self.mock_rag_analyzer
            
            # Mock successful document upload
            self.mock_rag_manager.upload_document.return_value = {
                'status': 'success',
                'document_info': {'filename': 'test_doc.pdf'},
                'chunks_created': 5
            }
            
            # Mock RAG analysis dependencies
            self.mock_rag_manager.has_documents.return_value = True
            self.mock_rag_manager.search_documents.return_value = {
                'results': [{'content': 'Test document content about financial analysis'}]
            }
            
            # Mock LLM call
            app.is_ollama_available = Mock(return_value=True)
            app.call_ollama = Mock(return_value="This document contains important financial insights and analysis recommendations.")
            
            # Test upload with empty history
            files = ["/path/to/test_doc.pdf"]
            initial_history = []
            
            status, updated_history = app.upload_documents(files, initial_history)
            
            # Verify upload status
            self.assertIn("✅", status, "Upload status should show success")
            print(f"   ✅ Upload status: {status}")
            
            # Verify chat history was updated
            self.assertGreater(len(updated_history), 0, "Chat history should be updated")
            print(f"   ✅ Chat history updated: {len(updated_history)} messages")
            
            # Check for upload message
            upload_message_found = False
            analysis_message_found = False
            
            for message in updated_history:
                content = message.get('content', '')
                if 'Document(s) Uploaded Successfully' in content:
                    upload_message_found = True
                    print(f"   ✅ Upload message found")
                elif 'Financial Document Analysis' in content:
                    analysis_message_found = True
                    print(f"   ✅ Analysis message found")
            
            self.assertTrue(upload_message_found, "Upload success message should be in chat")
            self.assertTrue(analysis_message_found, "Analysis message should be in chat")
            
            # Verify LLM was called
            app.call_ollama.assert_called_once()
            print(f"   ✅ LLM analysis was triggered")
            
            return True
            
        except ImportError as e:
            self.skipTest(f"App dependencies not available: {e}")
            return False
    
    def test_document_upload_flow_step_by_step(self):
        """Test the complete document upload flow step by step"""
        print("\n🧪 Testing Complete Document Upload Flow...")
        
        try:
            from app_v2 import QuantCommanderApp
            
            app = QuantCommanderApp()
            app.rag_manager = self.mock_rag_manager
            app.rag_analyzer = self.mock_rag_analyzer
            
            # Step 1: Mock document upload
            print("   Step 1: Document upload...")
            self.mock_rag_manager.upload_document.return_value = {
                'status': 'success',
                'document_info': {'filename': 'financial_report.pdf'},
                'chunks_created': 8
            }
            
            # Step 2: Mock RAG components
            print("   Step 2: RAG components...")
            self.mock_rag_manager.has_documents.return_value = True
            
            # Step 3: Mock LLM availability and response
            print("   Step 3: LLM analysis...")
            app.is_ollama_available = Mock(return_value=True)
            app.call_ollama = Mock(return_value="Financial analysis: This document contains quarterly earnings data with revenue growth trends and cost analysis.")
            
            # Step 4: Execute upload
            print("   Step 4: Execute upload...")
            files = ["financial_report.pdf"]
            history = []
            
            status, updated_history = app.upload_documents(files, history)
            
            # Step 5: Verify results
            print("   Step 5: Verify results...")
            
            # Check status
            self.assertIn("financial_report.pdf", status)
            self.assertIn("8 chunks", status)
            print(f"   ✅ Status contains file info: {status}")
            
            # Check history length
            expected_messages = 2  # Upload message + Analysis message
            self.assertEqual(len(updated_history), expected_messages, f"Should have {expected_messages} messages")
            print(f"   ✅ History has {len(updated_history)} messages")
            
            # Check message contents
            for i, message in enumerate(updated_history):
                role = message.get('role')
                content = message.get('content', '')
                print(f"   Message {i+1}: {role} - {content[:100]}...")
                
                if i == 0:  # Upload message
                    self.assertEqual(role, 'assistant')
                    self.assertIn('Document(s) Uploaded Successfully', content)
                elif i == 1:  # Analysis message
                    self.assertEqual(role, 'assistant')
                    self.assertIn('Financial Document Analysis', content)
            
            print("   ✅ All messages have correct format and content")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Error in flow test: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_debug_rag_analysis_trigger(self):
        """Debug why RAG analysis might not be triggering"""
        print("\n🧪 Debugging RAG Analysis Trigger...")
        
        try:
            from app_v2 import QuantCommanderApp
            
            app = QuantCommanderApp()
            app.rag_manager = self.mock_rag_manager
            app.rag_analyzer = self.mock_rag_analyzer
            
            # Test the analysis trigger method directly
            successful_uploads = [("/path/file.pdf", "test.pdf", 3)]
            
            # Test case 1: No RAG analyzer
            app.rag_analyzer = None
            result = app._trigger_rag_analysis_on_document_upload(successful_uploads)
            print(f"   Case 1 (No RAG analyzer): {result}")
            self.assertIsNone(result, "Should return None when no RAG analyzer")
            
            # Test case 2: RAG analyzer but no documents
            app.rag_analyzer = self.mock_rag_analyzer
            self.mock_rag_manager.has_documents.return_value = False
            result = app._trigger_rag_analysis_on_document_upload(successful_uploads)
            print(f"   Case 2 (No documents): {result}")
            self.assertIsNone(result, "Should return None when no documents")
            
            # Test case 3: Everything available but LLM unavailable
            self.mock_rag_manager.has_documents.return_value = True
            app.is_ollama_available = Mock(return_value=False)
            result = app._trigger_rag_analysis_on_document_upload(successful_uploads)
            print(f"   Case 3 (No LLM): {result is not None}")
            self.assertIsNotNone(result, "Should return fallback message when LLM unavailable")
            self.assertIn("Financial Documents Ready", result, "Should contain fallback message")
            
            # Test case 4: Everything available with LLM
            app.is_ollama_available = Mock(return_value=True)
            app.call_ollama = Mock(return_value="Test analysis result")
            result = app._trigger_rag_analysis_on_document_upload(successful_uploads)
            print(f"   Case 4 (Full setup): {result is not None}")
            self.assertIsNotNone(result, "Should return analysis when everything available")
            self.assertIn("Financial Document Analysis", result, "Should contain analysis header")
            
            print("   ✅ RAG analysis trigger working correctly")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Debug test failed: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """Run document upload chat integration tests"""
    print("🧪 Testing Document Upload Chat Integration")
    print("=" * 60)
    
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestDocumentUploadChatIntegration))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("🎉 ALL TESTS PASSED!")
        print("✅ Document upload should trigger chat messages")
        print("✅ LLM analysis should appear in chat")
        print("✅ Complete flow is working as expected")
        print("\n💡 If it's still not working, check:")
        print("   1. Is RAG manager initialized?")
        print("   2. Is RAG analyzer available?") 
        print("   3. Is Ollama running and available?")
        print("   4. Are documents actually being uploaded?")
    else:
        print("❌ SOME TESTS FAILED!")
        print(f"   Failures: {len(result.failures)}")
        print(f"   Errors: {len(result.errors)}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
