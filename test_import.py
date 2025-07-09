#!/usr/bin/env python3
"""
Quick test script to validate app functionality
"""

try:
    print("Testing imports...")
    
    # Test core imports
    from core.app_core import AppCore
    print("✅ AppCore imported")
    
    from handlers.file_handler import FileHandler
    print("✅ FileHandler imported")
    
    from handlers.chat_handler import ChatHandler
    print("✅ ChatHandler imported")
    
    from handlers.quick_action_handler import QuickActionHandler
    print("✅ QuickActionHandler imported")
    
    # Test main app
    from app_v2 import QuantCommanderApp
    print("✅ QuantCommanderApp imported")
    
    # Test initialization
    app = QuantCommanderApp()
    print("✅ App initialized successfully")
    
    print("\n🎉 All basic functionality validated!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
