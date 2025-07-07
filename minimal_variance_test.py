"""
Minimal test to verify variance analysis signature fix
"""

try:
    from analyzers.variance_analyzer import VarianceAnalyzer
    print("✅ VarianceAnalyzer imported successfully")
    
    # Create instance
    analyzer = VarianceAnalyzer()
    print("✅ VarianceAnalyzer instance created")
    
    # Test sample data
    import pandas as pd
    data = pd.DataFrame({
        'actual': [100, 200, 150],
        'planned': [90, 180, 160]
    })
    
    # Test the analysis method
    result = analyzer.comprehensive_variance_analysis(
        data=data,
        actual_col='actual',
        planned_col='planned'
    )
    
    print(f"✅ Analysis completed: {type(result)}")
    print(f"Result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
    
    # Test the format method that was causing issues
    formatted = analyzer.format_comprehensive_analysis(result)
    print(f"✅ Formatting completed: {len(formatted)} characters")
    print("First 100 chars:", formatted[:100])
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
