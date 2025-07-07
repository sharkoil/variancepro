"""
Test Enhanced Top/Bottom Analysis with LLM Commentary and Multi-Timespan Variance
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

# Import the core app and handler
from core.app_core import AppCore
from handlers.quick_action_handler import QuickActionHandler


class TestEnhancedTopBottomAnalysis:
    """Test enhanced top/bottom analysis features"""
    
    def setup_method(self):
        """Set up test environment"""
        self.app_core = AppCore()
        self.handler = QuickActionHandler(self.app_core)
        
    def create_test_data_with_dates(self):
        """Create test data with date columns for multi-timespan analysis"""
        np.random.seed(42)  # For reproducible results
        
        dates = pd.date_range('2024-01-01', periods=100, freq='D')
        categories = ['Product A', 'Product B', 'Product C', 'Product D', 'Product E', 'Product F']
        
        data = []
        for i, date in enumerate(dates):
            for category in categories:
                value = np.random.normal(1000, 200) + (i * 10)  # Trending upward
                data.append({
                    'Date': date,
                    'Category': category,
                    'Sales': max(100, value),  # Ensure positive values
                    'Budget': max(100, value * 0.9 + np.random.normal(0, 50))  # Budget variation
                })
        
        return pd.DataFrame(data)
    
    def create_simple_test_data(self):
        """Create simple test data without dates"""
        return pd.DataFrame({
            'Product': ['A', 'B', 'C', 'D', 'E'],
            'Revenue': [10000, 8000, 6000, 4000, 2000],
            'Profit': [3000, 2500, 1800, 1200, 600]
        })
    
    def test_enhanced_top_analysis_with_dates(self):
        """Test enhanced top analysis with date-based multi-timespan variance"""
        # Setup test data
        test_data = self.create_test_data_with_dates()
        self.app_core.set_current_data(test_data, "Test data with enhanced analysis")
        
        # Test top 5 analysis
        response = self.handler._handle_top_bottom_action("top5")
        
        # Verify response structure
        assert "🔍 **Top 5 Analysis" in response
        assert "Statistical Summary" in response
        assert "Mean" in response
        assert "Range" in response
        assert "Standard Deviation" in response
        
        # Check for multi-timeframe analysis
        if "Multi-Timeframe Variance Analysis" in response:
            assert "Daily" in response or "Weekly" in response or "Monthly" in response
        
        # Check for AI commentary
        assert "AI Analysis" in response or "AI Insights" in response or "Statistical Analysis" in response
        
        print("✅ Enhanced top analysis with dates test passed")
    
    def test_enhanced_bottom_analysis_with_dates(self):
        """Test enhanced bottom analysis with date-based variance"""
        # Setup test data
        test_data = self.create_test_data_with_dates()
        self.app_core.set_current_data(test_data, "Test data for bottom analysis")
        
        # Test bottom 5 analysis
        response = self.handler._handle_top_bottom_action("bottom5")
        
        # Verify response structure
        assert "🔍 **Bottom 5 Analysis" in response
        assert "Statistical Summary" in response
        
        print("✅ Enhanced bottom analysis with dates test passed")
    
    def test_enhanced_numeric_analysis_without_categories(self):
        """Test enhanced analysis for numeric-only data"""
        # Create numeric-only data
        test_data = pd.DataFrame({
            'Value': [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]
        })
        self.app_core.set_current_data(test_data, "Numeric only test data")
        
        # Test top analysis
        response = self.handler._handle_top_bottom_action("top5")
        
        # Verify response
        assert "🔍 **Top 5 Analysis" in response
        assert "percentile" in response.lower()  # Should show percentile information
        assert "Statistical Analysis" in response or "AI Insights" in response
        
        print("✅ Enhanced numeric analysis test passed")
    
    def test_multi_timeframe_analysis_methods(self):
        """Test the multi-timeframe analysis helper methods"""
        test_data = self.create_test_data_with_dates()
        
        # Test multi-timeframe analysis
        result = self.handler._perform_multi_timeframe_analysis(
            test_data, 'Sales', 'Category'
        )
        
        # Should return some analysis or indication of no date columns
        assert isinstance(result, str)
        assert len(result) > 0
        
        print("✅ Multi-timeframe analysis methods test passed")
    
    def test_variance_analysis_for_numeric_data(self):
        """Test variance analysis for numeric-only data"""
        test_data = pd.DataFrame({
            'Values': [100, 150, 200, 175, 225, 180, 250, 190, 275, 210]
        })
        
        # Test numeric variance analysis
        result = self.handler._perform_numeric_variance_analysis(test_data, 'Values')
        
        # Verify variance metrics
        assert "Coefficient of Variation" in result
        assert "Variance" in result
        assert "IQR" in result
        
        print("✅ Numeric variance analysis test passed")
    
    def test_llm_commentary_fallback(self):
        """Test that fallback commentary works when LLM is unavailable"""
        # Setup simple test data
        test_data = self.create_simple_test_data()
        result_data = test_data.nlargest(3, 'Revenue')
        
        stats = {
            'mean': result_data['Revenue'].mean(),
            'median': result_data['Revenue'].median(),
            'std': result_data['Revenue'].std(),
            'range': result_data['Revenue'].max() - result_data['Revenue'].min()
        }
        
        # Test fallback commentary
        commentary = self.handler._generate_fallback_commentary(
            result_data, "top", 3, "Revenue", stats
        )
        
        # Verify fallback content
        assert "Performance Range" in commentary
        assert "Average Performance" in commentary
        assert "Variability" in commentary
        
        print("✅ LLM commentary fallback test passed")
    
    @patch('core.app_core.AppCore.is_ollama_available')
    @patch('core.app_core.AppCore.call_ollama')
    def test_llm_commentary_integration(self, mock_call_ollama, mock_is_available):
        """Test LLM commentary integration"""
        # Mock LLM availability and response
        mock_is_available.return_value = True
        mock_call_ollama.return_value = "This is test LLM commentary about the top performers showing significant variance in performance."
        
        # Setup test data
        test_data = self.create_simple_test_data()
        result_data = test_data.nlargest(3, 'Revenue')
        
        stats = {
            'mean': result_data['Revenue'].mean(),
            'median': result_data['Revenue'].median(),
            'std': result_data['Revenue'].std(),
            'range': result_data['Revenue'].max() - result_data['Revenue'].min()
        }
        
        # Test LLM commentary generation
        commentary = self.handler._generate_llm_commentary_for_top_bottom(
            result_data, "top", 3, "Revenue", "Product", stats, test_data['Revenue'].sum(), ""
        )
        
        # Verify LLM was called and response formatted
        assert mock_call_ollama.called
        assert "test LLM commentary" in commentary
        
        print("✅ LLM commentary integration test passed")
    
    def test_date_column_detection(self):
        """Test date column detection functionality"""
        # Test data with various date column types
        test_data = pd.DataFrame({
            'date_column': pd.date_range('2024-01-01', periods=5),
            'datetime_col': pd.date_range('2024-01-01', periods=5),
            'timestamp': pd.date_range('2024-01-01', periods=5),
            'regular_col': [1, 2, 3, 4, 5]
        })
        
        # Test date detection
        date_columns = self.handler._detect_date_columns(test_data)
        
        # Should detect the date columns
        assert len(date_columns) >= 1
        assert any('date' in col.lower() for col in date_columns)
        
        print("✅ Date column detection test passed")
    
    def test_comprehensive_enhanced_workflow(self):
        """Test the complete enhanced workflow end-to-end"""
        # Create comprehensive test dataset
        test_data = self.create_test_data_with_dates()
        self.app_core.set_current_data(test_data, "Comprehensive test dataset")
        
        # Test all quick actions with enhanced analysis
        actions = ["top5", "bottom5", "top10", "bottom10"]
        
        for action in actions:
            response = self.handler._handle_top_bottom_action(action)
            
            # Verify comprehensive response structure
            assert f"🔍 **{action.replace('5', ' 5').replace('10', ' 10').title()} Analysis" in response
            assert "$" in response  # Should have monetary formatting
            assert "%" in response  # Should have percentage information
            
            # Should have statistical content
            assert any(keyword in response for keyword in [
                "Mean", "Range", "Standard Deviation", "Statistical", 
                "Analysis", "Variance", "AI", "Commentary"
            ])
        
        print("✅ Comprehensive enhanced workflow test passed")
    
    def test_error_handling_in_enhanced_analysis(self):
        """Test error handling in enhanced analysis methods"""
        # Test with empty data
        empty_data = pd.DataFrame()
        self.app_core.set_current_data(empty_data, "Empty test data")
        
        # Should handle gracefully
        response = self.handler._handle_top_bottom_action("top5")
        assert "Error" in response or "No" in response
        
        # Test with invalid data
        invalid_data = pd.DataFrame({'text_only': ['a', 'b', 'c']})
        self.app_core.set_current_data(invalid_data, "Invalid test data")
        
        response = self.handler._handle_top_bottom_action("top5")
        assert "No numeric columns" in response
        
        print("✅ Error handling in enhanced analysis test passed")


def run_enhanced_analysis_tests():
    """Run all enhanced analysis tests"""
    test_instance = TestEnhancedTopBottomAnalysis()
    
    test_methods = [
        test_instance.test_enhanced_top_analysis_with_dates,
        test_instance.test_enhanced_bottom_analysis_with_dates,
        test_instance.test_enhanced_numeric_analysis_without_categories,
        test_instance.test_multi_timeframe_analysis_methods,
        test_instance.test_variance_analysis_for_numeric_data,
        test_instance.test_llm_commentary_fallback,
        test_instance.test_llm_commentary_integration,
        test_instance.test_date_column_detection,
        test_instance.test_comprehensive_enhanced_workflow,
        test_instance.test_error_handling_in_enhanced_analysis
    ]
    
    print("🚀 Running Enhanced Top/Bottom Analysis Tests...")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_method in test_methods:
        try:
            test_instance.setup_method()
            test_method()
            passed += 1
        except Exception as e:
            print(f"❌ {test_method.__name__} failed: {str(e)}")
            failed += 1
    
    print("=" * 60)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    print("🎉 Enhanced analysis testing complete!")
    
    return passed, failed


if __name__ == "__main__":
    run_enhanced_analysis_tests()
