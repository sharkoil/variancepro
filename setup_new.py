"""
Fresh Setup Script for Ollama + StarCoder2
Installs and configures everything needed for the financial chat app
"""

import subprocess
import sys
import time
import requests
import json
from pathlib import Path

def run_command(command, description, check_output=False):
    """Run a command with error handling"""
    print(f"🔄 {description}...")
    try:
        if check_output:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                print(f"✅ {description} completed successfully")
                return result.stdout.strip()
            else:
                print(f"❌ {description} failed: {result.stderr}")
                return None
        else:
            result = subprocess.run(command, shell=True, timeout=300)
            if result.returncode == 0:
                print(f"✅ {description} completed successfully")
                return True
            else:
                print(f"❌ {description} failed")
                return False
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} timed out")
        return False
    except Exception as e:
        print(f"❌ {description} error: {e}")
        return False

def check_ollama_running():
    """Check if Ollama service is running"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        return response.status_code == 200
    except:
        return False

def install_python_requirements():
    """Install Python requirements"""
    return run_command(
        f"{sys.executable} -m pip install -r requirements_new.txt",
        "Installing Python requirements"
    )

def install_ollama():
    """Install Ollama"""
    print("📦 Installing Ollama...")
    
    # For Windows, download and run installer
    print("Please download Ollama from: https://ollama.com/download")
    print("After installation, the service should start automatically.")
    
    # Wait for user confirmation
    input("Press Enter after you've installed Ollama...")
    
    # Check if Ollama is running
    for i in range(10):
        if check_ollama_running():
            print("✅ Ollama is running!")
            return True
        print(f"⏳ Waiting for Ollama to start... ({i+1}/10)")
        time.sleep(3)
    
    print("❌ Ollama is not responding. Please check the installation.")
    return False

def install_starcoder2():
    """Install StarCoder2 model"""
    if not check_ollama_running():
        print("❌ Ollama is not running. Cannot install StarCoder2.")
        return False
    
    print("📥 Downloading StarCoder2 model (this may take several minutes)...")
    
    # Pull the StarCoder2 model
    result = run_command(
        "ollama pull starcoder2:latest",
        "Downloading StarCoder2 model",
        check_output=True
    )
    
    if result is not None:
        print("✅ StarCoder2 model installed successfully!")
        return True
    else:
        print("❌ Failed to install StarCoder2 model")
        return False

def test_starcoder2():
    """Test StarCoder2 functionality"""
    if not check_ollama_running():
        print("❌ Ollama is not running. Cannot test StarCoder2.")
        return False
    
    print("🧪 Testing StarCoder2...")
    
    test_prompt = "Write a simple Python function to calculate compound interest"
    
    try:
        payload = {
            "model": "starcoder2:latest",
            "prompt": test_prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "max_tokens": 200
            }        }
        
        response = requests.post(
            "http://localhost:11434/api/generate",
            json=payload,
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            generated_text = result.get('response', '')
            if generated_text:
                print("✅ StarCoder2 is working correctly!")
                print(f"Sample response: {generated_text[:100]}...")
                return True
        
        print("❌ StarCoder2 test failed")
        return False
        
    except Exception as e:
        print(f"❌ StarCoder2 test error: {e}")
        return False

def create_sample_data():
    """Create a sample financial dataset for testing"""
    print("📊 Creating sample financial data...")
    
    try:
        import pandas as pd
        import numpy as np
        from datetime import datetime, timedelta
        
        # Generate sample financial data
        np.random.seed(42)
        
        dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
        
        data = {
            'Date': dates,
            'Revenue': np.random.normal(50000, 10000, len(dates)).round(2),
            'Costs': np.random.normal(30000, 5000, len(dates)).round(2),
            'Profit': 0,  # Will calculate
            'Department': np.random.choice(['Sales', 'Marketing', 'Operations', 'IT'], len(dates)),
            'Region': np.random.choice(['North', 'South', 'East', 'West'], len(dates))
        }
        
        df = pd.DataFrame(data)
        df['Profit'] = df['Revenue'] - df['Costs']
        
        # Save to CSV
        df.to_csv('sample_financial_data.csv', index=False)
        print("✅ Sample data created: sample_financial_data.csv")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create sample data: {e}")
        return False

def main():
    """Main setup process"""
    print("🚀 Financial Chat App Setup - Fresh Start")
    print("=" * 50)
    
    success_count = 0
    total_steps = 5
    
    # Step 1: Install Python requirements
    if install_python_requirements():
        success_count += 1
    
    # Step 2: Install Ollama
    if install_ollama():
        success_count += 1
    
    # Step 3: Install StarCoder2
    if install_starcoder2():
        success_count += 1
    
    # Step 4: Test StarCoder2
    if test_starcoder2():
        success_count += 1
    
    # Step 5: Create sample data
    if create_sample_data():
        success_count += 1
    
    # Summary
    print("\n" + "=" * 50)
    print(f"Setup completed: {success_count}/{total_steps} steps successful")
    
    if success_count == total_steps:
        print("✅ Setup completed successfully!")
        print("\nTo start the app, run:")
        print("python app_new.py")
    else:
        print("⚠️ Setup completed with some issues.")
        print("Please check the errors above and resolve them.")
    
    print("\n📚 Quick troubleshooting:")
    print("- Ensure Ollama is downloaded from https://ollama.com/download")
    print("- Check if Ollama service is running")
    print("- Verify internet connection for model downloads")

if __name__ == "__main__":
    main()
