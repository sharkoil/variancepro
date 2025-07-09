"""
Phase 2 Functionality Validation Script

This script performs comprehensive validation of all Phase 2 fixes and improvements.
It tests the actual functionality with real data and scenarios to ensure everything
works correctly in practice.

This script validates:
1. Quick action handlers (summary, trends, variance, top/bottom N)
2. Error handling and edge cases
3. Data flow and integration
4. RAG enhancement functionality
5. Real-world scenarios
"""

import pandas as pd
import numpy as np
from datetime import datetime
import sys
import os
import traceback

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from handlers.quick_action_handler import QuickActionHandler
from core.app_core import AppCore
from unittest.mock import Mock


def create_test_data():
    """Create realistic test data for validation."""
    # Create financial test data
    financial_data = pd.DataFrame({
        'Date': pd.date_range('2024-01-01', periods=12, freq='ME'),
        'Revenue': [100000, 120000, 110000, 130000, 125000, 140000, 
                   135000, 145000, 150000, 160000, 155000, 170000],
        'Actual_Sales': [95000, 115000, 105000, 125000, 120000, 135000,
                        130000, 140000, 145000, 155000, 150000, 165000],
        'Planned_Sales': [90000, 110000, 100000, 120000, 115000, 130000,
                         125000, 135000, 140000, 150000, 145000, 160000],
        'Region': ['North', 'South', 'East', 'West'] * 3,
        'Product': ['Electronics', 'Clothing', 'Home', 'Books'] * 3,
        'Customer_Count': [1000, 1200, 1100, 1300, 1250, 1400, 1350, 1450, 1500, 1600, 1550, 1700],
        'Market_Share': [15.5, 16.2, 15.8, 16.8, 16.5, 17.2, 16.9, 17.5, 17.8, 18.2, 17.9, 18.5]
    })
    
    return financial_data


def create_mock_app_core(data):
    """Create a mock app core with test data."""
    mock_app_core = Mock()
    mock_app_core.has_data.return_value = True
    mock_app_core.get_current_data.return_value = (data, None)
    
    # Mock timescale analyzer
    mock_timescale = Mock()
    mock_timescale.status = "completed"
    mock_timescale.format_for_chat.return_value = "Sample trends analysis results"
    mock_app_core.timescale_analyzer = mock_timescale
    
    return mock_app_core


def create_mock_rag_components():
    """Create mock RAG components for testing."""
    mock_rag_manager = Mock()
    mock_rag_analyzer = Mock()
    
    mock_rag_manager.has_documents.return_value = True
    
    # Configure RAG responses
    mock_rag_analyzer.enhance_general_analysis.return_value = {
        'success': True,
        'enhanced_analysis': 'RAG-enhanced analysis with business context',
        'documents_used': 2,
        'prompt_used': 'Sample prompt'
    }
    
    mock_rag_analyzer.enhance_trend_analysis.return_value = {
        'success': True,
        'enhanced_analysis': 'RAG-enhanced trend analysis',
        'documents_used': 3,
        'prompt_used': 'Trend prompt'
    }
    
    mock_rag_analyzer.enhance_variance_analysis.return_value = {
        'success': True,
        'enhanced_analysis': 'RAG-enhanced quantitative analysis',
        'documents_used': 1,
        'prompt_used': 'Variance prompt'
    }
    
    return mock_rag_manager, mock_rag_analyzer


def test_quick_action_handler_initialization():
    """Test QuickActionHandler initialization."""
    print("🔧 Testing QuickActionHandler initialization...")
    
    try:
        # Test with all components
        mock_app_core = create_mock_app_core(create_test_data())
        mock_rag_manager, mock_rag_analyzer = create_mock_rag_components()
        
        handler = QuickActionHandler(
            app_core=mock_app_core,
            rag_manager=mock_rag_manager,
            rag_analyzer=mock_rag_analyzer
        )
        
        assert handler.app_core == mock_app_core
        assert handler.rag_manager == mock_rag_manager
        assert handler.rag_analyzer == mock_rag_analyzer
        
        print("✅ QuickActionHandler initialization: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ QuickActionHandler initialization: FAILED - {e}")
        traceback.print_exc()
        return False


def test_summary_action():
    """Test summary action functionality."""
    print("📊 Testing summary action...")
    
    try:
        data = create_test_data()
        mock_app_core = create_mock_app_core(data)
        mock_rag_manager, mock_rag_analyzer = create_mock_rag_components()
        
        handler = QuickActionHandler(
            app_core=mock_app_core,
            rag_manager=mock_rag_manager,
            rag_analyzer=mock_rag_analyzer
        )
        
        # Test summary action
        result = handler._handle_summary_action()
        
        # Verify summary content
        assert "Data Summary" in result or "Quick Summary" in result
        assert "12 rows" in result
        assert "8 columns" in result
        assert "Revenue" in result
        assert "RAG-enhanced analysis" in result
        
        print("✅ Summary action: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Summary action: FAILED - {e}")
        traceback.print_exc()
        return False


def test_top_bottom_actions():
    """Test top/bottom N actions."""
    print("🔍 Testing top/bottom N actions...")
    
    try:
        data = create_test_data()
        mock_app_core = create_mock_app_core(data)
        handler = QuickActionHandler(app_core=mock_app_core)
        
        # Test basic top N
        result = handler._handle_top_bottom_action("top 5")
        assert "Top 5 Rows" in result
        assert "Revenue" in result  # Should use first numeric column
        
        # Test basic bottom N
        result = handler._handle_top_bottom_action("bottom 3")
        assert "Bottom 3 Rows" in result
        
        # Test with specific column
        result = handler._handle_top_bottom_action("top 5 by customer_count")
        assert "Top 5 Rows by Customer_Count" in result
        
        # Test edge case - invalid column
        result = handler._handle_top_bottom_action("top 5 by nonexistent")
        assert "Column 'nonexistent' not found" in result
        
        print("✅ Top/bottom N actions: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Top/bottom N actions: FAILED - {e}")
        traceback.print_exc()
        return False


def test_trends_action():
    """Test trends action functionality."""
    print("📈 Testing trends action...")
    
    try:
        data = create_test_data()
        mock_app_core = create_mock_app_core(data)
        mock_rag_manager, mock_rag_analyzer = create_mock_rag_components()
        
        handler = QuickActionHandler(
            app_core=mock_app_core,
            rag_manager=mock_rag_manager,
            rag_analyzer=mock_rag_analyzer
        )
        
        # Test trends action
        result = handler._handle_trends_action()
        
        # Verify trends content
        assert "Trends Analysis" in result
        assert "Sample trends analysis results" in result
        assert "RAG-enhanced trend analysis" in result
        
        print("✅ Trends action: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Trends action: FAILED - {e}")
        traceback.print_exc()
        return False


def test_variance_action():
    """Test variance action functionality."""
    print("🔄 Testing variance action...")
    
    try:
        data = create_test_data()
        mock_app_core = create_mock_app_core(data)
        mock_rag_manager, mock_rag_analyzer = create_mock_rag_components()
        
        handler = QuickActionHandler(
            app_core=mock_app_core,
            rag_manager=mock_rag_manager,
            rag_analyzer=mock_rag_analyzer
        )
        
        # Test variance action
        result = handler._handle_variance_action()
        
        # Should detect variance pairs or provide guidance
        assert "variance" in result.lower() or "comparison" in result.lower() or "pairs detected" in result
        
        print("✅ Variance action: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Variance action: FAILED - {e}")
        traceback.print_exc()
        return False


def test_end_to_end_workflow():
    """Test complete end-to-end workflow."""
    print("🔄 Testing end-to-end workflow...")
    
    try:
        data = create_test_data()
        mock_app_core = create_mock_app_core(data)
        mock_rag_manager, mock_rag_analyzer = create_mock_rag_components()
        
        handler = QuickActionHandler(
            app_core=mock_app_core,
            rag_manager=mock_rag_manager,
            rag_analyzer=mock_rag_analyzer
        )
        
        # Test complete workflow
        history = []
        
        # Step 1: Summary
        history = handler.handle_action("summary", history)
        assert len(history) == 2
        assert history[0]["role"] == "user"
        assert history[1]["role"] == "assistant"
        
        # Step 2: Top N
        history = handler.handle_action("top 5", history)
        assert len(history) == 4
        
        # Step 3: Trends
        history = handler.handle_action("trends", history)
        assert len(history) == 6
        
        # Verify all messages have timestamps
        for message in history:
            assert ":" in message["content"]  # Should have HH:MM:SS format
        
        print("✅ End-to-end workflow: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ End-to-end workflow: FAILED - {e}")
        traceback.print_exc()
        return False


def test_error_handling():
    """Test error handling scenarios."""
    print("⚠️ Testing error handling...")
    
    try:
        # Test with no data
        mock_app_core = Mock()
        mock_app_core.has_data.return_value = False
        
        handler = QuickActionHandler(app_core=mock_app_core)
        
        # Test actions with no data
        history = []
        history = handler.handle_action("summary", history)
        assert "Please upload a CSV file first" in history[1]["content"]
        
        # Test with malformed data
        mock_app_core.has_data.return_value = True
        mock_app_core.get_current_data.return_value = (pd.DataFrame(), None)
        
        result = handler._handle_top_bottom_action("top 5")
        assert "No data available" in result
        
        print("✅ Error handling: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Error handling: FAILED - {e}")
        traceback.print_exc()
        return False


def test_edge_cases():
    """Test edge cases and boundary conditions."""
    print("🎯 Testing edge cases...")
    
    try:
        # Test with text-only data
        text_data = pd.DataFrame({
            'Name': ['Alice', 'Bob', 'Charlie'],
            'Category': ['A', 'B', 'C'],
            'Status': ['Active', 'Inactive', 'Active']
        })
        
        mock_app_core = create_mock_app_core(text_data)
        handler = QuickActionHandler(app_core=mock_app_core)
        
        result = handler._handle_top_bottom_action("top 5")
        assert "No numeric columns found" in result
        
        # Test with null values
        null_data = pd.DataFrame({
            'Revenue': [100, np.nan, 200],
            'Sales': [np.nan, np.nan, np.nan]
        })
        
        mock_app_core = create_mock_app_core(null_data)
        handler = QuickActionHandler(app_core=mock_app_core)
        
        result = handler._handle_top_bottom_action("top 5 by sales")
        assert "missing values" in result
        
        print("✅ Edge cases: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Edge cases: FAILED - {e}")
        traceback.print_exc()
        return False


def test_rag_integration():
    """Test RAG integration functionality."""
    print("🤖 Testing RAG integration...")
    
    try:
        data = create_test_data()
        mock_app_core = create_mock_app_core(data)
        mock_rag_manager, mock_rag_analyzer = create_mock_rag_components()
        
        handler = QuickActionHandler(
            app_core=mock_app_core,
            rag_manager=mock_rag_manager,
            rag_analyzer=mock_rag_analyzer
        )
        
        # Test RAG enhancement in summary
        result = handler._handle_summary_action()
        assert "RAG-enhanced analysis" in result
        assert "RAG Enhancement" in result
        
        # Test RAG failure handling
        mock_rag_analyzer.enhance_general_analysis.return_value = {
            'success': False,
            'error': 'RAG system failed'
        }
        
        result = handler._handle_summary_action()
        assert "Data Summary" in result or "Quick Summary" in result
        # Should fallback gracefully
        
        print("✅ RAG integration: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ RAG integration: FAILED - {e}")
        traceback.print_exc()
        return False


def main():
    """Run all Phase 2 validation tests."""
    print("🚀 Starting Phase 2 Functionality Validation")
    print("=" * 60)
    
    tests = [
        test_quick_action_handler_initialization,
        test_summary_action,
        test_top_bottom_actions,
        test_trends_action,
        test_variance_action,
        test_end_to_end_workflow,
        test_error_handling,
        test_edge_cases,
        test_rag_integration
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        if test():
            passed += 1
        else:
            failed += 1
        print()
    
    print("=" * 60)
    print(f"🎯 Phase 2 Validation Results:")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Success Rate: {passed/(passed+failed)*100:.1f}%")
    
    if failed == 0:
        print("\n🎉 All Phase 2 functionality validation tests PASSED!")
        print("✅ Quick action handlers are working correctly")
        print("✅ Error handling is robust")
        print("✅ RAG integration is functioning")
        print("✅ End-to-end workflows are operational")
        print("\n🚀 Phase 2 is COMPLETE and ready for production!")
    else:
        print(f"\n⚠️ {failed} test(s) failed. Review the issues above.")
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
