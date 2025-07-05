"""
Simple verification script to test NL-to-SQL framework components
"""

def test_imports():
    """Test that all imports work correctly"""
    print("🧪 Testing NL-to-SQL Framework Components...")
    print("=" * 50)
    
    try:
        import pandas as pd
        print("✅ pandas imported")
    except Exception as e:
        print(f"❌ pandas failed: {e}")
        return False
    
    try:
        from analyzers.strategy_1_llm_enhanced import LLMEnhancedNLToSQL
        print("✅ Strategy 1 (LLM-Enhanced) imported")
    except Exception as e:
        print(f"❌ Strategy 1 failed: {e}")
        return False
    
    try:
        from analyzers.strategy_2_semantic_parsing import SemanticNLToSQL
        print("✅ Strategy 2 (Semantic Parsing) imported")
    except Exception as e:
        print(f"❌ Strategy 2 failed: {e}")
        return False
    
    try:
        from analyzers.nl_to_sql_tester import NLToSQLTester
        print("✅ NL-to-SQL Tester imported")
    except Exception as e:
        print(f"❌ NL-to-SQL Tester failed: {e}")
        return False
    
    try:
        from ui.nl_to_sql_testing_ui import NLToSQLTestingUI
        print("✅ Testing UI imported")
    except Exception as e:
        print(f"❌ Testing UI failed: {e}")
        return False
    
    return True

def test_basic_functionality():
    """Test basic functionality with sample data"""
    print("\n🔬 Testing Basic Functionality...")
    print("=" * 50)
    
    try:
        import pandas as pd
        from analyzers.strategy_2_semantic_parsing import SemanticNLToSQL
        
        # Create test data
        data = {
            'Region': ['North', 'South', 'East', 'West'],
            'Sales_Actual': [15000, 12000, 18000, 14000],
            'Product': ['Widget A', 'Widget B', 'Widget C', 'Widget D']
        }
        df = pd.DataFrame(data)
        print("✅ Test data created")
        
        # Initialize strategy
        strategy = SemanticNLToSQL()
        print("✅ Strategy 2 initialized")
        
        # Set schema context
        schema_info = {
            'columns': list(df.columns),
            'column_types': {col: str(dtype) for col, dtype in df.dtypes.items()},
            'sample_values': {col: df[col].unique()[:3].tolist() for col in df.columns}
        }
        strategy.set_schema_context(schema_info, 'test_data')
        print("✅ Schema context set")
        
        # Test translation
        test_query = "Show me sales where region is North"
        result = strategy.translate_to_sql(test_query)
        print("✅ Translation completed")
        
        print(f"\nTest Query: '{test_query}'")
        print(f"Generated SQL: {result.sql_query}")
        print(f"Success: {result.success}")
        print(f"Confidence: {result.confidence:.2f}")
        print(f"Explanation: {result.explanation}")
        
        # Verify the SQL contains WHERE clause (key improvement)
        if 'WHERE' in result.sql_query.upper():
            print("🎯 SUCCESS: Generated SQL contains WHERE clause!")
        else:
            print("⚠️ WARNING: No WHERE clause found")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_framework_initialization():
    """Test full framework initialization"""
    print("\n🚀 Testing Framework Initialization...")
    print("=" * 50)
    
    try:
        from ui.nl_to_sql_testing_ui import NLToSQLTestingUI
        
        # Initialize with sample data
        testing_ui = NLToSQLTestingUI()
        print("✅ Testing UI initialized with sample data")
        
        # Check if data is loaded
        if testing_ui.current_data is not None:
            print(f"✅ Sample data loaded: {testing_ui.current_data.shape[0]} rows, {testing_ui.current_data.shape[1]} columns")
        else:
            print("⚠️ No data loaded")
        
        # Check if tester is initialized
        if testing_ui.tester is not None:
            print("✅ Tester framework initialized")
        else:
            print("⚠️ Tester not initialized")
        
        return True
        
    except Exception as e:
        print(f"❌ Framework initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🧪 NL-to-SQL Testing Framework Verification")
    print("=" * 60)
    
    # Test imports
    if not test_imports():
        print("\n❌ Import tests failed. Please check dependencies.")
        return False
    
    # Test basic functionality
    if not test_basic_functionality():
        print("\n❌ Basic functionality tests failed.")
        return False
    
    # Test framework initialization
    if not test_framework_initialization():
        print("\n❌ Framework initialization failed.")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 ALL TESTS PASSED!")
    print("=" * 60)
    print()
    print("🚀 Ready to test NL-to-SQL strategies!")
    print()
    print("Next steps:")
    print("1. Run: python launch_testing.py")
    print("2. Choose option 1 for full app with testing tab")
    print("3. Or choose option 2 for standalone testing")
    print()
    print("📖 See docs/NL_TO_SQL_TESTING_FRAMEWORK.md for detailed guide")
    
    return True

if __name__ == "__main__":
    main()
