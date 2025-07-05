"""
Quick test script to verify UI color scheme fixes
"""

import gradio as gr

def test_color_scheme():
    """Test the improved color scheme"""
    
    # Same CSS as the enhanced UI
    custom_css = """
    /* Global light theme override */
    body, .gradio-container, .app, .main-wrap {
        color: #000000 !important;
        background-color: #ffffff !important;
    }
    
    /* All input elements */
    .gr-textbox, .gr-dropdown, .gr-button, .gr-html, .gr-markdown, 
    .gr-textbox input, .gr-dropdown select, input, textarea, select {
        color: #000000 !important;
        background-color: #ffffff !important;
        border: 1px solid #ddd !important;
    }
    
    /* Buttons */
    .gr-button {
        background-color: #f8f9fa !important;
        border: 1px solid #dee2e6 !important;
        color: #000000 !important;
    }
    
    .gr-button:hover {
        background-color: #e9ecef !important;
        color: #000000 !important;
    }
    
    .gr-button.primary {
        background-color: #007bff !important;
        border-color: #007bff !important;
        color: #ffffff !important;
    }
    
    /* HTML content and markdown */
    .gr-html, .gr-html *, .gr-markdown, .gr-markdown * {
        color: #000000 !important;
        background-color: transparent !important;
    }
    
    /* Tabs */
    .gr-tab-nav {
        background-color: #f8f9fa !important;
        border-bottom: 1px solid #dee2e6 !important;
    }
    
    .gr-tab-nav .gr-tab {
        color: #000000 !important;
        background-color: #ffffff !important;
        border: 1px solid #dee2e6 !important;
    }
    
    .gr-tab-nav .gr-tab.selected {
        background-color: #007bff !important;
        color: #ffffff !important;
    }
    
    /* Text areas and inputs */
    .gr-textbox textarea, .gr-textbox input {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #ced4da !important;
    }
    
    /* Labels */
    .gr-form label, .gr-textbox label, .gr-dropdown label, .gr-button label {
        color: #000000 !important;
        font-weight: 500 !important;
    }
    
    /* Fix for any remaining dark elements */
    * {
        color: inherit !important;
    }
    
    /* Force light theme on all child elements */
    .dark, .dark *, [data-theme="dark"], [data-theme="dark"] * {
        color: #000000 !important;
        background-color: #ffffff !important;
    }
    """
    
    def process_text(text):
        return f"<div style='color: #000000; background-color: #ffffff; padding: 10px; border: 1px solid #ddd;'>You entered: <strong>{text}</strong></div>"
    
    def process_dropdown(choice):
        return f"<div style='color: #000000; background-color: #ffffff; padding: 10px; border: 1px solid #ddd;'>You selected: <strong>{choice}</strong></div>"
    
    with gr.Blocks(
        title="Color Scheme Test", 
        theme=gr.themes.Soft(
            primary_hue="blue",
            secondary_hue="gray", 
            neutral_hue="gray"
        ),
        css=custom_css
    ) as interface:
        
        gr.Markdown("# 🎨 Color Scheme Test")
        gr.Markdown("This interface should have black text on white backgrounds - no dark gray/black backgrounds that make text unreadable.")
        
        with gr.Tab("📝 Text Input Test"):
            text_input = gr.Textbox(
                label="Test Text Input",
                placeholder="Type something here...",
                lines=3
            )
            text_button = gr.Button("Test Button", variant="primary")
            text_output = gr.HTML()
            
            text_button.click(process_text, inputs=text_input, outputs=text_output)
        
        with gr.Tab("📋 Dropdown Test"):
            dropdown_input = gr.Dropdown(
                label="Test Dropdown",
                choices=["Option 1", "Option 2", "Option 3"],
                value="Option 1"
            )
            dropdown_button = gr.Button("Test Dropdown", variant="secondary")
            dropdown_output = gr.HTML()
            
            dropdown_button.click(process_dropdown, inputs=dropdown_input, outputs=dropdown_output)
        
        gr.Markdown("### Status Messages Test")
        gr.HTML("""
        <div style='color: #155724; background-color: #d4edda; border: 1px solid #c3e6cb; padding: 10px; border-radius: 4px; margin: 10px 0;'>
            ✅ This is a success message - should be green text on light green background
        </div>
        <div style='color: #721c24; background-color: #f8d7da; border: 1px solid #f5c6cb; padding: 10px; border-radius: 4px; margin: 10px 0;'>
            ❌ This is an error message - should be red text on light red background
        </div>
        <div style='color: #004085; background-color: #cce7ff; border: 1px solid #80c7ff; padding: 10px; border-radius: 4px; margin: 10px 0;'>
            ℹ️ This is an info message - should be blue text on light blue background
        </div>
        """)
    
    return interface

if __name__ == "__main__":
    print("🎨 Testing color scheme fixes...")
    interface = test_color_scheme()
    interface.launch(server_port=7863, share=False, debug=True)
