"""
AI-Powered Financial Data Analysis
Modern chat interface with comprehensive financial analytics
"""

import gradio as gr
import pandas as pd
import requests
import json
import io
import time
import traceback
from typing import List, Tuple, Optional, Dict, Any

# Import our modular components
from config.settings import Settings
from data.csv_loader import CSVLoader, CSVLoadError
from analyzers.contributor_analyzer import ContributorAnalyzer
from analyzers.financial_analyzer import FinancialAnalyzer
from analyzers.timescale_analyzer import TimescaleAnalyzer
from analyzers.news_analyzer_v2 import NewsAnalyzer
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
        
        # Initialize AI components
        self.llm_interpreter = LLMInterpreter(self.settings)
        self.narrative_generator = NarrativeGenerator(self.llm_interpreter)
        
        # Application state
        self.current_data = None
        self.data_summary = None
        self.column_suggestions = None
        self.analysis_history = []
    
    def upload_csv(self, file) -> Tuple[str, str, Optional[Dict]]:
        """Handle CSV file upload with enhanced processing"""
        if file is None:
            return "No file uploaded", "No data available", None
        
        try:
            print(f"[DEBUG] Attempting to load CSV file: {file.name}")
            
            # Load CSV using our improved CSV loader
            self.current_data = self.csv_loader.load_csv(file.name)
            print(f"[DEBUG] CSV loaded successfully. Shape: {self.current_data.shape}")
            
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
                self.column_suggestions = {}
                print(f"[DEBUG] Error getting column suggestions: {str(e)}")
            
            # Create enhanced preview - without the analysis
            preview_parts = [
                "✅ **Data loaded successfully!**",
                "",
                "📊 **Dataset Overview:**",
                f"• **Rows**: {len(self.current_data):,}",
                f"• **Columns**: {len(self.current_data.columns)}",
                "",
                "📋 **Column Information:**"
            ]
            
            # Add column info with error handling
            try:
                for col_type, columns in self.csv_loader.column_info.items():
                    if columns and col_type != 'financial_columns':
                        if isinstance(columns, list) and len(columns) > 0:
                            preview_parts.append(f"• **{col_type.replace('_', ' ').title()}**: {', '.join(columns[:5])}")
                
                # Add financial columns info
                financial_cols = self.csv_loader.column_info.get('financial_columns', {})
                if isinstance(financial_cols, dict) and financial_cols:
                    preview_parts.append("• **Financial Columns Detected:**")
                    for fin_type, fin_cols in financial_cols.items():
                        if isinstance(fin_cols, list) and fin_cols:
                            preview_parts.append(f"  - {fin_type.replace('_', ' ').title()}: {', '.join(fin_cols[:3])}")
            except Exception as e:
                preview_parts.append(f"• **Column Analysis**: Error - {str(e)}")
            
            preview_parts.extend([
                "",
                "🎯 **Quick Analysis Suggestions:**",
                "• Type 'analyze contribution' for 80/20 Pareto analysis",
                "• Type 'analyze variance' for budget vs actual comparison",
                "• Type 'analyze trends' for time-series analysis",
                "• Ask questions like 'What are the top contributors to revenue?'",
                ""
            ])
            
            # Auto-generate timescale analysis (like the original) - but for the chat
            analysis_message = None
            
            try:
                # Check if we have date and numeric columns for timescale analysis
                date_cols = self.csv_loader.column_info.get('date_columns', [])
                numeric_cols = self.csv_loader.column_info.get('numeric_columns', [])
                
                print(f"[DEBUG] Auto-analysis - Date columns: {date_cols}")
                print(f"[DEBUG] Auto-analysis - Numeric columns: {numeric_cols}")
                
                if date_cols and numeric_cols:
                    # Perform automatic timescale analysis
                    date_col = date_cols[0]  # Use first date column
                    print(f"[DEBUG] Performing timescale analysis with date column: {date_col}")
                    
                    # Use dedicated TimescaleAnalyzer for comprehensive analysis
                    try:
                        timescale_results = self.timescale_analyzer.analyze(
                            data=self.current_data,
                            date_col=date_col,
                            value_cols=numeric_cols
                        )
                        print(f"[DEBUG] Timescale analysis completed successfully")
                        
                        # Format the timescale analysis for chat
                        formatted_results = self.timescale_analyzer.format_for_chat()
                        print(f"[DEBUG] Formatted timescale results length: {len(formatted_results)}")
                        
                        # Create an automatic analysis message for the chat
                        analysis_message = {
                            'type': 'timescale',
                            'content': formatted_results
                        }
                        
                    except Exception as e:
                        print(f"[DEBUG] Error in timescale analysis: {str(e)}")
                        print(f"[DEBUG] Traceback: {traceback.format_exc()}")
                        analysis_message = {
                            'type': 'error',
                            'content': f"❌ **Timescale Analysis Error**: {str(e)}"
                        }
                
                else:
                    print("[DEBUG] No date or numeric columns found for timescale analysis, using fallback")
                    # Fallback to other analysis types if no timescale data
                    if (self.column_suggestions.get('category_columns') and 
                        self.column_suggestions.get('value_columns')):
                        
                        category_col = self.column_suggestions['category_columns'][0]
                        value_col = self.column_suggestions['value_columns'][0]
                        
                        # Perform contribution analysis as fallback
                        results = self.contributor_analyzer.analyze(
                            data=self.current_data,
                            category_col=category_col,
                            value_col=value_col
                        )
                        
                        # Format for chat
                        formatted_results = self.contributor_analyzer.format_for_chat()
                        analysis_message = {
                            'type': 'contribution',
                            'content': f"📊 **AUTOMATIC CONTRIBUTION ANALYSIS**\n\n{formatted_results}"
                        }
                    
                    else:
                        analysis_message = {
                            'type': 'info',
                            'content': "ℹ️ **AUTOMATIC ANALYSIS**\n\nUnable to automatically determine the best analysis type.\nPlease use the chat commands or quick buttons to run specific analyses."
                        }
                        
            except Exception as e:
                print(f"[DEBUG] Auto-analysis overall error: {str(e)}")
                analysis_message = {
                    'type': 'error',
                    'content': f"❌ **Auto-analysis Error**: {str(e)}"
                }
            
            # Add data preview section (without analysis)
            preview_parts.extend([
                "",
                "📄 **Data Preview (first 5 rows):**"
            ])
            
            # Add data preview
            try:
                preview_table = self.current_data.head(5).to_string(index=False, max_cols=8)
                preview_parts.append(f"```\n{preview_table}\n```")
            except Exception as e:
                preview_parts.append(f"Error displaying preview: {str(e)}")
            
            enhanced_preview = "\n".join(preview_parts)
            
            return enhanced_preview, self.data_summary, analysis_message
            
        except CSVLoadError as e:
            return f"❌ **Data Loading Error**: {str(e)}", "No data available", None
        except Exception as e:
            error_msg = f"❌ **Unexpected Error**: {str(e)}"
            print(f"Debug - Upload error: {str(e)}")
            import traceback
            traceback.print_exc()
            return error_msg, "No data available", None
    

    
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
        """Process user query using LLM-powered intent recognition"""
        try:
            # First, try LLM-powered intent classification if available
            if self.llm_interpreter.is_available:
                intent_response = self._classify_user_intent(query)
                if intent_response:
                    return intent_response
            
            # Fallback to keyword-based detection if LLM unavailable
            print("[DEBUG] LLM unavailable, using keyword fallback")
            
            # Quick analysis commands (fallback)
            if any(word in query for word in ['contribution', 'pareto', '80/20', 'top contributors']):
                return self._perform_contribution_analysis(query)
            
            elif any(word in query for word in ['variance', 'budget', 'actual', 'vs']):
                return self._perform_variance_analysis(query)
            
            elif any(word in query for word in ['trend', 'ttm', 'trailing', 'time series']):
                return self._perform_trend_analysis(query)
            
            elif any(word in query for word in ['summary', 'overview', 'describe']):
                return self._generate_data_overview()
            
            # Top N / Bottom N fallback detection
            elif any(word in query for word in ['top ', 'best ', 'highest ', 'largest ', 'most ']):
                return self._perform_top_n_analysis(query, is_bottom=False)
            
            elif any(word in query for word in ['bottom ', 'worst ', 'lowest ', 'smallest ', 'least ']):
                return self._perform_top_n_analysis(query, is_bottom=True)
            
            # General response for unrecognized queries
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
            date_col = date_cols[0]
            
            # Determine analysis type based on query
            if any(word in query for word in ['timescale', 'time scale', 'all periods']):
                # Use TimescaleAnalyzer for comprehensive multi-period analysis
                try:
                    print(f"[DEBUG] Performing comprehensive timescale analysis with date column: {date_col}")
                    numeric_cols = self.csv_loader.column_info.get('numeric_columns', [])
                    
                    # Use TimescaleAnalyzer for multi-period analysis
                    timescale_results = self.timescale_analyzer.analyze(
                        data=self.current_data,
                        date_col=date_col,
                        value_cols=numeric_cols
                    )
                    
                    # Return formatted results from TimescaleAnalyzer
                    return self.timescale_analyzer.format_for_chat()
                except Exception as e:
                    print(f"[DEBUG] Error in comprehensive timescale analysis: {str(e)}")
                    # Fall back to standard trend analysis if timescale fails
                    pass
            
            # Standard trend analysis if not using timescale or if timescale failed
            value_col = value_cols[0]
            category_col = category_cols[0] if category_cols else None
            
            # Determine analysis type based on query
            if any(word in query for word in ['ttm', 'trailing', 'twelve']):
                analysis_type = 'ttm'
            else:
                analysis_type = 'trend'
            
            # Perform analysis with FinancialAnalyzer
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
        """Generate AI-powered response to general queries with enhanced context"""
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
            
            # Build comprehensive context for AI including data samples
            context = {
                'dataset_info': {
                    'rows': len(self.current_data),
                    'columns': len(self.current_data.columns),
                    'column_names': list(self.current_data.columns),
                    'column_types': dict(self.csv_loader.column_info),
                    'data_summary': self.data_summary,
                    'available_analyses': self._get_available_analyses()
                },
                'sample_data': {
                    'first_few_rows': self.current_data.head(3).to_dict('records'),
                    'data_range': {
                        col: {
                            'min': self.current_data[col].min() if self.current_data[col].dtype in ['int64', 'float64'] else None,
                            'max': self.current_data[col].max() if self.current_data[col].dtype in ['int64', 'float64'] else None,
                            'unique_count': self.current_data[col].nunique()
                        } for col in self.current_data.columns[:5]  # Limit to first 5 columns
                    }
                }
            }
            
            # Enhanced prompt for contextual understanding
            enhanced_prompt = f"""
You are Aria Sterling, a professional financial analyst AI assistant. You have access to a dataset and should provide insightful, actionable responses.

USER QUESTION: "{query}"

DATASET CONTEXT:
- {len(self.current_data):,} rows × {len(self.current_data.columns)} columns
- Columns: {', '.join(self.current_data.columns)}
- Available analyses: {', '.join(self._get_available_analyses())}

RESPONSE GUIDELINES:
1. Provide specific, actionable insights based on the actual data structure
2. Reference specific columns and data patterns when relevant
3. Suggest appropriate analyses if the user's question could be answered with a specific analysis type
4. Be conversational but professional
5. If asking about specific metrics, explain what columns contain that information
6. Always relate your response to the actual dataset structure and content

Provide a helpful, contextual response as Aria Sterling.
"""
            
            # Query the AI with enhanced context
            ai_response = self.llm_interpreter.query_llm(enhanced_prompt, context)
            
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
        
        with gr.Blocks(title="AI Financial Analysis", theme=gr.themes.Soft()) as interface:
            
            # Add the logo image using the Image component
            with gr.Row():
                with gr.Column():
                    gr.Image("logo.png", show_label=False, height=120, width=None)
                    
            with gr.Row():
                with gr.Column():
                    gr.HTML("""
                    <div style="text-align: center; margin-top: -20px;">
                        <h1 style="color: #043B4A; margin: 0;">AI-Powered Financial Data Analysis</h1>
                        <p style="font-size: 18px;">
                            Professional insights and analysis powered by artificial intelligence
                        </p>
                    </div>
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
                        avatar_images=["👤", "🤖"],
                        value=[(None, "👋 Welcome! I'm Aria Sterling, your AI financial analyst. 📊 Upload your financial data and chat with me for comprehensive insights and analysis! 💼✨")]
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
                fn=self.get_status,
                outputs=[status_display]
            )
            
            # Custom file upload event handler that adds analysis to chat
            def handle_file_upload(file, chatbot):
                if file is None:
                    return None, "No data available", chatbot, "<i>Upload data to see available fields</i>", "<i>Upload data to see available fields</i>", "<i>Upload data to see available fields</i>", "<i>Upload data to see available fields</i>"
                
                preview, data_summary, analysis_message = self.upload_csv(file)
                
                # Generate field picker HTML
                date_html = self._generate_field_picker_html(
                    self.csv_loader.column_info.get('date_columns', []), 
                    "date"
                )
                numeric_html = self._generate_field_picker_html(
                    self.csv_loader.column_info.get('numeric_columns', []), 
                    "numeric"
                )
                category_html = self._generate_field_picker_html(
                    self.column_suggestions.get('category_columns', []), 
                    "category"
                )
                value_html = self._generate_field_picker_html(
                    self.column_suggestions.get('value_columns', []), 
                    "value"
                )
                
                # Start with the primary analysis message if available
                updated_chatbot = chatbot
                if analysis_message:
                    bot_message = analysis_message['content']
                    updated_chatbot = updated_chatbot + [("CSV File Loaded", bot_message)]
                
                # Add News Analysis as second message
                try:
                    print("[DEBUG] Starting news analysis...")
                    news_results = self.news_analyzer.analyze_data_context(
                        data=self.current_data,
                        column_info=self.csv_loader.column_info
                    )
                    
                    if news_results and isinstance(news_results, dict) and news_results.get('search_queries'):
                        print(f"[DEBUG] News search queries: {news_results.get('search_queries')}")
                        # Display up to 6 news items, 3 per location/query
                        formatted_results = news_results.copy()
                        if len(formatted_results.get('news_items', [])) > 6:
                            formatted_results['news_items'] = formatted_results['news_items'][:6]
                        news_content = self.news_analyzer.format_news_for_chat(formatted_results)
                        updated_chatbot = updated_chatbot + [("Business Context Analysis", news_content)]
                        print(f"[DEBUG] News analysis added to chat")
                    else:
                        print("[DEBUG] No news results found or no location data detected")
                        fallback_news_content = "📰 **BUSINESS CONTEXT ANALYSIS**\n\nNo location data detected in your dataset for relevant business news analysis. Focus on core data metrics instead."
                        updated_chatbot = updated_chatbot + [("Business Context Analysis", fallback_news_content)]
                        
                except Exception as e:
                    print(f"[DEBUG] News analysis error: {str(e)}")
                    # Add error message to chat as well
                    error_content = f"📰 **BUSINESS CONTEXT ANALYSIS**\n\n⚠️ Unable to fetch business context: {str(e)}\n\nContinuing with data analysis..."
                    updated_chatbot = updated_chatbot + [("Business Context Analysis", error_content)]
                
                return preview, data_summary, updated_chatbot, date_html, numeric_html, category_html, value_html
            
            file_input.change(
                fn=handle_file_upload,
                inputs=[file_input, chatbot],
                outputs=[data_preview, data_summary_state, chatbot, date_columns_display, numeric_columns_display, category_columns_display, value_columns_display]
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
                fn=lambda hist: self.chat_response("analyze timescale trends for all periods", hist),
                inputs=[chatbot],
                outputs=[chatbot, chat_input]
            )
            
            summary_btn.click(
                fn=lambda hist: self.chat_response("summary", hist),
                inputs=[chatbot],
                outputs=[chatbot, chat_input]
            )
            
            # Top N / Bottom N button handlers
            top_n_btn.click(
                fn=lambda hist: self.chat_response("show me the top 10 performers", hist),
                inputs=[chatbot],
                outputs=[chatbot, chat_input]
            )
            
            bottom_n_btn.click(
                fn=lambda hist: self.chat_response("show me the bottom 10 performers", hist),
                inputs=[chatbot],
                outputs=[chatbot, chat_input]
            )
            
            top_5_btn.click(
                fn=lambda hist: self.chat_response("show me the top 5 performers", hist),
                inputs=[chatbot],
                outputs=[chatbot, chat_input]
            )
            
            bottom_5_btn.click(
                fn=lambda hist: self.chat_response("show me the bottom 5 performers", hist),
                inputs=[chatbot],
                outputs=[chatbot, chat_input]
            )
        
        return interface

    def _classify_user_intent(self, query: str) -> Optional[str]:
        """Use LLM to classify user intent and route to appropriate analysis"""
        try:
            # Build context about available analysis types based on data
            available_analyses = []
            suggestions = self.column_suggestions
            
            if suggestions.get('category_columns') and suggestions.get('value_columns'):
                available_analyses.append("contribution_analysis")
            
            if suggestions.get('budget_vs_actual'):
                available_analyses.append("variance_analysis")
            
            if self.csv_loader.column_info.get('date_columns'):
                available_analyses.append("trend_analysis")
            
            # Always available
            available_analyses.extend(["data_overview", "general_question"])
            
            # Create intent classification prompt
            intent_prompt = f"""
You are an AI assistant that classifies user queries about financial data analysis.

AVAILABLE ANALYSIS TYPES:
{', '.join(available_analyses)}

USER QUERY: "{query}"

DATASET CONTEXT:
- Rows: {len(self.current_data):,}
- Columns: {list(self.current_data.columns)}
- Available columns: {dict(self.csv_loader.column_info)}

CLASSIFICATION RULES:
1. contribution_analysis: Questions about top performers, pareto analysis, biggest contributors, 80/20 rule, ranking, market share
2. variance_analysis: Questions about budget vs actual, variances, over/under budget, performance vs target
3. trend_analysis: Questions about trends, time series, growth, patterns over time, seasonal analysis, forecasting
4. top_n_analysis: Questions asking for top N, best N, highest N, largest N, most N (e.g., "top 10 products", "best 5 states")
5. bottom_n_analysis: Questions asking for bottom N, worst N, lowest N, smallest N, least N (e.g., "bottom 5 performers", "worst 3 regions")
6. data_overview: Questions asking for summary, overview, description of the data, capabilities, what can be analyzed
7. general_question: All other questions that need contextual answers about the data

RESPOND WITH ONLY ONE WORD - THE CLASSIFICATION TYPE (e.g., "contribution_analysis" or "top_n_analysis")
"""
            
            # Query the LLM for intent classification
            print(f"[DEBUG] Classifying intent for query: {query}")
            ai_response = self.llm_interpreter.query_llm(intent_prompt, {})
            
            if not ai_response.success:
                print(f"[DEBUG] Intent classification failed: {ai_response.error}")
                return None
            
            # Parse the classification result
            classification = ai_response.content.strip().lower()
            print(f"[DEBUG] LLM classified intent as: {classification}")
            
            # Route to appropriate analysis based on classification
            if classification == "contribution_analysis":
                if "contribution_analysis" in available_analyses:
                    print("[DEBUG] Routing to contribution analysis")
                    return self._perform_contribution_analysis(query)
                else:
                    return "⚠️ **Contribution analysis not available** - Missing required category and value columns"
            
            elif classification == "variance_analysis":
                if "variance_analysis" in available_analyses:
                    print("[DEBUG] Routing to variance analysis")
                    return self._perform_variance_analysis(query)
                else:
                    return "⚠️ **Variance analysis not available** - Missing required budget/actual columns"
            
            elif classification == "trend_analysis":
                if "trend_analysis" in available_analyses:
                    print("[DEBUG] Routing to trend analysis")
                    return self._perform_trend_analysis(query)
                else:
                    return "⚠️ **Trend analysis not available** - Missing required date column"
            
            elif classification == "top_n_analysis":
                print("[DEBUG] Routing to top N analysis")
                return self._perform_top_n_analysis(query, is_bottom=False)
            
            elif classification == "bottom_n_analysis":
                print("[DEBUG] Routing to bottom N analysis")
                return self._perform_top_n_analysis(query, is_bottom=True)
            
            elif classification == "data_overview":
                print("[DEBUG] Routing to data overview")
                return self._generate_data_overview()
            
            elif classification == "general_question":
                print("[DEBUG] Routing to general AI response")
                return self._generate_ai_response(query)
            
            else:
                print(f"[DEBUG] Unrecognized classification: {classification}, using general response")
                return self._generate_ai_response(query)
        
        except Exception as e:
            print(f"[DEBUG] Error in intent classification: {str(e)}")
            return None  # Fall back to keyword matching

    def _get_available_analyses(self) -> List[str]:
        """Get list of available analysis types based on current dataset"""
        available = []
        suggestions = self.column_suggestions
        
        if suggestions.get('category_columns') and suggestions.get('value_columns'):
            available.append("Contribution Analysis (80/20 Pareto)")
        
        if suggestions.get('budget_vs_actual'):
            available.append("Variance Analysis (Budget vs Actual)")
        
        if self.csv_loader.column_info.get('date_columns'):
            available.append("Trend Analysis (Time Series & TTM)")
        
        # Top N / Bottom N analysis (always available if we have categorical and numeric data)
        if suggestions.get('category_columns') and (suggestions.get('value_columns') or self.csv_loader.column_info.get('numeric_columns')):
            available.append("Top N / Bottom N Analysis")
        
        # Always available
        available.append("Data Overview & Summary")
        
        return available

    def _perform_top_n_analysis(self, query: str, is_bottom: bool = False) -> str:
        """Perform Top N or Bottom N analysis using LLM to understand parameters"""
        try:
            # Use LLM to extract analysis parameters from the query
            if not self.llm_interpreter.is_available:
                return (
                    "⚠️ **Top/Bottom N Analysis Requires AI**\n\n"
                    "This analysis type requires the AI assistant to understand your query parameters. "
                    "Please ensure Ollama/Gemma3 is running.\n\n"
                    "Alternative: Use specific commands like 'analyze contribution' for similar insights."
                )
            
            # Get available columns for analysis
            suggestions = self.column_suggestions
            category_cols = suggestions.get('category_columns', [])
            value_cols = suggestions.get('value_columns', [])
            numeric_cols = self.csv_loader.column_info.get('numeric_columns', [])
            
            # Create parameter extraction prompt
            direction = "bottom" if is_bottom else "top"
            param_prompt = f"""
You are analyzing a user query to extract parameters for {direction} N analysis on financial data.

USER QUERY: "{query}"

AVAILABLE COLUMNS IN DATASET:
- Category/Grouping columns: {category_cols}
- Value/Numeric columns: {value_cols}
- All numeric columns: {numeric_cols}
- All available columns: {list(self.current_data.columns)}

TASK: Extract these 3 parameters from the user query:

1. N (number): How many items to show (look for numbers like "5", "10", "top 3", etc. Default: 10)
2. GROUP_BY_COLUMN: What to group/rank by (Product, State, Category, etc. - must be from available columns)
3. VALUE_COLUMN: What metric to measure/sort by (Budget, Actual, Sales, Revenue, etc. - must be numeric)

EXTRACTION RULES:
- If user doesn't specify N, use 10
- If user doesn't specify group_by_column, use the first category column: {category_cols[0] if category_cols else 'Product'}
- If user doesn't specify value_column, use the first value column: {value_cols[0] if value_cols else numeric_cols[0] if numeric_cols else 'Actual'}
- Column names must EXACTLY match available columns (case sensitive)

EXAMPLES:
- "top 5 products by sales" → n=5, group_by_column="Product", value_column="Sales"  
- "bottom 10 states" → n=10, group_by_column="State", value_column=<best numeric column>
- "worst performers" → n=10, group_by_column=<best category column>, value_column=<best numeric column>

RESPOND ONLY WITH VALID JSON (no explanation):
{{
    "n": <number>,
    "group_by_column": "<exact_column_name>",
    "value_column": "<exact_column_name>"
}}
"""
            
            # Extract parameters using LLM
            print(f"[DEBUG] Extracting {direction} N parameters from query: '{query}'")
            param_response = self.llm_interpreter.query_llm(param_prompt, {})
            
            if not param_response.success:
                return f"❌ **Parameter Extraction Error**: {param_response.error}"
            
            # **CRITICAL**: Check if the AI response is being accidentally returned as analysis
            raw_response = param_response.content.strip()
            print(f"[DEBUG] AI Parameter Response: {raw_response}")
            
            # Make sure we're not accidentally returning the raw LLM response
            if raw_response.startswith('{') and raw_response.endswith('}'):
                print("[DEBUG] Response looks like pure JSON - proceeding with parameter extraction")
            else:
                print(f"[DEBUG] Response contains more than JSON: {len(raw_response)} chars")
                # If the LLM gave us more than just JSON, extract just the JSON part
                if '{' in raw_response and '}' in raw_response:
                    print("[DEBUG] Found JSON within larger response")
                else:
                    return f"❌ **Invalid Parameter Response**: Expected JSON format but got: {raw_response[:200]}..."
            
            # Parse the JSON response with better error handling
            try:
                import json
                print(f"[DEBUG] Raw LLM response: {param_response.content}")
                
                # Clean up the response (remove any extra text)
                response_text = param_response.content.strip()
                
                # Find JSON content (look for {...})
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}') + 1
                
                if start_idx == -1 or end_idx == 0:
                    raise ValueError("No JSON found in response")
                
                json_text = response_text[start_idx:end_idx]
                print(f"[DEBUG] Extracted JSON: {json_text}")
                
                params = json.loads(json_text)
                
                n = params.get('n', 10)
                group_by_col = params.get('group_by_column')
                value_col = params.get('value_column')
                
                print(f"[DEBUG] Parsed parameters - N: {n}, Group: {group_by_col}, Value: {value_col}")
                
                # Validate and fix parameters
                if not isinstance(n, int) or n <= 0:
                    n = 10
                
                # Validate group_by_column exists
                if not group_by_col or group_by_col not in self.current_data.columns:
                    if category_cols:
                        group_by_col = category_cols[0]
                        print(f"[DEBUG] Using fallback group column: {group_by_col}")
                    else:
                        return "⚠️ **No suitable grouping column found in data**"
                
                # Validate value_column exists and is numeric
                if not value_col or value_col not in self.current_data.columns:
                    if value_cols:
                        value_col = value_cols[0]
                        print(f"[DEBUG] Using fallback value column: {value_col}")
                    elif numeric_cols:
                        value_col = numeric_cols[0]
                        print(f"[DEBUG] Using fallback numeric column: {value_col}")
                    else:
                        return "⚠️ **No suitable numeric column found in data**"
                
                print(f"[DEBUG] Final parameters - N: {n}, Group: {group_by_col}, Value: {value_col}")
                
            except (json.JSONDecodeError, ValueError, KeyError) as e:
                print(f"[DEBUG] JSON parsing failed: {e}")
                print(f"[DEBUG] Raw response was: {param_response.content}")
                
                # Fallback to intelligent defaults
                n = 10
                
                # Extract number from query if possible
                import re
                numbers = re.findall(r'\b(\d+)\b', query)
                if numbers:
                    try:
                        n = int(numbers[0])
                        if n > 100:  # Reasonable limit
                            n = 10
                    except ValueError:
                        n = 10
                
                # Use first available columns as fallback
                group_by_col = category_cols[0] if category_cols else None
                value_col = value_cols[0] if value_cols else (numeric_cols[0] if numeric_cols else None)
                
                if not group_by_col or not value_col:
                    return "⚠️ **Cannot determine analysis parameters** - Please specify columns explicitly"
                
                print(f"[DEBUG] Using fallback parameters - N: {n}, Group: {group_by_col}, Value: {value_col}")
            
            # Validate columns exist
            if not group_by_col or group_by_col not in self.current_data.columns:
                return (
                    f"⚠️ **Invalid Group Column**: '{group_by_col}' not found.\n\n"
                    f"Available columns: {', '.join(self.current_data.columns)}"
                )
            
            if not value_col or value_col not in self.current_data.columns:
                return (
                    f"⚠️ **Invalid Value Column**: '{value_col}' not found.\n\n"
                    f"Available numeric columns: {', '.join(numeric_cols)}"
                )
            
            # Perform the Top/Bottom N analysis
            try:
                # Group by the specified column and aggregate the value column
                if self.current_data[value_col].dtype not in ['int64', 'float64']:
                    return f"⚠️ **Non-numeric Value Column**: '{value_col}' must be numeric for ranking analysis."
                
                # Aggregate data
                grouped = self.current_data.groupby(group_by_col)[value_col].agg(['sum', 'mean', 'count']).reset_index()
                grouped.columns = [group_by_col, f'{value_col}_Total', f'{value_col}_Average', 'Record_Count']
                
                # Sort and get top/bottom N
                ascending = is_bottom  # Bottom N = ascending sort
                sorted_data = grouped.sort_values(f'{value_col}_Total', ascending=ascending).head(n)
                
                # Format results
                direction_text = "Bottom" if is_bottom else "Top"
                results = [
                    f"🎯 **{direction_text} {n} {group_by_col} by {value_col}**",
                    "",
                    f"📊 **Analysis**: {direction_text} {n} analysis of {group_by_col} ranked by {value_col}",
                    "",
                    "📋 **Results:**"
                ]
                
                for idx, row in sorted_data.iterrows():
                    rank = len(sorted_data) - sorted_data.index.get_loc(idx) if is_bottom else sorted_data.index.get_loc(idx) + 1
                    total = f"{row[f'{value_col}_Total']:,.0f}" if pd.notnull(row[f'{value_col}_Total']) else "N/A"
                    avg = f"{row[f'{value_col}_Average']:,.0f}" if pd.notnull(row[f'{value_col}_Average']) else "N/A"
                    count = f"{row['Record_Count']:,}" if pd.notnull(row['Record_Count']) else "N/A"
                    
                    results.append(f"**{rank}. {row[group_by_col]}**")
                    results.append(f"   • Total {value_col}: {total}")
                    results.append(f"   • Average {value_col}: {avg}")
                    results.append(f"   • Records: {count}")
                    results.append("")
                
                # Add summary statistics
                total_sum = sorted_data[f'{value_col}_Total'].sum()
                overall_sum = grouped[f'{value_col}_Total'].sum()
                percentage = (total_sum / overall_sum * 100) if overall_sum > 0 else 0
                
                results.extend([
                    "📈 **Summary:**",
                    f"• {direction_text} {n} {group_by_col} represent {percentage:.1f}% of total {value_col}",
                    f"• Combined {value_col}: {total_sum:,.0f}",
                    f"• Average per {group_by_col}: {total_sum/len(sorted_data):,.0f}"
                ])
                
                # Generate AI insights if available
                if self.llm_interpreter.is_available:
                    context = {
                        'analysis_type': f'{direction}_n_analysis',
                        'parameters': {
                            'n': n,
                            'group_by_column': group_by_col,
                            'value_column': value_col,
                            'direction': direction
                        },
                        'results': sorted_data.to_dict('records'),
                        'summary_stats': {
                            'percentage_of_total': percentage,
                            'combined_value': total_sum,
                            'average_per_item': total_sum/len(sorted_data)
                        }
                    }
                    
                    insight_prompt = f"Provide business insights on this {direction} {n} analysis of {group_by_col} by {value_col}"
                    ai_response = self.llm_interpreter.query_llm(insight_prompt, context)
                    
                    if ai_response.success:
                        ai_insights = self.narrative_generator.format_for_chat(
                            ai_response.content,
                            f"AI Insights - {direction_text} {n} Analysis"
                        )
                        results.extend(["", ai_insights])
                
                return "\n".join(results)
                
            except Exception as e:
                return f"❌ **Analysis Execution Error**: {str(e)}"
                
        except Exception as e:
            return f"❌ **Top/Bottom N Analysis Error**: {str(e)}"

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
