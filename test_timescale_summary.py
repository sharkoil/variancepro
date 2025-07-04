#!/usr/bin/env python3
"""
Test script for the enhanced timescale analyzer with AI summary
"""

import sys
import os
import pandas as pd

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from analyzers.timescale_analyzer import TimescaleAnalyzer
from config.settings import Settings

def test_timescale_summary():
    """Test the new AI summary functionality"""
    print("🧪 Testing Enhanced Timescale Analyzer with AI Summary")
    print("=" * 60)
    
    # Load test data
    test_data_path = "sample_data/sample_variance_data.csv"
    if not os.path.exists(test_data_path):
        print(f"❌ Test data not found: {test_data_path}")
        return False
    
    try:
        # Load the test dataset
        df = pd.read_csv(test_data_path)
        print(f"✅ Loaded test data: {len(df)} rows, {len(df.columns)} columns")
        print(f"   Columns: {list(df.columns)}")
        
        # Initialize settings
        settings = Settings()
        
        # Create and run timescale analyzer
        analyzer = TimescaleAnalyzer(settings.__dict__)
        
        print("\n🔍 Running timescale analysis...")
        result = analyzer.analyze(df, date_col='Date', value_cols=['Budget', 'Actual'])
        
        if not result:
            print("❌ Analysis failed")
            return False
            
        print("✅ Analysis completed successfully")
        
        # Test the new format_for_chat method
        print("\n📝 Testing enhanced format_for_chat with AI summary...")
        formatted_output = analyzer.format_for_chat()
        
        print("\n" + "="*60)
        print("ENHANCED TIMESCALE ANALYZER OUTPUT:")
        print("="*60)
        print(formatted_output)
        print("="*60)
        
        # Check if output contains expected elements
        checks = [
            ("AI Summary section", "Key Findings:" in formatted_output),
            ("Collapsible details", "<details>" in formatted_output and "</details>" in formatted_output),
            ("Summary tag", "<summary>" in formatted_output),
            ("Non-empty content", len(formatted_output) > 100)
        ]
        
        print("\n🧪 Validation Checks:")
        all_passed = True
        for check_name, passed in checks:
            status = "✅" if passed else "❌"
            print(f"   {status} {check_name}")
            if not passed:
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_timescale_summary()
    exit_code = 0 if success else 1
    print(f"\n{'✅ Test PASSED' if success else '❌ Test FAILED'}")
    exit(exit_code)
