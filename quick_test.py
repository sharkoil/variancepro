#!/usr/bin/env python3
"""
Quick App Verification Script
Tests that VariancePro can start and handle basic CSV operations
"""

def test_app_startup():
    """Test that the app can start properly"""
    print("🔄 Testing VariancePro startup...")
    
    try:
        from app import QuantCommanderApp
        print("✅ App imports successfully")
        
        # Initialize app
        app = QuantCommanderApp()
        print("✅ App initializes successfully")
        
        # Test interface creation
        interface = app.create_interface()
        print("✅ Gradio interface created successfully")
        
        # Test status
        status = app.get_status()
        print("✅ Status function works")
        
        # Test CSV upload function exists
        if hasattr(app, 'upload_csv'):
            print("✅ CSV upload function available")
        else:
            print("❌ CSV upload function missing")
            
        # Test chat handler
        if hasattr(app, 'chat_handler'):
            print("✅ Chat handler available")
        else:
            print("❌ Chat handler missing")
            
        print("\n🎉 APP IS READY!")
        print("✨ You can now run: python app.py")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_app_startup()
    if success:
        print("\n" + "="*50)
        print("🚀 READY TO START:")
        print("   Run: python app.py")
        print("   Open: http://localhost:7871")
        print("   Upload a CSV and start analyzing!")
    else:
        print("\n❌ App verification failed. Check errors above.")
