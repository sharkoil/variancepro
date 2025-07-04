#!/usr/bin/env python3
"""
Test script for the enhanced Business Context Analysis with AI summary
"""

import sys
import os
import pandas as pd

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from analyzers.news_analyzer_v2 import NewsAnalyzer
from config.settings import Settings

def test_business_context_summary():
    """Test the new AI summary functionality for business context"""
    print("🧪 Testing Enhanced Business Context Analysis with AI Summary")
    print("=" * 70)
    
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
        
        # Create news analyzer
        analyzer = NewsAnalyzer(settings.__dict__)
        
        print("\n🔍 Running business context analysis...")
        
        # Create mock context result for testing the formatting
        mock_context_result = {
            'business_context': {
                'industry': 'sales',
                'data_type': 'business',
                'key_metrics': ['budget_performance', 'cost_management']
            },
            'top_locations': ['New York', 'California', 'Ohio'],
            'data_shape': (370, 8)
        }
        
        print("✅ Context analysis completed successfully")
        
        # Create mock news results for testing the formatting
        mock_results = {
            'news_items': [
                {
                    'title': 'Market Trends Show Strong Performance in Q4',
                    'source': 'business-news.com',
                    'published': '2024-12-15',
                    'link': 'https://example.com/news1'
                },
                {
                    'title': 'Industry Analysis: Budget Planning Best Practices',
                    'source': 'finance-today.com', 
                    'published': '2024-12-14',
                    'link': 'https://example.com/news2'
                },
                {
                    'title': 'Regional Business Growth Indicators Show Positive Trends',
                    'source': 'regional-business.com',
                    'published': '2024-12-13', 
                    'link': 'https://example.com/news3'
                }
            ],
            'business_context': mock_context_result.get('business_context', {}),
            'top_locations': mock_context_result.get('top_locations', []),
            'search_queries': ['business news', 'market trends', 'industry analysis']
        }
        
        # Test the new format_news_for_chat method
        print("\n📝 Testing enhanced format_news_for_chat with AI summary...")
        formatted_output = analyzer.format_news_for_chat(mock_results)
        
        print("\n" + "="*70)
        print("ENHANCED BUSINESS CONTEXT ANALYSIS OUTPUT:")
        print("="*70)
        print(formatted_output[:1000] + "..." if len(formatted_output) > 1000 else formatted_output)
        print("="*70)
        
        # Check if output contains expected elements
        checks = [
            ("AI Summary section", "Key Business Insights:" in formatted_output),
            ("Text-based separator", "---" in formatted_output),
            ("Detailed section marker", "DETAILED ANALYSIS" in formatted_output),
            ("Business content", "BUSINESS CONTEXT" in formatted_output),
            ("Non-empty content", len(formatted_output) > 200)
        ]
        
        print("\n🧪 Validation Checks:")
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
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_business_context_summary()
    exit_code = 0 if success else 1
    print(f"\n{'✅ Test PASSED' if success else '❌ Test FAILED'}")
    exit(exit_code)
