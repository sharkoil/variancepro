#!/usr/bin/env python3
"""
Simple test to verify the enhanced timescale analyzer functionality
"""

import sys
import os
import pandas as pd

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_enhanced_timescale():
    """Test the enhanced timescale analyzer directly"""
    print("🧪 Testing Enhanced Timescale Analyzer (Direct)")
    print("=" * 60)
    
    try:
        from analyzers.timescale_analyzer import TimescaleAnalyzer
        from config.settings import Settings
        
        # Load test data
        test_data_path = "sample_data/sample_variance_data.csv"
        df = pd.read_csv(test_data_path)
        print(f"✅ Loaded test data: {len(df)} rows, {len(df.columns)} columns")
        
        # Create analyzer
        settings = Settings()
        analyzer = TimescaleAnalyzer(settings.__dict__)
        
        # Run analysis
        print("\n🔍 Running timescale analysis...")
        result = analyzer.analyze(df, date_col='Date', value_cols=['Budget', 'Actual'])
        
        if result:
            print("✅ Analysis completed successfully")
            
            # Get formatted output
            formatted_output = analyzer.format_for_chat()
            
            print("\n📝 Enhanced Output Preview (first 500 chars):")
            print("-" * 50)
            print(formatted_output[:500] + "..." if len(formatted_output) > 500 else formatted_output)
            print("-" * 50)
            
            # Validate key features
            checks = [
                ("AI Summary", "Key Findings:" in formatted_output),
                ("Text-based separator", "---" in formatted_output),
                ("Detailed section marker", "DETAILED ANALYSIS" in formatted_output),
                ("Timescale content", "ANALYSIS" in formatted_output),
                ("Length check", len(formatted_output) > 200)
            ]
            
            print("\n🧪 Feature Validation:")
            all_passed = True
            for check_name, passed in checks:
                status = "✅" if passed else "❌"
                print(f"   {status} {check_name}")
                if not passed:
                    all_passed = False
            
            # Show structure analysis
            if "---" in formatted_output and "DETAILED ANALYSIS" in formatted_output:
                summary_part = formatted_output.split("---")[0]
                details_part = formatted_output.split("DETAILED ANALYSIS")[1] if "DETAILED ANALYSIS" in formatted_output else ""
                
                print(f"\n📊 Structure Analysis:")
                print(f"   • Summary section: {len(summary_part)} characters")
                print(f"   • Details section: {len(details_part)} characters")
                if len(details_part) > 0:
                    print(f"   • Summary/Details ratio: {len(summary_part)/len(details_part):.2f}")
            
            return all_passed
            
        else:
            print("❌ Analysis failed")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_enhanced_timescale()
    print(f"\n{'✅ SUCCESS: Enhanced timescale analyzer working perfectly!' if success else '❌ FAILED: Issues detected'}")
    exit(0 if success else 1)
