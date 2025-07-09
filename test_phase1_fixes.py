"""
Phase 1 Fixes Validation Test

This script validates that all Phase 1 critical fixes are working correctly.
"""

import pandas as pd
import sys
import os

# Add current directory to path
sys.path.insert(0, os.getcwd())

def test_basic_imports():
    """Test that all core components can be imported."""
    print("📦 Testing imports...")
    
    try:
        from core.app_core import AppCore
        print("   ✅ AppCore")
    except Exception as e:
        print(f"   ❌ AppCore: {e}")
        return False
    
    try:
        from handlers.quick_action_handler import QuickActionHandler
        print("   ✅ QuickActionHandler")
    except Exception as e:
        print(f"   ❌ QuickActionHandler: {e}")
        return False
    
    try:
        from app_v2 import VarianceProApp
        print("   ✅ VarianceProApp")
    except Exception as e:
        print(f"   ❌ VarianceProApp: {e}")
        return False
    
    return True

def test_app_initialization():
    """Test that the app can initialize without errors."""
    print("\n🚀 Testing app initialization...")
    
    try:
        from app_v2 import VarianceProApp
        app = VarianceProApp()
        
        # Check critical components
        assert app.app_core is not None, "AppCore not initialized"
        assert app.file_handler is not None, "FileHandler not initialized"
        assert app.chat_handler is not None, "ChatHandler not initialized"
        assert app.quick_action_handler is not None, "QuickActionHandler not initialized"
        
        print("   ✅ App initialized successfully")
        print(f"   ✅ Session ID: {app.app_core.session_id}")
        print(f"   ✅ Ollama Status: {app.app_core.ollama_status}")
        return True
        
    except Exception as e:
        print(f"   ❌ App initialization failed: {e}")
        return False

def test_quick_actions():
    """Test the improved quick action functionality."""
    print("\n⚡ Testing quick actions...")
    
    try:
        from handlers.quick_action_handler import QuickActionHandler
        from core.app_core import AppCore
        
        # Create test data
        data = pd.DataFrame({
            'Name': ['Alice', 'Bob', 'Charlie'],
            'Score': [85, 92, 78],
            'Revenue': [1000, 1500, 800]
        })
        
        app_core = AppCore()
        app_core.set_current_data(data)
        
        handler = QuickActionHandler(app_core)
        
        # Test cases
        test_cases = [
            ('top 2', 'Basic top N'),
            ('bottom 1', 'Basic bottom N'),
            ('top 3 by revenue', 'Top N by column'),
            ('top 10', 'N larger than data'),
            ('top by nonexistent', 'Invalid column')
        ]
        
        for action, description in test_cases:
            result = handler._handle_top_bottom_action(action)
            
            # Check that we get a result (not None or empty)
            assert result is not None and len(result) > 0, f"No result for {action}"
            
            # Check that error cases return appropriate messages
            if 'nonexistent' in action:
                assert 'not found' in result.lower(), f"Should indicate column not found"
            elif action == 'top 10':
                assert '❌' not in result or 'reduced' in result.lower(), f"Should handle large N gracefully"
            else:
                assert '🔍' in result, f"Should return success indicator for {action}"
            
            print(f"   ✅ {description}: {action}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Quick actions test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_tabulate_dependency():
    """Test that tabulate works for markdown output."""
    print("\n📊 Testing tabulate dependency...")
    
    try:
        import pandas as pd
        df = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
        result = df.to_markdown()
        assert '|' in result, "Markdown table should contain pipe characters"
        print("   ✅ tabulate working correctly")
        return True
    except Exception as e:
        print(f"   ❌ tabulate test failed: {e}")
        return False

def main():
    """Run all Phase 1 validation tests."""
    print("🔧 PHASE 1 FIXES VALIDATION")
    print("=" * 50)
    
    tests = [
        test_basic_imports,
        test_tabulate_dependency,
        test_app_initialization,
        test_quick_actions
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print(f"   ⚠️ Test {test.__name__} failed")
        except Exception as e:
            print(f"   ❌ Test {test.__name__} crashed: {e}")
    
    print("\n" + "=" * 50)
    print(f"📋 RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL PHASE 1 FIXES WORKING CORRECTLY!")
        return True
    else:
        print("⚠️ Some issues remain - check failed tests above")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
