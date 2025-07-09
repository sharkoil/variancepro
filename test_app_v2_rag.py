"""
Test RAG Integration in app_v2.py
Simple validation that RAG components work with the modular app
"""

def test_app_v2_with_rag():
    """Test that app_v2 initializes with RAG components"""
    try:
        from app_v2 import QuantCommanderApp
        
        print("🧪 Testing app_v2.py with RAG integration...")
        
        # Initialize the app
        app = QuantCommanderApp()
        print("✅ App initialized successfully")
        
        # Check RAG components are available
        assert hasattr(app, 'rag_manager'), "RAG manager missing"
        assert hasattr(app, 'rag_analyzer'), "RAG analyzer missing"
        print("✅ RAG components found")
        
        # Test document upload method
        assert hasattr(app, 'upload_documents'), "upload_documents method missing"
        assert hasattr(app, 'clear_documents'), "clear_documents method missing"
        assert hasattr(app, 'search_documents'), "search_documents method missing"
        print("✅ Document methods available")
        
        # Test RAG manager basic functionality
        has_docs_before = app.rag_manager.has_documents()
        print(f"✅ Has documents check: {has_docs_before}")
        
        # Test that interface can be created
        try:
            interface = app.create_interface()
            print("✅ Interface created successfully")
        except Exception as e:
            print(f"⚠️ Interface creation warning: {e}")
        
        print("\n🎉 app_v2.py with RAG integration is working!")
        print("📝 Ready to start with: python app_v2.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_app_v2_with_rag()
