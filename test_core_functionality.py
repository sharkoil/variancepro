#!/usr/bin/env python3
"""
Simple test to verify core VariancePro functionality
"""

import pandas as pd
import sys
import os

def test_basic_imports():
    """Test that all core modules import correctly"""
    print("🔄 Testing imports...")
    
    try:
        from config.settings import Settings
        print("✅ Settings imported")
        
        from data.csv_loader import CSVLoader
        print("✅ CSVLoader imported")
        
        from ui.interface_builder import InterfaceBuilder
        print("✅ InterfaceBuilder imported")
        
        from ui.chat_handler import ChatHandler
        print("✅ ChatHandler imported")
        
        from utils.session_manager import SessionManager
        print("✅ SessionManager imported")
        
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_basic_functionality():
    """Test basic app initialization"""
    print("\n🔄 Testing basic functionality...")
    
    try:
        from config.settings import Settings
        from data.csv_loader import CSVLoader
        from utils.session_manager import SessionManager
        
        # Test settings
        settings = Settings()
        print(f"✅ Settings initialized: {settings.app_name} v{settings.app_version}")
        
        # Test session manager
        session_mgr = SessionManager()
        print(f"✅ Session manager initialized: {session_mgr.session_id}")
        
        # Test CSV loader
        csv_loader = CSVLoader(settings)
        print("✅ CSV loader initialized")
        
        return True
    except Exception as e:
        print(f"❌ Functionality error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_csv_processing():
    """Test CSV processing with sample data"""
    print("\n🔄 Testing CSV processing...")
    
    try:
        from config.settings import Settings
        from data.csv_loader import CSVLoader
        
        # Create sample data
        sample_data = pd.DataFrame({
            'Product': ['Widget A', 'Widget B', 'Widget C'],
            'Sales': [1000, 1500, 800],
            'Budget': [900, 1400, 1000],
            'Region': ['North', 'South', 'East']
        })
        
        # Save to temporary CSV
        sample_file = 'test_sample.csv'
        sample_data.to_csv(sample_file, index=False)
        
        # Test loading
        settings = Settings()
        csv_loader = CSVLoader(settings)
        loaded_data = csv_loader.load_csv(sample_file)
        
        print(f"✅ Sample CSV loaded: {loaded_data.shape[0]} rows, {loaded_data.shape[1]} columns")
        print(f"✅ Columns: {list(loaded_data.columns)}")
        
        # Test column suggestions
        suggestions = csv_loader.get_column_suggestions()
        print(f"✅ Column suggestions: {suggestions}")
        
        # Cleanup
        os.remove(sample_file)
        
        return True
    except Exception as e:
        print(f"❌ CSV processing error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_app_initialization():
    """Test full app initialization"""
    print("\n🔄 Testing app initialization...")
    
    try:
        from app import QuantCommanderApp
        
        app = QuantCommanderApp()
        print("✅ QuantCommanderApp initialized successfully")
        
        # Test status
        status = app.get_status()
        print(f"✅ Status generated: {len(status)} characters")
        
        return True
    except Exception as e:
        print(f"❌ App initialization error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🧪 VariancePro Core Functionality Test")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_basic_imports),
        ("Basic Functionality", test_basic_functionality),
        ("CSV Processing", test_csv_processing),
        ("App Initialization", test_app_initialization)
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n📋 Running: {name}")
        success = test_func()
        results.append((name, success))
        
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS:")
    
    all_passed = True
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status}: {name}")
        if not success:
            all_passed = False
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED! Core functionality is working.")
        print("✨ The app should be ready for use with 'python app.py'")
    else:
        print("\n⚠️ Some tests failed. Check the errors above.")
        
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
