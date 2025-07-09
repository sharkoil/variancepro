"""
UI Event Handlers for Quant Commander
Handles all user interface events and interactions
"""

from typing import List, Dict, Tuple
import gradio as gr


class UIEventHandlers:
    """Handles all UI events for the Quant Commander application"""
    
    def __init__(self, app):
        """Initialize handlers with reference to main app"""
        self.app = app
    
    def handle_file_upload(self, file) -> str:
        """Handle CSV file upload event"""
        return self.app.upload_csv(file)
    
    def handle_chat_input(self, message: str, history: List[Dict]) -> Tuple[List[Dict], str]:
        """Handle chat input from user"""
        return self.app.chat_response(message, history)
    
    def handle_contribution_button(self, history: List[Dict]) -> Tuple[List[Dict], str]:
        """Handle contribution analysis button click"""
        return self.app.chat_response("analyze contribution", history)
    
    def handle_variance_button(self, history: List[Dict]) -> Tuple[List[Dict], str]:
        """Handle quantitative analysis button click"""
        return self.app.chat_response("analyze variance", history)
    
    def handle_trend_button(self, history: List[Dict]) -> Tuple[List[Dict], str]:
        """Handle trend analysis button click"""
        return self.app.chat_response("analyze trends", history)
    
    def handle_summary_button(self, history: List[Dict]) -> Tuple[List[Dict], str]:
        """Handle summary button click"""
        return self.app.chat_response("summary", history)
    
    def handle_sql_test_button(self, history: List[Dict]) -> Tuple[List[Dict], str]:
        """Handle SQL testing button click"""
        if self.app.current_data is None:
            message = "⚠️ Please upload a CSV file first to test SQL queries."
        else:
            message = "🧪 **SQL Testing Mode**\n\nTry these example queries:\n• 'Show top 5 regions by sales'\n• 'Find products with satisfaction above 3'\n• 'List variance greater than 1000'\n• 'Sum of actual sales by product'"
        return self.app.chat_response(message, history)
    
    def handle_news_button(self, history: List[Dict]) -> Tuple[List[Dict], str]:
        """Handle news context button click"""
        return self.app.chat_response("get news context for this data", history)
    
    def handle_export_button(self, history: List[Dict]) -> Tuple[List[Dict], str]:
        """Handle export button click"""
        if self.app.current_data is None:
            message = "⚠️ Please upload a CSV file first to export data."
        else:
            message = f"💾 **Export Options**\n\n📊 Current dataset: {len(self.app.current_data)} rows, {len(self.app.current_data.columns)} columns\n\n• Type 'export to csv' to download current data\n• Type 'export analysis' to save analysis results\n• Type 'export summary' to get a data summary report"
        return self.app.chat_response(message, history)
    
    def bind_events(self, components: Dict):
        """Bind all event handlers to UI components"""
        # Extract components
        file_input = components['file_input']
        data_preview = components['data_preview']
        chatbot = components['chatbot']
        chat_input = components['chat_input']
        send_btn = components['send_btn']
        contrib_btn = components['contrib_btn']
        variance_btn = components['variance_btn']
        trend_btn = components['trend_btn']
        summary_btn = components['summary_btn']
        sql_test_btn = components['sql_test_btn']
        news_btn = components['news_btn']
        export_btn = components['export_btn']
        
        # File upload events
        file_input.change(
            fn=self.handle_file_upload,
            inputs=[file_input],
            outputs=[data_preview]
        )
        
        # Chat events
        send_btn.click(
            fn=self.handle_chat_input,
            inputs=[chat_input, chatbot],
            outputs=[chatbot, chat_input]
        )
        
        chat_input.submit(
            fn=self.handle_chat_input,
            inputs=[chat_input, chatbot],
            outputs=[chatbot, chat_input]
        )
        
        # Quick action button events
        contrib_btn.click(
            fn=self.handle_contribution_button,
            inputs=[chatbot],
            outputs=[chatbot, chat_input]
        )
        
        variance_btn.click(
            fn=self.handle_variance_button,
            inputs=[chatbot],
            outputs=[chatbot, chat_input]
        )
        
        trend_btn.click(
            fn=self.handle_trend_button,
            inputs=[chatbot],
            outputs=[chatbot, chat_input]
        )
        
        summary_btn.click(
            fn=self.handle_summary_button,
            inputs=[chatbot],
            outputs=[chatbot, chat_input]
        )
        
        # Advanced action button events
        sql_test_btn.click(
            fn=self.handle_sql_test_button,
            inputs=[chatbot],
            outputs=[chatbot, chat_input]
        )
        
        news_btn.click(
            fn=self.handle_news_button,
            inputs=[chatbot],
            outputs=[chatbot, chat_input]
        )
        
        export_btn.click(
            fn=self.handle_export_button,
            inputs=[chatbot],
            outputs=[chatbot, chat_input]
        )
