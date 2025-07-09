"""
Phase 2: Integration Test Suite for Quant Commander

This test suite focuses on integration testing to verify that all components
work together correctly after the Phase 1 fixes and modular refactoring.

Tests cover:
- End-to-end workflows
- Component integration
- Data flow validation
- Handler coordination
- Real-world scenarios

Following quality standards: modular design, type hints, descriptive names,
comprehensive test coverage >80%, clear comments for novice developers.
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import sys
import os
from typing import Dict, List, Any, Optional
import tempfile
import io

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from handlers.quick_action_handler import QuickActionHandler
from handlers.timestamp_handler import TimestampHandler
from core.app_core import AppCore


class TestPhase2Integration:
    """
    Integration test suite for Phase 2 functionality verification.
    
    This class tests the integration between different components
    to ensure they work together correctly in real-world scenarios.
    """
    
    def setup_method(self):
        """
        Set up integration test fixtures.
        
        Creates realistic test scenarios with multiple components interacting.
        """
        # Create realistic sample data for integration tests
        self.sample_business_data = pd.DataFrame({
            'Date': pd.date_range('2024-01-01', periods=12, freq='M'),
            'Revenue': [100000, 120000, 110000, 130000, 125000, 140000, 
                       135000, 145000, 150000, 160000, 155000, 170000],
            'Actual_Sales': [95000, 115000, 105000, 125000, 120000, 135000,
                            130000, 140000, 145000, 155000, 150000, 165000],
            'Planned_Sales': [90000, 110000, 100000, 120000, 115000, 130000,
                             125000, 135000, 140000, 150000, 145000, 160000],
            'Region': ['North', 'South', 'East', 'West'] * 3,
            'Product_Category': ['Electronics', 'Clothing', 'Home', 'Books'] * 3,
            'Customer_Count': [1000, 1200, 1100, 1300, 1250, 1400, 1350, 1450, 1500, 1600, 1550, 1700],
            'Market_Share': [15.5, 16.2, 15.8, 16.8, 16.5, 17.2, 16.9, 17.5, 17.8, 18.2, 17.9, 18.5]
        })
        
        # Create mock components that simulate real behavior
        self.mock_app_core = Mock()
        self.mock_rag_manager = Mock()
        self.mock_rag_analyzer = Mock()
        
        # Configure realistic mock behaviors
        self.mock_app_core.has_data.return_value = True
        self.mock_app_core.get_current_data.return_value = (self.sample_business_data, None)
        self.mock_rag_manager.has_documents.return_value = True
        
        # Create handler for integration testing
        self.handler = QuickActionHandler(
            app_core=self.mock_app_core,
            rag_manager=self.mock_rag_manager,
            rag_analyzer=self.mock_rag_analyzer
        )
    
    def test_end_to_end_workflow_summary_to_drilldown(self):
        """
        Test complete end-to-end workflow from summary to detailed analysis.
        
        Simulates a realistic user workflow: summary → trends → variance → top N.
        """
        # Step 1: Get initial summary
        history = []
        history = self.handler.handle_action("summary", history)
        
        assert len(history) == 2
        assert "Data Summary" in history[1]["content"] or "Quick Summary" in history[1]["content"]
        summary_content = history[1]["content"]
        
        # Verify summary contains key information
        assert "12 rows" in summary_content
        assert "8 columns" in summary_content
        assert "Revenue" in summary_content
        
        # Step 2: Follow up with trends analysis
        history = self.handler.handle_action("trends", history)
        
        # Should have 4 messages now (2 user + 2 assistant)
        assert len(history) == 4
        
        # Step 3: Analyze variance
        history = self.handler.handle_action("variance", history)
        
        # Should have 6 messages now
        assert len(history) == 6
        
        # Step 4: Get top performers
        history = self.handler.handle_action("top 5", history)
        
        # Should have 8 messages now
        assert len(history) == 8
        assert "Top 5 Rows" in history[7]["content"]
        
        # Verify all messages have proper structure
        for i, message in enumerate(history):
            assert "role" in message
            assert "content" in message
            assert message["role"] in ["user", "assistant"]
            
            # Verify timestamps are present
            if i > 0:  # Skip first message which might not have timestamp
                assert any(char.isdigit() for char in message["content"])
    
    def test_integration_with_different_data_types(self):
        """
        Test integration with various data types and structures.
        
        Verifies that the system handles different data formats correctly.
        """
        # Test with mixed data types
        mixed_data = pd.DataFrame({
            'Date': pd.date_range('2024-01-01', periods=5),
            'Revenue': [100.5, 200.75, 150.25, 300.0, 250.5],
            'Category': ['A', 'B', 'A', 'C', 'B'],
            'IsActive': [True, False, True, True, False],
            'Score': [85, 92, 78, 95, 88],
            'Description': ['Product A', 'Product B', 'Product A', 'Product C', 'Product B']
        })
        
        self.mock_app_core.get_current_data.return_value = (mixed_data, None)
        
        # Test various actions with mixed data
        result = self.handler._handle_summary_action()
        assert "Data Summary" in result or "Quick Summary" in result
        
        result = self.handler._handle_top_bottom_action("top 3")
        assert "Top 3 Rows" in result
        
        result = self.handler._handle_top_bottom_action("bottom 2 by score")
        assert "Bottom 2 Rows by Score" in result
    
    def test_integration_with_large_dataset(self):
        """
        Test integration with larger datasets to verify performance.
        
        Ensures that the system can handle realistic dataset sizes.
        """
        # Create larger dataset
        large_data = pd.DataFrame({
            'Date': pd.date_range('2020-01-01', periods=1000, freq='D'),
            'Revenue': np.random.normal(10000, 2000, 1000),
            'Units_Sold': np.random.poisson(100, 1000),
            'Region': np.random.choice(['North', 'South', 'East', 'West'], 1000),
            'Product': np.random.choice(['A', 'B', 'C', 'D', 'E'], 1000),
            'Customer_Type': np.random.choice(['New', 'Existing', 'Premium'], 1000)
        })
        
        self.mock_app_core.get_current_data.return_value = (large_data, None)
        
        # Test performance with large dataset
        import time
        
        # Summary should be fast
        start_time = time.time()
        result = self.handler._handle_summary_action()
        summary_time = time.time() - start_time
        
        assert summary_time < 5.0  # Should complete within 5 seconds
        assert "1,000 rows" in result  # Formatted with comma
        assert "6 columns" in result
        
        # Top N should be fast
        start_time = time.time()
        result = self.handler._handle_top_bottom_action("top 10")
        top_n_time = time.time() - start_time
        
        assert top_n_time < 3.0  # Should complete within 3 seconds
        assert "Top 10 Rows" in result
    
    def test_integration_error_recovery(self):
        """
        Test integration error recovery and graceful degradation.
        
        Verifies that errors in one component don't break the entire system.
        """
        # Test scenario: RAG system fails but base functionality continues
        self.mock_rag_analyzer.enhance_general_analysis.side_effect = Exception("RAG system down")
        
        # Summary should still work with fallback
        result = self.handler._handle_summary_action()
        assert "Data Summary" in result or "Quick Summary" in result
        assert "RAG Enhancement" not in result  # Should not include failed RAG
        
        # Test scenario: Timescale analyzer fails but other functions work
        self.mock_app_core.timescale_analyzer = None
        
        result = self.handler._handle_trends_action()
        assert "Timescale analyzer not available" in result
        
        # But other functions should still work
        result = self.handler._handle_top_bottom_action("top 5")
        assert "Top 5 Rows" in result
    
    def test_integration_data_flow_validation(self):
        """
        Test data flow validation across all components.
        
        Verifies that data flows correctly through the entire system.
        """
        # Test data flow: app_core → handler → analysis → response
        
        # Verify data is properly retrieved
        data, summary = self.handler.app_core.get_current_data()
        assert data is not None
        assert len(data) > 0
        
        # Verify data is properly processed in summary
        result = self.handler._handle_summary_action()
        assert str(len(data)) in result  # Row count should be included
        assert str(len(data.columns)) in result  # Column count should be included
        
        # Verify data flows correctly to top/bottom analysis
        result = self.handler._handle_top_bottom_action("top 5")
        
        # Should use first numeric column by default
        numeric_columns = data.select_dtypes(include=['number']).columns
        if len(numeric_columns) > 0:
            assert numeric_columns[0] in result
    
    def test_integration_timestamp_functionality(self):
        """
        Test timestamp functionality integration.
        
        Verifies that timestamps are properly added throughout the system.
        """
        # Test timestamp integration in full workflow
        history = []
        
        # Add multiple actions to test timestamp consistency
        history = self.handler.handle_action("summary", history)
        history = self.handler.handle_action("top 5", history)
        history = self.handler.handle_action("trends", history)
        
        # Verify all messages have timestamps
        for message in history:
            content = message["content"]
            # Check for timestamp format (HH:MM:SS)
            import re
            timestamp_pattern = r'\d{2}:\d{2}:\d{2}'
            assert re.search(timestamp_pattern, content), f"No timestamp found in: {content[:100]}..."
    
    def test_integration_rag_enhancement_workflow(self):
        """
        Test RAG enhancement integration across different analysis types.
        
        Verifies that RAG enhancement works consistently across all analysis types.
        """
        # Configure RAG responses for different analysis types
        self.mock_rag_analyzer.enhance_general_analysis.return_value = {
            'success': True,
            'enhanced_analysis': 'RAG-enhanced summary with business insights',
            'documents_used': 2,
            'prompt_used': 'Summary enhancement prompt'
        }
        
        self.mock_rag_analyzer.enhance_trend_analysis.return_value = {
            'success': True,
            'enhanced_analysis': 'RAG-enhanced trend analysis with market context',
            'documents_used': 3,
            'prompt_used': 'Trend enhancement prompt'
        }
        
        self.mock_rag_analyzer.enhance_variance_analysis.return_value = {
            'success': True,
            'enhanced_analysis': 'RAG-enhanced quantitative analysis with performance insights',
            'documents_used': 1,
            'prompt_used': 'Variance enhancement prompt'
        }
        
        # Test summary enhancement
        result = self.handler._handle_summary_action()
        assert "RAG-enhanced summary with business insights" in result
        assert "RAG Enhancement**: Analysis enhanced with 2 document(s)" in result
        
        # Test trends enhancement
        mock_timescale = Mock()
        mock_timescale.status = "completed"
        mock_timescale.format_for_chat.return_value = "Base trends analysis"
        self.mock_app_core.timescale_analyzer = mock_timescale
        
        result = self.handler._handle_trends_action()
        assert "RAG-enhanced trend analysis with market context" in result
        assert "RAG Enhancement**: Analysis enhanced with 3 document(s)" in result
        
        # Test variance enhancement
        with patch('analyzers.quant_analyzer.QuantAnalyzer') as mock_variance_class:
            mock_analyzer = Mock()
            mock_variance_class.return_value = mock_analyzer
            
            mock_analyzer.detect_variance_pairs.return_value = [
                {'actual': 'Actual_Sales', 'planned': 'Planned_Sales'}
            ]
            mock_analyzer.comprehensive_variance_analysis.return_value = {
                'variance_summary': 'Base quantitative analysis'
            }
            mock_analyzer.format_comprehensive_analysis.return_value = "Base quantitative analysis"
            
            result = self.handler._handle_variance_action()
            assert "RAG-enhanced quantitative analysis with performance insights" in result
            assert "RAG Enhancement**: Analysis enhanced with 1 document(s)" in result
    
    def test_integration_edge_case_combinations(self):
        """
        Test integration with various edge case combinations.
        
        Verifies that the system handles multiple edge cases simultaneously.
        """
        # Test with data that has multiple edge cases
        edge_case_data = pd.DataFrame({
            'Date': pd.date_range('2024-01-01', periods=3),
            'Revenue': [100, np.nan, 200],  # Has null values
            'Sales': [np.nan, np.nan, np.nan],  # All null values
            'Category': ['A', 'B', 'C'],  # Text only
            'Empty_Col': [None, None, None]  # All None
        })
        
        self.mock_app_core.get_current_data.return_value = (edge_case_data, None)
        
        # Test summary with edge cases
        result = self.handler._handle_summary_action()
        assert "Data Summary" in result or "Quick Summary" in result
        
        # Test top/bottom with edge cases
        result = self.handler._handle_top_bottom_action("top 5")
        # Should handle null values gracefully
        assert "Top" in result or "No numeric columns" in result or "missing values" in result
        
        # Test with column that has all null values
        result = self.handler._handle_top_bottom_action("top 5 by sales")
        assert "missing values" in result or "Column 'sales' not found" in result
    
    def test_integration_concurrent_operations(self):
        """
        Test integration with concurrent operations simulation.
        
        Verifies that the system can handle multiple operations without conflicts.
        """
        # Simulate concurrent operations by running multiple actions quickly
        results = []
        
        for i in range(5):
            result = self.handler._handle_summary_action()
            results.append(result)
            
            result = self.handler._handle_top_bottom_action(f"top {i+1}")
            results.append(result)
        
        # Verify all operations completed successfully
        assert len(results) == 10
        
        # Verify each result is valid
        for i, result in enumerate(results):
            assert isinstance(result, str)
            assert len(result) > 0
            
            if i % 2 == 0:  # Summary results
                assert "Data Summary" in result or "Quick Summary" in result
            else:  # Top N results
                assert "Top" in result or "Analysis" in result


class TestPhase2RealWorldScenarios:
    """
    Test suite for real-world scenario validation.
    
    This class tests the system with realistic business scenarios
    to ensure it performs well in actual use cases.
    """
    
    def setup_method(self):
        """
        Set up real-world scenario test fixtures.
        
        Creates realistic business data and scenarios for testing.
        """
        # Create realistic financial data
        self.financial_data = pd.DataFrame({
            'Date': pd.date_range('2023-01-01', periods=24, freq='M'),
            'Revenue': np.random.normal(1000000, 200000, 24),
            'Expenses': np.random.normal(800000, 150000, 24),
            'Profit': lambda x: x['Revenue'] - x['Expenses'],
            'Budget_Revenue': np.random.normal(950000, 180000, 24),
            'Budget_Expenses': np.random.normal(750000, 140000, 24),
            'Department': np.random.choice(['Sales', 'Marketing', 'Operations', 'IT'], 24),
            'Region': np.random.choice(['North', 'South', 'East', 'West'], 24),
            'Customer_Satisfaction': np.random.normal(4.2, 0.5, 24),
            'Employee_Count': np.random.poisson(50, 24)
        })
        
        # Calculate profit properly
        self.financial_data['Profit'] = self.financial_data['Revenue'] - self.financial_data['Expenses']
        
        # Create sales performance data
        self.sales_data = pd.DataFrame({
            'Date': pd.date_range('2024-01-01', periods=52, freq='W'),
            'Sales_Target': np.random.normal(50000, 10000, 52),
            'Actual_Sales': np.random.normal(48000, 12000, 52),
            'Leads_Generated': np.random.poisson(100, 52),
            'Conversion_Rate': np.random.beta(2, 8, 52),
            'Sales_Rep': np.random.choice(['Alice', 'Bob', 'Charlie', 'Diana', 'Eve'], 52),
            'Territory': np.random.choice(['North', 'South', 'East', 'West', 'Central'], 52),
            'Product_Line': np.random.choice(['Premium', 'Standard', 'Basic'], 52)
        })
        
        # Mock components
        self.mock_app_core = Mock()
        self.mock_rag_manager = Mock()
        self.mock_rag_analyzer = Mock()
        
        # Configure for financial data by default
        self.mock_app_core.has_data.return_value = True
        self.mock_app_core.get_current_data.return_value = (self.financial_data, None)
        self.mock_rag_manager.has_documents.return_value = True
        
        self.handler = QuickActionHandler(
            app_core=self.mock_app_core,
            rag_manager=self.mock_rag_manager,
            rag_analyzer=self.mock_rag_analyzer
        )
    
    def test_financial_analysis_scenario(self):
        """
        Test complete financial analysis scenario.
        
        Simulates a CFO analyzing financial performance data.
        """
        # CFO wants to understand overall financial performance
        history = []
        
        # Step 1: Get financial overview
        history = self.handler.handle_action("summary", history)
        summary_content = history[1]["content"]
        
        assert "24 rows" in summary_content
        assert "Revenue" in summary_content
        assert "Expenses" in summary_content
        assert "Profit" in summary_content
        
        # Step 2: Identify top performing periods
        history = self.handler.handle_action("top 5 by profit", history)
        top_content = history[3]["content"]
        
        assert "Top 5 Rows by Profit" in top_content
        
        # Step 3: Analyze variance between budget and actual
        history = self.handler.handle_action("variance", history)
        variance_content = history[5]["content"]
        
        # Should detect Quantitative trading analysis
        assert "variance" in variance_content.lower() or "comparison" in variance_content.lower()
        
        # Verify complete workflow
        assert len(history) == 6  # 3 user + 3 assistant messages
    
    def test_sales_performance_scenario(self):
        """
        Test sales performance analysis scenario.
        
        Simulates a sales manager analyzing team performance.
        """
        # Configure for sales data
        self.mock_app_core.get_current_data.return_value = (self.sales_data, None)
        
        # Sales manager wants to analyze team performance
        history = []
        
        # Step 1: Get sales overview
        history = self.handler.handle_action("summary", history)
        summary_content = history[1]["content"]
        
        assert "52 rows" in summary_content  # Weekly data
        assert "Sales_Target" in summary_content or "Actual_Sales" in summary_content
        
        # Step 2: Find top performing weeks
        history = self.handler.handle_action("top 10 by actual", history)
        top_content = history[3]["content"]
        
        assert "Top 10 Rows by Actual_Sales" in top_content
        
        # Step 3: Analyze sales vs target variance
        history = self.handler.handle_action("variance", history)
        variance_content = history[5]["content"]
        
        # Should detect Sales_Target vs Actual_Sales variance
        assert len(variance_content) > 100  # Should have substantial analysis
    
    def test_data_quality_scenario(self):
        """
        Test data quality analysis scenario.
        
        Simulates an analyst dealing with data quality issues.
        """
        # Create data with quality issues
        quality_data = pd.DataFrame({
            'Date': pd.date_range('2024-01-01', periods=10),
            'Revenue': [100, np.nan, 200, 300, np.nan, 400, 500, np.nan, 600, 700],
            'Sales': [90, 180, np.nan, 290, 380, np.nan, 490, 580, np.nan, 690],
            'Region': ['North', None, 'South', 'East', '', 'West', 'North', 'South', None, 'East'],
            'Valid_Data': [1, 0, 1, 1, 0, 1, 1, 0, 1, 1]  # 1 = valid, 0 = invalid
        })
        
        self.mock_app_core.get_current_data.return_value = (quality_data, None)
        
        # Analyst needs to understand data quality
        history = []
        
        # Step 1: Get data overview
        history = self.handler.handle_action("summary", history)
        summary_content = history[1]["content"]
        
        assert "10 rows" in summary_content
        assert "5 columns" in summary_content
        
        # Step 2: Try to get top performers (should handle null values)
        history = self.handler.handle_action("top 5 by revenue", history)
        top_content = history[3]["content"]
        
        # Should either show results or indicate data quality issues
        assert "Top 5 Rows" in top_content or "missing values" in top_content
        
        # Step 3: Try quantitative analysis
        history = self.handler.handle_action("variance", history)
        variance_content = history[5]["content"]
        
        # Should handle the analysis or provide appropriate feedback
        assert len(variance_content) > 50  # Should have some response
    
    def test_mixed_data_types_scenario(self):
        """
        Test mixed data types analysis scenario.
        
        Simulates analysis of diverse data types in business context.
        """
        # Create mixed data types
        mixed_data = pd.DataFrame({
            'Date': pd.date_range('2024-01-01', periods=8),
            'Revenue': [100.5, 200.75, 150.25, 300.0, 250.5, 180.25, 220.75, 190.5],
            'IsProfit': [True, True, False, True, True, False, True, False],
            'Rating': ['A', 'B', 'B', 'A', 'A', 'C', 'B', 'C'],
            'Score': [85, 92, 78, 95, 88, 72, 90, 80],
            'Category': ['Premium', 'Standard', 'Basic', 'Premium', 'Standard', 'Basic', 'Premium', 'Standard'],
            'Count': [10, 15, 8, 20, 12, 6, 18, 14]
        })
        
        self.mock_app_core.get_current_data.return_value = (mixed_data, None)
        
        # Analyst needs to work with mixed data types
        history = []
        
        # Step 1: Understand data structure
        history = self.handler.handle_action("summary", history)
        summary_content = history[1]["content"]
        
        assert "8 rows" in summary_content
        assert "7 columns" in summary_content
        
        # Step 2: Get top performers by revenue
        history = self.handler.handle_action("top 3 by revenue", history)
        top_content = history[3]["content"]
        
        assert "Top 3 Rows by Revenue" in top_content
        
        # Step 3: Get top performers by score
        history = self.handler.handle_action("top 3 by score", history)
        score_content = history[5]["content"]
        
        assert "Top 3 Rows by Score" in score_content
        
        # Verify all operations completed successfully
        assert len(history) == 6
    
    def test_no_data_scenario(self):
        """
        Test scenario when no data is available.
        
        Simulates user trying to analyze before uploading data.
        """
        # Configure no data available
        self.mock_app_core.has_data.return_value = False
        
        # User tries various actions without data
        history = []
        
        # Try summary
        history = self.handler.handle_action("summary", history)
        assert "Please upload a CSV file first" in history[1]["content"]
        
        # Try top N
        history = self.handler.handle_action("top 5", history)
        assert "Please upload a CSV file first" in history[3]["content"]
        
        # Try trends
        history = self.handler.handle_action("trends", history)
        assert "Please upload a CSV file first" in history[5]["content"]
        
        # Try variance
        history = self.handler.handle_action("variance", history)
        assert "Please upload a CSV file first" in history[7]["content"]
        
        # All should have consistent warning message
        for i in range(1, 8, 2):  # Assistant messages at odd indices
            assert "Please upload a CSV file first" in history[i]["content"]


if __name__ == "__main__":
    """
    Run the comprehensive Phase 2 integration test suite.
    
    This will execute all integration tests and provide detailed feedback
    on system integration and real-world scenario performance.
    """
    pytest.main([__file__, "-v", "--tb=short", "--durations=10"])
