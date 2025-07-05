#!/usr/bin/env python3
"""Test the read more/less functionality in the welcome message"""

import sys
import os
sys.path.insert(0, '.')

def test_read_more_functionality():
    print("🧪 Testing Read More/Less Functionality")
    print("=" * 50)
    
    try:
        # Import the app
        from app_new import QuantCommanderApp
        
        print("1. ✅ App imported successfully")
        
        # Initialize the app
        app = QuantCommanderApp()
        print("2. ✅ App initialized")
        
        # Check if the interface can be created
        interface = app.create_interface()
        print("3. ✅ Interface created successfully")
        
        # Extract the welcome message content
        chatbot_config = None
        for component in interface.blocks.values():
            if hasattr(component, 'value') and component.value:
                if isinstance(component.value, list) and len(component.value) > 0:
                    if 'Welcome to VariancePro' in str(component.value[0]):
                        chatbot_config = component.value[0]
                        break
        
        if chatbot_config:
            content = chatbot_config['content']
            print("4. ✅ Welcome message found")
            
            # Check for read more/less elements
            checks = [
                ('expandable-content', 'Expandable container div'),
                ('class="dots"', 'Dots element'),
                ('class="more-text"', 'Hidden content element'),
                ('toggleWelcomeContent', 'JavaScript toggle function'),
                ('Read More', 'Read more button text'),
                ('Read Less', 'Read less button text')
            ]
            
            print("\n📋 Checking read more/less components:")
            all_passed = True
            
            for check, description in checks:
                if check in content:
                    print(f"   ✅ {description}")
                else:
                    print(f"   ❌ {description} - NOT FOUND")
                    all_passed = False
            
            if all_passed:
                print("\n🎉 All read more/less components found!")
                
                # Check content structure
                print("\n📝 Content structure validation:")
                
                # Count content sections
                sections = [
                    'Analysis Types',
                    'Smart Features', 
                    'How to Get Started',
                    'Advanced Capabilities'
                ]
                
                found_sections = 0
                for section in sections:
                    if section in content:
                        print(f"   ✅ {section} section found")
                        found_sections += 1
                    else:
                        print(f"   ❌ {section} section missing")
                
                print(f"\n📊 Found {found_sections}/{len(sections)} content sections")
                
                if found_sections >= 3:
                    print("✅ Sufficient content for read more/less functionality")
                else:
                    print("⚠️ May need more content sections")
            
            else:
                print("\n❌ Some components missing - functionality may not work")
                
        else:
            print("4. ❌ Welcome message not found in interface")
            
        print(f"\n🎯 Test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_read_more_functionality()
