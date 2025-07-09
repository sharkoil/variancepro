#!/usr/bin/env python3
"""
Test script to verify quick action behavior in Quant Commander v2.0
Tests that quick actions create proper user-assistant chat interactions
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app_v2 import QuantCommanderApp

def test_quick_actions():
    """Test that quick actions create proper chat interactions"""
    
    print("🧪 Testing Quant Commander v2.0 Quick Actions...")
    
    # Initialize app
    app = QuantCommanderApp()
    
    # Test initial empty history
    initial_history = [{"role": "assistant", "content": "Welcome to Quant Commander v2.0!"}]
    
    print(f"\n📋 Initial history length: {len(initial_history)}")
    
    # Test summary action without data
    print("\n🔍 Testing 'summary' action without data...")
    updated_history = app._quick_action("summary", initial_history.copy())
    
    print(f"📊 History length after summary action: {len(updated_history)}")
    print(f"👤 Last user message: {updated_history[-2]['content']}")
    print(f"🤖 Last assistant message: {updated_history[-1]['content'][:100]}...")
    
    # Test trends action without data
    print("\n📈 Testing 'trends' action without data...")
    updated_history2 = app._quick_action("trends", updated_history.copy())
    
    print(f"📊 History length after trends action: {len(updated_history2)}")
    print(f"👤 Last user message: {updated_history2[-2]['content']}")
    print(f"🤖 Last assistant message: {updated_history2[-1]['content'][:100]}...")
    
    # Test top 5 action without data
    print("\n🏆 Testing 'top 5' action without data...")
    updated_history3 = app._quick_action("top 5", updated_history2.copy())
    
    print(f"📊 History length after top 5 action: {len(updated_history3)}")
    print(f"👤 Last user message: {updated_history3[-2]['content']}")
    print(f"🤖 Last assistant message: {updated_history3[-1]['content'][:100]}...")
    
    # Verify each action created exactly 2 new messages (user + assistant)
    expected_lengths = [1, 3, 5, 7]  # Initial + 2 per action
    actual_lengths = [
        len(initial_history),
        len(updated_history), 
        len(updated_history2),
        len(updated_history3)
    ]
    
    print(f"\n✅ Verification:")
    print(f"Expected history lengths: {expected_lengths}")
    print(f"Actual history lengths: {actual_lengths}")
    
    if expected_lengths == actual_lengths:
        print("🎉 SUCCESS: All quick actions create proper user-assistant interactions!")
        return True
    else:
        print("❌ FAILURE: Quick actions not creating proper interactions!")
        return False

def test_chat_response():
    """Test that regular chat also creates proper interactions"""
    
    print("\n🧪 Testing regular chat response...")
    
    app = QuantCommanderApp()
    initial_history = [{"role": "assistant", "content": "Welcome!"}]
    
    # Test regular chat
    updated_history, cleared_input = app.chat_response("Hello", initial_history.copy())
    
    print(f"📊 History length after chat: {len(updated_history)}")
    print(f"📝 Input cleared: '{cleared_input}' (should be empty)")
    print(f"👤 User message: {updated_history[-2]['content']}")
    print(f"🤖 Assistant message: {updated_history[-1]['content'][:50]}...")
    
    if len(updated_history) == 3 and cleared_input == "":
        print("✅ Chat response working correctly!")
        return True
    else:
        print("❌ Chat response has issues!")
        return False

if __name__ == "__main__":
    print("🚀 Quant Commander v2.0 Quick Action Test Suite")
    print("=" * 50)
    
    try:
        quick_actions_ok = test_quick_actions()
        chat_response_ok = test_chat_response()
        
        print("\n" + "=" * 50)
        if quick_actions_ok and chat_response_ok:
            print("🎉 ALL TESTS PASSED! Quick actions work correctly.")
            sys.exit(0)
        else:
            print("❌ SOME TESTS FAILED! Check implementation.")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Test execution error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
