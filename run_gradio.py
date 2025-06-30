#!/usr/bin/env python3
"""
Launch script for VariancePro Gradio App
"""

import subprocess
import sys
import os

def main():
    """Launch the Gradio app"""
    print("🚀 Starting VariancePro Gradio App...")
    print("📊 Financial Data Analysis Chat")
    print("-" * 40)
    
    # Change to the script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    try:
        # Run the Gradio app
        subprocess.run([sys.executable, "app.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running the app: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 App stopped by user")
        sys.exit(0)

if __name__ == "__main__":
    main()
