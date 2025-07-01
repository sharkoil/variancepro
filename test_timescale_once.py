#!/usr/bin/env python3
"""
Test Timescale Analysis Display Once
Verifies that timescale analysis only appears on first data load, not every Q&A
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

def test_timescale_once():
    """Test that timescale analysis only shows once"""
    
    print("🧪 TESTING TIMESCALE ANALYSIS DISPLAY")
    print("="*60)
    
    try:
        from app import AriaFinancialChat
        
        # Initialize chat system
        chat = AriaFinancialChat()
        
        # First analysis - should include timescale
        print("📋 1. First analysis (should include timescale)...")
        response1, status1 = chat.analyze_data("sample_financial_data.csv", "analyze this data")
        
        print(f"   Status: {status1}")
        print(f"   Contains timescale: {'timescale' in response1.lower()}")
        print(f"   Timescale shown flag: {chat.timescale_shown}")
        
        # Second analysis - should NOT include timescale
        print("\n📋 2. Second analysis (should NOT include timescale)...")
        response2, status2 = chat.analyze_data("sample_financial_data.csv", "what are the key trends?")
        
        print(f"   Status: {status2}")
        print(f"   Contains timescale: {'timescale' in response2.lower()}")
        print(f"   Timescale shown flag: {chat.timescale_shown}")
        
        # Third analysis - should NOT include timescale
        print("\n📋 3. Third analysis (should NOT include timescale)...")
        response3, status3 = chat.analyze_data("sample_financial_data.csv", "perform contribution analysis")
        
        print(f"   Status: {status3}")
        print(f"   Contains timescale: {'timescale' in response3.lower()}")
        print(f"   Timescale shown flag: {chat.timescale_shown}")
        
        # Verify results
        print(f"\n📊 RESULTS SUMMARY")
        print("-" * 30)
        
        timescale_in_first = 'timescale' in response1.lower()
        timescale_in_second = 'timescale' in response2.lower()
        timescale_in_third = 'timescale' in response3.lower()
        
        print(f"✅ First response includes timescale: {timescale_in_first}")
        print(f"❌ Second response excludes timescale: {not timescale_in_second}")
        print(f"❌ Third response excludes timescale: {not timescale_in_third}")
        
        if timescale_in_first and not timescale_in_second and not timescale_in_third:
            print(f"\n🎉 SUCCESS! Timescale analysis only shown once")
            return True
        else:
            print(f"\n❌ FAILED! Timescale analysis behavior incorrect")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_timescale_once()
