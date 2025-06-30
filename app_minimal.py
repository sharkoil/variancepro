#!/usr/bin/env python3
"""
MINIMAL VariancePro App - ONLY Chat and Data tabs - NO VISUALIZATION WHATSOEVER
"""

import gradio as gr
import pandas as pd
import numpy as np
import io

def minimal_create_interface():
    """Create the minimal Gradio interface with ONLY 2 tabs"""
    
    with gr.Blocks(
        title="VariancePro - NO VIZ",
        theme=gr.themes.Soft(),
        css="""
        .container { max-width: 1200px; margin: auto; }
        .data-grid { max-height: 500px; overflow: auto; }
        """
    ) as interface:
        
        gr.Markdown("# 🚀 VariancePro - NO VISUALIZATION")
        gr.Markdown("### ONLY 2 TABS: Chat and Data")
        
        # Create tabs - ONLY 2!
        with gr.Tabs():
            # Tab 1: Chat Analysis
            with gr.TabItem("💬 Chat Analysis"):
                gr.Markdown("### Chat functionality here")
                
                chatbot = gr.Chatbot(
                    label="💬 Financial Analysis Chat",
                    height=400,
                    show_label=True,
                    type="messages"
                )
                
                user_input = gr.Textbox(
                    label="Ask about your financial data:",
                    placeholder="Enter your question here",
                    lines=2
                )
                
                submit_btn = gr.Button("🔍 Analyze", variant="primary")
            
            # Tab 2: Data View - ONLY!
            with gr.TabItem("📊 Data View"):
                gr.Markdown("### Data view functionality here")
                
                data_grid = gr.DataFrame(
                    label="📈 Data Grid",
                    interactive=False,
                    wrap=True
                )
        
        # Simple event handler
        def simple_chat(message, history):
            history.append({"role": "user", "content": message})
            history.append({"role": "assistant", "content": f"You said: {message}"})
            return history, ""
        
        submit_btn.click(
            simple_chat,
            inputs=[user_input, chatbot],
            outputs=[chatbot, user_input]
        )
    
    return interface

if __name__ == "__main__":
    print("🚀 Starting MINIMAL VariancePro - NO VISUALIZATION!")
    print("📊 ONLY 2 TABS: Chat and Data")
    
    demo = minimal_create_interface()
    demo.launch(
        server_name="127.0.0.1",
        server_port=7865,
        share=False,
        debug=False,
        show_error=True
    )
