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
from analyzers.enhanced_nl_to_sql_translator import EnhancedNLToSQLTranslator
from analyzers.strategy_1_llm_enhanced import LLMEnhancedNLToSQL
from analyzers.query_router import QueryRouter
from analyzers.analysis_coordinator import AnalysisCoordinator
from ai.llm_interpreter import LLMInterpreter
from ai.narrative_generator import NarrativeGenerator
from ui.event_handlers import UIEventHandlers
from ui.chat_interface_enhancer import ChatInterfaceEnhancer
from ui.advanced_interface_components import FieldPicker, DataVisualizer, ExportManager

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
        
        # Initialize AI components first
        self.llm_interpreter = LLMInterpreter(self.settings)
        self.narrative_generator = NarrativeGenerator(self.llm_interpreter)
        
        # Initialize SQL components
        self.sql_engine = SQLQueryEngine()
        self.nl_to_sql = NLToSQLTranslator(self.settings)
        self.enhanced_nl_to_sql = EnhancedNLToSQLTranslator()
        self.llm_enhanced_sql = LLMEnhancedNLToSQL(self.llm_interpreter)
        self.query_router = QueryRouter(self.settings)
        
        # Initialize analysis coordinator
        self.analysis_coordinator = AnalysisCoordinator(self)
        
        # Initialize UI event handlers and enhancers
        self.event_handlers = UIEventHandlers(self)
        self.chat_enhancer = ChatInterfaceEnhancer(character_threshold=150)
        
        # Initialize advanced interface components
        self.field_picker = FieldPicker(self)
        self.data_visualizer = DataVisualizer(self)
        self.export_manager = ExportManager(self)
        
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
                
                # Initialize enhanced SQL translators with schema context
                self._initialize_sql_translators()
                
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
                response = self.analysis_coordinator.process_user_query(message)
            
            # Add assistant response to history
            history.append({"role": "assistant", "content": response})
            
            return history, ""
            
        except Exception as e:
            error_response = f"❌ **Error processing your request**: {str(e)}"
            history.append({"role": "assistant", "content": error_response})
            return history, ""
    
    def create_interface(self):
        """Create the Gradio interface with advanced features"""
        with gr.Blocks(title="AI Financial Analysis", theme=gr.themes.Soft()) as interface:
            # Header
            gr.Markdown("# 🏦 AI-Powered Financial Analysis")
            gr.Markdown("*Upload your financial data and chat with AI for comprehensive insights*")
            
            # Main interface with tabs
            with gr.Tabs():
                with gr.TabItem("💬 Chat Analysis"):
                    self._create_chat_tab()
                
                with gr.TabItem("🎯 Query Builder"):
                    self._create_query_builder_tab()
                
                with gr.TabItem("📊 Visualizations"):
                    self._create_visualization_tab()
                
                with gr.TabItem("💾 Export & Reports"):
                    self._create_export_tab()
        
        return interface
    
    def _create_chat_tab(self):
        """Create the main chat interface tab"""
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
                
                # Advanced actions
                gr.Markdown("**Advanced Features:**")
                with gr.Row():
                    sql_test_btn = gr.Button("🧪 Test SQL", size="sm", variant="secondary")
                    news_btn = gr.Button("📰 News Context", size="sm", variant="secondary")
                    export_btn = gr.Button("💾 Export", size="sm", variant="secondary")
        
        # Store components for event binding
        self.chat_components = {
            'file_input': file_input,
            'data_preview': data_preview,
            'chatbot': chatbot,
            'chat_input': chat_input,
            'send_btn': send_btn,
            'contrib_btn': contrib_btn,
            'variance_btn': variance_btn,
            'trend_btn': trend_btn,
            'summary_btn': summary_btn,
            'sql_test_btn': sql_test_btn,
            'news_btn': news_btn,
            'export_btn': export_btn
        }
        
        # Bind events
        self.event_handlers.bind_events(self.chat_components)
    
    def _create_query_builder_tab(self):
        """Create the advanced query builder tab"""
        gr.Markdown("### 🎯 Advanced Query Builder")
        gr.Markdown("*Build complex queries using visual field selection and filters*")
        
        # Field picker interface
        picker_components = self.field_picker.create_field_picker_interface()
        
        # Store components for later use
        self.picker_components = picker_components
        
        # Bind field picker events
        self._bind_field_picker_events()
    
    def _create_visualization_tab(self):
        """Create the data visualization tab"""
        gr.Markdown("### 📊 Data Visualizations")
        gr.Markdown("*Create interactive charts and graphs from your data*")
        
        # Visualization interface
        viz_components = self.data_visualizer.create_visualization_interface()
        
        # Store components
        self.viz_components = viz_components
        
        # Bind visualization events
        self._bind_visualization_events()
    
    def _create_export_tab(self):
        """Create the export and reports tab"""
        gr.Markdown("### 💾 Export & Reports")
        gr.Markdown("*Export your data and generate comprehensive analysis reports*")
        
        # Export interface
        export_components = self.export_manager.create_export_interface()
        
        # Store components
        self.export_components = export_components
        
        # Bind export events
        self._bind_export_events()
    
    def _bind_field_picker_events(self):
        """Bind events for field picker components"""
        try:
            # Update field choices when data is loaded
            def update_picker_on_data_load():
                return self.field_picker.update_field_choices()
            
            # Update query preview when selections change
            def update_query_preview(selected_fields, aggregation, group_by, filters_text):
                return self.field_picker.update_query_preview(selected_fields, aggregation, group_by, filters_text)
            
            # Add filter
            def add_filter(field, operator, value, current_filters):
                return self.field_picker.add_filter(field, operator, value, current_filters)
            
            # Execute query
            def execute_field_query(query_text):
                if self.current_data is None:
                    return [{"role": "assistant", "content": "⚠️ Please upload a CSV file first."}]
                return self.chat_response(query_text, [])
            
            # Bind the events (simplified - would need proper gradio event binding)
            
        except Exception as e:
            print(f"Error binding field picker events: {e}")
    
    def _bind_visualization_events(self):
        """Bind events for visualization components"""
        try:
            # Create chart
            def create_chart(chart_type, x_field, y_field):
                return self.data_visualizer.generate_chart(chart_type, x_field, y_field)
            
            # Update field choices for visualization
            def update_viz_fields():
                fields = self.field_picker.get_available_fields()
                return gr.Dropdown(choices=fields), gr.Dropdown(choices=fields)
            
        except Exception as e:
            print(f"Error binding visualization events: {e}")
    
    def _bind_export_events(self):
        """Bind events for export components"""
        try:
            # Export data
            def export_data(export_format, include_filters):
                return self.export_manager.export_data(export_format, include_filters)
            
        except Exception as e:
            print(f"Error binding export events: {e}")

    def _initialize_sql_translators(self):
        """Initialize enhanced SQL translators with current data schema"""
        if self.current_data is None:
            return
            
        try:
            # Build schema info for enhanced translators
            schema_info = {
                'table_name': 'data',
                'columns': list(self.current_data.columns),
                'column_types': {col: str(dtype) for col, dtype in self.current_data.dtypes.items()},
                'sample_values': {col: self.current_data[col].dropna().head(3).tolist() 
                                for col in self.current_data.columns}
            }
            
            # Set schema context for enhanced translators
            self.enhanced_nl_to_sql.set_schema_context(schema_info, 'data')
            self.llm_enhanced_sql.schema_info = schema_info
            self.llm_enhanced_sql.table_name = 'data'
            
            print(f"[DEBUG] SQL translators initialized with {len(schema_info['columns'])} columns")
            
        except Exception as e:
            print(f"[DEBUG] Error initializing SQL translators: {e}")

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
            server_port=7872,
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
