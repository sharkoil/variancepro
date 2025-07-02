"""
VariancePro - Launch Script
Quick launcher for the VariancePro application with system checks
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

def check_gemma3():
    """Check if Gemma3 model is available"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            model_names = [model.get('name', '') for model in models]
            return any('gemma3' in name.lower() for name in model_names)
        return False
    except:
        return False

def main():
    """Main launcher for VariancePro"""
    print("🚀 VariancePro - AI-Powered Financial Analysis")
    print("=" * 50)
    
    # Check Ollama
    print("🔍 Checking Ollama service...")
    if check_ollama():
        print("✅ Ollama is running")
        
        # Check Gemma3
        print("🔍 Checking Gemma3 model...")
        if check_gemma3():
            print("✅ Gemma3 model is available")
            ai_status = "Full AI features enabled"
        else:
            print("⚠️ Gemma3 model not found")
            print("   AI features will be limited")
            ai_status = "Limited AI features (no LLM)"
    else:
        print("❌ Ollama is not running")
        print("   AI features will be disabled")
        ai_status = "No AI features (Ollama offline)"
    
    print(f"\n🤖 AI Status: {ai_status}")
    print("✅ All core analysis features available")
    print("\n🚀 Starting VariancePro...")
    
    # Start the app
    try:
        subprocess.run([sys.executable, "app_new.py"])
    except KeyboardInterrupt:
        print("\n👋 VariancePro shutdown complete")
    except Exception as e:
        print(f"\n❌ Error starting VariancePro: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Run: pip install -r requirements.txt")
        print("2. Ensure Python 3.8+ is being used")
        print("3. For AI features: ollama pull gemma3:latest")

if __name__ == "__main__":
    main()
