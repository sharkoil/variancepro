"""Test document upload fix"""
try:
    from app_v2 import VarianceProApp
    
    # Initialize app (with RAG disabled)
    app = VarianceProApp()
    print("✅ App initialized")
    
    # Test document upload with RAG disabled
    result = app.upload_documents(["test.pdf"])
    print(f"Document upload result: {result}")
    
    # Test document clear with RAG disabled  
    result = app.clear_documents()
    print(f"Document clear result: {result}")
    
    # Test document search with RAG disabled
    result = app.search_documents("test query")
    print(f"Document search result: {result}")
    
    if "temporarily disabled" in result:
        print("✅ Document methods properly handle RAG being disabled")
    else:
        print("❌ Document methods not handling RAG being disabled properly")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
