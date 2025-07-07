"""
VariancePro v2.0 - Refactored Modular Architecture
Main application orchestrator - focuses on interface coordination only
"""

import os
import gradio as gr
from typing import List, Dict

# Import our modular components
from core.app_core import AppCore
from handlers.file_handler import FileHandler
from handlers.chat_handler import ChatHandler
from handlers.quick_action_handler import QuickActionHandler
from analyzers.variance_analyzer import VarianceAnalyzer

# Import RAG components for document enhancement
from analyzers.rag_document_manager import RAGDocumentManager
from analyzers.rag_enhanced_analyzer import RAGEnhancedAnalyzer


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
        
        # Initialize variance analyzer
        self.variance_analyzer = VarianceAnalyzer()
        
        # Initialize RAG components for document enhancement
        self.rag_manager = RAGDocumentManager()
        self.rag_analyzer = RAGEnhancedAnalyzer(self.rag_manager)
        
        # Initialize quick action handler with RAG components
        self.quick_action_handler = QuickActionHandler(self.app_core, self.rag_manager, self.rag_analyzer)
        
        print("🚀 VariancePro v2.0 modular architecture initialized with RAG")
    
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
        Handle chat messages - delegates to chat handler with RAG enhancement
        
        Args:
            message: User's input message
            history: Current chat history
            
        Returns:
            tuple: (updated_history, empty_string_for_input_clearing)
        """
        # Get the standard response from the chat handler
        updated_history, clear_input = self.chat_handler.process_message(message, history)
        
        # If we have documents and this looks like an analysis request, enhance with RAG
        if (self.rag_manager.has_documents() and 
            any(keyword in message.lower() for keyword in ['variance', 'trend', 'analysis', 'summary', 'contribution'])):
            
            try:
                # Get the last assistant response
                if updated_history and updated_history[-1]['role'] == 'assistant':
                    last_response = updated_history[-1]['content']
                    
                    # Try to enhance with RAG
                    if 'variance' in message.lower():
                        enhanced_result = self.rag_analyzer.enhance_variance_analysis(
                            variance_data={'analysis': last_response},
                            analysis_context=f"User query: {message}"
                        )
                    elif 'trend' in message.lower():
                        enhanced_result = self.rag_analyzer.enhance_trend_analysis(
                            trend_data={'analysis': last_response},
                            analysis_context=f"User query: {message}"
                        )
                    else:
                        enhanced_result = self.rag_analyzer.enhance_general_analysis(
                            analysis_data={'analysis': last_response},
                            analysis_context=f"User query: {message}"
                        )
                    
                    # If enhancement was successful, replace the response
                    if enhanced_result.get('success'):
                        enhanced_response = enhanced_result.get('enhanced_response', last_response)
                        # Add a note that documents were used
                        enhanced_response += "\n\n📚 *Enhanced with insights from uploaded documents*"
                        updated_history[-1]['content'] = enhanced_response
                        
            except Exception as e:
                # If RAG enhancement fails, just continue with standard response
                print(f"RAG enhancement failed: {e}")
        
        return updated_history, clear_input
    
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
    
    def upload_documents(self, files) -> str:
        """
        Handle document upload for RAG enhancement
        
        Args:
            files: List of uploaded document files
            
        Returns:
            str: Upload status message
        """
        if not files:
            return "⚠️ No files selected"
        
        try:
            upload_results = []
            for file in files:
                if file is None:
                    continue
                
                # Handle file path properly - Gradio sometimes returns the file path directly
                file_path = file if isinstance(file, str) else getattr(file, 'name', str(file))
                
                print(f"[DEBUG] Attempting to upload file: {file_path}")
                result = self.rag_manager.upload_document(file_path)
                
                if result.get('status') == 'success':
                    filename = result.get('document_info', {}).get('filename', 'Unknown')
                    chunks = result.get('chunks_created', 0)
                    upload_results.append(f"✅ {filename}: {chunks} chunks")
                else:
                    filename = os.path.basename(file_path) if file_path else 'Unknown'
                    error_msg = result.get('message', 'Unknown error')
                    upload_results.append(f"❌ {filename}: {error_msg}")
            
            if not upload_results:
                return "⚠️ No valid files to process"
            
            return "\n".join(upload_results)
            
        except Exception as e:
            return f"❌ Error uploading documents: {str(e)}"
    
    def clear_documents(self) -> str:
        """Clear all uploaded documents"""
        try:
            self.rag_manager.clear_all_documents()
            return "✅ All documents cleared"
        except Exception as e:
            return f"❌ Error clearing documents: {str(e)}"
    
    def search_documents(self, query: str) -> str:
        """Search through uploaded documents"""
        if not query.strip():
            return "Please enter a search query"
        
        try:
            results = self.rag_manager.retrieve_relevant_chunks(query, max_chunks=3)
            
            if not results:
                return "No relevant content found in uploaded documents"
            
            formatted_results = []
            for i, chunk in enumerate(results, 1):
                formatted_results.append(
                    f"**Result {i}**\n"
                    f"Document: {chunk.get('document_name', 'Unknown')}\n"
                    f"Content: {chunk.get('content', '')[:200]}...\n"
                )
            
            return "\n".join(formatted_results)
            
        except Exception as e:
            return f"❌ Error searching documents: {str(e)}"

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
                        lines=6,
                        interactive=False
                    )
                    
                    # RAG Documents section
                    gr.Markdown("### 📚 Documents (RAG)")
                    doc_files = gr.File(
                        label="Upload PDFs/Text",
                        file_types=[".pdf", ".txt"],
                        type="filepath",
                        file_count="multiple"
                    )
                    
                    with gr.Row():
                        upload_docs_btn = gr.Button("📤 Upload", size="sm", variant="secondary")
                        clear_docs_btn = gr.Button("🗑️ Clear", size="sm", variant="secondary")
                    
                    doc_status = gr.Textbox(
                        label="Document Status",
                        value="No documents uploaded",
                        lines=3,
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
            
            # Document upload events
            upload_docs_btn.click(
                fn=self.upload_documents,
                inputs=[doc_files],
                outputs=[doc_status]
            )
            
            clear_docs_btn.click(
                fn=self.clear_documents,
                inputs=[],
                outputs=[doc_status]
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
