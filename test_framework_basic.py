"""
Simple test to verify NL-to-SQL testing framework is working
"""

def test_basic_functionality():
    """Test basic functionality of the framework"""
    
    print("🧪 Testing NL-to-SQL Framework Components...")
    
    try:
        # Test imports
        from analyzers.enhanced_nl_to_sql_translator import EnhancedNLToSQLTranslator
        from analyzers.strategy_1_llm_enhanced import LLMEnhancedNLToSQL
        from analyzers.strategy_2_semantic_parsing import SemanticNLToSQL
        from analyzers.nl_to_sql_tester import NLToSQLTester
        from ai.llm_interpreter import LLMInterpreter
        from config.settings import Settings
        print("✅ All imports successful")
        
        # Test basic instantiation
        settings = Settings()
        llm_interpreter = LLMInterpreter(settings)
        
        current_translator = EnhancedNLToSQLTranslator()
        strategy_1_translator = LLMEnhancedNLToSQL(llm_interpreter)
        strategy_2_translator = SemanticNLToSQL()
        print("✅ All translators instantiated successfully")
        
        # Test with sample data
        import pandas as pd
        sample_data = pd.DataFrame({
            'Region': ['North', 'South', 'East', 'West'],
            'Sales': [1000, 2000, 1500, 1800],
            'Product': ['A', 'B', 'C', 'D']
        })
        
        tester = NLToSQLTester(sample_data, llm_interpreter)
        tester.initialize_strategies(
            current_translator,
            strategy_1_translator,
            strategy_2_translator
        )
        print("✅ Testing framework initialized successfully")
        
        # Test enhanced UI
        from ui.nl_to_sql_testing_ui_enhanced import EnhancedNLToSQLTestingUI
        ui = EnhancedNLToSQLTestingUI(settings=settings)
        print("✅ Enhanced UI instantiated successfully")
        print(f"📋 Found {len(ui.available_models)} available models")
        print(f"🤖 Current model: {ui.current_model}")
        
        print("\n🎉 All components working correctly!")
        return True
        
    except Exception as e:
        import traceback
        print(f"❌ Error: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_basic_functionality()
    if success:
        print("\n✅ Framework is ready for use!")
    else:
        print("\n❌ Please check the errors above")
