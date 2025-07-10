"""
Quant Commander v2.0 - Refactored Modular Architecture
Main application orchestrator - focuses on interface coordination only
"""

import os
import gradio as gr
from typing import List, Dict, Tuple

# Import our modular components
from core.app_core import AppCore
from handlers.file_handler import FileHandler
from handlers.chat_handler import ChatHandler
from handlers.quick_action_handler import QuickActionHandler
from analyzers.variance_analyzer import QuantAnalyzer

# Import RAG components for document enhancement
from analyzers.rag_document_manager import RAGDocumentManager
from analyzers.rag_enhanced_analyzer import RAGEnhancedAnalyzer


class QuantCommanderApp:
    """
    Main application orchestrator for Quant Commander v2.0
    
    This class has been refactored to follow modular design principles.
    It now focuses solely on coordinating components and creating the interface.
    Core functionality has been extracted to dedicated modules.
    """
    
    def __init__(self):
        """Initialize the modular application components"""
        # Initialize core application logic
        self.app_core = AppCore()
        self.chat_handler = ChatHandler(self.app_core)
        
        # Initialize variance analyzer with error handling
        try:
            self.quant_analyzer = QuantAnalyzer()
            print("✅ Variance analyzer initialized successfully")
        except Exception as e:
            print(f"⚠️ Variance analyzer initialization failed: {e}")
            print(f"   → Quantitative analysis will be unavailable")
            self.quant_analyzer = None
        
        # Initialize RAG components for document enhancement with comprehensive error handling
        self.rag_manager = None
        self.rag_analyzer = None
        
        try:
            print("[DEBUG] Attempting to initialize RAG components...")
            self.rag_manager = RAGDocumentManager()
            print("[DEBUG] RAG Document Manager initialized")
            
            self.rag_analyzer = RAGEnhancedAnalyzer(self.rag_manager)
            print("[DEBUG] RAG Enhanced Analyzer initialized")
            
            print("✅ RAG components initialized successfully")
            rag_status = "enabled"
            
        except ImportError as e:
            print(f"⚠️ RAG initialization failed - missing dependencies: {e}")
            print(f"   → Document enhancement features will be unavailable")
            print(f"   → Install missing packages to enable RAG functionality")
            rag_status = "disabled (missing dependencies)"
            
        except Exception as e:
            print(f"⚠️ RAG initialization failed - unexpected error: {e}")
            print(f"   → Document enhancement features will be unavailable")
            print(f"   → Check system configuration and dependencies")
            rag_status = "disabled (configuration error)"
        
        # Initialize handlers with RAG components
        self.file_handler = FileHandler(self.app_core, self.rag_manager, self.rag_analyzer)
        
        # Initialize quick action handler with RAG components (handles None gracefully)
        try:
            self.quick_action_handler = QuickActionHandler(self.app_core, self.rag_manager, self.rag_analyzer)
            print("✅ Quick action handler initialized successfully")
        except Exception as e:
            print(f"❌ Critical error: Quick action handler initialization failed: {e}")
            raise  # This is critical - app cannot function without quick actions
        
        # Final initialization status
        print(f"🚀 Quant Commander v2.0 modular architecture initialized (RAG {rag_status})")
    
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
        
        # Enhanced RAG integration - check if we have documents and can enhance ANY query
        if (self.rag_manager is not None and 
            self.rag_analyzer is not None and
            self.rag_manager.has_documents()):
            
            try:
                # Get the last assistant response
                if updated_history and updated_history[-1]['role'] == 'assistant':
                    last_response = updated_history[-1]['content']
                    
                    # Enhanced RAG logic - try to enhance any meaningful query
                    analysis_keywords = ['variance', 'trend', 'analysis', 'summary', 'contribution']
                    question_keywords = ['what', 'why', 'how', 'when', 'where', 'explain', 'tell me', 'show me', 'compare', 'calculate']
                    
                    # Check if this is an analysis request or a question that could benefit from documents
                    has_analysis_keyword = any(keyword in message.lower() for keyword in analysis_keywords)
                    has_question_keyword = any(keyword in message.lower() for keyword in question_keywords)
                    is_meaningful_query = len(message.strip()) > 10  # Avoid enhancing very short messages
                    
                    if has_analysis_keyword or (has_question_keyword and is_meaningful_query):
                        print(f"🔍 Attempting RAG enhancement for: {message[:50]}...")
                        
                        # Try to enhance with RAG based on query type
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
                            # Use general enhancement for all other questions
                            enhanced_result = self.rag_analyzer.enhance_general_analysis(
                                analysis_data={'analysis': last_response, 'user_query': message},
                                analysis_context=f"User query: {message}"
                            )
                        
                        # If enhancement was successful, replace the response
                        if enhanced_result.get('success'):
                            enhanced_response = enhanced_result.get('enhanced_response', last_response)
                            # Add a note that documents were used
                            enhanced_response += "\n\n📚 *Enhanced with insights from uploaded documents*"
                            updated_history[-1]['content'] = enhanced_response
                            print(f"✅ RAG enhancement successful, used {enhanced_result.get('documents_used', 0)} document(s)")
                        else:
                            print(f"⚠️ RAG enhancement failed: {enhanced_result.get('error', 'Unknown error')}")
                    else:
                        print(f"ℹ️ RAG enhancement skipped - query doesn't match enhancement criteria")
                        
            except Exception as e:
                # If RAG enhancement fails, just continue with standard response
                print(f"❌ RAG enhancement error: {e}")
        
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
    
    def upload_documents(self, files, history: List[Dict] = None) -> Tuple[str, List[Dict]]:
        """
        Handle document upload for RAG enhancement
        
        Args:
            files: List of uploaded document files
            history: Current chat history (optional)
            
        Returns:
            Tuple[str, List[Dict]]: (upload_status, updated_history)
        """
        if history is None:
            history = []
        
        print(f"[DEBUG] upload_documents called with {len(files) if files else 0} files")
        print(f"[DEBUG] Initial history length: {len(history)}")
        
        # Check if RAG is available
        if self.rag_manager is None:
            print("[DEBUG] RAG manager is None - components not available")
            return "⚠️ Document upload temporarily disabled - RAG components not available", history
        
        if not files:
            print("[DEBUG] No files provided")
            return "⚠️ No files selected", history
        
        try:
            upload_results = []
            successful_uploads = []
            
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
                    successful_uploads.append((file_path, filename, chunks))
                    print(f"[DEBUG] Successfully uploaded {filename} with {chunks} chunks")
                else:
                    filename = os.path.basename(file_path) if file_path else 'Unknown'
                    error_msg = result.get('message', 'Unknown error')
                    upload_results.append(f"❌ {filename}: {error_msg}")
                    print(f"[DEBUG] Failed to upload {filename}: {error_msg}")
            
            if not upload_results:
                print("[DEBUG] No upload results")
                return "⚠️ No valid files to process", history
            
            # Add document upload success message to chat
            if successful_uploads:
                upload_message = {
                    "role": "assistant",
                    "content": f"📚 **Document(s) Uploaded Successfully!**\n\n{chr(10).join(upload_results)}"
                }
                history.append(upload_message)
                print(f"[DEBUG] Added upload message to history")
                
                # Trigger automatic RAG analysis for uploaded documents
                print(f"[DEBUG] Triggering RAG analysis for {len(successful_uploads)} documents...")
                rag_analysis = self._trigger_rag_analysis_on_document_upload(successful_uploads)
                
                if rag_analysis:
                    rag_message = {
                        "role": "assistant",
                        "content": rag_analysis
                    }
                    history.append(rag_message)
                    print(f"[DEBUG] Added RAG analysis to history")
                else:
                    print(f"[DEBUG] No RAG analysis returned")
            
            print(f"[DEBUG] Final history length: {len(history)}")
            return "\n".join(upload_results), history
            
        except Exception as e:
            print(f"[DEBUG] Exception in upload_documents: {e}")
            import traceback
            traceback.print_exc()
            return f"❌ Error uploading documents: {str(e)}", history
    
    def clear_documents(self) -> str:
        """Clear all uploaded documents"""
        # Check if RAG is available
        if self.rag_manager is None:
            return "⚠️ Document management temporarily disabled - RAG components not available"
        
        try:
            self.rag_manager.clear_all_documents()
            return "✅ All documents cleared"
        except Exception as e:
            return f"❌ Error clearing documents: {str(e)}"
    
    def search_documents(self, query: str) -> str:
        """Search through uploaded documents"""
        # Check if RAG is available
        if self.rag_manager is None:
            return "⚠️ Document search temporarily disabled - RAG components not available"
        
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

    def _trigger_rag_analysis_on_document_upload(self, successful_uploads: List[Tuple]) -> str:
        """
        Trigger automatic RAG analysis when documents are uploaded.
        
        Args:
            successful_uploads: List of tuples (file_path, filename, chunks)
            
        Returns:
            str: RAG analysis result or None if not available
        """
        try:
            print(f"[DEBUG] Starting RAG analysis for {len(successful_uploads)} documents...")
            
            # Check if RAG analyzer is available
            if not self.rag_analyzer:
                print("[DEBUG] RAG analyzer not available for document upload analysis")
                # Return fallback message instead of None
                return f"""📚 **Documents Uploaded Successfully**

Successfully uploaded {len(successful_uploads)} document(s). The content is now available for analysis.

💡 **Try asking**:
- "What are the main themes in these documents?"
- "How do these documents relate to my data?"
- "Summarize the key insights from the uploaded content"

Your documents are ready to enhance data analysis!"""
            
            # Check if there are documents loaded
            if not self.rag_manager or not self.rag_manager.has_documents():
                print("[DEBUG] No RAG documents available for analysis")
                # Return fallback message instead of None
                return f"""📚 **Documents Processing**

Uploaded {len(successful_uploads)} document(s). Processing for analysis...

💡 **Next Steps**: Ask me questions about the content or request analysis of your data!"""
            
            print("🔍 Performing automatic RAG analysis on uploaded documents...")
            
            # Create context about the uploaded documents
            upload_context = f"""**Documents Uploaded:**
"""
            for file_path, filename, chunks in successful_uploads:
                upload_context += f"- {filename} ({chunks} chunks)\n"
            
            # Get document summaries if available
            document_summaries = []
            try:
                print("[DEBUG] Getting document summaries...")
                # Try to get a summary of the uploaded documents
                for file_path, filename, chunks in successful_uploads:
                    # Use RAG search to get key content from the document
                    search_result = self.rag_manager.search_documents(
                        query=f"main topics and key insights from {filename}",
                        max_results=3
                    )
                    if search_result.get('results'):
                        key_content = search_result['results'][0].get('content', '')[:500]  # First 500 chars
                        document_summaries.append(f"**{filename}**: {key_content}...")
                        print(f"[DEBUG] Got summary for {filename}: {len(key_content)} chars")
            except Exception as e:
                print(f"[DEBUG] Error getting document summaries: {e}")
            
            # Create comprehensive prompt for RAG analysis
            if document_summaries:
                analysis_prompt = f"""You are a finance expert analyst. Analyze the following uploaded documents:

{upload_context}

**Document Content Preview:**
{chr(10).join(document_summaries)}

As a finance persona, provide a concise analysis focusing on:
1. Main financial topics and themes
2. Key insights and findings relevant to financial analysis
3. Potential applications for quantitative data analysis
4. Suggested questions users might ask about financial data

Keep the response under 300 words and make it actionable for financial data analysis."""
            else:
                analysis_prompt = f"""You are a finance expert analyst. The following documents have been uploaded:

{upload_context}

As a finance persona, provide a brief analysis of:
1. What type of financial content was likely uploaded based on filenames
2. Potential financial insights available
3. Suggested questions for financial analysis

Keep the response under 200 words and focus on financial analysis applications."""
            
            print(f"[DEBUG] Created analysis prompt ({len(analysis_prompt)} chars)")
            
            # Request RAG-enhanced analysis
            print("[DEBUG] Checking if Ollama is available...")
            if self.is_ollama_available():
                print("[DEBUG] Calling Ollama for RAG analysis...")
                rag_result = self.call_ollama(analysis_prompt)
                
                if rag_result:
                    documents_count = len(successful_uploads)
                    print(f"[DEBUG] Got RAG analysis result ({len(rag_result)} chars)")
                    return f"""🤖 **Financial Document Analysis** (Based on {documents_count} document(s))

{rag_result}

💡 **Next Steps**: Ask me specific questions about the financial content, or request analysis of your data in context of these documents!"""
                else:
                    print("[DEBUG] Ollama call returned empty result")
            else:
                print("[DEBUG] Ollama not available")
            
            # Fallback if LLM is not available
            print("[DEBUG] Using fallback analysis message")
            return f"""📚 **Financial Documents Ready for Analysis**

Successfully uploaded {len(successful_uploads)} document(s). The content is now available for enhanced financial analysis.

💡 **Try asking**:
- "What are the main financial themes in these documents?"
- "How do these documents relate to my financial data?"
- "Summarize the key financial insights from the uploaded content"
- "What financial metrics should I focus on?"

Your documents are ready to enhance financial data analysis!"""
                
        except Exception as e:
            print(f"[DEBUG] Error in RAG document analysis: {e}")
            import traceback
            traceback.print_exc()
            return None

    
    def is_ollama_available(self) -> bool:
        """
        Check if Ollama LLM service is available.
        
        Returns:
            bool: True if Ollama is available, False otherwise
        """
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def call_ollama(self, prompt: str, model: str = "llama3.1") -> str:
        """
        Call Ollama LLM service with the given prompt.
        
        Args:
            prompt: The prompt to send to the LLM
            model: The model to use (default: llama3.1)
            
        Returns:
            str: LLM response or None if failed
        """
        try:
            import requests
            import json
            
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "")
            else:
                print(f"❌ Ollama API error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Ollama call failed: {e}")
            return None

    def create_interface(self) -> gr.Blocks:
        """
        Create the Gradio interface with modular component integration
        
        Returns:
            gr.Blocks: The complete Gradio interface
        """
        # Read custom CSS
        custom_css = ""
        css_path = os.path.join(os.path.dirname(__file__), "static", "styles.css")
        if os.path.exists(css_path):
            with open(css_path, 'r') as f:
                custom_css = f.read()
        
        with gr.Blocks(
            title="Quant Commander v2.0", 
            theme=gr.themes.Soft(),
            css=custom_css
        ) as interface:
            # Header
            gr.Markdown("# 📊 Quant Commander v2.0")
            gr.Markdown("*AI-Powered Quantitative Trading Analysis & Command Center*")
            
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
                        value="Ready to upload PDF/text documents for enhanced analysis",
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
                            "content": "👋 Welcome to Quant Commander v2.0 with modular architecture! Upload your CSV file and I'll analyze it for you."
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
                inputs=[doc_files, chatbot],
                outputs=[doc_status, chatbot]
            )
            
            clear_docs_btn.click(
                fn=self.clear_documents,
                inputs=[],
                outputs=[doc_status]
            )
        
        return interface


def main():
    """Main entry point for Quant Commander v2.0"""
    print("🚀 Starting Quant Commander v2.0 with Modular Architecture...")
    
    app = QuantCommanderApp()
    interface = app.create_interface()
    
    print("✅ Modular application ready")
    print(f"🌐 Access at: http://localhost:7873")
    
    interface.launch(
        server_name="localhost",  # Changed from 0.0.0.0 to avoid postMessage origin issues
        server_port=7873,
        share=False,
        debug=True,
        show_error=True,
        allowed_paths=["./static"],  # Allow static files access with relative path
        favicon_path="./static/logo.png"  # Set favicon with relative path
    )


if __name__ == "__main__":
    main()
