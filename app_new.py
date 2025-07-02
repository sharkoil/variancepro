"""
VariancePro - AI-Powered Financial Data Analysis
Modern chat interface with comprehensive financial analytics
"""

import gradio as gr
import pandas as pd
import requests
import json
import io
import time
from typing import List, Tuple, Optional, Dict, Any

# Import our modular components
from config.settings import Settings
from data.csv_loader import CSVLoader, CSVLoadError
from analyzers.contributor_analyzer import ContributorAnalyzer
from analyzers.financial_analyzer import FinancialAnalyzer
from ai.llm_interpreter import LLMInterpreter
from ai.narrative_generator import NarrativeGenerator

class VarianceProApp:
    """Main VariancePro application class with modular architecture"""
    
    def __init__(self):
        """Initialize the application with all components"""
        # Initialize settings
        self.settings = Settings()
        
        # Initialize data loader
        self.csv_loader = CSVLoader(self.settings)
        
        # Initialize analyzers
        self.contributor_analyzer = ContributorAnalyzer(self.settings)
        self.financial_analyzer = FinancialAnalyzer(self.settings)
        
        # Initialize AI components
        self.llm_interpreter = LLMInterpreter(self.settings)
        self.narrative_generator = NarrativeGenerator(self.llm_interpreter)
        
        # Application state
        self.current_data = None
        self.data_summary = None
        self.column_suggestions = None
        self.analysis_history = []
    
    def upload_csv(self, file) -> Tuple[str, str]:
        """Handle CSV file upload with enhanced processing"""
        if file is None:
            return "No file uploaded", "No data available"
        
        try:
            # Load CSV using our CSV loader
            self.current_data = self.csv_loader.load_csv(file.name)
            
            # Get data summary and suggestions
            self.data_summary = self.csv_loader.get_data_summary()
            self.column_suggestions = self.csv_loader.get_column_suggestions()
            
            # Create enhanced preview
            preview_parts = [
                "✅ **Data loaded successfully!**",
                "",
                "📊 **Dataset Overview:**",
                f"• **Rows**: {len(self.current_data):,}",
                f"• **Columns**: {len(self.current_data.columns)}",
                "",
                "📋 **Column Information:**"
            ]
            
            # Add column info
            for col_type, columns in self.csv_loader.column_info.items():
                if columns and col_type != 'financial_columns':
                    preview_parts.append(f"• **{col_type.replace('_', ' ').title()}**: {', '.join(columns[:5])}")
            
            # Add financial columns info
            financial_cols = self.csv_loader.column_info.get('financial_columns', {})
            if financial_cols:
                preview_parts.append("• **Financial Columns Detected:**")
                for fin_type, fin_cols in financial_cols.items():
                    if fin_cols:
                        preview_parts.append(f"  - {fin_type.replace('_', ' ').title()}: {', '.join(fin_cols[:3])}")
            
            preview_parts.extend([
                "",
                "🎯 **Quick Analysis Suggestions:**",
                "• Type 'analyze contribution' for 80/20 Pareto analysis",
                "• Type 'analyze variance' for budget vs actual comparison",
                "• Type 'analyze trends' for time-series analysis",
                "• Ask questions like 'What are the top contributors to revenue?'",
                "",
                "📄 **Data Preview (first 5 rows):**"
            ])
            
            # Add data preview
            preview_table = self.current_data.head(5).to_string(index=False, max_cols=8)
            preview_parts.append(f"```\n{preview_table}\n```")
            
            enhanced_preview = "\n".join(preview_parts)
            
            return enhanced_preview, self.data_summary
            
        except CSVLoadError as e:
            return f"❌ **Data Loading Error**: {str(e)}", "No data available"
        except Exception as e:
            return f"❌ **Unexpected Error**: {str(e)}", "No data available"
    
    def upload_csv(self, file) -> Tuple[str, str]:
        """Handle CSV file upload and return preview + summary"""
        if file is None:
            return "No file uploaded", "No data available"
        
        try:
            # Read the CSV file
            if hasattr(file, 'name'):
                df = pd.read_csv(file.name)
            else:
                df = pd.read_csv(io.StringIO(file))
            
            self.current_data = df
            
            # Generate data summary
            self.data_summary = self._generate_data_summary(df)
            
            # Create preview (first 10 rows)
            preview = df.head(10).to_string(index=False)
            
            return f"✅ Data loaded successfully!\n\n{preview}", self.data_summary
            
        except Exception as e:
            return f"❌ Error loading CSV: {str(e)}", "No data available"
    
    def chat_response(self, message: str, history: List[Tuple[str, str]]) -> Tuple[List[Tuple[str, str]], str]:
        """Enhanced chat response with AI-powered analysis"""
        if not message.strip():
            return history, ""
        
        try:
            # Check if data is loaded
            if self.current_data is None:
                response = "⚠️ **No data loaded**. Please upload a CSV file first to start analysis."
                history.append((message, response))
                return history, ""
            
            # Analyze the user's query to determine intent
            response = self._process_user_query(message.lower().strip())
            
            # Add to history
            history.append((message, response))
            
            return history, ""
            
        except Exception as e:
            error_response = f"❌ **Error processing request**: {str(e)}"
            history.append((message, error_response))
            return history, ""
    
    def _process_user_query(self, query: str) -> str:
        """Process user query and generate appropriate response"""
        try:
            # Quick analysis commands
            if any(word in query for word in ['contribution', 'pareto', '80/20', 'top contributors']):
                return self._perform_contribution_analysis(query)
            
            elif any(word in query for word in ['variance', 'budget', 'actual', 'vs']):
                return self._perform_variance_analysis(query)
            
            elif any(word in query for word in ['trend', 'ttm', 'trailing', 'time series']):
                return self._perform_trend_analysis(query)
            
            elif any(word in query for word in ['summary', 'overview', 'describe']):
                return self._generate_data_overview()
            
            # General AI-powered response
            else:
                return self._generate_ai_response(query)
                
        except Exception as e:
            return f"❌ **Analysis Error**: {str(e)}"
    
    def _perform_contribution_analysis(self, query: str) -> str:
        """Perform contribution analysis"""
        try:
            # Use column suggestions to find best columns
            suggestions = self.column_suggestions
            
            # Find category and value columns
            category_cols = suggestions.get('category_columns', [])
            value_cols = suggestions.get('value_columns', [])
            
            if not category_cols or not value_cols:
                return (
                    "⚠️ **Cannot perform contribution analysis**\n\n"
                    "Required columns not found:\n"
                    f"• Category columns available: {category_cols}\n"
                    f"• Value columns available: {value_cols}\n\n"
                    "Please ensure your data has categorical columns (like Product, Customer) "
                    "and numeric value columns (like Sales, Revenue)."
                )
            
            # Use first available columns
            category_col = category_cols[0]
            value_col = value_cols[0]
            
            # Perform analysis
            results = self.contributor_analyzer.analyze(
                data=self.current_data,
                category_col=category_col,
                value_col=value_col
            )
            
            # Generate AI narrative if available
            if self.llm_interpreter.is_available:
                context = {
                    'dataset_info': {
                        'rows': len(self.current_data),
                        'columns': len(self.current_data.columns),
                        'category_column': category_col,
                        'value_column': value_col
                    },
                    'analysis_results': results
                }
                
                ai_response = self.llm_interpreter.query_llm(
                    f"Provide insights on this contribution analysis of {value_col} by {category_col}",
                    context
                )
                
                if ai_response.success:
                    ai_insights = self.narrative_generator.format_for_chat(
                        ai_response.content, 
                        "AI-Powered Insights"
                    )
                    
                    formatted_results = self.contributor_analyzer.format_for_chat()
                    return f"{formatted_results}\n\n{ai_insights}"
            
            # Return formatted results
            return self.contributor_analyzer.format_for_chat()
            
        except Exception as e:
            return f"❌ **Contribution Analysis Error**: {str(e)}"
    
    def _perform_variance_analysis(self, query: str) -> str:
        """Perform variance analysis"""
        try:
            # Find required columns
            suggestions = self.column_suggestions
            budget_vs_actual = suggestions.get('budget_vs_actual', {})
            date_cols = self.csv_loader.column_info.get('date_columns', [])
            
            if not budget_vs_actual or not date_cols:
                return (
                    "⚠️ **Cannot perform variance analysis**\n\n"
                    "Required columns not found:\n"
                    f"• Budget/Actual pairs: {list(budget_vs_actual.keys())}\n"
                    f"• Date columns: {date_cols}\n\n"
                    "Please ensure your data has budget and actual columns (like Sales_Budget, Sales_Actual) "
                    "and a date column."
                )
            
            # Use first available budget/actual pair
            budget_col = list(budget_vs_actual.keys())[0]
            actual_col = budget_vs_actual[budget_col]
            date_col = date_cols[0]
            
            # Perform analysis
            results = self.financial_analyzer.analyze(
                data=self.current_data,
                date_col=date_col,
                value_col=actual_col,
                budget_col=budget_col,
                analysis_type='variance'
            )
            
            # Generate AI narrative if available
            if self.llm_interpreter.is_available:
                context = {
                    'dataset_info': {
                        'rows': len(self.current_data),
                        'date_column': date_col,
                        'actual_column': actual_col,
                        'budget_column': budget_col
                    },
                    'analysis_results': results
                }
                
                ai_response = self.llm_interpreter.query_llm(
                    f"Provide insights on this budget vs actual variance analysis",
                    context
                )
                
                if ai_response.success:
                    ai_insights = self.narrative_generator.format_for_chat(
                        ai_response.content,
                        "AI-Powered Insights"
                    )
                    
                    formatted_results = self.financial_analyzer.format_for_chat()
                    return f"{formatted_results}\n\n{ai_insights}"
            
            # Return formatted results
            return self.financial_analyzer.format_for_chat()
            
        except Exception as e:
            return f"❌ **Variance Analysis Error**: {str(e)}"
    
    def _perform_trend_analysis(self, query: str) -> str:
        """Perform trend analysis"""
        try:
            # Find required columns
            suggestions = self.column_suggestions
            value_cols = suggestions.get('value_columns', [])
            date_cols = self.csv_loader.column_info.get('date_columns', [])
            category_cols = suggestions.get('category_columns', [])
            
            if not value_cols or not date_cols:
                return (
                    "⚠️ **Cannot perform trend analysis**\n\n"
                    "Required columns not found:\n"
                    f"• Value columns: {value_cols}\n"
                    f"• Date columns: {date_cols}\n\n"
                    "Please ensure your data has numeric value columns and a date column."
                )
            
            # Use first available columns
            value_col = value_cols[0]
            date_col = date_cols[0]
            category_col = category_cols[0] if category_cols else None
            
            # Determine analysis type based on query
            if any(word in query for word in ['ttm', 'trailing', 'twelve']):
                analysis_type = 'ttm'
            else:
                analysis_type = 'trend'
            
            # Perform analysis
            results = self.financial_analyzer.analyze(
                data=self.current_data,
                date_col=date_col,
                value_col=value_col,
                category_col=category_col,
                analysis_type=analysis_type
            )
            
            # Generate AI narrative if available
            if self.llm_interpreter.is_available:
                context = {
                    'dataset_info': {
                        'rows': len(self.current_data),
                        'date_column': date_col,
                        'value_column': value_col,
                        'category_column': category_col,
                        'analysis_type': analysis_type
                    },
                    'analysis_results': results
                }
                
                ai_response = self.llm_interpreter.query_llm(
                    f"Provide insights on this {analysis_type} analysis",
                    context
                )
                
                if ai_response.success:
                    ai_insights = self.narrative_generator.format_for_chat(
                        ai_response.content,
                        "AI-Powered Insights"
                    )
                    
                    formatted_results = self.financial_analyzer.format_for_chat()
                    return f"{formatted_results}\n\n{ai_insights}"
            
            # Return formatted results
            return self.financial_analyzer.format_for_chat()
            
        except Exception as e:
            return f"❌ **Trend Analysis Error**: {str(e)}"
    
    def _generate_data_overview(self) -> str:
        """Generate comprehensive data overview"""
        try:
            overview_parts = [
                "📊 **COMPREHENSIVE DATA OVERVIEW**",
                "",
                self.data_summary,
                "",
                "🎯 **Analysis Capabilities Detected:**"
            ]
            
            # Add capabilities based on available columns
            suggestions = self.column_suggestions
            
            if suggestions.get('category_columns') and suggestions.get('value_columns'):
                overview_parts.append("✅ **Contribution Analysis (80/20 Pareto)** - Available")
            
            if suggestions.get('budget_vs_actual'):
                overview_parts.append("✅ **Variance Analysis (Budget vs Actual)** - Available")
            
            if self.csv_loader.column_info.get('date_columns'):
                overview_parts.append("✅ **Trend Analysis (TTM & Time Series)** - Available")
            
            # Add data quality information
            quality = self.csv_loader.data_quality
            if quality.get('missing_data'):
                overview_parts.extend([
                    "",
                    "⚠️ **Data Quality Notes:**"
                ])
                for col, info in quality['missing_data'].items():
                    if info['percentage'] > 5:  # Only show if > 5% missing
                        overview_parts.append(f"• {col}: {info['percentage']:.1f}% missing values")
            
            # Generate AI summary if available
            if self.llm_interpreter.is_available:
                context = {
                    'dataset_info': {
                        'rows': len(self.current_data),
                        'columns': len(self.current_data.columns),
                        'column_types': dict(self.csv_loader.column_info)
                    }
                }
                
                ai_response = self.llm_interpreter.query_llm(
                    "Provide a professional executive summary of this dataset's analytical potential",
                    context
                )
                
                if ai_response.success:
                    ai_summary = self.narrative_generator.format_for_chat(
                        ai_response.content,
                        "AI Executive Summary"
                    )
                    overview_parts.extend(["", ai_summary])
            
            return "\n".join(overview_parts)
            
        except Exception as e:
            return f"❌ **Overview Generation Error**: {str(e)}"
    
    def _generate_ai_response(self, query: str) -> str:
        """Generate AI-powered response to general queries"""
        try:
            if not self.llm_interpreter.is_available:
                return (
                    "🤖 **AI Assistant Unavailable**\n\n"
                    "The AI assistant (Ollama/Gemma3) is not available. "
                    "You can still use the following analysis commands:\n\n"
                    "• `analyze contribution` - 80/20 Pareto analysis\n"
                    "• `analyze variance` - Budget vs Actual comparison\n"
                    "• `analyze trends` - Time series and TTM analysis\n"
                    "• `summary` - Data overview and capabilities"
                )
            
            # Build context for AI
            context = {
                'dataset_info': {
                    'rows': len(self.current_data),
                    'columns': len(self.current_data.columns),
                    'column_types': dict(self.csv_loader.column_info),
                    'data_summary': self.data_summary
                }
            }
            
            # Query the AI
            ai_response = self.llm_interpreter.query_llm(query, context)
            
            if ai_response.success:
                return self.narrative_generator.format_for_chat(
                    ai_response.content,
                    "Aria Sterling - Financial Analyst"
                )
            else:
                return (
                    f"❌ **AI Response Error**: {ai_response.error}\n\n"
                    "You can still use the following analysis commands:\n\n"
                    "• `analyze contribution` - 80/20 Pareto analysis\n"
                    "• `analyze variance` - Budget vs Actual comparison\n"
                    "• `analyze trends` - Time series and TTM analysis\n"
                    "• `summary` - Data overview and capabilities"
                )
        
        except Exception as e:
            return f"❌ **AI Processing Error**: {str(e)}"
    
    def get_status(self) -> str:
        """Get comprehensive system status"""
        status_parts = [
            "🔍 **VARIANCEPRO SYSTEM STATUS**",
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
            f"✅ Contributor Analyzer: Ready",
            f"✅ Financial Analyzer: Ready",
            f"✅ Narrative Generator: Ready"
        ])
        
        return "\n".join(status_parts)
    
    def create_interface(self):
        """Create the enhanced Gradio interface"""
        
        with gr.Blocks(title="VariancePro - AI Financial Analysis", theme=gr.themes.Soft()) as interface:
            
            gr.HTML("""
            <h1 style="text-align: center; color: #2E86AB;">� VariancePro</h1>
            <h2 style="text-align: center; color: #A23B72;">AI-Powered Financial Data Analysis</h2>
            <p style="text-align: center; font-size: 18px;">
                Upload your financial data and chat with Aria Sterling for comprehensive insights and analysis
            </p>
            """)
            
            with gr.Row():
                with gr.Column(scale=1):
                    # Status panel
                    status_display = gr.Markdown(value=self.get_status())
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
                
                with gr.Column(scale=2):
                    # Chat interface
                    gr.Markdown("### 💬 Chat with Aria Sterling")
                    gr.Markdown("*Professional Financial Analyst AI Assistant*")
                    
                    chatbot = gr.Chatbot(
                        label="Financial Analysis Chat",
                        height=450,
                        show_label=True,
                        placeholder="Start by uploading a CSV file, then ask questions or request analysis...",
                        avatar_images=["👤", "🤖"]
                    )
                    
                    with gr.Row():
                        chat_input = gr.Textbox(
                            placeholder="Ask about your data: 'analyze contribution', 'show trends', 'variance analysis', or ask any question...",
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
                        trend_btn = gr.Button("� Trend Analysis", size="sm")
                        summary_btn = gr.Button("📋 Data Summary", size="sm")
            
            # Data summary (hidden, for context)
            data_summary_state = gr.State("")
            
            # Event handlers
            refresh_btn.click(
                fn=self.get_status,
                outputs=[status_display]
            )
            
            file_input.change(
                fn=self.upload_csv,
                inputs=[file_input],
                outputs=[data_preview, data_summary_state]
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
            
            # Quick action button handlers
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
    """Main entry point for VariancePro"""
    print("🚀 Starting VariancePro - AI-Powered Financial Analysis...")
    print("📊 Initializing modular components...")
    
    try:
        app = VarianceProApp()
        print("✅ All components initialized successfully")
        
        interface = app.create_interface()
        print("✅ Gradio interface created")
        
        print("🌐 Starting web server...")
        print("📝 Access the application at: http://localhost:7860")
        
        interface.launch(
            server_name="0.0.0.0",
            server_port=7860,
            share=False,
            debug=True,
            show_error=True
        )
        
    except Exception as e:
        print(f"❌ Failed to start VariancePro: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
