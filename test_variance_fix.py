"""
Test script to validate quantitative analysis functionality after fixing the signature mismatch.
"""

import sys
import os
import pandas as pd

# Add project root to path
sys.path.insert(0, os.path.abspath('.'))

# Import required modules
from analyzers.quant_analyzer import QuantAnalyzer
from handlers.quick_action_handler import QuickActionHandler
from core.app_core import AppCore

def test_variance_analysis():
    """Test quantitative analysis with sample data"""
    
    # Create sample data
    sample_data = pd.DataFrame({
        'Product': ['Widget A', 'Widget B', 'Widget C', 'Widget D'],
        'Actual_Sales': [15000, 22000, 18000, 25000],
        'Planned_Sales': [12000, 20000, 20000, 23000],
        'Budget': [11000, 19000, 19500, 22000],
        'Date': pd.to_datetime(['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04'])
    })
    
    print("📊 Testing Variance Analysis...")
    print(f"Sample data shape: {sample_data.shape}")
    print(f"Columns: {list(sample_data.columns)}")
    print()
    
    # Test direct variance analyzer
    print("1. Testing QuantAnalyzer directly...")
    quant_analyzer = QuantAnalyzer()
    
    # Test variance column detection
    variance_columns = quant_analyzer.detect_variance_columns(sample_data)
    print(f"Detected variance columns: {variance_columns}")
    print()
    
    # Test comprehensive analysis
    try:
        result = quant_analyzer.comprehensive_variance_analysis(
            data=sample_data,
            actual_col='Actual_Sales',
            planned_col='Planned_Sales',
            date_col='Date'
        )
        
        if 'error' in result:
            print(f"❌ Analysis error: {result['error']}")
        else:
            print("✅ Comprehensive analysis completed successfully")
            print(f"Result keys: {list(result.keys())}")
            
            # Test formatting
            formatted_result = quant_analyzer.format_comprehensive_analysis(result)
            print("✅ Formatting completed successfully")
            print("\nFormatted Analysis:")
            print("=" * 50)
            print(formatted_result[:500] + "..." if len(formatted_result) > 500 else formatted_result)
            print("=" * 50)
            
    except Exception as e:
        print(f"❌ Error in quantitative analysis: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print()
    
    # Test via QuickActionHandler
    print("2. Testing via QuickActionHandler...")
    try:
        # Initialize app core and handler
        app_core = AppCore()
        app_core.current_data = sample_data
        
        handler = QuickActionHandler(app_core=app_core)
        
        # Test quantitative analysis button
        result = handler.handle_variance_analysis()
        
        print("✅ QuickActionHandler quantitative analysis completed")
        print("\nHandler Result:")
        print("=" * 50)
        print(result[:500] + "..." if len(result) > 500 else result)
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Error in QuickActionHandler: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_variance_analysis()
