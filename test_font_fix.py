#!/usr/bin/env python3
"""
Quick test script to verify font color fixes in NL-to-SQL testing UI
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.nl_to_sql_testing_ui import NLToSQLTestingUI
import time

def test_font_fixes():
    """Test the font color fixes"""
    print("🧪 Testing Font Color Fixes...")
    
    # Initialize the testing UI with sample data
    ui = NLToSQLTestingUI()
    
    # Test single query formatting
    print("\n📝 Testing single query result formatting...")
    
    # Create a mock result for testing
    class MockResult:
        def __init__(self):
            self.query = "Show me sales where region is North"
            self.current_sql = "SELECT * FROM test_data LIMIT 100"
            self.current_explanation = "Basic query without WHERE clause"
            self.current_confidence = 0.5
            self.strategy_1_sql = "SELECT * FROM test_data WHERE region = 'North'"
            self.strategy_1_explanation = "Enhanced query with WHERE clause"
            self.strategy_1_confidence = 0.85
            self.strategy_2_sql = "SELECT Sales_Actual, Region FROM test_data WHERE Region = 'north'"
            self.strategy_2_explanation = "Semantic parsing with specific columns"
            self.strategy_2_confidence = 0.90
            self.quality_scores = {'current': 32.8, 'strategy_1': 85.5, 'strategy_2': 90.2}
            self.recommendations = [
                "Consider switching to strategy_2 (score: 90.2 vs current: 32.8)",
                "Current implementation missing WHERE clause - likely returning all rows",
                "Strategy 2 shows better column selection"
            ]
            self.execution_times = {'current': 0.001, 'strategy_1': 0.002, 'strategy_2': 0.001}
    
    mock_result = MockResult()
    
    # Test the formatting function
    formatted_html = ui._format_single_query_results(mock_result)
    
    # Check if black color styling is applied
    if 'color: #000000' in formatted_html:
        print("✅ Single query formatting includes black text styling")
    else:
        print("❌ Single query formatting missing black text styling")
    
    # Test recommendations formatting
    print("\n📝 Testing recommendations formatting...")
    recommendations_html = ui._format_recommendations(mock_result.recommendations, mock_result.quality_scores)
    
    if 'color: #000000' in recommendations_html:
        print("✅ Recommendations formatting includes black text styling")
    else:
        print("❌ Recommendations formatting missing black text styling")
    
    # Test comprehensive summary formatting
    print("\n📝 Testing comprehensive summary formatting...")
    
    mock_comprehensive = {
        'total_queries': 10,
        'strategy_wins': {'current': 2, 'strategy_1': 1, 'strategy_2': 7},
        'average_scores': {'current': 40.5, 'strategy_1': 45.2, 'strategy_2': 85.8},
        'average_times': {'current': 0.001, 'strategy_1': 0.002, 'strategy_2': 0.001}
    }
    
    comprehensive_html = ui._format_comprehensive_summary(mock_comprehensive)
    
    if 'color: #000000' in comprehensive_html:
        print("✅ Comprehensive summary includes black text styling")
    else:
        print("❌ Comprehensive summary missing black text styling")
    
    # Test schema display
    print("\n📝 Testing schema display formatting...")
    schema_html = ui._get_schema_info_display()
    
    if 'color: #000000' in schema_html:
        print("✅ Schema display includes black text styling")
    else:
        print("❌ Schema display missing black text styling")
    
    # Test stats display
    print("\n📝 Testing stats display formatting...")
    stats_html = ui._get_data_stats_display()
    
    if 'color: #000000' in stats_html:
        print("✅ Stats display includes black text styling")
    else:
        print("❌ Stats display missing black text styling")
    
    print("\n🎉 Font color fix testing completed!")
    print("\n💡 Key improvements made:")
    print("   • All text elements now have explicit black color (#000000)")
    print("   • Error messages have proper red styling with readable text")
    print("   • Background colors are set to white (#ffffff) for contrast")
    print("   • Custom CSS added to Gradio interface for consistent styling")
    print("   • All HTML content uses inline styles to override theme defaults")
    
    print(f"\n🌐 Launch the interface with: python test_nl_to_sql_strategies.py")
    print(f"   The interface will be available at: http://localhost:7860")

if __name__ == "__main__":
    test_font_fixes()
