"""
Test script for the new modular VariancePro architecture
Tests basic functionality and imports
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modular components can be imported successfully"""
    print("🧪 Testing modular imports...")
    
    try:
        # Test session manager
        from utils.session_manager import SessionManager
        session_mgr = SessionManager()
        print(f"✅ SessionManager: Session ID {session_mgr.session_id}")
        
        # Test basic app components
        from config.settings import Settings
        settings = Settings()
        print("✅ Settings imported successfully")
        
        # Test new UI components (these might fail if gradio isn't available, but imports should work)
        from ui.chat_handler import ChatHandler
        from ui.analysis_handlers import AnalysisHandlers
        from ui.interface_builder import InterfaceBuilder
        print("✅ UI components imported successfully")
        
        # Test main app (without initializing to avoid gradio dependency)
        print("✅ All imports successful!")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_session_manager():
    """Test session manager functionality"""
    print("\n🧪 Testing SessionManager functionality...")
    
    try:
        from utils.session_manager import SessionManager
        
        # Create session manager
        session = SessionManager()
        
        # Test basic properties
        session_id = session.get_session_id()
        print(f"✅ Session ID: {session_id}")
        
        # Test timestamp formatting
        timestamp = session.get_current_timestamp()
        print(f"✅ Current timestamp: {timestamp}")
        
        # Test chat timestamp
        chat_ts = session.format_chat_timestamp()
        print(f"✅ Chat timestamp: {chat_ts}")
        
        # Test message timestamping
        test_message = "This is a test message"
        timestamped = session.add_timestamp_to_message(test_message)
        print(f"✅ Timestamped message:\n{timestamped}")
        
        # Test welcome message
        welcome = session.create_welcome_message()
        print(f"✅ Welcome message:\n{welcome}")
        
        return True
        
    except Exception as e:
        print(f"❌ SessionManager test failed: {e}")
        return False

def test_modular_structure():
    """Test that the modular structure is working correctly"""
    print("\n🧪 Testing modular structure...")
    
    try:
        # Test that we can create mock app instance for handlers
        class MockApp:
            def __init__(self):
                from utils.session_manager import SessionManager
                self.session_manager = SessionManager()
                self.current_data = None
                self.llm_interpreter = None
                
        mock_app = MockApp()
        
        # Test chat handler initialization
        from ui.chat_handler import ChatHandler
        chat_handler = ChatHandler(mock_app)
        print("✅ ChatHandler initialized successfully")
        
        # Test analysis handlers initialization
        from ui.analysis_handlers import AnalysisHandlers
        analysis_handlers = AnalysisHandlers(mock_app)
        print("✅ AnalysisHandlers initialized successfully")
        
        # Test interface builder initialization
        from ui.interface_builder import InterfaceBuilder
        interface_builder = InterfaceBuilder(mock_app)
        print("✅ InterfaceBuilder initialized successfully")
        
        print("✅ Modular structure working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Modular structure test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🚀 Testing new modular VariancePro architecture...")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("Import Test", test_imports()))
    results.append(("SessionManager Test", test_session_manager()))
    results.append(("Modular Structure Test", test_modular_structure()))
    
    # Print results
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS:")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:<25} {status}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    if all_passed:
        print("🎉 All tests passed! The modular architecture is working correctly.")
        print("\n💡 Next steps:")
        print("1. Run 'python app.py' to start the new modular application")
        print("2. Test timestamp functionality in the web interface")
        print("3. Verify session management is working properly")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
    
    print(f"\n🆔 Test session completed")

if __name__ == "__main__":
    main()
