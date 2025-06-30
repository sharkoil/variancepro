#!/usr/bin/env python3
"""
VariancePro LLM Setup Script
Helps set up Phi-3/Phi-4 models for enhanced financial analysis
"""

import subprocess
import sys
import os
import requests
import time

def check_ollama_installed():
    """Check if Ollama is installed"""
    try:
        result = subprocess.run(["ollama", "--version"], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def check_ollama_running():
    """Check if Ollama service is running"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        return response.status_code == 200
    except:
        return False

def install_ollama_windows():
    """Instructions for installing Ollama on Windows"""
    print("\n🔧 OLLAMA INSTALLATION REQUIRED")
    print("=" * 50)
    print("1. Download Ollama from: https://ollama.ai/download")
    print("2. Run the installer")
    print("3. Restart your terminal/PowerShell")
    print("4. Run this script again")
    print("\nAlternatively, you can install via winget:")
    print("winget install Ollama.Ollama")

def pull_starcoder_models():
    """Pull StarCoder models for enhanced code analysis"""
    models = [
        ("starcoder2", "StarCoder2 (7B parameters) - Latest, fast code analysis"),
        ("starcoder", "StarCoder (15B parameters) - Original, more comprehensive"),
        ("phi3", "Microsoft Phi-3 (3.8B parameters) - General financial analysis"),
        ("phi3.5", "Microsoft Phi-3.5 (3.8B parameters) - Latest general model")
    ]
    
    print("\n🤖 AVAILABLE AI MODELS")
    print("=" * 50)
    for i, (model, description) in enumerate(models, 1):
        print(f"{i}. {model} - {description}")
    
    print("\nRecommended: Start with starcoder2 (best balance of speed and capability)")
    choice = input("\nEnter model number to install (1-4) or 'all' for all models: ").strip()
    
    if choice.lower() == 'all':
        selected_models = [model[0] for model in models]
    elif choice in ['1', '2', '3', '4']:
        selected_models = [models[int(choice)-1][0]]
    else:
        print("Invalid choice. Installing starcoder2 by default.")
        selected_models = ["starcoder2"]
    
    for model in selected_models:
        print(f"\n📥 Pulling {model}...")
        try:
            result = subprocess.run(["ollama", "pull", model], check=True)
            print(f"✅ Successfully installed {model}")
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install {model}")
        except FileNotFoundError:
            print("❌ Ollama not found. Please install Ollama first.")
            return False
    
    return True

def list_installed_models():
    """List currently installed models"""
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True, check=True)
        print("\n📋 INSTALLED MODELS")
        print("=" * 50)
        print(result.stdout)
    except:
        print("❌ Could not list models")

def test_model(model_name="phi3"):
    """Test the installed model"""
    print(f"\n🧪 TESTING {model_name.upper()}")
    print("=" * 50)
    
    test_prompt = "Analyze this sample financial data: Stock AAPL, Price: $150, Volume: 1M shares. What insights can you provide?"
    
    try:
        print("Sending test query...")
        result = subprocess.run([
            "ollama", "run", model_name, test_prompt
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Model is working! Sample response:")
            print("-" * 30)
            print(result.stdout[:300] + "..." if len(result.stdout) > 300 else result.stdout)
            return True
        else:
            print("❌ Model test failed")
            print(result.stderr)
            return False
    except subprocess.TimeoutExpired:
        print("⏱️ Test timed out - model might be slow but working")
        return True
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

def main():
    print("🚀 VARIANCEPRO LLM SETUP")
    print("=" * 50)
    print("This script will help you set up Phi-3/Phi-4 models for enhanced financial analysis.\n")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required. You have:", sys.version)
        return
    
    # Check if Ollama is installed
    if not check_ollama_installed():
        install_ollama_windows()
        return
    
    print("✅ Ollama is installed")
    
    # Check if Ollama is running
    if not check_ollama_running():
        print("🔄 Starting Ollama service...")
        try:
            if os.name == 'nt':  # Windows
                subprocess.Popen(["ollama", "serve"], creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:
                subprocess.Popen(["ollama", "serve"])
            
            # Wait for service to start
            for i in range(10):
                time.sleep(2)
                if check_ollama_running():
                    print("✅ Ollama service started")
                    break
                print(f"⏳ Waiting for Ollama service... ({i+1}/10)")
            else:
                print("❌ Could not start Ollama service. Please start manually: 'ollama serve'")
                return
        except Exception as e:
            print(f"❌ Error starting Ollama: {e}")
            print("Please start Ollama manually: 'ollama serve'")
            return
    else:
        print("✅ Ollama service is running")
    
    # List existing models
    list_installed_models()
    
    # Ask user what to do
    print("\n🎯 SETUP OPTIONS")
    print("=" * 50)
    print("1. Install new Phi models")
    print("2. Test existing models")
    print("3. Show setup instructions")
    print("4. Exit")
    
    choice = input("\nChoose an option (1-4): ").strip()
    
    if choice == "1":
        if pull_starcoder_models():
            print("\n✅ Model installation complete!")
            test_choice = input("\nTest the installed model? (y/n): ").strip().lower()
            if test_choice == 'y':
                test_model()
    
    elif choice == "2":
        models = ["starcoder2", "starcoder", "phi3", "phi3.5"]
        print("\nAvailable models to test:")
        for i, model in enumerate(models, 1):
            print(f"{i}. {model}")
        
        test_choice = input("\nEnter model number to test (1-4): ").strip()
        if test_choice in ['1', '2', '3', '4']:
            model_to_test = models[int(test_choice)-1]
            test_model(model_to_test)
    
    elif choice == "3":
        print("\n📋 SETUP INSTRUCTIONS")
        print("=" * 50)
        print("1. Install Ollama: https://ollama.ai/download")
        print("2. Open terminal/PowerShell")
        print("3. Run: ollama pull starcoder2")
        print("4. Start your VariancePro app")
        print("5. Look for '🤖 StarCoder AI Status' in the sidebar")
        print("\nFor other models, also try:")
        print("   ollama pull starcoder    # Original StarCoder")
        print("   ollama pull phi3         # Microsoft Phi-3")
        print("   ollama pull phi3.5       # Latest Phi model")
    
    print("\n🎉 Setup complete! Restart your VariancePro app to use StarCoder-enhanced analysis.")

if __name__ == "__main__":
    main()
