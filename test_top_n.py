#!/usr/bin/env python3
"""
Test script for Top N / Bottom N parameter extraction
"""

import pandas as pd
from app_new import VarianceProApp

def test_parameter_extraction():
    """Test various Top N / Bottom N queries"""
    
    # Load sample data
    sample_data = pd.read_csv('sample_variance_data.csv')
    print(f"Sample data loaded: {sample_data.shape}")
    
    # Initialize app
    app = VarianceProApp()
    app.current_data = sample_data
    
    # Set up CSV loader info
    app.csv_loader.column_info = {
        'date_columns': ['Date'],
        'numeric_columns': ['Budget', 'Actual', 'Margin'],
        'category_columns': ['Product', 'Category', 'State', 'Type']
    }
    
    app.column_suggestions = {
        'category_columns': ['Product', 'Category', 'State', 'Type'],
        'value_columns': ['Budget', 'Actual', 'Margin']
    }
    
    # Test queries
    test_queries = [
        "Show me the top 10 products by budget",
        "What are the bottom 5 states by actual sales",
        "Top 3 categories by margin",
        "Worst 7 performers by budget",
        "Best 5 states",
        "Bottom performers"
    ]
    
    print("\n" + "="*50)
    print("TESTING TOP N / BOTTOM N PARAMETER EXTRACTION")
    print("="*50)
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        print("-" * 40)
        
        # Test both top and bottom
        is_bottom = any(word in query.lower() for word in ['bottom', 'worst'])
        
        try:
            result = app._perform_top_n_analysis(query, is_bottom=is_bottom)
            print("✅ Analysis completed successfully")
            print(f"Result length: {len(result)} characters")
            
            # Show first few lines of result
            lines = result.split('\n')[:5]
            for line in lines:
                print(f"  {line}")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_parameter_extraction()
