
import gradio as gr
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app import QuantCommanderApp

class InterfaceBuilder:
    def __init__(self, app: "QuantCommanderApp"):
        self.app = app

    def create_interface(self):
        """Create the enhanced Gradio interface"""
        
        with gr.Blocks(title="AI Financial Analysis", theme=gr.themes.Soft(), css="""
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
        """) as interface:
            
            # Professional header with logo, title, and status indicators
            with gr.Row():
                with gr.Column(scale=2):
                    # Logo left-aligned
                    gr.Image("logo.png", show_label=False, height=80, width=None, container=False)
                
                with gr.Column(scale=6):
                    # Centered title with more space
                    gr.HTML("""
                    <div style="text-align: center; padding: 20px 0;">
                        <h2 style="color: #043B4A; margin: 0; font-size: 24px; font-weight: 600;">
                            Professional Financial Analysis Platform
                        </h2>
                        <p style="font-size: 16px; color: #666; margin: 8px 0 0 0;">
                            AI-powered insights and analysis for data-driven decisions
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
        </style>
                    """)
                
                with gr.Column(scale=2):
                    # Status indicators
                    gr.HTML("""
                    <div style="text-align: right; padding: 15px 0;">
                        <div style="margin-bottom: 8px;">
                            <span id="ollama-status" style="display: inline-block; width: 12px; height: 12px; border-radius: 50%; background: #ff4444; margin-right: 5px;"></span>
                            <span style="font-size: 12px; color: #666;">Ollama</span>
                        </div>
                        <div style="margin-bottom: 8px;">
                            <span id="app-status" style="display: inline-block; width: 12px; height: 12px; border-radius: 50%; background: #44ff44; margin-right: 5px;"></span>
                            <span style="font-size: 12px; color: #666;">App Server</span>
                        </div>
                        <div>
                            <a href="https://github.com/sharkoil/quantcommander" target="_blank" 
                               style="color: #043B4A; text-decoration: none; font-size: 12px;">
                                📚 Help & Docs
                            </a>
                        </div>
                    </div>
                    
                    <script>
                        // Function to update status indicators
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
            
            # Main content area - properly structured layout
            with gr.Row():
                with gr.Column(scale=1):
                    # Left sidebar - Status panel
                    status_display = gr.Markdown(value=self.app.get_status())
                    refresh_btn = gr.Button("🔄 Refresh Status", size="sm")
                    
                    # File upload section
                    gr.Markdown("### 📊 Upload Financial Data")
                    file_input = gr.File(
                        label="CSV File",
                        file_types=[".csv"],
                        type="filepath"
                    )
                    
                    # Data preview with file analysis
                    data_preview = gr.Textbox(
                        label="Data Summary & Analysis",
                        value="Upload a CSV file to get started with AI-powered financial analysis",
                        lines=12,
                        max_lines=20,
                        interactive=False
                    )
                
                
                with gr.Column(scale=2):
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
                        value=[{"role": "assistant", "content": """👋 **Welcome to Quant Commander!** I'm Aria Sterling, your AI financial analyst.

📊 Upload your financial data and chat with me for comprehensive insights and analysis!

🆔 **Session ID**: loading...
⏰ **Started**: loading...

##  What I Can Do For You:

### 📈 **Analysis Types**
• **Contribution Analysis**: 80/20 Pareto analysis to identify top performers
• **Variance Analysis**: Budget vs Actual performance tracking
• **Trend Analysis**: Time series patterns and trailing twelve months (TTM)
• **Top/Bottom N**: Rankings and performance comparisons
• **Custom SQL Queries**: Natural language to SQL translation

### 🎯 **Smart Features**
• **Auto-detect data patterns** in your CSV files
• **Context-aware responses** based on your specific data
• **Interactive field picker** for building queries
• **Real-time insights** with AI-powered analysis
• **Professional reporting** with charts and tables

### 💡 **How to Get Started**
1. **Upload** your CSV file using the upload button
2. **Explore** the auto-generated data summary
3. **Ask questions** like "analyze contribution" or "show trends"
4. **Use quick buttons** for instant analysis
5. **Click field names** to build custom queries

### 🔧 **Advanced Capabilities**
• Multi-threaded SQL processing for large datasets
• Intelligent column detection (dates, categories, financials)
• Business context integration with news analysis
• Session management with full history tracking
• Export-ready formatted reports

💼✨ Ready to transform your data into strategic intelligence!"""}]
                    )
                    
                    with gr.Row():
                        chat_input = gr.Textbox(
                            placeholder="Ask about your data: 'analyze contribution', 'show trends', 'quantitative analysis', or ask any question...",
                            label="Your Message",
                            lines=2,
                            scale=4
                        )
                        send_btn = gr.Button("Send 📤", scale=1, variant="primary")
                    
                    # Quick action buttons
                    gr.Markdown("**Quick Analysis Commands:**")
                    with gr.Row():
                        contrib_btn = gr.Button("📈 Contribution Analysis", size="sm")
                        variance_btn = gr.Button("💰 Variance Analysis", size="sm")
                        trend_btn = gr.Button("📊 Trend Analysis", size="sm")
                        summary_btn = gr.Button("📋 Data Summary", size="sm")
                    
                    # Top N / Bottom N buttons
                    gr.Markdown("**Top/Bottom Analysis:**")
                    with gr.Row():
                        top_n_btn = gr.Button("🔝 Top 10", size="sm")
                        bottom_n_btn = gr.Button("🔻 Bottom 10", size="sm")
                        top_5_btn = gr.Button("⭐ Top 5", size="sm")
                        bottom_5_btn = gr.Button("⚠️ Bottom 5", size="sm")
                    
                    # Field Picker Section
                    gr.Markdown("### 🎯 Field Picker")
                    gr.Markdown("*Click on field names to add them to your chat query*")
                    
                    # Example usage
                    gr.Markdown("""
                    **💡 Example Usage:**
                    • Click "Product" + type "top 10" → "Product top 10"
                    • Click "State" + "Budget" → "State Budget analysis"
                    • Build queries like: "Show me top 5 [Category] by [Actual]"
                    """)
                    
                    # Column type sections
                    with gr.Row():
                        with gr.Column():
                            gr.Markdown("**📅 Date Columns:**")
                            date_columns_display = gr.HTML(value="<i>Upload data to see available fields</i>")
                        
                        with gr.Column():
                            gr.Markdown("**📊 Numeric Columns:**")
                            numeric_columns_display = gr.HTML(value="<i>Upload data to see available fields</i>")
                    
                    with gr.Row():
                        with gr.Column():
                            gr.Markdown("**🏷️ Category Columns:**")
                            category_columns_display = gr.HTML(value="<i>Upload data to see available fields</i>")
                        
                        with gr.Column():
                            gr.Markdown("**💰 Value Columns:**")
                            value_columns_display = gr.HTML(value="<i>Upload data to see available fields</i>")
            
            # Data summary (hidden, for context)
            data_summary_state = gr.State("")
            
            # Event handlers
            refresh_btn.click(
                fn=self.app.get_status,
                outputs=[status_display]
            )
            
            # Custom file upload event handler that adds analysis to chat
            def handle_file_upload(file, chatbot):
                if file is None:
                    return None, "No data available", chatbot, "<i>Upload data to see available fields</i>", "<i>Upload data to see available fields</i>", "<i>Upload data to see available fields</i>", "<i>Upload data to see available fields</i>"
                
                preview, data_summary, analysis_message = self.app.upload_csv(file)
                
                # Generate field picker HTML
                date_html = self.app._generate_field_picker_html(
                    self.app.csv_loader.column_info.get('date_columns', []), 
                    "date"
                )
                numeric_html = self.app._generate_field_picker_html(
                    self.app.csv_loader.column_info.get('numeric_columns', []), 
                    "numeric"
                )
                category_html = self.app._generate_field_picker_html(
                    self.app.column_suggestions.get('category_columns', []), 
                    "category"
                )
                value_html = self.app._generate_field_picker_html(
                    self.app.column_suggestions.get('value_columns', []), 
                    "value"
                )
                
                # Start with the primary analysis message if available
                updated_chatbot = chatbot
                if analysis_message:
                    bot_message = analysis_message['content']
                    updated_chatbot = updated_chatbot + [{"role": "user", "content": "CSV File Loaded"}, {"role": "assistant", "content": bot_message}]
                
                # Add News Analysis as second message
                try:
                    print("[DEBUG] Starting news analysis...")
                    news_results = self.app.news_analyzer.analyze_data_context(
                        data=self.app.current_data,
                        column_info=self.app.csv_loader.column_info
                    )
                    
                    if news_results and isinstance(news_results, dict) and news_results.get('search_queries'):
                        print(f"[DEBUG] News search queries: {news_results.get('search_queries')}")
                        # Display up to 6 news items, 3 per location/query
                        formatted_results = news_results.copy()
                        if len(formatted_results.get('news_items', [])) > 6:
                            formatted_results['news_items'] = formatted_results['news_items'][:6]
                        news_content = self.app.news_analyzer.format_news_for_chat(formatted_results)
                        updated_chatbot = updated_chatbot + [{"role": "user", "content": "Business Context Analysis"}, {"role": "assistant", "content": news_content}]
                        print(f"[DEBUG] News analysis added to chat")
                    else:
                        print("[DEBUG] No news results found or no location data detected")
                        fallback_news_content = "📰 **BUSINESS CONTEXT ANALYSIS**\n\nNo location data detected in your dataset for relevant business news analysis. Focus on core data metrics instead."
                        updated_chatbot = updated_chatbot + [{"role": "user", "content": "Business Context Analysis"}, {"role": "assistant", "content": fallback_news_content}]
                        
                except Exception as e:
                    print(f"[DEBUG] News analysis error: {str(e)}")
                    # Add error message to chat as well
                    error_content = f"📰 **BUSINESS CONTEXT ANALYSIS**\n\n⚠️ Unable to fetch business context: {str(e)}\n\nContinuing with data analysis..."
                    updated_chatbot = updated_chatbot + [{"role": "user", "content": "Business Context Analysis"}, {"role": "assistant", "content": error_content}]
                
                return preview, data_summary, updated_chatbot, date_html, numeric_html, category_html, value_html
            
            file_input.change(
                fn=handle_file_upload,
                inputs=[file_input, chatbot],
                outputs=[data_preview, data_summary_state, chatbot, date_columns_display, numeric_columns_display, category_columns_display, value_columns_display]
            )
            
            send_btn.click(
                fn=self.app.chat_response,
                inputs=[chat_input, chatbot],
                outputs=[chatbot, chat_input]
            )
            
            chat_input.submit(
                fn=self.app.chat_response,
                inputs=[chat_input, chatbot],
                outputs=[chatbot, chat_input]
            )
            
            # Quick action button handlers
            contrib_btn.click(
                fn=lambda hist: self.app.chat_response("analyze contribution", hist),
                inputs=[chatbot],
                outputs=[chatbot, chat_input]
            )
            
            variance_btn.click(
                fn=lambda hist: self.app.chat_response("analyze variance", hist),
                inputs=[chatbot],
                outputs=[chatbot, chat_input]
            )
            
            trend_btn.click(
                fn=lambda hist: self.app.chat_response("analyze timescale trends for all periods", hist),
                inputs=[chatbot],
                outputs=[chatbot, chat_input]
            )
            
            summary_btn.click(
                fn=lambda hist: self.app.chat_response("summary", hist),
                inputs=[chatbot],
                outputs=[chatbot, chat_input]
            )
            
            # Top N / Bottom N button handlers
            top_n_btn.click(
                fn=lambda hist: self.app.chat_response("show me the top 10 performers", hist),
                inputs=[chatbot],
                outputs=[chatbot, chat_input]
            )
            
            bottom_n_btn.click(
                fn=lambda hist: self.app.chat_response("show me the bottom 10 performers", hist),
                inputs=[chatbot],
                outputs=[chatbot, chat_input]
            )
            
            top_5_btn.click(
                fn=lambda hist: self.app.chat_response("show me the top 5 performers", hist),
                inputs=[chatbot],
                outputs=[chatbot, chat_input]
            )
            
            bottom_5_btn.click(
                fn=lambda hist: self.app.chat_response("show me the bottom 5 performers", hist),
                inputs=[chatbot],
                outputs=[chatbot, chat_input]
            )
        
        # Interface is complete - removed testing framework integration
        print("✅ Gradio interface created")
        
        return interface
