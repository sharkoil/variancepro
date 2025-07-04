#!/usr/bin/env python3
"""
Test individual analyzers to identify and fix issues
"""

import pandas as pd
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_individual_analyzers():
    """Test each analyzer individually to identify issues"""
    try:
        print("🔄 Testing individual analyzers...")
        
        from app_new import QuantCommanderApp
        app = QuantCommanderApp()
        
        # Create test data
        sample_data = pd.DataFrame({
            'Product': ['Widget A', 'Widget B', 'Widget C', 'Widget D', 'Widget E'],
            'Sales': [1000, 1500, 800, 2000, 1200],
            'Budget': [900, 1400, 1000, 1800, 1100],
            'Actual': [1000, 1500, 800, 2000, 1200],
            'Region': ['North', 'South', 'North', 'West', 'East'],
            'Quarter': ['Q1', 'Q1', 'Q2', 'Q2', 'Q1'],
            'Date': pd.date_range('2024-01-01', periods=5, freq='ME')
        })
        
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
        
        # Test 1: Contribution Analyzer
        print("\n🔄 Testing Contribution Analyzer...")
        app.column_suggestions = {
            'category_columns': ['Product', 'Region'],
            'value_columns': ['Sales', 'Budget', 'Actual']
        }
        
        try:
            response = app._perform_contribution_analysis("analyze contribution")
            print(f"✅ Contribution Analyzer works ({len(response)} chars)")
        except Exception as e:
            print(f"❌ Contribution Analyzer failed: {str(e)}")
            import traceback
            traceback.print_exc()
        
        # Test 2: Variance Analyzer - check what it expects
        print("\n🔄 Testing Variance Analyzer...")
        print("Checking what variance analyzer expects...")
        
        # Check the variance analyzer source to understand the expected format
        from analyzers.financial_analyzer import FinancialAnalyzer
        
        # Test with different column_suggestions formats
        test_formats = [
            {
                'category_columns': ['Product', 'Region'],
                'value_columns': ['Sales', 'Budget', 'Actual'],
                'budget_vs_actual': {
                    'budget_columns': ['Budget'],
                    'actual_columns': ['Actual']
                }
            },
            {
                'category_columns': ['Product', 'Region'],
                'value_columns': ['Sales', 'Budget', 'Actual'],
                'budget_vs_actual': {'Budget': 'Actual'}
            },
            {
                'category_columns': ['Product', 'Region'],
                'value_columns': ['Sales', 'Budget', 'Actual'],
                'budget_columns': ['Budget'],
                'actual_columns': ['Actual']
            }
        ]
        
        for i, format_test in enumerate(test_formats):
            print(f"  Testing format {i+1}...")
            app.column_suggestions = format_test
            try:
                response = app._perform_variance_analysis("analyze variance")
                print(f"  ✅ Format {i+1} works ({len(response)} chars)")
                break
            except Exception as e:
                print(f"  ❌ Format {i+1} failed: {str(e)}")
        
        # Test 3: Trend Analyzer
        print("\n🔄 Testing Trend Analyzer...")
        app.column_suggestions = {
            'category_columns': ['Product', 'Region'],
            'value_columns': ['Sales', 'Budget', 'Actual']
        }
        
        try:
            response = app._perform_trend_analysis("analyze trends")
            print(f"✅ Trend Analyzer works ({len(response)} chars)")
        except Exception as e:
            print(f"❌ Trend Analyzer failed: {str(e)}")
            import traceback
            traceback.print_exc()
        
        # Test 4: Data Overview
        print("\n🔄 Testing Data Overview...")
        try:
            response = app._generate_data_overview()
            print(f"✅ Data Overview works ({len(response)} chars)")
        except Exception as e:
            print(f"❌ Data Overview failed: {str(e)}")
            import traceback
            traceback.print_exc()
        
        # Test 5: Top N Analyzer
        print("\n🔄 Testing Top N Analyzer...")
        try:
            response = app._perform_top_n_analysis("top 5 products", is_bottom=False)
            print(f"✅ Top N Analyzer works ({len(response)} chars)")
        except Exception as e:
            print(f"❌ Top N Analyzer failed: {str(e)}")
            import traceback
            traceback.print_exc()
        
        return True
        
    except Exception as e:
        print(f"\n❌ Individual analyzer test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_individual_analyzers()
    sys.exit(0 if success else 1)
