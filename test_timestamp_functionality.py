#!/usr/bin/env python3
"""
Test script for verifying timestamp functionality in Quant Commander v2.0
Tests that each chat message and quick action includes browser-local-time timestamps
"""

import sys
import os
from datetime import datetime
from typing import List, Dict

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the app
try:
    from app_v2 import QuantCommanderApp
    print("✅ Successfully imported QuantCommanderApp")
except ImportError as e:
    print(f"❌ Failed to import QuantCommanderApp: {e}")
    sys.exit(1)

def test_timestamp_functionality():
    """Test that timestamps are added to all chat messages"""
    print("\n🧪 Testing Timestamp Functionality")
    print("=" * 50)
    
    # Initialize the app
    app = QuantCommanderApp()
    print(f"✅ App initialized with session ID: {app.session_id}")
    
    # Test 1: Chat message with timestamp
    print("\n📝 Test 1: Chat message with timestamp")
    test_history = []
    
    # Send a test message
    test_message = "Hello, can you help me with data analysis?"
    updated_history, _ = app.chat_response(test_message, test_history)
    
    print(f"Original message: '{test_message}'")
    print(f"Number of messages after chat: {len(updated_history)}")
    
    if len(updated_history) >= 2:
        user_msg = updated_history[-2]
        assistant_msg = updated_history[-1]
        
        print(f"User message content: {user_msg['content']}")
        print(f"Assistant message content: {assistant_msg['content'][:100]}...")
        
        # Check if timestamps are present (look for [HH:MM:SS] format)
        user_has_timestamp = "[" in user_msg['content'] and "]" in user_msg['content']
        assistant_has_timestamp = "[" in assistant_msg['content'] and "]" in assistant_msg['content']
        
        print(f"✅ User message has timestamp: {user_has_timestamp}")
        print(f"✅ Assistant message has timestamp: {assistant_has_timestamp}")
        
        if user_has_timestamp and assistant_has_timestamp:
            print("🎉 Test 1 PASSED: Both messages have timestamps")
        else:
            print("❌ Test 1 FAILED: Missing timestamps")
    else:
        print("❌ Test 1 FAILED: Not enough messages in history")
    
    # Test 2: Quick action with timestamp
    print("\n🚀 Test 2: Quick action with timestamp")
    test_history_2 = []
    
    # Test quick action
    updated_history_2 = app._quick_action("summary", test_history_2)
    
    print(f"Number of messages after quick action: {len(updated_history_2)}")
    
    if len(updated_history_2) >= 2:
        user_msg_2 = updated_history_2[-2]
        assistant_msg_2 = updated_history_2[-1]
        
        print(f"Quick action user message: {user_msg_2['content']}")
        print(f"Quick action assistant message: {assistant_msg_2['content'][:100]}...")
        
        # Check if timestamps are present
        user_has_timestamp_2 = "[" in user_msg_2['content'] and "]" in user_msg_2['content']
        assistant_has_timestamp_2 = "[" in assistant_msg_2['content'] and "]" in assistant_msg_2['content']
        
        print(f"✅ Quick action user message has timestamp: {user_has_timestamp_2}")
        print(f"✅ Quick action assistant message has timestamp: {assistant_has_timestamp_2}")
        
        if user_has_timestamp_2 and assistant_has_timestamp_2:
            print("🎉 Test 2 PASSED: Quick action messages have timestamps")
        else:
            print("❌ Test 2 FAILED: Missing timestamps in quick action")
    else:
        print("❌ Test 2 FAILED: Not enough messages from quick action")
    
    # Test 3: Timestamp format validation
    print("\n⏰ Test 3: Timestamp format validation")
    
    # Test the helper method directly
    test_message = "Test message"
    test_timestamp = datetime.now().strftime("%H:%M:%S")
    timestamped_message = app._add_timestamp_to_message(test_message, test_timestamp)
    
    print(f"Original: '{test_message}'")
    print(f"Timestamped: '{timestamped_message}'")
    
    # Check format: should have HTML span with timestamp
    has_span = "<span" in timestamped_message and "</span>" in timestamped_message
    has_bracket_format = f"[{test_timestamp}]" in timestamped_message
    
    print(f"✅ Has HTML span: {has_span}")
    print(f"✅ Has correct timestamp format: {has_bracket_format}")
    
    if has_span and has_bracket_format:
        print("🎉 Test 3 PASSED: Timestamp format is correct")
    else:
        print("❌ Test 3 FAILED: Incorrect timestamp format")
    
    print("\n" + "=" * 50)
    print("🏁 Timestamp functionality testing complete!")

if __name__ == "__main__":
    test_timestamp_functionality()
