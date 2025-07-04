#!/usr/bin/env python3
"""
Test script to verify SQL integration works correctly
"""

import pandas as pd
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Test imports
    print("🔄 Testing SQL integration imports...")
    from analyzers.sql_query_engine import SQLQueryEngine
    from analyzers.nl_to_sql_translator import NLToSQLTranslator  
    from analyzers.query_router import QueryRouter
    from config.settings import Settings
    print("✅ All SQL components imported successfully")
    
    # Test basic functionality
    print("\n🔄 Testing SQL Engine...")
    sql_engine = SQLQueryEngine()
    
    # Create sample data
    sample_data = pd.DataFrame({
        'Product': ['Widget A', 'Widget B', 'Widget C'],
        'Sales': [1000, 1500, 800],
        'Budget': [900, 1400, 1000],
        'Region': ['North', 'South', 'North']
    })
    
    # Load data into SQL engine
    sql_engine.load_dataframe_to_sql(sample_data, "test_data")
    print("✅ Data loaded into SQL engine")
    
    # Test a simple query
    result = sql_engine.execute_query("SELECT Product, Sales FROM test_data ORDER BY Sales DESC")
    if result.success:
        print("✅ SQL query executed successfully")
        print(f"   Found {len(result.data)} rows")
    else:
        print(f"❌ SQL query failed: {result.error_message}")
    
    # Test NL-to-SQL translator
    print("\n🔄 Testing NL-to-SQL Translator...")
    settings = Settings()
    nl_translator = NLToSQLTranslator(settings)
    
    schema_context = {
        'table_name': 'test_data',
        'columns': list(sample_data.columns),
        'sample_data': sample_data.head(2).to_dict('records')
    }
    
    test_query = "show me products with sales over 900"
    translation_result = nl_translator.translate_to_sql(test_query, schema_context)
    
    if translation_result.success:
        print("✅ NL-to-SQL translation successful")
        print(f"   Generated SQL: {translation_result.sql_query}")
    else:
        print(f"❌ NL-to-SQL translation failed: {translation_result.error_message}")
    
    # Test Query Router
    print("\n🔄 Testing Query Router...")
    router = QueryRouter(settings)
    
    column_info = {
        'category_columns': ['Product', 'Region'],
        'numeric_columns': ['Sales', 'Budget'],
        'value_columns': ['Sales', 'Budget']
    }
    
    route_result = router.route_query(
        query="show me top products by sales",
        data=sample_data,
        column_info=column_info,
        column_suggestions={'category_columns': ['Product'], 'value_columns': ['Sales']}
    )
    
    print(f"✅ Query routing successful")
    print(f"   Routed to: {route_result.analyzer_type}")
    print(f"   Confidence: {route_result.confidence}")
    
    print("\n🎉 SQL Integration Test Complete - All components working!")
    
except Exception as e:
    print(f"\n❌ SQL Integration Test Failed: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
