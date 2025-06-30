"""
Quick test script for the Financial Chat App
Tests core functionality without running the full interface
"""

def test_app_components():
    """Test all app components"""
    print("🧪 Testing Financial Chat App Components")
    print("=" * 50)
    
    success_count = 0
    total_tests = 7  # Updated test count
    
    # Test 1: Import testing
    try:
        import gradio as gr
        import pandas as pd
        import requests
        import numpy as np
        print("✅ Test 1: All imports successful")
        success_count += 1
    except Exception as e:
        print(f"❌ Test 1: Import failed - {e}")
    
    # Test 2: Sample data loading
    try:
        df = pd.read_csv('sample_financial_data.csv')
        print(f"✅ Test 2: Sample data loaded ({df.shape[0]} rows, {df.shape[1]} cols)")
        success_count += 1
    except Exception as e:
        print(f"❌ Test 2: Sample data loading failed - {e}")
    
    # Test 3: Ollama connectivity
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=3)
        if response.status_code == 200:
            print("✅ Test 3: Ollama is available")
        else:
            print("⚠️ Test 3: Ollama responded but with non-200 status")
        success_count += 1
    except:
        print("❌ Test 3: Ollama not available (run setup_new.py)")
    
    # Test 4: StarCoder2 availability
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=3)
        if response.status_code == 200:
            models = response.json().get('models', [])
            starcoder_available = any('starcoder2' in model.get('name', '') for model in models)
            if starcoder_available:
                print("✅ Test 4: StarCoder2 model available")
                success_count += 1
            else:
                print("❌ Test 4: StarCoder2 model not found")
        else:
            print("❌ Test 4: Cannot check StarCoder2 (Ollama issue)")
    except:
        print("❌ Test 4: Cannot check StarCoder2 (Ollama not running)")
    
    # Test 5: App class initialization
    try:
        from app_new import FinancialChatApp
        app = FinancialChatApp()
        print("✅ Test 5: App class initialized successfully")
        success_count += 1
    except Exception as e:
        print(f"❌ Test 5: App initialization failed - {e}")
    
    # Test 6: Data processing test
    try:
        import pandas as pd
        df = pd.read_csv('sample_financial_data.csv')
        summary = f"""Dataset Summary:
- Shape: {df.shape[0]} rows, {df.shape[1]} columns
- Columns: {', '.join(df.columns.tolist())}"""
        print("✅ Test 6: Data processing works")
        success_count += 1
    except Exception as e:
        print(f"❌ Test 6: Data processing failed - {e}")
    
    # Test 7: DeepSeek LLM integration
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=3)
        if response.status_code == 200:
            models = response.json().get('models', [])
            deepseek_available = any('deepseek' in model.get('name', '').lower() for model in models)
            if deepseek_available:
                print("✅ Test 7: DeepSeek model available")
                success_count += 1
            else:
                print("❌ Test 7: DeepSeek model not found")
        else:
            print("❌ Test 7: Cannot check DeepSeek (Ollama issue)")
    except:
        print("❌ Test 7: Cannot check DeepSeek (Ollama not running)")
    
    # Summary
    print("\n" + "=" * 50)
    print(f"Test Results: {success_count}/{total_tests} passed")
    
    if success_count >= 5:  # Updated threshold
        print("🎉 App is ready to use!")
        print("\n🚀 To start the app:")
        print("   python app_new.py")
        print("   OR")
        print("   double-click start_app.bat")
    else:
        print("⚠️ Some issues found. Please check the errors above.")
        if success_count < 3:  # Updated threshold
            print("💡 Try running: python setup_new.py")
    
    return success_count >= 5  # Updated threshold

if __name__ == "__main__":
    test_app_components()
