#!/usr/bin/env python3
"""
Final test for NewsAnalyzer v2 integration
"""

import pandas as pd
from config.settings import Settings
from data.csv_loader import CSVLoader
from analyzers.news_analyzer_v2 import NewsAnalyzer
from ai.llm_interpreter import LLMInterpreter

def test_news_analyzer_v2():
    """Test the NewsAnalyzer v2 with sample data"""
    print("🧪 Testing NewsAnalyzer v2...")
    
    try:
        # Initialize components
        settings = Settings()
        csv_loader = CSVLoader(settings)
        news_analyzer = NewsAnalyzer(settings)
        llm_interpreter = LLMInterpreter(settings)
        
        # Load sample data
        data = csv_loader.load_csv("sample_variance_data.csv")
        column_info = csv_loader.column_info
        
        print(f"✅ Data loaded: {data.shape}")
        print(f"✅ LLM available: {llm_interpreter.is_available}")
        
        # Test news analysis
        print("\n🔍 Running full analysis...")
        results = news_analyzer.analyze_data_context(data, column_info, llm_interpreter)
        
        print("\n📊 Analysis Results:")
        print(f"• Location columns: {results.get('location_columns', [])}")
        print(f"• Top locations: {results.get('top_locations', [])}")
        print(f"• Search queries: {results.get('search_queries', [])}")
        print(f"• News items found: {len(results.get('news_items', []))}")
        
        # Display news items
        news_items = results.get('news_items', [])
        if news_items:
            print("\n📰 News Items:")
            for i, item in enumerate(news_items, 1):
                print(f"  {i}. {item.get('title', 'No title')} - {item.get('source', 'Unknown source')}")
        
        # Test formatting
        formatted = news_analyzer.format_news_for_chat(results)
        print(f"\n📝 Formatted chat message ({len(formatted)} chars):")
        print("---")
        print(formatted[:500] + "..." if len(formatted) > 500 else formatted)
        print("---")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_news_analyzer_v2()
