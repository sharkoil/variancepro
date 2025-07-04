#!/usr/bin/env python3
"""
Test existing functionality to ensure NL-to-SQL doesn't interfere
Tests that existing analyzers are properly preserved and SQL is only invoked when appropriate
"""

import pandas as pd
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_analyzer_preservation():
    """Test that existing analyzers work correctly and SQL doesn't interfere"""
    try:
        print("🔄 Testing analyzer preservation and proper SQL routing...")
        
        from app_new import QuantCommanderApp
        app = QuantCommanderApp()
        
        # Create comprehensive test data
        sample_data = pd.DataFrame({
            'Product': ['Widget A', 'Widget B', 'Widget C', 'Widget D', 'Widget E'],
            'Sales': [1000, 1500, 800, 2000, 1200],
            'Budget': [900, 1400, 1000, 1800, 1100],
            'Actual': [1000, 1500, 800, 2000, 1200],
            'Region': ['North', 'South', 'North', 'West', 'East'],
            'Quarter': ['Q1', 'Q1', 'Q2', 'Q2', 'Q1'],
            'Date': pd.date_range('2024-01-01', periods=5, freq='ME')
        })
        
        # Set up app state
        app.current_data = sample_data
        app.csv_loader.column_info = {
            'category_columns': ['Product', 'Region', 'Quarter'],
            'numeric_columns': ['Sales', 'Budget', 'Actual'],
            'value_columns': ['Sales', 'Budget', 'Actual'],
            'date_columns': ['Date'],
            'financial_columns': {
                'budget_columns': ['Budget'],
                'actual_columns': ['Actual']
            }
        }
        app.column_suggestions = {
            'category_columns': ['Product', 'Region'],
            'value_columns': ['Sales', 'Budget', 'Actual'],
            'budget_vs_actual': {'Budget': 'Actual'}
        }
        
        # Load data into SQL engine
        app.sql_engine.load_dataframe_to_sql(sample_data, "data")
        app._sql_data_loaded = True
        
        print("✅ Test data and app state initialized")
        
        # Test 1: Contribution Analysis (should NOT use SQL)
        print("\n🔄 Test 1: Contribution Analysis routing...")
        queries = [
            "analyze contribution",
            "show me contribution analysis", 
            "pareto analysis",
            "80/20 analysis",
            "top contributors"
        ]
        
        for query in queries:
            print(f"  Testing: '{query}'")
            route_result = app.query_router.route_query(
                query=query,
                data=sample_data,
                column_info=app.csv_loader.column_info,
                column_suggestions=app.column_suggestions
            )
            
            assert route_result.analyzer_type == 'contribution', f"Expected 'contribution', got '{route_result.analyzer_type}' for '{query}'"
            print(f"    ✅ Routed to: {route_result.analyzer_type} (confidence: {route_result.confidence})")
        
        # Test 2: Variance Analysis (should NOT use SQL)
        print("\n🔄 Test 2: Variance Analysis routing...")
        queries = [
            "analyze variance",
            "budget vs actual",
            "variance analysis",
            "over budget analysis",
            "actual vs budget"
        ]
        
        for query in queries:
            print(f"  Testing: '{query}'")
            route_result = app.query_router.route_query(
                query=query,
                data=sample_data,
                column_info=app.csv_loader.column_info,
                column_suggestions=app.column_suggestions
            )
            
            assert route_result.analyzer_type == 'variance', f"Expected 'variance', got '{route_result.analyzer_type}' for '{query}'"
            print(f"    ✅ Routed to: {route_result.analyzer_type} (confidence: {route_result.confidence})")
        
        # Test 3: Trend Analysis (should NOT use SQL)
        print("\n🔄 Test 3: Trend Analysis routing...")
        queries = [
            "analyze trends",
            "trend analysis",
            "time series analysis",
            "ttm analysis",
            "trailing twelve months"
        ]
        
        for query in queries:
            print(f"  Testing: '{query}'")
            route_result = app.query_router.route_query(
                query=query,
                data=sample_data,
                column_info=app.csv_loader.column_info,
                column_suggestions=app.column_suggestions
            )
            
            assert route_result.analyzer_type == 'trend', f"Expected 'trend', got '{route_result.analyzer_type}' for '{query}'"
            print(f"    ✅ Routed to: {route_result.analyzer_type} (confidence: {route_result.confidence})")
        
        # Test 4: Top/Bottom N Analysis (should NOT use SQL for simple cases)
        print("\n🔄 Test 4: Top/Bottom N Analysis routing...")
        queries = [
            "top 5 products",
            "best 10 performers",
            "bottom 3 regions",
            "worst 5 products",
            "show me top performers"
        ]
        
        for query in queries:
            print(f"  Testing: '{query}'")
            route_result = app.query_router.route_query(
                query=query,
                data=sample_data,
                column_info=app.csv_loader.column_info,
                column_suggestions=app.column_suggestions
            )
            
            expected = 'top_n' if any(word in query.lower() for word in ['top', 'best']) else 'bottom_n'
            assert route_result.analyzer_type in ['top_n', 'bottom_n'], f"Expected top_n/bottom_n, got '{route_result.analyzer_type}' for '{query}'"
            print(f"    ✅ Routed to: {route_result.analyzer_type} (confidence: {route_result.confidence})")
        
        # Test 5: Data Overview (should NOT use SQL)
        print("\n🔄 Test 5: Data Overview routing...")
        queries = [
            "summary",
            "overview", 
            "describe the data",
            "what data do we have",
            "show me data summary"
        ]
        
        for query in queries:
            print(f"  Testing: '{query}'")
            route_result = app.query_router.route_query(
                query=query,
                data=sample_data,
                column_info=app.csv_loader.column_info,
                column_suggestions=app.column_suggestions
            )
            
            assert route_result.analyzer_type == 'overview', f"Expected 'overview', got '{route_result.analyzer_type}' for '{query}'"
            print(f"    ✅ Routed to: {route_result.analyzer_type} (confidence: {route_result.confidence})")
        
        # Test 6: Queries that SHOULD use SQL
        print("\n🔄 Test 6: SQL-appropriate queries...")
        queries = [
            "show me products where sales > 1000",
            "list all regions with budget below 1000", 
            "find products in Q1",
            "SELECT * FROM data",
            "count how many products have sales over 1500",
            "what is the total sales by quarter"
        ]
        
        for query in queries:
            print(f"  Testing: '{query}'")
            route_result = app.query_router.route_query(
                query=query,
                data=sample_data,
                column_info=app.csv_loader.column_info,
                column_suggestions=app.column_suggestions
            )
            
            assert route_result.analyzer_type == 'sql', f"Expected 'sql', got '{route_result.analyzer_type}' for '{query}'"
            print(f"    ✅ Routed to: {route_result.analyzer_type} (confidence: {route_result.confidence})")
        
        print("\n🔄 Test 7: End-to-end analyzer functionality...")
        
        # Test actual analyzer execution to ensure they still work
        test_queries = [
            ("analyze contribution", "contribution"),
            ("analyze variance", "variance"),
            ("analyze trends", "trend"),
            ("show me data summary", "overview")
        ]
        
        for query, expected_type in test_queries:
            print(f"  Testing full execution: '{query}'")
            try:
                response = app._process_user_query(query)
                
                # Verify we got a proper response (not an error)
                assert not response.startswith("❌"), f"Got error for '{query}': {response[:100]}"
                assert len(response) > 50, f"Response too short for '{query}': {len(response)} chars"
                
                # Verify response contains expected content
                if expected_type == "contribution":
                    assert any(word in response.lower() for word in ["contribution", "pareto", "analysis"]), f"Contribution response doesn't contain expected keywords"
                elif expected_type == "variance":
                    assert any(word in response.lower() for word in ["variance", "budget", "actual"]), f"Variance response doesn't contain expected keywords"
                elif expected_type == "trend":
                    assert any(word in response.lower() for word in ["trend", "time", "analysis"]), f"Trend response doesn't contain expected keywords"
                elif expected_type == "overview":
                    assert any(word in response.lower() for word in ["overview", "summary", "data"]), f"Overview response doesn't contain expected keywords"
                
                print(f"    ✅ Full execution successful ({len(response)} chars)")
                
            except Exception as e:
                print(f"    ❌ Execution failed: {str(e)}")
                raise
        
        print("\n🎉 ALL ANALYZER PRESERVATION TESTS PASSED!")
        print("🔧 Verified:")
        print("  ✅ Contribution Analysis - Routes correctly, avoids SQL")
        print("  ✅ Variance Analysis - Routes correctly, avoids SQL") 
        print("  ✅ Trend Analysis - Routes correctly, avoids SQL")
        print("  ✅ Top/Bottom N Analysis - Routes correctly, avoids SQL")
        print("  ✅ Data Overview - Routes correctly, avoids SQL")
        print("  ✅ SQL Queries - Properly detected and routed to SQL")
        print("  ✅ End-to-end Execution - All analyzers work correctly")
        print("  ✅ No Interference - SQL doesn't break existing functionality")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Analyzer preservation test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_analyzer_preservation()
    sys.exit(0 if success else 1)
