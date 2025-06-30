#!/usr/bin/env python3
"""
Setup script for VariancePro with Phi4 integration
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

def check_phi4_installed():
    """Check if Phi4 is installed"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            return any("phi4" in model["name"] for model in models)
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

def install_requirements():
    """Install Python requirements"""
    if os.path.exists("requirements.txt"):
        return run_command(f"{sys.executable} -m pip install -r requirements.txt", 
                         "Installing Python requirements")
    else:
        print("⚠️ requirements.txt not found")
        return False

def main():
    """Main setup process"""
    print("🚀 VariancePro Phi4 Setup")
    print("=" * 40)
    
    # Check Python
    print(f"🐍 Python version: {sys.version}")
    
    # Check Ollama
    if not check_command_exists("ollama"):
        print("❌ Ollama not found!")
        print("📥 Please install Ollama from: https://ollama.ai/download")
        print("   Then run this script again.")
        return False
    else:
        print("✅ Ollama found")
    
    # Install Python requirements
    if not install_requirements():
        print("❌ Failed to install Python requirements")
        return False
    
    # Start Ollama if not running
    if not check_ollama_running():
        print("🔄 Starting Ollama service...")
        if not run_command("ollama serve", "Starting Ollama"):
            print("❌ Failed to start Ollama")
            print("💡 Try running 'ollama serve' manually in another terminal")
            return False
        time.sleep(3)  # Give Ollama time to start
    else:
        print("✅ Ollama is running")
    
    # Install Phi4 if not present
    if not check_phi4_installed():
        print("📥 Installing Phi4 model (this may take several minutes)...")
        if run_command("ollama pull phi4", "Installing Phi4"):
            print("✅ Phi4 installed successfully")
        else:
            print("❌ Failed to install Phi4")
            return False
    else:
        print("✅ Phi4 is already installed")
    
    # Final check
    print("\n🔍 Final System Check:")
    print("=" * 30)
    
    if check_ollama_running():
        print("✅ Ollama service: Running")
    else:
        print("❌ Ollama service: Not running")
        
    if check_phi4_installed():
        print("✅ Phi4 model: Available")
    else:
        print("❌ Phi4 model: Not found")
    
    print("\n🚀 Setup complete!")
    print("💡 Run 'python app.py' to start VariancePro")
    print("🌐 Access at: http://localhost:7860")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
