#!/usr/bin/env python3
"""
Test script for NewsAnalyzer integration
"""

import pandas as pd
from config.settings import Settings
from data.csv_loader import CSVLoader
from analyzers.news_analyzer import NewsAnalyzer

def test_news_analyzer():
    """Test the NewsAnalyzer with sample data"""
    print("🧪 Testing NewsAnalyzer...")
    
    try:
        # Initialize components
        settings = Settings()
        csv_loader = CSVLoader(settings)
        news_analyzer = NewsAnalyzer(settings)
        
        print("✅ Components initialized")
        
        # Load sample data
        sample_file = "sample_variance_data.csv"
        data = csv_loader.load_csv(sample_file)
        print(f"✅ Sample data loaded: {data.shape}")
        
        # Get column info
        column_info = csv_loader.column_info
        print(f"✅ Column info: {column_info}")
        
        # Test news analysis
        print("\n📰 Starting news analysis...")
        results = news_analyzer.analyze_data_context(data, column_info)
        
        if results:
            print(f"✅ News analysis completed")
            print(f"📍 Location columns detected: {results.get('location_columns', [])}")
            print(f"🏢 Business context: {results.get('business_context', {})}")
            print(f"🔍 Search queries: {results.get('search_queries', [])}")
            print(f"📰 News items found: {len(results.get('news_items', []))}")
            
            # Test formatting for chat
            if results.get('news_items'):
                formatted = news_analyzer.format_news_for_chat(results)
                print(f"\n📝 Formatted chat message length: {len(formatted)} characters")
                print(f"📝 First 200 chars: {formatted[:200]}...")
            else:
                print("⚠️ No news items to format")
        else:
            print("❌ No results from news analysis")
            
    except Exception as e:
        print(f"❌ Error testing NewsAnalyzer: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_news_analyzer()
