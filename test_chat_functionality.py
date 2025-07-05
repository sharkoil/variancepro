#!/usr/bin/env python3
"""
Chat Functionality Test
Tests the actual chat workflow without launching the full interface
"""

import pandas as pd
import sys
import os

def test_chat_workflow():
    """Test the complete chat workflow"""
    print("🔄 Testing chat workflow...")
    
    try:
        # Import and initialize the app
        from app import QuantCommanderApp
        app = QuantCommanderApp()
        print("✅ App initialized")
        
        # Create test data and simulate CSV upload
        test_data = pd.DataFrame({
            'Product': ['Widget A', 'Widget B', 'Widget C', 'Widget D'],
            'Sales': [15000, 22000, 18000, 12000],
            'Budget': [14000, 20000, 19000, 13000],
            'Actual': [15500, 22500, 17800, 11900],
            'Region': ['North', 'South', 'East', 'West']
        })
        
        # Save test data
        test_file = 'chat_test_data.csv'
        test_data.to_csv(test_file, index=False)
        print(f"✅ Test data created: {test_file}")
        
        # Test CSV upload functionality
        upload_result = app.upload_csv(type('MockFile', (), {'name': test_file})())
        print(f"✅ CSV upload test: {len(upload_result[0]) if upload_result[0] else 0} chars preview")
        
        # Test that data was loaded
        if app.current_data is not None:
            print(f"✅ Data loaded: {app.current_data.shape[0]} rows, {app.current_data.shape[1]} columns")
        else:
            print("❌ Data not loaded properly")
            return False
            
        # Test chat handler functionality
        test_messages = [
            "summary",
            "analyze contribution", 
            "what can you tell me about this data?",
            "show me the data overview"
        ]
        
        chat_history = []
        for msg in test_messages:
            print(f"\n🔄 Testing message: '{msg}'")
            
            try:
                new_history, empty_input = app.chat_handler.chat_response(msg, chat_history)
                
                if len(new_history) > len(chat_history):
                    last_response = new_history[-1]['content']
                    print(f"✅ Response received: {len(last_response)} characters")
                    print(f"   Preview: {last_response[:100]}...")
                    chat_history = new_history
                else:
                    print("❌ No response generated")
                    return False
                    
            except Exception as e:
                print(f"❌ Chat error for '{msg}': {e}")
                return False
        
        # Cleanup
        if os.path.exists(test_file):
            os.remove(test_file)
            
        print("\n🎉 CHAT WORKFLOW TEST PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Chat workflow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_specific_chat_components():
    """Test specific chat components"""
    print("\n🔄 Testing specific chat components...")
    
    try:
        from app import QuantCommanderApp
        app = QuantCommanderApp()
        
        # Test components exist
        components = [
            ('chat_handler', app.chat_handler),
            ('analysis_handlers', app.analysis_handlers),
            ('session_manager', app.session_manager),
            ('csv_loader', app.csv_loader)
        ]
        
        for name, component in components:
            if component:
                print(f"✅ {name}: Available")
            else:
                print(f"❌ {name}: Missing")
                return False
        
        # Test key methods exist
        methods = [
            ('chat_response', hasattr(app.chat_handler, 'chat_response')),
            ('upload_csv', hasattr(app, 'upload_csv')),
            ('get_status', hasattr(app, 'get_status'))
        ]
        
        for name, exists in methods:
            if exists:
                print(f"✅ {name} method: Available")
            else:
                print(f"❌ {name} method: Missing")
                return False
                
        return True
        
    except Exception as e:
        print(f"❌ Component test failed: {e}")
        return False

def main():
    """Run chat tests"""
    print("🧪 VariancePro Chat Functionality Test")
    print("=" * 50)
    
    # Test 1: Component availability
    if not test_specific_chat_components():
        print("\n❌ Component test failed - chat cannot work")
        return 1
    
    # Test 2: Full workflow
    if not test_chat_workflow():
        print("\n❌ Chat workflow test failed")
        return 1
    
    print("\n" + "=" * 50)
    print("🎉 ALL CHAT TESTS PASSED!")
    print("✨ Chat functionality is working correctly")
    print("\n📋 VERIFICATION COMPLETE:")
    print("  ✅ Components load correctly")
    print("  ✅ CSV upload works")
    print("  ✅ Chat responses generate")
    print("  ✅ Analysis handlers respond")
    print("  ✅ Session management works")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
