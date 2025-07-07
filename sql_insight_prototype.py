"""
SQL Insight Engine Prototype - Standalone Launcher
AI-Powered SQL Query Analysis with Smart Field Detection

This prototype demonstrates the concept from the SQL GUI article with:
1. Field picker with AI-powered type inference using Ollama/Gemma
2. SQL query execution with safety validation
3. LLM-powered insights generation
4. Query template management
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.sql_insight_ui import create_sql_insight_interface
import gradio as gr

def main():
    """
    Launch the SQL Insight Engine prototype
    """
    print("🚀 Starting SQL Insight Engine Prototype...")
    print("🧠 Features:")
    print("   • AI-powered field type detection")
    print("   • Smart query suggestions")
    print("   • LLM-generated insights")
    print("   • Query template management")
    print("   • Safe SQL execution")
    print()
    
    # Create the interface
    interface = create_sql_insight_interface()
    
    # Launch with custom settings
    interface.launch(
        server_name="0.0.0.0",
        server_port=7875,
        share=False,
        debug=True,
        show_tips=True,
        quiet=False
    )

if __name__ == "__main__":
    main()
