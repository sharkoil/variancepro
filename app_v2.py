"""
VariancePro v2.0 - Refactored Modular Architecture
Main application orchestrator - focuses on interface coordination only
"""

import gradio as gr
from typing import List, Dict

# Import our modular components
from core.app_core import AppCore
from handlers.file_handler import FileHandler
from handlers.chat_handler import ChatHandler
from handlers.quick_action_handler import QuickActionHandler
from analyzers.variance_analyzer import VarianceAnalyzer


class VarianceProApp:
    """
    Main application orchestrator for VariancePro v2.0
    
    This class has been refactored to follow modular design principles.
    It now focuses solely on coordinating components and creating the interface.
    Core functionality has been extracted to dedicated modules.
    """
    
    def __init__(self):
        """Initialize the modular application components"""
        # Initialize core application logic
        self.app_core = AppCore()
        
        # Initialize handlers
        self.file_handler = FileHandler(self.app_core)
        self.chat_handler = ChatHandler(self.app_core)
        self.quick_action_handler = QuickActionHandler(self.app_core)
        
        # Initialize variance analyzer
        self.variance_analyzer = VarianceAnalyzer()
        
        print("🚀 VariancePro v2.0 modular architecture initialized")
    
    def upload_csv(self, file, history: List[Dict]) -> tuple[str, List[Dict]]:
        """
        Handle CSV file upload - delegates to file handler
        
        Args:
            file: The uploaded file object
            history: Current chat history
            
        Returns:
            tuple: (upload_status, updated_history)
        """
        return self.file_handler.handle_upload(file, history)
    
    def chat_response(self, message: str, history: List[Dict]) -> tuple[List[Dict], str]:
        """
        Handle chat messages - delegates to chat handler
        
        Args:
            message: User's input message
            history: Current chat history
            
        Returns:
            tuple: (updated_history, empty_string_for_input_clearing)
        """
        return self.chat_handler.process_message(message, history)
    
    def quick_action(self, action: str, history: List[Dict]) -> List[Dict]:
        """
        Handle quick action buttons - delegates to quick action handler
        
        Args:
            action: The action to perform (summary, trends, etc.)
            history: Current chat history
            
        Returns:
            List[Dict]: Updated chat history
        """
        return self.quick_action_handler.handle_action(action, history)
    
    def create_interface(self) -> gr.Blocks:
        """
        Create the Gradio interface with modular component integration
        
        Returns:
            gr.Blocks: The complete Gradio interface
        """
        with gr.Blocks(title="VariancePro v2.0", theme=gr.themes.Soft()) as interface:
            # Header
            gr.Markdown("# 📊 VariancePro v2.0")
            gr.Markdown("*AI-Powered Financial Data Analysis with Modular Architecture*")
            
            with gr.Row():
                with gr.Column(scale=1):
                    # File upload section
                    gr.Markdown("### 📁 Upload Data")
                    file_input = gr.File(
                        label="CSV File",
                        file_types=[".csv"],
                        type="filepath"
                    )
                    
                    # Upload status
                    upload_status = gr.Textbox(
                        label="Upload Status",
                        value="Ready to upload CSV file...",
                        lines=8,
                        interactive=False
                    )
                
                with gr.Column(scale=2):
                    # Chat interface
                    gr.Markdown("### 💬 Analysis Chat")
                    
                    chatbot = gr.Chatbot(
                        label="AI Assistant",
                        height=400,
                        type="messages",
                        value=[{
                            "role": "assistant", 
                            "content": "👋 Welcome to VariancePro v2.0 with modular architecture! Upload your CSV file and I'll analyze it for you."
                        }]
                    )
                    
                    with gr.Row():
                        chat_input = gr.Textbox(
                            placeholder="Ask about your data...",
                            label="Your Message",
                            scale=4
                        )
                        send_btn = gr.Button("Send 📤", scale=1, variant="primary")
                    
                    # Quick Analysis Buttons
                    gr.Markdown("**Quick Analysis:**")
                    with gr.Row():
                        summary_btn = gr.Button("📋 Summary", size="sm")
                        trends_btn = gr.Button("📈 Trends", size="sm")
                        variance_btn = gr.Button("📊 Variance", size="sm", variant="secondary")
                        
                    # Top N / Bottom N Buttons
                    gr.Markdown("**Top/Bottom Analysis:**")
                    with gr.Row():
                        top5_btn = gr.Button("🔝 Top 5", size="sm", variant="secondary")
                        bottom5_btn = gr.Button("🔻 Bottom 5", size="sm", variant="secondary")
                        top10_btn = gr.Button("📊 Top 10", size="sm", variant="secondary")
                        bottom10_btn = gr.Button("📉 Bottom 10", size="sm", variant="secondary")
            
            # Footer with status
            with gr.Row():
                gr.Markdown(f"""
**Session**: `{self.app_core.session_id}` | **Ollama**: {self.app_core.ollama_status} | **Status**: {self.app_core.gradio_status} | **Architecture**: Modular v2.0
                """)
            
            # Event bindings - connecting UI to handlers
            file_input.change(
                fn=self.upload_csv,
                inputs=[file_input, chatbot],
                outputs=[upload_status, chatbot]
            )
            
            send_btn.click(
                fn=self.chat_response,
                inputs=[chat_input, chatbot],
                outputs=[chatbot, chat_input]
            )
            
            chat_input.submit(
                fn=self.chat_response,
                inputs=[chat_input, chatbot],
                outputs=[chatbot, chat_input]
            )
            
            # Quick Analysis button events
            summary_btn.click(
                fn=lambda h: self.quick_action("summary", h),
                inputs=[chatbot],
                outputs=[chatbot]
            )
            
            trends_btn.click(
                fn=lambda h: self.quick_action("trends", h),
                inputs=[chatbot],
                outputs=[chatbot]
            )
            
            variance_btn.click(
                fn=lambda h: self.quick_action("variance", h),
                inputs=[chatbot],
                outputs=[chatbot]
            )
            
            # Top N / Bottom N button events
            top5_btn.click(
                fn=lambda h: self.quick_action("top 5", h),
                inputs=[chatbot],
                outputs=[chatbot]
            )
            
            bottom5_btn.click(
                fn=lambda h: self.quick_action("bottom 5", h),
                inputs=[chatbot],
                outputs=[chatbot]
            )
            
            top10_btn.click(
                fn=lambda h: self.quick_action("top 10", h),
                inputs=[chatbot],
                outputs=[chatbot]
            )
            
            bottom10_btn.click(
                fn=lambda h: self.quick_action("bottom 10", h),
                inputs=[chatbot],
                outputs=[chatbot]
            )
        
        return interface


def main():
    """Main entry point for VariancePro v2.0"""
    print("🚀 Starting VariancePro v2.0 with Modular Architecture...")
    
    app = VarianceProApp()
    interface = app.create_interface()
    
    print("✅ Modular application ready")
    print(f"🌐 Access at: http://localhost:7873")
    
    interface.launch(
        server_name="0.0.0.0",
        server_port=7873,
        share=False,
        debug=True,
        show_error=True
    )


if __name__ == "__main__":
    main()
