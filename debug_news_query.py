#!/usr/bin/env python3
"""
Debug script for NewsAnalyzer query generation
"""

import pandas as pd
from config.settings import Settings
from data.csv_loader import CSVLoader
from analyzers.news_analyzer import NewsAnalyzer
from ai.llm_interpreter import LLMInterpreter

def debug_news_query_generation():
    """Debug the news query generation process"""
    print("🔍 Debugging NewsAnalyzer query generation...")
    
    try:
        # Initialize components
        settings = Settings()
        csv_loader = CSVLoader(settings)
        news_analyzer = NewsAnalyzer(settings)
        llm_interpreter = LLMInterpreter(settings)
        
        # Load sample data
        data = csv_loader.load_csv("sample_variance_data.csv")
        column_info = csv_loader.column_info
        
        # Check LLM availability
        print(f"🤖 LLM available: {llm_interpreter.is_available}")
        
        # Get context
        context = news_analyzer.analyze_data_context(data, column_info)
        print(f"📊 Context: {context}")
        
        # Test query generation
        print("\n🔍 Testing query generation...")
        query = news_analyzer.generate_news_query(context, llm_interpreter)
        print(f"✅ Generated query: '{query}'")
        
        # Test news fetching
        if query and query.strip():
            print(f"\n📰 Testing news fetch with query: '{query}'")
            news_items = news_analyzer.fetch_news(query, max_articles=3)
            print(f"📰 Found {len(news_items)} news items")
            for i, item in enumerate(news_items, 1):
                print(f"  {i}. {item.get('title', 'No title')} - {item.get('source', 'Unknown source')}")
        else:
            print("❌ No query generated, can't test news fetch")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_news_query_generation()
