#!/usr/bin/env python3
"""
Test script to verify that the contribution and variance analysis functions work correctly
after fixing the format_currency method calls.
"""

import pandas as pd
import sys
import os

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from analyzers.contributor_analyzer import ContributorAnalyzer
from analyzers.financial_analyzer import FinancialAnalyzer
from data.csv_loader import CSVLoader
from config.settings import Settings

def test_contribution_analysis():
    """Test the contribution analysis functionality"""
    print("🧪 Testing Contribution Analysis...")
    
    try:
        # Initialize settings and loader
        settings = Settings()
        loader = CSVLoader(settings)
        df = loader.load_csv("sample_variance_data.csv")
        
        # Initialize analyzer
        analyzer = ContributorAnalyzer(settings)
        
        # Test analysis
        results = analyzer.analyze(df, 'Product', 'Actual')
        
        print("✅ Contribution Analysis - SUCCESS")
        print(f"📊 Results preview (first 200 chars): {str(results)[:200]}...")
        return True
        
    except Exception as e:
        print(f"❌ Contribution Analysis - FAILED: {str(e)}")
        return False

def test_variance_analysis():
    """Test the variance analysis functionality"""
    print("\n🧪 Testing Variance Analysis...")
    
    try:
        # Initialize settings and loader
        settings = Settings()
        loader = CSVLoader(settings)
        df = loader.load_csv("sample_variance_data.csv")
        
        # Initialize analyzer
        analyzer = FinancialAnalyzer(settings)
        
        # Test analysis (using budget vs actual)
        results = analyzer.analyze(
            df, 
            date_col='Date', 
            value_col='Actual', 
            budget_col='Budget', 
            category_col='Product',
            analysis_type='variance'
        )
        
        print("✅ Variance Analysis - SUCCESS")
        print(f"📊 Results preview (first 200 chars): {str(results)[:200]}...")
        return True
        
    except Exception as e:
        print(f"❌ Variance Analysis - FAILED: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Fixed Analyzers Test Suite")
    print("=" * 50)
    
    # Test both analyzers
    contrib_success = test_contribution_analysis()
    variance_success = test_variance_analysis()
    
    print("\n" + "=" * 50)
    print("📋 TEST SUMMARY:")
    print(f"   Contribution Analysis: {'✅ PASSED' if contrib_success else '❌ FAILED'}")
    print(f"   Variance Analysis: {'✅ PASSED' if variance_success else '❌ FAILED'}")
    
    if contrib_success and variance_success:
        print("\n🎉 ALL TESTS PASSED - Currency formatting errors have been fixed!")
    else:
        print("\n❌ Some tests failed - additional debugging needed")
        sys.exit(1)
