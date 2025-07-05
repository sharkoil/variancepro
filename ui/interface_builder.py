"""
UI Interface Builder for VariancePro
Handles Gradio interface creation and layout
"""

import gradio as gr
from datetime import datetime
from typing import Dict, List, Tuple, Any

from utils.session_manager import SessionManager


class InterfaceBuilder:
    """
    Handles the creation and configuration of the Gradio web interface
    Provides methods for building different UI components and layouts
    """
    
    def __init__(self, app_instance):
        """
        Initialize interface builder with reference to main app
        
        Args:
            app_instance: Reference to the main QuantCommanderApp instance
        """
        self.app = app_instance
    
    def create_interface(self):
        """Create the enhanced Gradio interface with session management"""
        
        with gr.Blocks(title="AI Financial Analysis", theme=gr.themes.Soft(), css=self._get_custom_css()) as interface:
            
            # Professional header with logo, title, and status indicators
            self._create_header()
            
            with gr.Row():
                with gr.Column(scale=1):
                    # Left panel - Status and file upload
                    status_display, refresh_btn, file_input, data_preview = self._create_left_panel()
                
                with gr.Column(scale=2):
                    # Right panel - Chat interface
                    chatbot, chat_input, send_btn = self._create_chat_panel()
                    
                    # Quick action buttons
                    quick_buttons = self._create_quick_action_buttons()
                    
                    # Field picker section
                    field_components = self._create_field_picker_section()
            
            # Hidden state components
            data_summary_state = gr.State("")
            
            # Set up event handlers
            self._setup_event_handlers(
                status_display, refresh_btn, file_input, data_preview, data_summary_state,
                chatbot, chat_input, send_btn, quick_buttons, field_components
            )
        
        return interface
    
    def _get_custom_css(self) -> str:
        """Get custom CSS for enhanced styling"""
        return """
        /* Custom CSS for better chat bubble contrast */
        .message-wrap.svelte-1lcyrx4.svelte-1lcyrx4.svelte-1lcyrx4 {
            background: rgba(255, 255, 255, 0.95) !important;
            border: 1px solid #e0e0e0 !important;
            border-radius: 12px !important;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1) !important;
            margin: 8px 0 !important;
        }
        
        /* User messages (right side) */
        .message-wrap.svelte-1lcyrx4.svelte-1lcyrx4.svelte-1lcyrx4:has(.user) {
            background: linear-gradient(135deg, #e3f2fd, #f0f8ff) !important;
            border-left: 4px solid #2196f3 !important;
        }
        
        /* Bot messages (left side) */
        .message-wrap.svelte-1lcyrx4.svelte-1lcyrx4.svelte-1lcyrx4:has(.bot) {
            background: linear-gradient(135deg, #f8f9fa, #ffffff) !important;
            border-left: 4px solid #4caf50 !important;
        }
        
        /* Message text styling */
        .message.svelte-1lcyrx4.svelte-1lcyrx4 {
            color: #2c3e50 !important;
            font-weight: 500 !important;
            line-height: 1.5 !important;
        }
        
        /* Chatbot container styling */
        .chatbot .wrap.svelte-1lcyrx4 {
            background: linear-gradient(135deg, #f8f9fa, #e9ecef) !important;
            border-radius: 12px !important;
            border: 1px solid #dee2e6 !important;
        }
        
        /* Better table styling within chat */
        .message table {
            background: rgba(255, 255, 255, 0.9) !important;
            border-radius: 8px !important;
            overflow: hidden !important;
        }
        
        .message table th {
            background: #f1f3f4 !important;
            color: #1a1a1a !important;
            font-weight: 600 !important;
        }
        
        .message table td {
            background: rgba(255, 255, 255, 0.95) !important;
            color: #2c3e50 !important;
        }
        
        /* Code block styling */
        .message pre, .message code {
            background: rgba(248, 249, 250, 0.95) !important;
            border: 1px solid #e9ecef !important;
            color: #495057 !important;
        }
        
        /* Read More/Less functionality styling */
        .expandable-content .more-text {
            display: none !important;
        }
        
        .expandable-content .dots {
            display: inline !important;
        }
        
        .expandable-content.expanded .more-text {
            display: inline !important;
        }
        
        .expandable-content.expanded .dots {
            display: none !important;
        }
        
        .read-more-btn {
            color: #2196f3 !important;
            cursor: pointer !important;
            text-decoration: underline !important;
            font-weight: 600 !important;
            margin-left: 5px !important;
            user-select: none !important;
            transition: all 0.2s ease !important;
        }
        
        .read-more-btn:hover {
            color: #1976d2 !important;
            text-decoration: none !important;
        }
        
        /* Override Gradio's link styling for read more button */
        .message .read-more-btn {
            color: #2196f3 !important;
            background: none !important;
            border: none !important;
            padding: 0 !important;
            font-size: inherit !important;
            text-decoration: underline !important;
        }
        """
    
    def _create_header(self):
        """Create the application header"""
        with gr.Row():
            with gr.Column(scale=2):
                gr.Markdown("# 📊 VariancePro", elem_classes=["header-title"])
            
            with gr.Column(scale=6):
                gr.Markdown(
                    "### AI-Powered Financial Intelligence Platform",
                    elem_classes=["header-subtitle"]
                )
            
            with gr.Column(scale=2):
                gr.HTML("""
                    <div style='text-align: right; margin-top: 10px;'>
                        <div style='display: inline-flex; align-items: center; gap: 10px;'>
                            <div style='display: flex; align-items: center; gap: 5px;'>
                                <div id='ollama-status' style='width: 10px; height: 10px; border-radius: 50%; background: #ff4444;'></div>
                                <span style='font-size: 12px; color: #666;'>AI</span>
                            </div>
                            <div style='display: flex; align-items: center; gap: 5px;'>
                                <div id='app-status' style='width: 10px; height: 10px; border-radius: 50%; background: #44ff44;'></div>
                                <span style='font-size: 12px; color: #666;'>App</span>
                            </div>
                        </div>
                    </div>
                    
                    <script>
                        function updateStatusIndicators() {
                            fetch('/api/status')
                                .then(response => response.json())
                                .then(data => {
                                    const ollamaStatus = document.getElementById('ollama-status');
                                    const appStatus = document.getElementById('app-status');
                                    
                                    if (ollamaStatus) {
                                        ollamaStatus.style.background = data.ollama_available ? '#44ff44' : '#ff4444';
                                    }
                                    if (appStatus) {
                                        appStatus.style.background = '#44ff44'; // App is running if we can execute this
                                    }
                                })
                                .catch(error => {
                                    console.log('Status check failed:', error);
                                    const ollamaStatus = document.getElementById('ollama-status');
                                    if (ollamaStatus) {
                                        ollamaStatus.style.background = '#ff4444';
                                    }
                                });
                        }
                        
                        // Update status on page load and every 30 seconds
                        updateStatusIndicators();
                        setInterval(updateStatusIndicators, 30000);
                    </script>
                """)
    
    def _create_left_panel(self) -> Tuple[gr.Markdown, gr.Button, gr.File, gr.Textbox]:
        """Create the left panel with status and file upload"""
        # Status panel
        status_display = gr.Markdown(value=self.app.get_status())
        refresh_btn = gr.Button("🔄 Refresh Status", size="sm")
        
        # File upload
        gr.Markdown("### 📊 Upload Financial Data")
        file_input = gr.File(
            label="Upload CSV File",
            file_types=[".csv"],
            type="filepath"
        )
        
        # Data preview
        data_preview = gr.Textbox(
            label="Data Analysis & Preview",
            value="Upload a CSV file to get started with AI-powered financial analysis",
            lines=12,
            max_lines=20,
            interactive=False
        )
        
        return status_display, refresh_btn, file_input, data_preview
    
    def _create_chat_panel(self) -> Tuple[gr.Chatbot, gr.Textbox, gr.Button]:
        """Create the chat interface panel"""
        # Chat interface
        gr.Markdown("### 💬 Chat with Aria Sterling")
        gr.Markdown("*Professional Financial Analyst AI Assistant*")
        
        chatbot = gr.Chatbot(
            label="Financial Analysis Chat",
            height=450,
            show_label=True,
            placeholder="Start by uploading a CSV file, then ask questions or request analysis...",
            avatar_images=["👤", "🤖"],
            type="messages",
            value=[{"role": "assistant", "content": self.app.chat_handler.session_manager.create_welcome_message()}]
        )
        
        with gr.Row():
            chat_input = gr.Textbox(
                placeholder="Ask about your data: 'analyze contribution', 'show trends', 'variance analysis', or ask any question...",
                label="Your Message",
                lines=2,
                scale=4
            )
            send_btn = gr.Button("Send", variant="primary", size="lg", scale=1)
        
        return chatbot, chat_input, send_btn
    
    def _create_quick_action_buttons(self) -> Dict[str, gr.Button]:
        """Create quick action buttons for common analyses"""
        gr.Markdown("**Quick Analysis Commands:**")
        
        buttons = {}
        
        with gr.Row():
            buttons['contrib'] = gr.Button("📈 Contribution Analysis", size="sm")
            buttons['variance'] = gr.Button("💰 Variance Analysis", size="sm")
            buttons['trend'] = gr.Button("📊 Trend Analysis", size="sm")
            buttons['summary'] = gr.Button("📋 Summary", size="sm")
        
        # Top N / Bottom N buttons
        gr.Markdown("**Top/Bottom Analysis:**")
        with gr.Row():
            buttons['top_n'] = gr.Button("🏆 Top 10", size="sm")
            buttons['bottom_n'] = gr.Button("⬇️ Bottom 10", size="sm")
            buttons['top_5'] = gr.Button("🥇 Top 5", size="sm")
            buttons['bottom_5'] = gr.Button("📉 Bottom 5", size="sm")
        
        return buttons
    
    def _create_field_picker_section(self) -> Dict[str, gr.HTML]:
        """Create the field picker section"""
        gr.Markdown("### 🎯 Field Picker")
        gr.Markdown("*Click on field names to add them to your chat query*")
        
        # Example usage
        gr.Markdown("""
        **💡 Example Usage:**
        • Click "Product" + type "top 10" → "Product top 10"
        • Click "State" + "Budget" → "State Budget analysis"
        • Build queries like: "Show me top 5 [Category] by [Actual]"
        """)
        
        components = {}
        
        # Column type sections
        with gr.Row():
            with gr.Column():
                gr.Markdown("**📅 Date Columns:**")
                components['date'] = gr.HTML(value="<i>Upload data to see available fields</i>")
            
            with gr.Column():
                gr.Markdown("**📊 Numeric Columns:**")
                components['numeric'] = gr.HTML(value="<i>Upload data to see available fields</i>")
        
        with gr.Row():
            with gr.Column():
                gr.Markdown("**🏷️ Category Columns:**")
                components['category'] = gr.HTML(value="<i>Upload data to see available fields</i>")
            
            with gr.Column():
                gr.Markdown("**💰 Value Columns:**")
                components['value'] = gr.HTML(value="<i>Upload data to see available fields</i>")
        
        return components
    
    def _setup_event_handlers(self, status_display, refresh_btn, file_input, data_preview, data_summary_state,
                             chatbot, chat_input, send_btn, quick_buttons, field_components):
        """Set up all event handlers for the interface"""
        
        # Refresh status button
        refresh_btn.click(
            fn=self.app.get_status,
            outputs=[status_display]  # Fixed: use status_display component, not refresh_btn.value
        )
        
        # File upload handler
        def handle_file_upload(file, chatbot):
            if file is None:
                return None, "No data available", chatbot, \
                       "<i>Upload data to see available fields</i>", \
                       "<i>Upload data to see available fields</i>", \
                       "<i>Upload data to see available fields</i>", \
                       "<i>Upload data to see available fields</i>"
            
            upload_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"[DEBUG] File upload starting: {file.name} at {upload_timestamp}")
            
            preview, data_summary, analysis_message = self.app.upload_csv(file)
            print(f"[DEBUG] Upload_csv returned: preview={len(preview) if preview else 0} chars, analysis_message={analysis_message is not None}")
            
            # Generate field picker HTML
            date_html = self._generate_field_picker_html(
                self.app.csv_loader.column_info.get('date_columns', []), 
                "date"
            )
            numeric_html = self._generate_field_picker_html(
                self.app.csv_loader.column_info.get('numeric_columns', []), 
                "numeric"
            )
            category_html = self._generate_field_picker_html(
                self.app.column_suggestions.get('category_columns', []) if self.app.column_suggestions else [], 
                "category"
            )
            value_html = self._generate_field_picker_html(
                self.app.column_suggestions.get('value_columns', []) if self.app.column_suggestions else [], 
                "value"
            )
            
            # Start with the primary analysis message if available
            updated_chatbot = chatbot
            if analysis_message:
                print(f"[DEBUG] Adding analysis message to chat: {len(analysis_message['content'])} chars")
                bot_message = self.app.chat_handler.session_manager.add_timestamp_to_message(
                    analysis_message['content']
                )
                updated_chatbot = updated_chatbot + [
                    {"role": "user", "content": f"📁 CSV File Loaded - {upload_timestamp}"}, 
                    {"role": "assistant", "content": bot_message}
                ]
                print(f"[DEBUG] Updated chatbot length: {len(updated_chatbot)}")
            else:
                print("[DEBUG] No analysis message received from upload_csv")
                # Add a basic message if no analysis message
                basic_message = f"📊 **DATA LOADED SUCCESSFULLY**\n\n{data_summary if data_summary else 'File uploaded and processed.'}"
                timestamped_basic = self.app.chat_handler.session_manager.add_timestamp_to_message(basic_message)
                updated_chatbot = updated_chatbot + [
                    {"role": "user", "content": f"📁 CSV File Loaded - {upload_timestamp}"}, 
                    {"role": "assistant", "content": timestamped_basic}
                ]
                print(f"[DEBUG] Added basic message, chatbot length: {len(updated_chatbot)}")
            
            # Add News Analysis as second message (simplified version)
            try:
                print("[DEBUG] Starting news analysis...")
                # Skip news analysis for now to isolate the issue
                print("[DEBUG] Skipping news analysis to debug upload issue")
                    
            except Exception as e:
                print(f"[DEBUG] News analysis error: {str(e)}")
            
            print(f"[DEBUG] Final chatbot length: {len(updated_chatbot)}")
            print(f"[DEBUG] Returning: preview, data_summary, updated_chatbot({len(updated_chatbot)}), field_htmls")
            return preview, data_summary, updated_chatbot, date_html, numeric_html, category_html, value_html
        
        file_input.change(
            fn=handle_file_upload,
            inputs=[file_input, chatbot],
            outputs=[data_preview, data_summary_state, chatbot, 
                    field_components['date'], field_components['numeric'], 
                    field_components['category'], field_components['value']]
        )
        
        # Chat event handlers
        send_btn.click(
            fn=self.app.chat_handler.chat_response,
            inputs=[chat_input, chatbot],
            outputs=[chatbot, chat_input]
        )
        
        chat_input.submit(
            fn=self.app.chat_handler.chat_response,
            inputs=[chat_input, chatbot],
            outputs=[chatbot, chat_input]
        )
        
        # Quick action button handlers
        quick_buttons['contrib'].click(
            fn=lambda hist: self.app.chat_handler.chat_response("analyze contribution", hist),
            inputs=[chatbot],
            outputs=[chatbot, chat_input]
        )
        
        quick_buttons['variance'].click(
            fn=lambda hist: self.app.chat_handler.chat_response("analyze variance", hist),
            inputs=[chatbot],
            outputs=[chatbot, chat_input]
        )
        
        quick_buttons['trend'].click(
            fn=lambda hist: self.app.chat_handler.chat_response("analyze timescale trends for all periods", hist),
            inputs=[chatbot],
            outputs=[chatbot, chat_input]
        )
        
        quick_buttons['summary'].click(
            fn=lambda hist: self.app.chat_handler.chat_response("summary", hist),
            inputs=[chatbot],
            outputs=[chatbot, chat_input]
        )
        
        # Top N / Bottom N button handlers
        quick_buttons['top_n'].click(
            fn=lambda hist: self.app.chat_handler.chat_response("show me the top 10 performers", hist),
            inputs=[chatbot],
            outputs=[chatbot, chat_input]
        )
        
        quick_buttons['bottom_n'].click(
            fn=lambda hist: self.app.chat_handler.chat_response("show me the bottom 10 performers", hist),
            inputs=[chatbot],
            outputs=[chatbot, chat_input]
        )
        
        quick_buttons['top_5'].click(
            fn=lambda hist: self.app.chat_handler.chat_response("show me the top 5 performers", hist),
            inputs=[chatbot],
            outputs=[chatbot, chat_input]
        )
        
        quick_buttons['bottom_5'].click(
            fn=lambda hist: self.app.chat_handler.chat_response("show me the bottom 5 performers", hist),
            inputs=[chatbot],
            outputs=[chatbot, chat_input]
        )
    
    def _generate_field_picker_html(self, columns, column_type="field"):
        """Generate clickable HTML buttons for field names"""
        if not columns:
            return "<i>No columns available</i>"
        
        html_parts = []
        for col in columns[:8]:  # Limit to 8 columns to avoid overcrowding
            # Create clickable button with JavaScript to add to chat input
            button_html = f'''
            <button 
                onclick="
                    let chatInput = document.querySelector('textarea[placeholder*=\\'Ask about your data\\']');
                    if (chatInput) {{
                        let currentValue = chatInput.value;
                        let newValue = currentValue + (currentValue ? ' ' : '') + '{col}';
                        chatInput.value = newValue;
                        chatInput.dispatchEvent(new Event('input', {{bubbles: true}}));
                        chatInput.focus();
                        
                        // Visual feedback
                        this.style.background = 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)';
                        this.style.transform = 'scale(0.95)';
                        setTimeout(() => {{
                            this.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
                            this.style.transform = 'scale(1)';
                        }}, 150);
                    }} else {{
                        alert('Chat input not found. Please make sure the page is fully loaded.');
                    }}
                "
                style="
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    border: none;
                    padding: 6px 12px;
                    margin: 3px;
                    border-radius: 15px;
                    cursor: pointer;
                    font-size: 12px;
                    font-weight: 600;
                    transition: all 0.2s ease;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    user-select: none;
                "
                onmouseover="this.style.transform='scale(1.05)'; this.style.boxShadow='0 4px 8px rgba(0,0,0,0.2)';"
                onmouseout="this.style.transform='scale(1)'; this.style.boxShadow='0 2px 4px rgba(0,0,0,0.1)';"
                title="Click to add '{col}' to your query"
            >
                {col}
            </button>
            '''
            html_parts.append(button_html)
        
        if len(columns) > 8:
            html_parts.append(f"<br><small style='color: #666; font-style: italic;'>... and {len(columns) - 8} more columns</small>")
        
        return ''.join(html_parts)
