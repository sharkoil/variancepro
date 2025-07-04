#!/usr/bin/env python3
"""
Test the enhanced timescale analyzer in the main app context
"""

import sys
import os
import pandas as pd

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app_new import QuantCommanderApp

def test_app_integration():
    """Test the enhanced timescale analyzer in the main app"""
    print("🧪 Testing Enhanced Timescale Analyzer in Main App")
    print("=" * 60)
    
    # Load test data
    test_data_path = "sample_data/sample_variance_data.csv"
    if not os.path.exists(test_data_path):
        print(f"❌ Test data not found: {test_data_path}")
        return False
    
    try:
        # Create app instance
        app = QuantCommanderApp()
        
        # Load the test dataset
        df = pd.read_csv(test_data_path)
        print(f"✅ Loaded test data: {len(df)} rows, {len(df.columns)} columns")
        
        # Load data into app
        app.data = df
        app.data_loaded = True
        app.data_info = f"{len(df)} rows, {len(df.columns)} columns"
        
        # Test timescale analysis query
        print("\n🔍 Testing timescale analysis query...")
        user_query = "show me timescale analysis for budget and actual"
        
        response = app._process_user_query(user_query)
        
        print("\n" + "="*60)
        print("MAIN APP TIMESCALE ANALYSIS OUTPUT:")
        print("="*60)
        print(response)
        print("="*60)
        
        # Check if output contains expected elements
        checks = [
            ("Contains summary section", "Key Findings:" in response),
            ("Contains collapsible details", "<details>" in response and "</details>" in response),
            ("Contains timescale content", "TIMESCALE ANALYSIS" in response),
            ("Non-empty response", len(response) > 100)
        ]
        
        print("\n🧪 Integration Validation Checks:")
        all_passed = True
        for check_name, passed in checks:
            status = "✅" if passed else "❌"
            print(f"   {status} {check_name}")
            if not passed:
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Integration test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_app_integration()
    exit_code = 0 if success else 1
    print(f"\n{'✅ Integration Test PASSED' if success else '❌ Integration Test FAILED'}")
    exit(exit_code)
