"""
Test script for the refactored VariancePro v2.0 application
"""

def test_imports():
    """Test that all modules can be imported"""
    try:
        from app_v2 import VarianceProApp
        from core.app_core import AppCore
        from handlers.file_handler import FileHandler
        from handlers.chat_handler import ChatHandler
        from handlers.quick_action_handler import QuickActionHandler
        from analyzers.variance_analyzer import VarianceAnalyzer
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_initialization():
    """Test that the app can be initialized"""
    try:
        from app_v2 import VarianceProApp
        app = VarianceProApp()
        print("✅ App initialization successful")
        print(f"   Session ID: {app.app_core.session_id}")
        print(f"   Ollama Status: {app.app_core.ollama_status}")
        return True
    except Exception as e:
        print(f"❌ Initialization error: {e}")
        return False

def test_variance_analyzer():
    """Test variance analyzer functionality"""
    try:
        from analyzers.variance_analyzer import VarianceAnalyzer
        import pandas as pd
        
        # Create sample data
        data = pd.DataFrame({
            'Actual Sales': [1000, 1200, 900, 1100],
            'Planned Sales': [950, 1150, 1000, 1050],
            'Budget': [900, 1100, 950, 1000],
            'Month': ['Jan', 'Feb', 'Mar', 'Apr']
        })
        
        analyzer = VarianceAnalyzer()
        
        # Test variance pair detection
        pairs = analyzer.detect_variance_pairs(data.columns.tolist())
        print(f"✅ Variance pairs detected: {len(pairs)}")
        
        # Test variance calculation
        if pairs:
            result = analyzer.calculate_variance(
                data=data,
                actual_col=pairs[0]['actual'],
                planned_col=pairs[0]['planned']
            )
            print("✅ Variance calculation successful")
            print("   Sample result:", result[:100] + "..." if len(result) > 100 else result)
        
        return True
    except Exception as e:
        print(f"❌ Variance analyzer error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Refactored VariancePro v2.0")
    print("=" * 50)
    
    results = []
    results.append(test_imports())
    results.append(test_initialization())
    results.append(test_variance_analyzer())
    
    print("=" * 50)
    if all(results):
        print("🎉 All tests passed! Refactoring successful.")
    else:
        print("⚠️  Some tests failed. Check errors above.")

if __name__ == "__main__":
    main()
