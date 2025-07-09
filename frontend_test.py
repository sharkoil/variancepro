#!/usr/bin/env python3
"""
Minimal frontend test to identify postMessage and resource loading issues
"""

import gradio as gr
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_frontend():
    """Test frontend functionality with minimal setup"""
    print("🔍 Testing frontend functionality...")
    
    def test_action(action_name):
        """Test action for buttons"""
        return f"✅ {action_name} action executed successfully!"
    
    # Create a simple interface
    with gr.Blocks(
        title="Quant Commander Frontend Test",
        theme=gr.themes.Soft(
            primary_hue="blue",
            secondary_hue="slate",
            neutral_hue="slate"
        )
    ) as interface:
        
        gr.Markdown("# Quant Commander Frontend Test")
        
        with gr.Row():
            with gr.Column():
                gr.Markdown("## Test Buttons")
                
                # Test buttons similar to the main app
                with gr.Row():
                    top5_btn = gr.Button("🔝 Top 5", size="sm", variant="secondary")
                    bottom5_btn = gr.Button("🔻 Bottom 5", size="sm", variant="secondary")
                    top10_btn = gr.Button("📊 Top 10", size="sm", variant="secondary")
                    bottom10_btn = gr.Button("📉 Bottom 10", size="sm", variant="secondary")
                
                # Output area
                output = gr.Textbox(label="Output", lines=5, max_lines=10)
        
        # Event bindings
        top5_btn.click(
            fn=lambda: test_action("Top 5"),
            inputs=[],
            outputs=[output]
        )
        
        bottom5_btn.click(
            fn=lambda: test_action("Bottom 5"),
            inputs=[],
            outputs=[output]
        )
        
        top10_btn.click(
            fn=lambda: test_action("Top 10"),
            inputs=[],
            outputs=[output]
        )
        
        bottom10_btn.click(
            fn=lambda: test_action("Bottom 10"),
            inputs=[],
            outputs=[output]
        )
    
    return interface

if __name__ == "__main__":
    print("🚀 Starting Quant Commander Frontend Test...")
    interface = test_frontend()
    print("✅ Test interface ready")
    print("🌐 Access at: http://localhost:7874")
    
    interface.launch(
        server_name="0.0.0.0",
        server_port=7874,
        share=False,
        debug=True,
        show_error=True
    )
