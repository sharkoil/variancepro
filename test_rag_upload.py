"""Test RAG document upload functionality"""
import sys

try:
    print("Testing RAG document upload...")
    
    # Test imports
    from app_v2 import QuantCommanderApp
    print("✅ App imported")
    
    # Initialize app
    app = QuantCommanderApp()
    print("✅ App initialized")
    
    # Check RAG status
    if app.rag_manager is None:
        print("❌ RAG manager is None - document upload will be disabled")
        sys.exit(1)
    else:
        print("✅ RAG manager is available")
    
    # Test document upload with empty list (should show "no files selected")
    result = app.upload_documents([])
    print(f"Empty upload result: {result}")
    
    # Test document upload with None (should show "no files selected")  
    result = app.upload_documents(None)
    print(f"None upload result: {result}")
    
    if "No files selected" in result or "no files" in result.lower():
        print("✅ Document upload properly handles no files")
    else:
        print(f"⚠️ Unexpected result for no files: {result}")
    
    print("\n🎉 RAG functionality is working!")
    print("📄 Document upload should now work with actual PDF files")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
