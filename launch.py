"""
Simple launcher for the Financial Chat App
Checks prerequisites and starts the application
"""

import subprocess
import sys
import requests
import time

def check_ollama():
    """Check if Ollama is running"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        return response.status_code == 200
    except:
        return False

def check_starcoder2():
    """Check if StarCoder2 model is available"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            model_names = [model.get('name', '') for model in models]
            return any('starcoder2' in name for name in model_names)
        return False
    except:
        return False

def main():
    """Main launcher"""
    print("🚀 Financial Chat App Launcher")
    print("=" * 40)
    
    # Check Ollama
    print("🔍 Checking Ollama...")
    if check_ollama():
        print("✅ Ollama is running")
    else:
        print("❌ Ollama is not running")
        print("Please start Ollama or run setup_new.py first")
        return
    
    # Check StarCoder2
    print("🔍 Checking StarCoder2...")
    if check_starcoder2():
        print("✅ StarCoder2 model is available")
    else:
        print("❌ StarCoder2 model not found")
        print("Please run setup_new.py to install the model")
        return
    
    print("\n✅ All prerequisites met!")
    print("🚀 Starting the Financial Chat App...")
    
    # Start the app
    try:
        subprocess.run([sys.executable, "app_new.py"])
    except KeyboardInterrupt:
        print("\n👋 App stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting app: {e}")

if __name__ == "__main__":
    main()
