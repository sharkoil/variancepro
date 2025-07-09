"""
Direct test of quantitative analysis using actual test data
"""

import pandas as pd
import sys
import os

# Add project to path
sys.path.insert(0, os.path.abspath('.'))

def test_with_actual_data():
    """Test quantitative analysis with real test data"""
    
    print("📊 Testing quantitative analysis with actual CSV data...")
    
    try:
        # Load test data
        data = pd.read_csv('oob_test_data.csv')
        print(f"✅ Loaded test data: {data.shape}")
        print(f"Columns: {list(data.columns)}")
        
        # Import and test variance analyzer
        from analyzers.quant_analyzer import QuantAnalyzer
        
        analyzer = QuantAnalyzer()
        print("✅ QuantAnalyzer created")
        
        # Detect variance columns
        variance_pairs = analyzer.detect_variance_columns(data)
        print(f"✅ Detected variance pairs: {variance_pairs}")
        
        # Run comprehensive analysis 
        result = analyzer.comprehensive_variance_analysis(
            data=data,
            actual_col='Actuals',
            planned_col='Budget',
            date_col='Date'
        )
        
        print(f"✅ Analysis completed, type: {type(result)}")
        
        if 'error' in result:
            print(f"❌ Analysis error: {result['error']}")
            return False
        else:
            print(f"Result keys: {list(result.keys())}")
        
        # Test the format method that was broken
        formatted = analyzer.format_comprehensive_analysis(result)
        print(f"✅ Formatting successful: {len(formatted)} characters")
        
        # Show first part of result
        print("\n" + "="*50)
        print("FORMATTED QUANTITATIVE ANALYSIS")
        print("="*50)
        print(formatted[:500] + "..." if len(formatted) > 500 else formatted)
        print("="*50)
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_quick_action_handler():
    """Test the quick action handler with actual data"""
    
    print("\n📋 Testing QuickActionHandler with actual data...")
    
    try:
        # Load test data  
        data = pd.read_csv('oob_test_data.csv')
        
        # Import components
        from core.app_core import AppCore
        from handlers.quick_action_handler import QuickActionHandler
        
        # Initialize
        app_core = AppCore()
        app_core.current_data = data
        
        handler = QuickActionHandler(app_core=app_core)
        print("✅ QuickActionHandler initialized")
        
        # Test quantitative analysis via handler (this was the broken part)
        result = handler.handle_variance_analysis()
        
        print(f"✅ Handler quantitative analysis completed: {len(result)} chars")
        
        # Show result preview
        print("\n" + "="*50)
        print("HANDLER QUANTITATIVE ANALYSIS RESULT")
        print("="*50)
        print(result[:300] + "..." if len(result) > 300 else result)
        print("="*50)
        
        return True
        
    except Exception as e:
        print(f"❌ Handler test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Quant Commander Variance Analysis Validation")
    print("="*60)
    
    success1 = test_with_actual_data()
    success2 = test_quick_action_handler()
    
    print("\n" + "="*60)
    print("FINAL RESULTS")
    print("="*60)
    
    if success1 and success2:
        print("🎉 ALL TESTS PASSED - Quantitative analysis is fixed!")
    else:
        print("❌ Some tests failed - see errors above")
        
    print("="*60)
