"""
VariancePro TimescaleAnalyzer Test with Sample Financial Data
"""

import pandas as pd
import os
import sys

# Import the TimescaleAnalyzer class from app.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app import TimescaleAnalyzer

def test_with_sample_data():
    """Test TimescaleAnalyzer with sample financial data"""
    print("📊 Loading sample financial data...")
    
    # Load sample data
    df = pd.read_csv('sample_financial_data.csv')
    print(f"✅ Loaded dataset with {len(df)} rows and {len(df.columns)} columns")
    print(f"📊 Columns: {', '.join(df.columns)}")
    
    # Create analyzer
    analyzer = TimescaleAnalyzer()
    
    # Test time granularity detection
    granularity = analyzer.detect_time_granularity(df, 'Date')
    print(f"📅 Detected time granularity: {granularity}")
    
    # Generate full analysis
    print("🚀 Generating automatic timescale analysis...")
    full_analysis = analyzer.generate_timescale_analysis(df)
    
    # Save analysis to file
    with open("sample_data_analysis.md", "w", encoding="utf-8") as f:
        f.write(full_analysis)
    
    print(f"\n✅ Analysis complete! Output saved to sample_data_analysis.md")
    
    return full_analysis

if __name__ == "__main__":
    print("="*80)
    print("VariancePro TimescaleAnalyzer Test with Sample Financial Data")
    print("="*80)
    
    test_with_sample_data()
    
    print("="*80)
