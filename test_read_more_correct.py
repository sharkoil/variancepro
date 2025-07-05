#!/usr/bin/env python3
"""Test the read more/less functionality in the correct app.py"""

import sys
import os
sys.path.insert(0, '.')

def test_read_more_in_app():
    print("🧪 Testing Read More/Less in Correct app.py")
    print("=" * 50)
    
    try:
        # Import the correct app
        from app import QuantCommanderApp
        
        print("1. ✅ App imported successfully")
        
        # Initialize the app
        app = QuantCommanderApp()
        print("2. ✅ App initialized")
        
        # Get the welcome message
        welcome_message = app.chat_handler.session_manager.create_welcome_message()
        print("3. ✅ Welcome message generated")
        
        # Check for read more/less elements
        checks = [
            ('expandable-content', 'Expandable container div'),
            ('class="dots"', 'Dots element'),
            ('class="more-text"', 'Hidden content element'),
            ('toggleWelcomeContent', 'JavaScript toggle function'),
            ('Read More', 'Read more button text'),
            ('Read Less', 'Read less button text'),
            ('Analysis Types', 'Content sections'),
            ('Smart Features', 'Feature descriptions'),
            ('How to Get Started', 'Instructions'),
            ('Advanced Capabilities', 'Advanced features')
        ]
        
        print("\n📋 Checking read more/less components:")
        all_passed = True
        
        for check, description in checks:
            if check in welcome_message:
                print(f"   ✅ {description}")
            else:
                print(f"   ❌ {description} - NOT FOUND")
                all_passed = False
        
        if all_passed:
            print("\n🎉 All read more/less components found!")
            print(f"\n📊 Welcome message length: {len(welcome_message)} characters")
            
            # Show first few lines
            lines = welcome_message.split('\n')
            print(f"📝 First 5 lines:")
            for i, line in enumerate(lines[:5]):
                print(f"   {i+1}: {line}")
                
        else:
            print("\n❌ Some components missing - functionality may not work")
            
        # Test interface creation
        print("\n4. Testing interface creation...")
        interface = app.create_interface()
        print("✅ Interface created successfully")
        
        print(f"\n🎯 Test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_read_more_in_app()
