"""
Quick verification that quantitative analysis is fixed
"""

print("🔍 Quick Variance Analysis Verification...")

try:
    # Test basic imports
    import pandas as pd
    from analyzers.quant_analyzer import QuantAnalyzer
    
    # Create simple test data
    data = pd.DataFrame({
        'Actual': [100, 200, 150],
        'Budget': [90, 180, 160]
    })
    
    # Test the exact workflow that was failing
    analyzer = QuantAnalyzer()
    result = analyzer.comprehensive_variance_analysis(
        data=data,
        actual_col='Actual',
        planned_col='Budget'
    )
    
    # This line was causing: "takes 1 positional argument but 2 were given"
    formatted = analyzer.format_comprehensive_analysis(result)
    
    print("✅ SUCCESS: Quantitative analysis is working!")
    print(f"✅ Generated {len(formatted)} characters of analysis")
    print("✅ No signature mismatch errors")
    
except Exception as e:
    print(f"❌ FAILED: {e}")
    import traceback
    traceback.print_exc()
