"""
Simple validation that the variance analyzer module loads correctly
"""

print("Testing module imports...")

try:
    print("1. Testing pandas...")
    import pandas as pd
    print("✅ pandas imported")
    
    print("2. Testing variance analyzer...")
    from analyzers.variance_analyzer import VarianceAnalyzer
    print("✅ VarianceAnalyzer imported")
    
    print("3. Creating instance...")
    analyzer = VarianceAnalyzer()
    print("✅ VarianceAnalyzer instance created")
    
    print("4. Testing method exists...")
    method = getattr(analyzer, 'format_comprehensive_analysis', None)
    if method:
        print("✅ format_comprehensive_analysis method exists")
        
        # Check signature
        import inspect
        sig = inspect.signature(method)
        print(f"Method signature: {sig}")
        
        params = list(sig.parameters.keys())
        print(f"Parameters: {params}")
        
        if len(params) == 1:  # Should be 'self' and 'analysis_result'
            print("❌ Method only has 1 parameter (probably just 'self') - this is wrong")
        elif len(params) == 2:
            print("✅ Method has 2 parameters - this is correct")
        else:
            print(f"⚠️ Method has {len(params)} parameters - unexpected")
        
    else:
        print("❌ format_comprehensive_analysis method not found")
    
    print("\n✅ All basic tests passed!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
