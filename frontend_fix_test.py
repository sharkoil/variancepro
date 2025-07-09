#!/usr/bin/env python3
"""
Comprehensive test of the frontend fixes
"""

import gradio as gr
import pandas as pd
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.app_core import AppCore
from handlers.chat_handler import ChatHandler
from handlers.quick_action_handler import QuickActionHandler

def create_full_test_interface():
    """Create a comprehensive test interface for all fixes"""
    
    # Initialize components
    app_core = AppCore()
    chat_handler = ChatHandler(app_core)
    quick_handler = QuickActionHandler(app_core)
    
    # Create sample data
    sample_data = pd.DataFrame({
        'Product': ['Widget A', 'Widget B', 'Widget C', 'Widget D', 'Widget E'],
        'Revenue': [100000, 85000, 120000, 95000, 110000],
        'Expenses': [30000, 25000, 35000, 28000, 32000],
        'Profit': [70000, 60000, 85000, 67000, 78000],
        'Units_Sold': [1000, 850, 1200, 950, 1100]
    })
    
    app_core.current_data = sample_data
    app_core.data_summary = "Sample product data with revenue, expenses, and profit"
    
    def test_manual_prompt(prompt):
        """Test manual prompt processing"""
        try:
            response = chat_handler._generate_response(prompt)
            return response
        except Exception as e:
            return f"Error: {str(e)}"
    
    def test_button_action(action):
        """Test button actions"""
        try:
            history = []
            updated_history = quick_handler.handle_action(action, history)
            if updated_history:
                return updated_history[-1]['content']
            return "No response generated"
        except Exception as e:
            return f"Error: {str(e)}"
    
    # Read custom CSS
    custom_css = ""
    css_path = os.path.join(os.path.dirname(__file__), "static", "styles.css")
    if os.path.exists(css_path):
        with open(css_path, 'r') as f:
            custom_css = f.read()
    
    # Create interface
    with gr.Blocks(
        title="Quant Commander - Frontend Fix Test",
        theme=gr.themes.Soft(),
        css=custom_css
    ) as interface:
        
        gr.Markdown("# 🔧 Quant Commander Frontend Fix Test")
        gr.Markdown("Testing all frontend fixes: manual prompts, button actions, and resource loading")
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("## Sample Data")
                gr.Dataframe(value=sample_data, interactive=False, height=200)
                
                gr.Markdown("## Quick Action Buttons")
                with gr.Row():
                    top5_btn = gr.Button("🔝 Top 5", size="sm", variant="secondary")
                    bottom5_btn = gr.Button("🔻 Bottom 5", size="sm", variant="secondary")
                    top10_btn = gr.Button("📊 Top 10", size="sm", variant="secondary")
                    bottom10_btn = gr.Button("📉 Bottom 10", size="sm", variant="secondary")
                
                gr.Markdown("## Manual Prompts")
                manual_input = gr.Textbox(
                    label="Type your prompt",
                    placeholder="Try: 'top 5', 'bottom 3', 'show me top 10', etc."
                )
                manual_btn = gr.Button("Submit Manual Prompt", variant="primary")
            
            with gr.Column(scale=2):
                gr.Markdown("## Results")
                results_output = gr.Textbox(
                    label="Output",
                    lines=20,
                    max_lines=25,
                    placeholder="Results will appear here..."
                )
        
        # Event handlers for buttons
        top5_btn.click(
            fn=lambda: test_button_action("top 5"),
            inputs=[],
            outputs=[results_output]
        )
        
        bottom5_btn.click(
            fn=lambda: test_button_action("bottom 5"),
            inputs=[],
            outputs=[results_output]
        )
        
        top10_btn.click(
            fn=lambda: test_button_action("top 10"),
            inputs=[],
            outputs=[results_output]
        )
        
        bottom10_btn.click(
            fn=lambda: test_button_action("bottom 10"),
            inputs=[],
            outputs=[results_output]
        )
        
        # Event handler for manual prompts
        manual_btn.click(
            fn=test_manual_prompt,
            inputs=[manual_input],
            outputs=[results_output]
        )
        
        manual_input.submit(
            fn=test_manual_prompt,
            inputs=[manual_input],
            outputs=[results_output]
        )
    
    return interface

if __name__ == "__main__":
    print("🚀 Starting Quant Commander Frontend Fix Test...")
    interface = create_full_test_interface()
    print("✅ Test interface ready")
    print("🌐 Access at: http://localhost:7876")
    print("🔍 Test both buttons and manual prompts")
    
    # Launch with all fixes applied
    interface.launch(
        server_name="localhost",  # Fix postMessage origin issues
        server_port=7876,
        share=False,
        debug=True,
        show_error=True,
        allowed_paths=["static"],  # Allow static files
        favicon_path="static/logo.png" if os.path.exists("static/logo.png") else None
    )
