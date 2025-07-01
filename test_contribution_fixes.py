#!/usr/bin/env python3
"""
Test Contribution Analysis Fixes
Verifies contribution analysis doesn't include timescale and doesn't suggest code
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

def test_contribution_fixes():
    """Test that contribution analysis is clean without timescale or code"""
    
    print("🧪 TESTING CONTRIBUTION ANALYSIS FIXES")
    print("="*60)
    
    try:
        from app import AriaFinancialChat
        
        # Initialize chat system
        chat = AriaFinancialChat()
        
        # Test contribution analysis request
        print("📋 Testing contribution analysis...")
        response, status = chat.analyze_data("sample_financial_data.csv", "perform contribution analysis")
        
        print(f"📊 Status: {status}")
        print(f"📝 Response length: {len(response)} characters")
        
        # Check for issues
        issues = []
        
        # Test 1: Should NOT contain timescale analysis
        if 'timescale' in response.lower():
            issues.append("❌ Contains timescale analysis")
        else:
            print("✅ No timescale analysis (correct)")
        
        # Test 2: Should NOT contain code suggestions
        code_indicators = ['```', 'python', 'import pandas', 'df.', 'import matplotlib', 'plt.']
        has_code = any(indicator in response.lower() for indicator in code_indicators)
        
        if has_code:
            issues.append("❌ Contains code suggestions")
        else:
            print("✅ No code suggestions (correct)")
        
        # Test 3: Should contain contribution analysis
        if 'contribution' in response.lower() and 'pareto' in response.lower():
            print("✅ Contains contribution analysis")
        else:
            issues.append("❌ Missing contribution analysis")
        
        # Test 4: Should have correct status
        if status == "[SUCCESS] Contribution analysis completed":
            print("✅ Correct status message")
        else:
            issues.append(f"❌ Wrong status: {status}")
        
        # Show excerpt of response
        print(f"\n💬 Response preview (first 300 chars):")
        print("-" * 40)
        print(response[:300] + "..." if len(response) > 300 else response)
        
        # Summary
        print(f"\n📊 TEST RESULTS")
        print("-" * 30)
        
        if not issues:
            print("🎉 ALL TESTS PASSED!")
            print("✅ Contribution analysis is clean")
            print("✅ No timescale redundancy")
            print("✅ No code suggestions")
            return True
        else:
            print("❌ ISSUES FOUND:")
            for issue in issues:
                print(f"   {issue}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_contribution_fixes()
