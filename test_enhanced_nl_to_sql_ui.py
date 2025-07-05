"""
Test script for the enhanced NL-to-SQL testing UI with model selection
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.nl_to_sql_testing_ui_enhanced import EnhancedNLToSQLTestingUI
from config.settings import Settings

def main():
    """Launch the enhanced testing UI"""
    print("🚀 Starting Enhanced NL-to-SQL Testing Framework...")
    
    # Initialize settings
    settings = Settings()
    
    # Create enhanced UI instance
    ui = EnhancedNLToSQLTestingUI(settings=settings)
    
    # Create and launch interface
    interface = ui.create_testing_interface()
    
    print("✅ Enhanced UI initialized successfully!")
    print(f"📋 Available models: {ui.available_models}")
    print(f"🤖 Current model: {ui.current_model}")
    print("🌐 Launching interface...")
    
    interface.launch(
        server_name="0.0.0.0", 
        server_port=7862,
        share=False,
        debug=True
    )

if __name__ == "__main__":
    main()
