"""Test RAG analyzer step by step"""
try:
    print("Step 1: Import RAG manager...")
    from analyzers.rag_document_manager import RAGDocumentManager
    print("✅ RAGDocumentManager imported")
    
    print("Step 2: Initialize RAG manager...")
    rag_manager = RAGDocumentManager()
    print("✅ RAGDocumentManager initialized")
    
    print("Step 3: Import RAG analyzer...")
    from analyzers.rag_enhanced_analyzer import RAGEnhancedAnalyzer
    print("✅ RAGEnhancedAnalyzer imported")
    
    print("Step 4: Initialize RAG analyzer...")
    print("(This might test Ollama connection...)")
    rag_analyzer = RAGEnhancedAnalyzer(rag_manager)
    print("✅ RAGEnhancedAnalyzer initialized")
    
    print("🎉 All RAG components working!")
    
except Exception as e:
    print(f"❌ Error at step: {e}")
    import traceback
    traceback.print_exc()
