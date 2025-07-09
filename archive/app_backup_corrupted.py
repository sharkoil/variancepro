"""
AI-Powered Quantitative Trading Analysis
Modern chat interface with comprehensive financial analytics
"""

import gradio as gr
import pandas as pd
import requests
import json
import io
import time
import traceback
import uuid
from datetime import datetime
from typing import List, Tuple, Optional, Dict, Any

# Import our modular components
from config.settings import Settings
from data.csv_loader import CSVLoader, CSVLoadError
from analyzers.contributor_analyzer import ContributorAnalyzer
from analyzers.financial_analyzer import FinancialAnalyzer
from analyzers.timescale_analyzer import TimescaleAnalyzer
from analyzers.news_analyzer_v2 import NewsAnalyzer
from analyzers.sql_query_engine import SQLQueryEngine
from analyzers.nl_to_sql_translator import NLToSQLTranslator
from analyzers.query_router import QueryRouter
from ai.llm_interpreter import LLMInterpreter
from ai.narrative_generator import NarrativeGenerator

class QuantCommanderApp:
    """Main financial analysis application class with modular architecture"""
    
    def __init__(self):
        """Initialize the application with all components"""
        # Initialize settings
        self.settings = Settings()
        
        # Initialize data loader
        self.csv_loader = CSVLoader(self.settings)
        
        # Initialize analyzers
        self.contributor_analyzer = ContributorAnalyzer(self.settings)
        self.financial_analyzer = FinancialAnalyzer(self.settings)
        self.timescale_analyzer = TimescaleAnalyzer(self.settings)
        self.news_analyzer = NewsAnalyzer(self.settings)
        
        # Initialize SQL components
        self.sql_engine = SQLQueryEngine()
        self.nl_to_sql = NLToSQLTranslator(self.settings)
        self.query_router = QueryRouter(self.settings)
        
        # Initialize AI components
        self.llm_interpreter = LLMInterpreter(self.settings)
        self.narrative_generator = NarrativeGenerator(self.llm_interpreter)
        
        # Application state
        self.current_data = None
        self.data_summary = None
        self.column_suggestions = None
        self.analysis_history = []
    
    def upload_csv(self, file) -> str:
        """Handle CSV file upload with enhanced processing"""
        if file is None:
            return "No file uploaded"
        
        try:
            print(f"[DEBUG] Attempting to load CSV file: {file.name}")
            
            # Load CSV using our improved CSV loader
            self.current_data = self.csv_loader.load_csv(file.name)
            print(f"[DEBUG] CSV loaded successfully. Shape: {self.current_data.shape}")
            
            # Get data summary and suggestions
            try:
                self.data_summary = self.csv_loader.get_data_summary()
                self.column_suggestions = self.csv_loader.get_column_suggestions()
            except Exception as e:
                print(f"[DEBUG] Error in data analysis: {e}")
            
            # Create preview
            preview_parts = [
                f"✅ **File loaded successfully!**",
                f"📊 **Rows**: {len(self.current_data):,}",
                f"📋 **Columns**: {len(self.current_data.columns)}",
                "",
                "🎯 **Quick Actions:**",
                "• Type 'analyze contribution' for top performers",
                "• Type 'summary' for data overview",
                "• Ask questions about your data",
                "",
                "📄 **Data Preview:**",
                "```",
                self.current_data.head(3).to_string(index=False, max_cols=6),
                "```"
            ]
            
            return "\n".join(preview_parts)
            
        except Exception as e:
            return f"❌ **Error loading file**: {str(e)}"
    
    def chat_response(self, message: str, history: List[Dict]) -> Tuple[List[Dict], str]:
        """Enhanced chat response with AI-powered analysis"""
        if not message.strip():
            return history, ""
        
        try:
            # Add user message to history
            history.append({"role": "user", "content": message})
            
            # Process the query
            if self.current_data is None:
                response = "⚠️ **Please upload a CSV file first** to start analyzing your data."
            else:
                response = self._process_user_query(message)
            
            # Add assistant response to history
            history.append({"role": "assistant", "content": response})
            
            return history, ""
            
        except Exception as e:
            error_response = f"❌ **Error processing your request**: {str(e)}"
            history.append({"role": "assistant", "content": error_response})
            return history, ""
    
    def _process_user_query(self, query: str) -> str:
        """Process user query with basic routing"""
        query_lower = query.lower()
        
        try:
            # Simple keyword-based routing
            if any(word in query_lower for word in ['contribution', 'pareto', '80/20', 'top contributors']):
                return self._perform_contribution_analysis(query)
            
            elif any(word in query_lower for word in ['variance', 'budget', 'actual']):
                return self._perform_variance_analysis(query)
            
            elif any(word in query_lower for word in ['trend', 'time', 'ttm']):
                return self._perform_trend_analysis(query)
            
            elif any(word in query_lower for word in ['summary', 'overview', 'describe']):
                return self._generate_data_overview()
            
            else:
                return self._generate_basic_response(query)
                
        except Exception as e:
            return f"❌ **Analysis Error**: {str(e)}"
    
    def _perform_contribution_analysis(self, query: str) -> str:
        """Perform contribution analysis"""
        try:
            if not self.column_suggestions:
                return "⚠️ **Data analysis not ready**. Please try uploading your file again."
            
            category_cols = self.column_suggestions.get('category_columns', [])
            value_cols = self.column_suggestions.get('value_columns', [])
            
            if not category_cols or not value_cols:
                return "⚠️ **Contribution analysis requires category and value columns**"
            
            # Use the analyzers
            results = self.contributor_analyzer.analyze(
                data=self.current_data,
                category_col=category_cols[0],
                value_col=value_cols[0]
            )
            
            return self.contributor_analyzer.format_for_chat()
            
        except Exception as e:
            return f"❌ **Contribution Analysis Error**: {str(e)}"
    
    def _perform_variance_analysis(self, query: str) -> str:
        """Perform quantitative analysis"""
        try:
            budget_vs_actual = self.column_suggestions.get('budget_vs_actual', {})
            
            if not budget_vs_actual:
                return "⚠️ **Quantitative analysis requires budget and actual columns**"
            
            budget_col = list(budget_vs_actual.keys())[0]
            actual_col = budget_vs_actual[budget_col]
            
            results = self.financial_analyzer.analyze(
                data=self.current_data,
                budget_col=budget_col,
                actual_col=actual_col
            )
            
            return self.financial_analyzer.format_for_chat()
            
        except Exception as e:
            return f"❌ **Variance Analysis Error**: {str(e)}"
    
    def _perform_trend_analysis(self, query: str) -> str:
        """Perform trend analysis"""
        try:
            date_cols = self.csv_loader.column_info.get('date_columns', [])
            numeric_cols = self.csv_loader.column_info.get('numeric_columns', [])
            
            if not date_cols or not numeric_cols:
                return "⚠️ **Trend analysis requires date and numeric columns**"
            
            results = self.timescale_analyzer.analyze(
                data=self.current_data,
                date_col=date_cols[0],
                value_cols=numeric_cols[:3]  # Limit to first 3 numeric columns
            )
            
            return self.timescale_analyzer.format_for_chat()
            
        except Exception as e:
            return f"❌ **Trend Analysis Error**: {str(e)}"
    
    def _generate_data_overview(self) -> str:
        """Generate data overview"""
        if not self.data_summary:
            return "⚠️ **No data summary available**. Please upload a file first."
        
        overview_parts = [
            "📊 **DATA OVERVIEW**",
            "",
            self.data_summary,
            "",
            f"📋 **Shape**: {len(self.current_data):,} rows × {len(self.current_data.columns)} columns",
            "",
            "🎯 **Available Analyses:**"
        ]
        
        # Add available analysis types
        if self.column_suggestions:
            if self.column_suggestions.get('category_columns') and self.column_suggestions.get('value_columns'):
                overview_parts.append("✅ Contribution Analysis")
            if self.column_suggestions.get('budget_vs_actual'):
                overview_parts.append("✅ Variance Analysis")
            if self.csv_loader.column_info.get('date_columns'):
                overview_parts.append("✅ Trend Analysis")
        
        return "\n".join(overview_parts)
    
    def _generate_basic_response(self, query: str) -> str:
        """Generate basic response for unrecognized queries"""
        return f"""
💬 **I can help you analyze your data!**

Here are some things you can try:
• **"analyze contribution"** - Find top performers (80/20 analysis)
• **"analyze variance"** - Compare budget vs actual
• **"analyze trends"** - Look at time-based patterns
• **"summary"** - Get a data overview

Your data has **{len(self.current_data):,} rows** and **{len(self.current_data.columns)} columns**.

What would you like to explore?
"""
    
    def create_interface(self):
        """Create the Gradio interface"""
        with gr.Blocks(title="AI Financial Analysis", theme=gr.themes.Soft()) as interface:
            # Header
            gr.Markdown("# 🏦 AI-Powered Financial Analysis")
            gr.Markdown("*Upload your financial data and chat with AI for comprehensive insights*")
            
            with gr.Row():
                with gr.Column(scale=1):
                    # File upload section
                    gr.Markdown("### 📊 Upload Data")
                    file_input = gr.File(
                        label="CSV File",
                        file_types=[".csv"],
                        type="filepath"
                    )
                    
                    # Data preview
                    data_preview = gr.Textbox(
                        label="Data Summary",
                        value="Upload a CSV file to get started with AI-powered analysis",
                        lines=12,
                        interactive=False
                    )
                
                with gr.Column(scale=2):
                    # Chat interface
                    gr.Markdown("### 💬 Chat Interface")
                    
                    chatbot = gr.Chatbot(
                        label="Financial Analysis Chat",
                        height=400,
                        type="messages",
                        value=[{"role": "assistant", "content": "👋 Welcome! Upload your CSV file and I'll help you analyze your financial data."}]
                    )
                    
                    with gr.Row():
                        chat_input = gr.Textbox(
                            placeholder="Ask about your data: 'analyze contribution', 'summary', etc.",
                            label="Your Message",
                            scale=4
                        )
                        send_btn = gr.Button("Send 📤", scale=1, variant="primary")
                    
                    # Quick action buttons
                    gr.Markdown("**Quick Actions:**")
                    with gr.Row():
                        contrib_btn = gr.Button("📈 Contribution", size="sm")
                        variance_btn = gr.Button("💰 Variance", size="sm")
                        trend_btn = gr.Button("📊 Trends", size="sm")
                        summary_btn = gr.Button("📋 Summary", size="sm")
            
            # Event handlers
            file_input.change(
                fn=self.upload_csv,
                inputs=[file_input],
                outputs=[data_preview]
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
            
            # Quick action handlers
            contrib_btn.click(
                fn=lambda hist: self.chat_response("analyze contribution", hist),
                inputs=[chatbot],
                outputs=[chatbot, chat_input]
            )
            
            variance_btn.click(
                fn=lambda hist: self.chat_response("analyze variance", hist),
                inputs=[chatbot],
                outputs=[chatbot, chat_input]
            )
            
            trend_btn.click(
                fn=lambda hist: self.chat_response("analyze trends", hist),
                inputs=[chatbot],
                outputs=[chatbot, chat_input]
            )
            
            summary_btn.click(
                fn=lambda hist: self.chat_response("summary", hist),
                inputs=[chatbot],
                outputs=[chatbot, chat_input]
            )
        
        return interface

def main():
    """Main entry point for AI-Powered Financial Analysis"""
    print("🚀 Starting AI-Powered Financial Analysis...")
    print("📊 Initializing modular components...")
    
    try:
        app = QuantCommanderApp()
        print("✅ All components initialized successfully")
        
        interface = app.create_interface()
        print("✅ Gradio interface created")
        
        print("🌐 Starting web server...")
        print("📝 Access the application at: http://localhost:7871")
        
        interface.launch(
            server_name="0.0.0.0",
            server_port=7871,
            share=False,
            debug=True,
            show_error=True
        )
        
    except Exception as e:
        print(f"❌ Failed to start application: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
