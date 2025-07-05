#!/usr/bin/env python3
"""
Test script for timescale analysis integration with CSV upload
"""

import pandas as pd
import sys
import os

def test_timescale_integration():
    """Test that timescale analysis is automatically generated on CSV upload"""
    print("🧪 Testing Timescale Analysis Integration")
    print("=" * 50)
    
    try:
        # Create test data with dates
        test_data = pd.DataFrame({
            'Date': ['2024-01-01', '2024-02-01', '2024-03-01', '2024-04-01'],
            'Sales': [1000, 1500, 1200, 1800],
            'Revenue': [2000, 2200, 2100, 2400],
            'Product': ['Widget A', 'Widget B', 'Widget C', 'Widget A']
        })
        
        # Save to temp file
        test_file = 'test_timescale_data.csv'
        test_data.to_csv(test_file, index=False)
        print(f"✅ Created test file: {test_file}")
        
        # Import and test the app
        from app import QuantCommanderApp
        
        app = QuantCommanderApp()
        print("✅ QuantCommanderApp initialized")
        
        # Mock file object
        class MockFile:
            def __init__(self, name):
                self.name = name
        
        # Test upload
        print("🔄 Testing CSV upload with timescale analysis...")
        result = app.upload_csv(MockFile(test_file))
        
        print(f"📊 Upload returned {len(result)} items:")
        print(f"   • Preview: {result[0] is not None}")
        print(f"   • Data Summary: {result[1] is not None}")
        print(f"   • Analysis Message: {result[2] is not None}")
        print(f"   • Timescale Message: {result[3] is not None}")
        
        # Check timescale message content
        if result[3]:
            timescale_content = result[3]['content']
            print(f"✅ Timescale analysis generated ({len(timescale_content)} chars)")
            print("\n📈 Timescale Content Preview:")
            print("-" * 30)
            print(timescale_content[:500] + "..." if len(timescale_content) > 500 else timescale_content)
            print("-" * 30)
        else:
            print("❌ No timescale analysis was generated")
        
        # Clean up
        os.remove(test_file)
        print(f"🧹 Cleaned up test file: {test_file}")
        
        return result[3] is not None
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the test"""
    success = test_timescale_integration()
    
    if success:
        print("\n🎉 SUCCESS: Timescale analysis integration is working!")
        print("✨ CSV uploads with date columns will now automatically generate time-phase analysis")
        return 0
    else:
        print("\n⚠️ FAILED: Timescale analysis integration is not working properly")
        return 1

if __name__ == "__main__":
    sys.exit(main())
