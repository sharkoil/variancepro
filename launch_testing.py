"""
Quick Launcher for NL-to-SQL Testing
Easy way to test the new strategies vs current implementation
"""

import os
import sys
import subprocess

def main():
    """Launch the testing framework"""
    
    print("🧪 NL-to-SQL Strategy Testing Launcher")
    print("=" * 50)
    print()
    
    # Check if we're in the right directory
    if not os.path.exists("app.py"):
        print("❌ Please run this from the VariancePro root directory")
        sys.exit(1)
    
    print("Choose how you want to test the NL-to-SQL strategies:")
    print()
    print("1. 🚀 Full App with Testing Tab (recommended)")
    print("2. 🧪 Standalone Testing Interface")
    print("3. 🔬 Quick Programmatic Demo")
    print("4. ❓ Show Integration Instructions")
    print()
    
    choice = input("Enter your choice (1-4): ").strip()
    
    if choice == "1":
        print("\n🚀 Launching full app with integrated testing...")
        print("📍 Look for the '🧪 NL-to-SQL Testing' tab in the interface")
        print("🌐 Opening at: http://localhost:7871")
        subprocess.run([sys.executable, "app.py"])
    
    elif choice == "2":
        print("\n🧪 Launching standalone testing interface...")
        print("🌐 Opening at: http://localhost:7860")
        subprocess.run([sys.executable, "test_nl_to_sql_strategies.py", "--mode", "standalone"])
    
    elif choice == "3":
        print("\n🔬 Running programmatic demo...")
        subprocess.run([sys.executable, "test_nl_to_sql_strategies.py", "--mode", "demo"])
    
    elif choice == "4":
        print("\n📖 Integration Instructions:")
        print("""
To add testing to any existing Gradio app:

1. Import the integration module:
   from ui.nl_to_sql_testing_integration import add_testing_to_main_app

2. After creating your main interface:
   demo = add_testing_to_main_app(demo, llm_interpreter)

3. The testing framework will appear as a new tab.

📝 Example:
```python
import gradio as gr
from ui.nl_to_sql_testing_integration import add_testing_to_main_app

# Your existing interface
with gr.Blocks() as demo:
    gr.Markdown("# My App")
    # ... your existing tabs

# Add testing framework
demo = add_testing_to_main_app(demo, llm_interpreter)

demo.launch()
```
        """)
    
    else:
        print("❌ Invalid choice. Please run again and choose 1-4.")

if __name__ == "__main__":
    main()
