"""Test RAG components"""
try:
    print("Testing RAG imports...")
    from analyzers.rag_document_manager import RAGDocumentManager
    print("✅ RAGDocumentManager imported")
    
    from analyzers.rag_enhanced_analyzer import RAGEnhancedAnalyzer
    print("✅ RAGEnhancedAnalyzer imported")
    
    # Test initialization
    rag_manager = RAGDocumentManager()
    print("✅ RAGDocumentManager initialized")
    
    rag_analyzer = RAGEnhancedAnalyzer(rag_manager)
    print("✅ RAGEnhancedAnalyzer initialized")
    
    print("🎉 RAG components working!")
    
except Exception as e:
    print(f"❌ RAG Error: {e}")
    import traceback
    traceback.print_exc()
