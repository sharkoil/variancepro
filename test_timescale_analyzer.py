"""
VariancePro TimescaleAnalyzer Test Script

This script tests the automatic timescale analysis functionality by:
1. Loading a sample dataset
2. Creating a TimescaleAnalyzer instance
3. Running the analysis functions
4. Displaying the results
"""

import pandas as pd
import numpy as np
import os
import sys
from datetime import datetime, timedelta

# Import the TimescaleAnalyzer class from app.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app import TimescaleAnalyzer

def create_test_data():
    """Create a synthetic dataset for testing"""
    # Create date range for the past 2 years with daily data
    end_date = datetime.now()
    start_date = end_date - timedelta(days=730)  # ~2 years
    
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Create a DataFrame
    df = pd.DataFrame({
        'date': dates,
        'sales': np.random.normal(1000, 200, size=len(dates)) * (1 + 0.0005 * np.arange(len(dates))),  # Trending up
        'expenses': np.random.normal(800, 150, size=len(dates)) * (1 + 0.0003 * np.arange(len(dates))),  # Trending up slower
        'customers': np.random.normal(500, 100, size=len(dates)) * (1 + np.sin(np.arange(len(dates)) * 0.1) * 0.1),  # Cyclical
    })
    
    # Add some quarterly effect (e.g., Q4 boost for sales)
    for i, date in enumerate(dates):
        if date.month in [10, 11, 12]:  # Q4 months
            df.loc[i, 'sales'] *= 1.2
    
    # Add some monthly seasonality
    for i, date in enumerate(dates):
        # Month-end effect
        if date.day >= 25:
            df.loc[i, 'sales'] *= 1.1
            df.loc[i, 'customers'] *= 1.15
    
    # Calculate profit
    df['profit'] = df['sales'] - df['expenses']
    
    # Add categorical column for region
    regions = ['North', 'South', 'East', 'West']
    df['region'] = np.random.choice(regions, size=len(dates))
    
    # Add product categories
    products = ['Electronics', 'Clothing', 'Home', 'Food']
    df['product'] = np.random.choice(products, size=len(dates))
    
    return df

def test_timescale_analyzer():
    """Test the TimescaleAnalyzer class"""
    print("🔍 Testing TimescaleAnalyzer functionality...")
    
    # Create test data
    df = create_test_data()
    print(f"✅ Created test dataset with {len(df)} rows and {len(df.columns)} columns")
    print(f"📅 Date range: {df['date'].min()} to {df['date'].max()}")
    print(f"📊 Columns: {', '.join(df.columns)}")
    
    # Create analyzer
    analyzer = TimescaleAnalyzer()
    print("✅ Created TimescaleAnalyzer instance")
    
    # Test time granularity detection
    granularity = analyzer.detect_time_granularity(df, 'date')
    print(f"📅 Detected time granularity: {granularity}")
    
    # Test aggregations
    value_cols = ['sales', 'expenses', 'profit', 'customers']
    print(f"🔢 Testing aggregations for columns: {', '.join(value_cols)}")
    
    aggregations = analyzer.prepare_timescale_aggregations(df, 'date', value_cols)
    for time_scale, agg_data in aggregations.items():
        if "data" in agg_data:
            print(f"✅ {time_scale.title()} aggregation: {len(agg_data['data'])} periods")
    
    # Test period-over-period analysis
    print("📈 Testing period-over-period analysis...")
    pop_analysis = analyzer.calculate_period_over_period_analysis(aggregations, value_cols)
    
    for time_scale, metrics in pop_analysis.items():
        print(f"📊 {time_scale.title()} analysis:")
        for metric, data in metrics.items():
            summary = data["summary"]
            print(f"  - {metric}: {summary['total_periods']} periods, " +
                  f"avg change: {summary['avg_pct_change']:.2f}%, " +
                  f"latest: {summary['latest_change']:.2f}%")
    
    # Test insights generation
    print("\n🧠 Generating insights...")
    insights = analyzer._generate_summary_insights(pop_analysis)
    print("\n" + insights)
    
    # Test full analysis
    print("\n🚀 Testing full automatic analysis...")
    full_analysis = analyzer.generate_timescale_analysis(df)
    print("\n" + full_analysis)
    
    return full_analysis

if __name__ == "__main__":
    print("="*80)
    print("VariancePro TimescaleAnalyzer Test")
    print("="*80)
    
    analysis = test_timescale_analyzer()
    
    # Save analysis to file
    with open("timescale_analysis_test_output.md", "w") as f:
        f.write(analysis)
    
    print("\n"+"="*80)
    print("Test completed! Results saved to timescale_analysis_test_output.md")
    print("="*80)
