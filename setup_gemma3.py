#!/usr/bin/env python3
"""
Setup script for VariancePro with Gemma3:12B integration
"""

import subprocess
import sys
import requests
import time
import os

def check_command_exists(command):
    """Check if a command exists in PATH"""
    try:
        subprocess.run([command, "--version"], 
                     capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def check_ollama_running():
    """Check if Ollama is running"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        return response.status_code == 200
    except:
        return False

def check_gemma3_installed():
    """Check if Gemma3:12B is installed"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            return any("gemma3:12b" in model["name"] for model in models)
    except:
        pass
    return False

def run_command(command, description):
    """Run a command with description"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def main():
    print("🚀 VariancePro Gemma3:12B Setup")
    print("=" * 40)
    
    # Check if Ollama is installed
    if not check_command_exists("ollama"):
        print("❌ Ollama not found. Please install Ollama first.")
        print("📥 Download from: https://ollama.ai/download")
        sys.exit(1)
    else:
        print("✅ Ollama is installed")
    
    # Check if Ollama is running
    if not check_ollama_running():
        print("🚀 Starting Ollama service...")
        if not run_command("ollama serve", "Starting Ollama"):
            print("⚠️ Failed to start Ollama. Please start it manually:")
            print("   ollama serve")
        
        # Wait a bit for Ollama to start
        print("⏳ Waiting for Ollama to start...")
        time.sleep(3)
    else:
        print("✅ Ollama is running")
    
    # Install Gemma3:12B if not present
    if not check_gemma3_installed():
        print("📥 Installing Gemma3:12B model (this may take several minutes)...")
        if run_command("ollama pull gemma3:12b", "Installing Gemma3:12B"):
            print("✅ Gemma3:12B installed successfully")
        else:
            print("❌ Failed to install Gemma3:12B")
            sys.exit(1)
    else:
        print("✅ Gemma3:12B is already installed")
    
    # Install Python dependencies
    print("📦 Installing Python dependencies...")
    if run_command(f"{sys.executable} -m pip install -r requirements.txt", 
                   "Installing Python packages"):
        print("✅ Python dependencies installed")
    else:
        print("❌ Failed to install Python dependencies")
        sys.exit(1)
    
    print("\n🎉 Setup Complete!")
    print("=" * 40)
    print("🚀 To start the app, run:")
    print("   python app.py")
    print("\n💡 The app will be available at: http://localhost:7860")
    
    # Ask if user wants to start the app
    if input("\n🚀 Start the app now? (y/n): ").lower().startswith('y'):
        print("🚀 Starting VariancePro...")
        os.system(f"{sys.executable} app.py")

if __name__ == "__main__":
    main()
