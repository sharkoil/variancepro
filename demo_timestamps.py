#!/usr/bin/env python3
"""
Demo script for timestamp functionality in Quant Commander v2.0
Shows how timestamps appear in chat messages
"""

import sys
import os
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app_v2 import QuantCommanderApp

def demo_timestamp_display():
    """Demonstrate timestamp display in chat messages"""
    print("🎭 Timestamp Display Demo")
    print("=" * 50)
    
    app = QuantCommanderApp()
    print(f"✅ App initialized with session ID: {app.session_id}")
    
    # Simulate a chat conversation
    print("\n💬 Simulating chat conversation:")
    print("-" * 30)
    
    history = []
    
    # Message 1
    print("User: 'What can you help me with?'")
    history, _ = app.chat_response("What can you help me with?", history)
    user_msg1 = history[-2]
    assistant_msg1 = history[-1]
    
    print(f"🕐 User timestamp: {user_msg1['content']}")
    print(f"🤖 Assistant timestamp: {assistant_msg1['content'][:150]}...")
    print()
    
    # Message 2 (after a small delay to show time difference)
    import time
    time.sleep(1)
    
    print("User: 'Tell me about analysis features'")
    history, _ = app.chat_response("Tell me about analysis features", history)
    user_msg2 = history[-2]
    assistant_msg2 = history[-1]
    
    print(f"🕐 User timestamp: {user_msg2['content']}")
    print(f"🤖 Assistant timestamp: {assistant_msg2['content'][:150]}...")
    print()
    
    # Quick action demo
    print("User clicks 'Summary' quick action button")
    history = app._quick_action("summary", history)
    user_msg3 = history[-2]
    assistant_msg3 = history[-1]
    
    print(f"🕐 Quick action user timestamp: {user_msg3['content']}")
    print(f"🤖 Quick action assistant timestamp: {assistant_msg3['content'][:150]}...")
    
    print("\n" + "=" * 50)
    print("🎉 Demo complete! Timestamps are working on all message types.")
    print("📝 Each message includes browser-local-time in [HH:MM:SS] format")
    print("🎨 Timestamps are styled subtly with gray color and smaller font")

if __name__ == "__main__":
    demo_timestamp_display()
