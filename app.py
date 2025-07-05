"""
VariancePro - AI-Powered Financial Intelligence Platform
Streamlined main application with modular architecture
"""

import gradio as gr
import pandas as pd
import traceback
from typing import List, Tuple, Optional, Dict, Any

# Import core components
from config.settings import Settings
from data.csv_loader import CSVLoader, CSVLoadError

# Import analyzers
from analyzers.contributor_analyzer import ContributorAnalyzer
from analyzers.financial_analyzer import FinancialAnalyzer
from analyzers.timescale_analyzer import TimescaleAnalyzer
from analyzers.news_analyzer_v2 import NewsAnalyzer
from analyzers.sql_query_engine import SQLQueryEngine
from analyzers.nl_to_sql_translator import NLToSQLTranslator
from analyzers.query_router import QueryRouter

# Import AI components
from ai.llm_interpreter import LLMInterpreter
from ai.narrative_generator import NarrativeGenerator

# Import new modular UI components
from ui.chat_handler import ChatHandler
from ui.analysis_handlers import AnalysisHandlers
from ui.interface_builder import InterfaceBuilder
from utils.session_manager import SessionManager


class QuantCommanderApp:
    """
    Main financial analysis application class with modular architecture
    Now streamlined with separated concerns for better maintainability
    """
    
    def __init__(self):
        """Initialize the application with all components"""
        print("🚀 Initializing VariancePro with modular architecture...")
        
        # Initialize session management first
        self.session_manager = SessionManager()
        
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
        
        # Initialize modular UI components
        self.chat_handler = ChatHandler(self)
        self.analysis_handlers = AnalysisHandlers(self)
        self.interface_builder = InterfaceBuilder(self)
        
        # Application state
        self.current_data = None
        self.data_summary = None
        self.column_suggestions = None
        self.analysis_history = []
        
        print("✅ All components initialized successfully")
    
    def upload_csv(self, file) -> Tuple[str, str, Optional[Dict], Optional[Dict]]:
        """Handle CSV file upload with enhanced processing and timestamp logging"""
        if file is None:
            return "No file uploaded", "No data available", None, None
        
        try:
            print(f"[DEBUG] Attempting to load CSV file: {file.name}")
            upload_time = self.session_manager.get_current_timestamp()
            print(f"[DEBUG] Upload started at: {upload_time}")
            
            # Load CSV using our improved CSV loader
            self.current_data = self.csv_loader.load_csv(file.name)
            print(f"[DEBUG] CSV loaded successfully. Shape: {self.current_data.shape}")
            
            # Load data into SQL engine for query capabilities
            try:
                self.sql_engine.load_dataframe_to_sql(self.current_data, table_name="data")
                self._sql_data_loaded = True
                print("[DEBUG] Data loaded into SQL engine successfully")
            except Exception as e:
                print(f"[DEBUG] Warning: Could not load data into SQL engine: {str(e)}")
                self._sql_data_loaded = False
            
            # Get data summary and suggestions with error handling
            try:
                self.data_summary = self.csv_loader.get_data_summary()
                print("[DEBUG] Data summary generated successfully")
            except Exception as e:
                self.data_summary = f"Error generating summary: {str(e)}"
                print(f"[DEBUG] Error generating data summary: {str(e)}")
                
            try:
                self.column_suggestions = self.csv_loader.get_column_suggestions()
                print(f"[DEBUG] Column suggestions generated successfully: {self.column_suggestions}")
            except Exception as e:
                self.column_suggestions = None
                print(f"[DEBUG] Error generating column suggestions: {str(e)}")
            
            # Generate enhanced analysis message with AI if available
            analysis_message = None
            if self.current_data is not None:
                try:
                    if self.llm_interpreter.is_available:
                        # Generate AI-powered initial analysis
                        context = {
                            'file_name': file.name,
                            'rows': len(self.current_data),
                            'columns': list(self.current_data.columns),
                            'data_sample': self.current_data.head(3).to_dict('records'),
                            'upload_time': upload_time,
                            'session_id': self.session_manager.session_id
                        }
                        
                        ai_prompt = f"Provide a brief welcome analysis for this uploaded dataset: {file.name}"
                        ai_response = self.llm_interpreter.query_llm(ai_prompt, context)
                        
                        if ai_response.success:
                            analysis_message = {
                                'role': 'assistant',
                                'content': f"📊 **DATA LOADED SUCCESSFULLY**\n\n{ai_response.content}\n\n{self.data_summary}"
                            }
                        else:
                            # Fallback to basic message
                            analysis_message = {
                                'role': 'assistant',
                                'content': f"📊 **DATA LOADED SUCCESSFULLY**\n\n{self.data_summary}"
                            }
                    else:
                        # Basic message when AI not available
                        analysis_message = {
                            'role': 'assistant',
                            'content': f"📊 **DATA LOADED SUCCESSFULLY**\n\n{self.data_summary}"
                        }
                        
                except Exception as e:
                    print(f"[DEBUG] Error generating analysis message: {str(e)}")
                    analysis_message = {
                        'role': 'assistant',
                        'content': f"📊 **DATA LOADED SUCCESSFULLY**\n\n{self.data_summary}"
                    }
            
            # Generate timescale analysis if data has date columns
            timescale_message = None
            date_cols = self.csv_loader.column_info.get('date_columns', [])
            if date_cols and len(date_cols) > 0:
                try:
                    print(f"[DEBUG] Generating automatic timescale analysis for date columns: {date_cols}")
                    # Perform timescale analysis
                    value_cols = self.column_suggestions.get('value_columns', []) if self.column_suggestions else []
                    if not value_cols:
                        value_cols = self.csv_loader.column_info.get('numeric_columns', [])
                    
                    if value_cols:
                        timescale_results = self.timescale_analyzer.analyze(
                            data=self.current_data,
                            date_col=date_cols[0],
                            value_cols=value_cols[:3]  # Limit to first 3 columns for performance
                        )
                        
                        timescale_content = self.timescale_analyzer.format_for_chat()
                        timescale_message = {
                            'role': 'assistant',
                            'content': timescale_content
                        }
                        print(f"[DEBUG] Timescale analysis generated successfully")
                    else:
                        print(f"[DEBUG] No numeric columns found for timescale analysis")
                except Exception as e:
                    print(f"[DEBUG] Error generating timescale analysis: {str(e)}")
                    import traceback
                    traceback.print_exc()
            
            # Return preview text and analysis messages
            preview_text = f"✅ **File uploaded successfully**\n\n{self.data_summary}"
            
            completion_time = self.session_manager.get_current_timestamp()
            print(f"[DEBUG] Upload completed at: {completion_time}")
            
            return preview_text, self.data_summary, analysis_message, timescale_message
            
        except CSVLoadError as e:
            error_msg = f"❌ **CSV Loading Error**: {str(e)}"
            print(f"[DEBUG] CSV loading error: {str(e)}")
            return error_msg, "", None, None
            
        except Exception as e:
            error_msg = f"❌ **Unexpected Error**: {str(e)}"
            print(f"[DEBUG] Unexpected error during upload: {str(e)}")
            traceback.print_exc()
            return error_msg, "", None, None
    
    def get_status(self) -> str:
        """Get comprehensive system status with session information"""
        status_parts = [
            "🔍 **VARIANCEPRO SYSTEM STATUS**",
            "",
            self.session_manager.format_status_session_info(),
            ""
        ]
        
        # LLM status
        if self.llm_interpreter.is_available:
            status_parts.append(f"✅ **AI Assistant**: {self.llm_interpreter.model_name} - Ready")
        else:
            status_parts.append(f"❌ **AI Assistant**: {self.llm_interpreter.model_name} - Offline")
            if self.llm_interpreter.last_error:
                status_parts.append(f"   Error: {self.llm_interpreter.last_error}")
        
        # Data status
        if self.current_data is not None:
            rows = len(self.current_data)
            cols = len(self.current_data.columns)
            status_parts.append(f"✅ **Dataset**: {rows:,} rows × {cols} columns loaded")
            
            # Analysis capabilities
            capabilities = []
            if self.column_suggestions:
                if self.column_suggestions.get('category_columns') and self.column_suggestions.get('value_columns'):
                    capabilities.append("Contribution Analysis")
                if self.column_suggestions.get('budget_vs_actual'):
                    capabilities.append("Variance Analysis")
                if self.csv_loader.column_info.get('date_columns'):
                    capabilities.append("Trend Analysis")
            
            if capabilities:
                status_parts.append(f"🎯 **Available Analyses**: {', '.join(capabilities)}")
        else:
            status_parts.append("⏳ **Dataset**: No data loaded")
        
        # System components
        status_parts.extend([
            "",
            "🧠 **System Components**:",
            f"✅ Settings: {self.settings.app_name} v{self.settings.app_version}",
            f"✅ CSV Loader: Ready",
            f"✅ Chat Handler: Ready",
            f"✅ Analysis Handlers: Ready",
            f"✅ Interface Builder: Ready"
        ])
        
        return "\n".join(status_parts)
    
    def create_interface(self):
        """Create the enhanced Gradio interface using the modular interface builder"""
        return self.interface_builder.create_interface()


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
        print(f"🆔 Session ID: {app.session_manager.session_id}")
        print(f"⏰ Started at: {app.session_manager.get_current_timestamp()}")
        
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
