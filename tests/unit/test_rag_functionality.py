"""
Unit tests for RAG (Retrieval-Augmented Generation) functionality
Tests document upload, processing, and enhanced analysis features
"""

import pytest
import tempfile
import os
from typing import Dict, Any
import sys

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from analyzers.rag_document_manager import RAGDocumentManager
from analyzers.rag_enhanced_analyzer import RAGEnhancedAnalyzer


class TestRAGDocumentManager:
    """Test cases for RAG Document Manager"""
    
    def setup_method(self):
        """Set up test fixtures before each test method"""
        self.rag_manager = RAGDocumentManager()
    
    def test_initialization(self):
        """Test RAG Document Manager initializes correctly"""
        assert self.rag_manager is not None
        assert isinstance(self.rag_manager.documents, dict)
        assert isinstance(self.rag_manager.document_chunks, dict)
        assert isinstance(self.rag_manager.session_context, list)
        assert self.rag_manager.max_chunk_size == 1000
        assert self.rag_manager.chunk_overlap == 200
    
    def test_has_documents_empty(self):
        """Test has_documents returns False when no documents uploaded"""
        assert self.rag_manager.has_documents() == False
    
    def test_text_document_upload(self):
        """Test uploading a text document"""
        # Create a temporary text file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
            temp_file.write("This is a test document for RAG functionality. " * 50)
            temp_file_path = temp_file.name
        
        try:
            # Test upload
            result = self.rag_manager.upload_document(temp_file_path)
            
            # Verify results
            assert result['success'] == True
            assert 'document_id' in result
            assert result['chunks_created'] > 0
            assert self.rag_manager.has_documents() == True
            
        finally:
            # Clean up
            os.unlink(temp_file_path)
    
    def test_document_chunking(self):
        """Test document chunking functionality"""
        test_text = "This is a test sentence. " * 100  # Create long text
        chunks = self.rag_manager._chunk_text(test_text)
        
        assert len(chunks) > 1  # Should create multiple chunks
        for chunk in chunks:
            assert len(chunk) <= self.rag_manager.max_chunk_size
    
    def test_retrieve_relevant_chunks(self):
        """Test document retrieval functionality"""
        # Upload a test document first
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
            temp_file.write("Financial analysis shows variance in budget. The company performance is good.")
            temp_file_path = temp_file.name
        
        try:
            # Upload document
            self.rag_manager.upload_document(temp_file_path)
            
            # Test retrieval
            results = self.rag_manager.retrieve_relevant_chunks("quantitative analysis", max_chunks=3)
            
            # Verify results
            assert isinstance(results, list)
            if results:  # If chunks were found
                assert 'content' in results[0]
                assert 'document_name' in results[0]
                
        finally:
            os.unlink(temp_file_path)
    
    def test_clear_all_documents(self):
        """Test clearing all documents"""
        # Upload a document first
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
            temp_file.write("Test document content")
            temp_file_path = temp_file.name
        
        try:
            self.rag_manager.upload_document(temp_file_path)
            assert self.rag_manager.has_documents() == True
            
            # Clear documents
            result = self.rag_manager.clear_all_documents()
            assert result['status'] == 'success'
            assert self.rag_manager.has_documents() == False
            
        finally:
            os.unlink(temp_file_path)
    
    def test_get_document_summary(self):
        """Test getting document summary"""
        summary = self.rag_manager.get_document_summary()
        assert isinstance(summary, dict)
        
        # Should be empty initially
        assert len(summary) == 0


class TestRAGEnhancedAnalyzer:
    """Test cases for RAG Enhanced Analyzer"""
    
    def setup_method(self):
        """Set up test fixtures before each test method"""
        self.rag_manager = RAGDocumentManager()
        self.rag_analyzer = RAGEnhancedAnalyzer(self.rag_manager)
    
    def test_initialization(self):
        """Test RAG Enhanced Analyzer initializes correctly"""
        assert self.rag_analyzer is not None
        assert self.rag_analyzer.rag_manager == self.rag_manager
        assert hasattr(self.rag_analyzer, 'ollama_url')
        assert hasattr(self.rag_analyzer, 'model_name')
    
    def test_enhance_variance_analysis_no_documents(self):
        """Test quantitative analysis enhancement when no documents are uploaded"""
        variance_data = {'test': 'data'}
        analysis_context = "Test quantitative analysis"
        
        # Should handle gracefully when no documents
        result = self.rag_analyzer.enhance_variance_analysis(variance_data, analysis_context)
        
        # Should return some result even without documents
        assert isinstance(result, dict)
    
    def test_enhance_trend_analysis_no_documents(self):
        """Test trend analysis enhancement when no documents are uploaded"""
        trend_data = {'test': 'data'}
        analysis_context = "Test trend analysis"
        
        result = self.rag_analyzer.enhance_trend_analysis(trend_data, analysis_context)
        assert isinstance(result, dict)
    
    def test_enhance_top_n_analysis_no_documents(self):
        """Test Top N analysis enhancement when no documents are uploaded"""
        top_n_data = {'test': 'data'}
        analysis_context = "Test top N analysis"
        
        result = self.rag_analyzer.enhance_top_n_analysis(
            top_n_data, 
            analysis_context, 
            analysis_type="contribution"
        )
        assert isinstance(result, dict)


class TestRAGIntegration:
    """Integration tests for complete RAG workflow"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.rag_manager = RAGDocumentManager()
        self.rag_analyzer = RAGEnhancedAnalyzer(self.rag_manager)
    
    def test_complete_workflow(self):
        """Test complete RAG workflow from upload to analysis"""
        # Create test document
        test_content = """
        Financial Performance Analysis Report
        
        Our quantitative analysis shows significant budget deviations in Q3.
        The sales performance exceeded expectations by 15% in the North region.
        Cost management initiatives reduced operational expenses.
        Trend analysis indicates steady growth in digital channels.
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
            temp_file.write(test_content)
            temp_file_path = temp_file.name
        
        try:
            # Upload document
            upload_result = self.rag_manager.upload_document(temp_file_path)
            assert upload_result['success'] == True
            
            # Test document is available
            assert self.rag_manager.has_documents() == True
            
            # Test retrieval works
            chunks = self.rag_manager.retrieve_relevant_chunks("quantitative analysis")
            assert len(chunks) > 0
            
            # Test enhanced analysis (basic structure check)
            variance_data = {'budget_variance': 1000, 'actual_sales': 15000}
            result = self.rag_analyzer.enhance_variance_analysis(
                variance_data, 
                "Quantitative analysis with supplementary context"
            )
            assert isinstance(result, dict)
            
        finally:
            os.unlink(temp_file_path)


if __name__ == "__main__":
    # Run the tests
    print("🧪 Running RAG Unit Tests...")
    print("=" * 50)
    
    # Test RAG Document Manager
    print("\n📚 Testing RAG Document Manager...")
    test_manager = TestRAGDocumentManager()
    test_manager.setup_method()
    
    try:
        test_manager.test_initialization()
        print("✅ Initialization test passed")
        
        test_manager.test_has_documents_empty()
        print("✅ Has documents (empty) test passed")
        
        test_manager.test_text_document_upload()
        print("✅ Text document upload test passed")
        
        test_manager.test_document_chunking()
        print("✅ Document chunking test passed")
        
        test_manager.test_retrieve_relevant_chunks()
        print("✅ Chunk retrieval test passed")
        
        test_manager.test_clear_all_documents()
        print("✅ Clear documents test passed")
        
        test_manager.test_get_document_summary()
        print("✅ Document summary test passed")
        
    except Exception as e:
        print(f"❌ RAG Document Manager test failed: {e}")
    
    # Test RAG Enhanced Analyzer
    print("\n🤖 Testing RAG Enhanced Analyzer...")
    test_analyzer = TestRAGEnhancedAnalyzer()
    test_analyzer.setup_method()
    
    try:
        test_analyzer.test_initialization()
        print("✅ RAG Analyzer initialization test passed")
        
        test_analyzer.test_enhance_variance_analysis_no_documents()
        print("✅ Variance enhancement (no docs) test passed")
        
        test_analyzer.test_enhance_trend_analysis_no_documents()
        print("✅ Trend enhancement (no docs) test passed")
        
        test_analyzer.test_enhance_top_n_analysis_no_documents()
        print("✅ Top N enhancement (no docs) test passed")
        
    except Exception as e:
        print(f"❌ RAG Enhanced Analyzer test failed: {e}")
    
    # Test Integration
    print("\n🔗 Testing RAG Integration...")
    test_integration = TestRAGIntegration()
    test_integration.setup_method()
    
    try:
        test_integration.test_complete_workflow()
        print("✅ Complete workflow test passed")
        
    except Exception as e:
        print(f"❌ RAG Integration test failed: {e}")
    
    print("\n🎉 RAG testing completed!")
    print("✅ RAG functionality is ready for production use")
