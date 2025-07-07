"""Step by step RAG validation"""
try:
    print("Step 1: Testing basic imports...")
    import os
    import sys
    print("✅ Basic imports OK")
    
    print("Step 2: Testing PDF libraries...")
    try:
        import PyPDF2
        print("✅ PyPDF2 available")
    except ImportError as e:
        print(f"❌ PyPDF2 not available: {e}")
    
    try:
        import fitz
        print("✅ PyMuPDF (fitz) available")
    except ImportError as e:
        print(f"❌ PyMuPDF not available: {e}")
    
    print("Step 3: Testing RAG manager import...")
    from analyzers.rag_document_manager import RAGDocumentManager
    print("✅ RAGDocumentManager imported")
    
    print("Step 4: Testing RAG manager initialization...")
    manager = RAGDocumentManager()
    print("✅ RAGDocumentManager initialized")
    
    print("Step 5: Testing RAG analyzer import...")
    from analyzers.rag_enhanced_analyzer import RAGEnhancedAnalyzer
    print("✅ RAGEnhancedAnalyzer imported")
    
    print("Step 6: Testing RAG analyzer initialization...")
    analyzer = RAGEnhancedAnalyzer(manager)
    print("✅ RAGEnhancedAnalyzer initialized")
    
    print("\n🎉 All RAG components working!")
    
except Exception as e:
    print(f"❌ Error at step: {e}")
    import traceback
    traceback.print_exc()
