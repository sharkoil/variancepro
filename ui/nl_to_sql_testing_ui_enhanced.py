"""
Enhanced UI Testing Framework for NL-to-SQL Strategy Comparison
Provides a safe testing interface to compare different strategies with model selection
"""

import gradio as gr
import pandas as pd
from typing import Dict, List, Any, Optional
import json
import time
from datetime import datetime
import traceback
import requests

# Import the testing framework and strategies
from analyzers.nl_to_sql_tester import NLToSQLTester, NLToSQLStrategy
from analyzers.enhanced_nl_to_sql_translator import EnhancedNLToSQLTranslator
from analyzers.strategy_1_llm_enhanced import LLMEnhancedNLToSQL
from analyzers.strategy_2_semantic_parsing import SemanticNLToSQL
from ai.llm_interpreter import LLMInterpreter
from config.settings import Settings


def get_available_ollama_models() -> List[str]:
    """
    Fetch available models from Ollama
    
    Returns:
        List of available model names
    """
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models_data = response.json()
            model_names = [model['name'] for model in models_data.get('models', [])]
            return sorted(model_names)
        else:
            return ["gemma3:latest"]  # Fallback default
    except Exception as e:
        print(f"Error fetching Ollama models: {e}")
        return ["gemma3:latest"]  # Fallback default


class EnhancedNLToSQLTestingUI:
    """
    Enhanced UI interface for testing and comparing NL-to-SQL strategies
    Allows safe evaluation without affecting production queries
    Includes model selection capabilities
    """
    
    def __init__(self, data_file_path: str = None, settings: Settings = None):
        """
        Initialize the enhanced testing UI
        
        Args:
            data_file_path: Path to CSV data file for testing
            settings: Application settings object
        """
        self.data_file_path = data_file_path
        self.settings = settings if settings else Settings()
        self.llm_interpreter = LLMInterpreter(self.settings)
        self.current_data = None
        self.tester = None
        
        # Initialize strategies
        self.current_translator = None
        self.strategy_1_translator = None
        self.strategy_2_translator = None
        
        # Test history
        self.test_history = []
        
        # Available models
        self.available_models = get_available_ollama_models()
        self.current_model = self.settings.llm_model
        
        # Initialize with sample data if no file provided
        if not data_file_path:
            self._load_sample_data()
        else:
            self._load_data_file(data_file_path)
    
    def _load_sample_data(self):
        """Load sample financial data for testing"""
        sample_data = {
            'Region': ['North', 'South', 'East', 'West', 'North', 'South', 'East', 'West'],
            'Product': ['Widget A', 'Widget B', 'Widget A', 'Widget B', 'Widget C', 'Widget A', 'Widget B', 'Widget C'],
            'Sales_Actual': [15000, 12000, 18000, 14000, 16000, 13000, 17000, 15500],
            'Sales_Budget': [14000, 11000, 17000, 13500, 15000, 12500, 16000, 14500],
            'Variance': [1000, 1000, 1000, 500, 1000, 500, 1000, 1000],
            'Quarter': ['Q1', 'Q1', 'Q1', 'Q1', 'Q2', 'Q2', 'Q2', 'Q2'],
            'Year': [2024, 2024, 2024, 2024, 2024, 2024, 2024, 2024]
        }
        
        self.current_data = pd.DataFrame(sample_data)
        self._initialize_testing_framework()
    
    def _load_data_file(self, file_path: str):
        """Load data from CSV file"""
        try:
            self.current_data = pd.read_csv(file_path)
            self._initialize_testing_framework()
        except Exception as e:
            print(f"Error loading data file: {e}")
            self._load_sample_data()
    
    def _initialize_testing_framework(self, model_name: Optional[str] = None):
        """Initialize the testing framework with current data"""
        if self.current_data is not None:
            # Update model if provided
            if model_name:
                self.current_model = model_name
                self.settings.llm_model = model_name
                self.llm_interpreter = LLMInterpreter(self.settings)

            # Initialize translators
            self.current_translator = EnhancedNLToSQLTranslator()
            self.strategy_1_translator = LLMEnhancedNLToSQL(self.llm_interpreter)
            self.strategy_2_translator = SemanticNLToSQL()
            
            # Initialize tester
            self.tester = NLToSQLTester(self.current_data, self.llm_interpreter)
            self.tester.initialize_strategies(
                self.current_translator,
                self.strategy_1_translator,
                self.strategy_2_translator
            )
    
    def create_testing_interface(self) -> gr.Blocks:
        """
        Create the Gradio interface for testing
        
        Returns:
            Gradio Blocks interface
        """
        # Custom CSS to fix color scheme and improve readability
        custom_css = """
        /* Global light theme override */
        body, .gradio-container, .app, .main-wrap {
            color: #000000 !important;
            background-color: #ffffff !important;
        }
        
        /* All input elements */
        .gr-textbox, .gr-dropdown, .gr-button, .gr-html, .gr-markdown, 
        .gr-textbox input, .gr-dropdown select, input, textarea, select {
            color: #000000 !important;
            background-color: #ffffff !important;
            border: 1px solid #ddd !important;
        }
        
        /* Buttons */
        .gr-button {
            background-color: #f8f9fa !important;
            border: 1px solid #dee2e6 !important;
            color: #000000 !important;
        }
        
        .gr-button:hover {
            background-color: #e9ecef !important;
            color: #000000 !important;
        }
        
        .gr-button.primary {
            background-color: #007bff !important;
            border-color: #007bff !important;
            color: #ffffff !important;
        }
        
        .gr-button.primary:hover {
            background-color: #0056b3 !important;
            border-color: #0056b3 !important;
            color: #ffffff !important;
        }
        
        /* HTML content and markdown */
        .gr-html, .gr-html *, .gr-markdown, .gr-markdown * {
            color: #000000 !important;
            background-color: transparent !important;
        }
        
        /* Tabs */
        .gr-tab-nav {
            background-color: #f8f9fa !important;
            border-bottom: 1px solid #dee2e6 !important;
        }
        
        .gr-tab-nav .gr-tab {
            color: #000000 !important;
            background-color: #ffffff !important;
            border: 1px solid #dee2e6 !important;
        }
        
        .gr-tab-nav .gr-tab.selected {
            background-color: #007bff !important;
            color: #ffffff !important;
        }
        
        /* Panels and containers */
        .gr-panel, .gr-form, .gr-box {
            background-color: #ffffff !important;
            border: 1px solid #dee2e6 !important;
        }
        
        /* Dropdown options */
        .gr-dropdown .choices__list {
            background-color: #ffffff !important;
            color: #000000 !important;
        }
        
        .gr-dropdown .choices__item {
            color: #000000 !important;
            background-color: #ffffff !important;
        }
        
        .gr-dropdown .choices__item--highlighted {
            background-color: #007bff !important;
            color: #ffffff !important;
        }
        
        /* Text areas and inputs */
        .gr-textbox textarea, .gr-textbox input {
            background-color: #ffffff !important;
            color: #000000 !important;
            border: 1px solid #ced4da !important;
        }
        
        .gr-textbox textarea:focus, .gr-textbox input:focus {
            border-color: #007bff !important;
            box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25) !important;
        }
        
        /* Labels */
        .gr-form label, .gr-textbox label, .gr-dropdown label, .gr-button label {
            color: #000000 !important;
            font-weight: 500 !important;
        }
        
        /* Success/Error messages styling */
        .success-message {
            color: #155724 !important;
            background-color: #d4edda !important;
            border: 1px solid #c3e6cb !important;
            padding: 10px !important;
            border-radius: 4px !important;
            margin: 10px 0 !important;
        }
        
        .error-message {
            color: #721c24 !important;
            background-color: #f8d7da !important;
            border: 1px solid #f5c6cb !important;
            padding: 10px !important;
            border-radius: 4px !important;
            margin: 10px 0 !important;
        }
        
        .info-message {
            color: #004085 !important;
            background-color: #cce7ff !important;
            border: 1px solid #80c7ff !important;
            padding: 10px !important;
            border-radius: 4px !important;
            margin: 10px 0 !important;
        }
        
        /* Fix for any remaining dark elements */
        * {
            color: inherit !important;
        }
        
        /* Force light theme on all child elements */
        .dark, .dark *, [data-theme="dark"], [data-theme="dark"] * {
            color: #000000 !important;
            background-color: #ffffff !important;
        }
        """
        
        with gr.Blocks(
            title="Enhanced NL-to-SQL Strategy Testing", 
            theme=gr.themes.Soft(
                primary_hue="blue",
                secondary_hue="gray",
                neutral_hue="gray"
            ), 
            css=custom_css
        ) as interface:
            gr.Markdown("# 🧪 **Enhanced NL-to-SQL Strategy Testing Framework**")
            gr.Markdown("Test and compare different strategies for natural language to SQL translation with model selection")
            
            # Model selection at the top
            with gr.Row():
                model_dropdown = gr.Dropdown(
                    label="🤖 Select LLM Model",
                    choices=self.available_models,
                    value=self.current_model,
                    interactive=True,
                    scale=3
                )
                
                apply_button = gr.Button("🔄 Apply Model", variant="secondary", scale=1)
                refresh_button = gr.Button("🔄 Refresh Models", variant="secondary", scale=1)
            
            status_output = gr.HTML()
            
            with gr.Tab("📊 Single Query Test"):
                self._create_single_query_tab()
            
            with gr.Tab("🏆 Strategy Comparison"):
                self._create_comparison_tab()
            
            with gr.Tab("📈 Comprehensive Testing"):
                self._create_comprehensive_tab()
            
            with gr.Tab("📋 Data Preview"):
                self._create_data_preview_tab()
            
            # Wire up model selection
            apply_button.click(
                self.update_model,
                inputs=[model_dropdown],
                outputs=[status_output]
            )
            
            refresh_button.click(
                self.refresh_models,
                outputs=[model_dropdown, status_output]
            )
        
        return interface
    
    def update_model(self, model_name: str) -> str:
        """
        Update LLM model and re-initialize framework
        
        Args:
            model_name: The new model name to use
            
        Returns:
            Status message
        """
        try:
            self._initialize_testing_framework(model_name=model_name)
            
            # Verify connection with new model
            if self.llm_interpreter.refresh_connection():
                return f"<div style='color: #28a745; background-color: #d4edda; border: 1px solid #c3e6cb; padding: 10px; border-radius: 4px;'>✅ Model '{model_name}' applied successfully and is active.</div>"
            else:
                return f"<div style='color: #dc3545; background-color: #f8d7da; border: 1px solid #f5c6cb; padding: 10px; border-radius: 4px;'>⚠️ Model '{model_name}' selected, but could not connect. Error: {self.llm_interpreter.last_error}</div>"

        except Exception as e:
            error_msg = f"Error applying model: {str(e)}"
            print(f"Full error: {traceback.format_exc()}")
            return f"<div style='color: #dc3545; background-color: #f8d7da; border: 1px solid #f5c6cb; padding: 10px; border-radius: 4px;'>{error_msg}</div>"
    
    def refresh_models(self) -> tuple:
        """
        Refresh the list of available models
        
        Returns:
            Tuple of (updated_dropdown_choices, status_message)
        """
        try:
            self.available_models = get_available_ollama_models()
            status_msg = f"<div style='color: #007bff; background-color: #cce7ff; border: 1px solid #80c7ff; padding: 10px; border-radius: 4px;'>🔄 Refreshed models. Found {len(self.available_models)} available models.</div>"
            return gr.Dropdown.update(choices=self.available_models), status_msg
        except Exception as e:
            error_msg = f"Error refreshing models: {str(e)}"
            status_msg = f"<div style='color: #dc3545; background-color: #f8d7da; border: 1px solid #f5c6cb; padding: 10px; border-radius: 4px;'>{error_msg}</div>"
            return gr.Dropdown.update(choices=self.available_models), status_msg
    
    def _create_single_query_tab(self):
        """Create the single query testing tab"""
        gr.Markdown("## Test a Single Query Against All Strategies")
        
        with gr.Row():
            with gr.Column(scale=2):
                query_input = gr.Textbox(
                    label="Natural Language Query",
                    placeholder="e.g., Show me sales where region is North",
                    lines=2
                )
                
                test_button = gr.Button("🧪 Test Query", variant="primary")
                
                # Quick test queries
                gr.Markdown("### Quick Test Queries:")
                quick_queries = [
                    "Show me sales where region is North",
                    "Find records where actual sales > 15000",
                    "Get data for Q1 2024",
                    "Show top 3 regions by sales",
                    "List products with variance greater than 800"
                ]
                
                for i, query in enumerate(quick_queries):
                    quick_button = gr.Button(f"📋 {query}", size="sm")
                    quick_button.click(
                        lambda q=query: q,
                        outputs=query_input
                    )
        
        with gr.Column(scale=3):
            results_display = gr.HTML(label="Test Results")
        
        test_button.click(
            self.test_single_query,
            inputs=[query_input],
            outputs=[results_display]
        )
    
    def _create_comparison_tab(self):
        """Create the strategy comparison tab"""
        gr.Markdown("## Side-by-Side Strategy Comparison")
        
        with gr.Row():
            query_input = gr.Textbox(
                label="Query to Compare",
                placeholder="Enter your natural language query",
                lines=2
            )
            compare_button = gr.Button("⚖️ Compare Strategies", variant="primary")
        
        with gr.Row():
            with gr.Column():
                gr.Markdown("### 🔵 Current Implementation")
                current_sql = gr.Code(label="Generated SQL", language="sql")
                current_explanation = gr.Textbox(label="Explanation", lines=3)
                current_confidence = gr.Number(label="Confidence Score")
            
            with gr.Column():
                gr.Markdown("### 🟢 Strategy 1: LLM-Enhanced")
                strategy1_sql = gr.Code(label="Generated SQL", language="sql")
                strategy1_explanation = gr.Textbox(label="Explanation", lines=3)
                strategy1_confidence = gr.Number(label="Confidence Score")
            
            with gr.Column():
                gr.Markdown("### 🟡 Strategy 2: Semantic Parsing")
                strategy2_sql = gr.Code(label="Generated SQL", language="sql")
                strategy2_explanation = gr.Textbox(label="Explanation", lines=3)
                strategy2_confidence = gr.Number(label="Confidence Score")
        
        with gr.Row():
            recommendations = gr.HTML(label="Recommendations")
        
        compare_button.click(
            self.compare_strategies,
            inputs=[query_input],
            outputs=[
                current_sql, current_explanation, current_confidence,
                strategy1_sql, strategy1_explanation, strategy1_confidence,
                strategy2_sql, strategy2_explanation, strategy2_confidence,
                recommendations
            ]
        )
    
    def _create_comprehensive_tab(self):
        """Create the comprehensive testing tab"""
        gr.Markdown("## Comprehensive Strategy Evaluation")
        
        with gr.Row():
            run_comprehensive_button = gr.Button("🚀 Run Comprehensive Test", variant="primary", size="lg")
            
        with gr.Row():
            comprehensive_results = gr.HTML(label="Comprehensive Test Results")
        
        with gr.Row():
            detailed_results = gr.Dataframe(
                label="Detailed Results",
                headers=["Query", "Current Score", "Strategy 1 Score", "Strategy 2 Score", "Winner", "Recommendations"]
            )
        
        run_comprehensive_button.click(
            self.run_comprehensive_test,
            outputs=[comprehensive_results, detailed_results]
        )
    
    def _create_data_preview_tab(self):
        """Create the data preview tab"""
        gr.Markdown("## Data Preview and Schema Information")
        
        if self.current_data is not None:
            with gr.Row():
                gr.Markdown(f"**Data Shape:** {self.current_data.shape[0]} rows × {self.current_data.shape[1]} columns")
            
            with gr.Row():
                data_preview = gr.Dataframe(
                    value=self.current_data.head(10),
                    label="Data Preview (First 10 rows)"
                )
            
            with gr.Row():
                with gr.Column():
                    schema_info = self._get_schema_info_display()
                    gr.HTML(schema_info, label="Schema Information")
                
                with gr.Column():
                    stats_info = self._get_data_stats_display()
                    gr.HTML(stats_info, label="Data Statistics")
    
    def test_single_query(self, query: str) -> str:
        """
        Test a single query against all strategies
        
        Args:
            query: Natural language query
            
        Returns:
            HTML formatted results
        """
        if not query or not self.tester:
            return "<div style='color: #dc3545; background-color: #f8d7da; border: 1px solid #f5c6cb; padding: 10px; border-radius: 4px;'>Please enter a query and ensure data is loaded.</div>"
        
        try:
            result = self.tester.test_single_query(query)
            
            # Add to history
            self.test_history.append({
                'timestamp': datetime.now().isoformat(),
                'query': query,
                'result': result,
                'model': self.current_model
            })
            
            return self._format_single_query_results(result)
            
        except Exception as e:
            error_msg = f"Error testing query: {str(e)}"
            print(f"Full error: {traceback.format_exc()}")
            return f"<div style='color: #dc3545; background-color: #f8d7da; border: 1px solid #f5c6cb; padding: 10px; border-radius: 4px;'>{error_msg}</div>"
    
    def compare_strategies(self, query: str) -> tuple:
        """
        Compare all strategies for a single query
        
        Args:
            query: Natural language query
            
        Returns:
            Tuple of results for each strategy
        """
        if not query or not self.tester:
            empty_result = ("", "", 0.0)
            return empty_result * 3 + ("Error: Please enter a query",)
        
        try:
            result = self.tester.test_single_query(query)
            
            recommendations_html = self._format_recommendations(result.recommendations, result.quality_scores)
            
            return (
                result.current_sql, result.current_explanation, result.current_confidence,
                result.strategy_1_sql, result.strategy_1_explanation, result.strategy_1_confidence,
                result.strategy_2_sql, result.strategy_2_explanation, result.strategy_2_confidence,
                recommendations_html
            )
            
        except Exception as e:
            error_msg = f"Error comparing strategies: {str(e)}"
            empty_result = ("", "", 0.0)
            return empty_result * 3 + (f"<div style='color: #dc3545; background-color: #f8d7da; border: 1px solid #f5c6cb; padding: 10px; border-radius: 4px;'>{error_msg}</div>",)
    
    def run_comprehensive_test(self) -> tuple:
        """
        Run comprehensive test across all test queries
        
        Returns:
            Tuple of (summary_html, detailed_dataframe)
        """
        if not self.tester:
            return "<div style='color: #dc3545; background-color: #f8d7da; border: 1px solid #f5c6cb; padding: 10px; border-radius: 4px;'>Testing framework not initialized</div>", []
        
        try:
            results = self.tester.run_comprehensive_test()
            
            summary_html = self._format_comprehensive_summary(results)
            detailed_df = self._format_detailed_results(results['all_results'])
            
            return summary_html, detailed_df
            
        except Exception as e:
            error_msg = f"Error running comprehensive test: {str(e)}"
            return f"<div style='color: #dc3545; background-color: #f8d7da; border: 1px solid #f5c6cb; padding: 10px; border-radius: 4px;'>{error_msg}</div>", []
    
    def _format_single_query_results(self, result) -> str:
        """Format single query results as HTML"""
        html = f"""
        <div style="padding: 20px; font-family: Arial, sans-serif; color: #000000; background-color: #ffffff;">
            <h3 style="color: #000000;">🧪 Test Results for: "{result.query}"</h3>
            <p style="color: #666; font-size: 0.9em; margin-bottom: 20px;">Using model: <strong>{self.current_model}</strong></p>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; margin: 20px 0;">
                <div style="border: 2px solid #007bff; border-radius: 8px; padding: 15px; background: #f8f9fa; color: #000000;">
                    <h4 style="color: #007bff; margin-top: 0;">🔵 Current Implementation</h4>
                    <p style="color: #000000;"><strong>SQL:</strong></p>
                    <code style="background: #e9ecef; padding: 10px; display: block; border-radius: 4px; white-space: pre-wrap; color: #000000;">{result.current_sql}</code>
                    <p style="color: #000000;"><strong>Explanation:</strong> {result.current_explanation}</p>
                    <p style="color: #000000;"><strong>Confidence:</strong> {result.current_confidence:.2f}</p>
                    <p style="color: #000000;"><strong>Quality Score:</strong> {result.quality_scores['current']:.1f}/100</p>
                </div>
                
                <div style="border: 2px solid #28a745; border-radius: 8px; padding: 15px; background: #f8f9fa; color: #000000;">
                    <h4 style="color: #28a745; margin-top: 0;">🟢 Strategy 1: LLM-Enhanced</h4>
                    <p style="color: #000000;"><strong>SQL:</strong></p>
                    <code style="background: #e9ecef; padding: 10px; display: block; border-radius: 4px; white-space: pre-wrap; color: #000000;">{result.strategy_1_sql}</code>
                    <p style="color: #000000;"><strong>Explanation:</strong> {result.strategy_1_explanation}</p>
                    <p style="color: #000000;"><strong>Confidence:</strong> {result.strategy_1_confidence:.2f}</p>
                    <p style="color: #000000;"><strong>Quality Score:</strong> {result.quality_scores['strategy_1']:.1f}/100</p>
                </div>
                
                <div style="border: 2px solid #ffc107; border-radius: 8px; padding: 15px; background: #f8f9fa; color: #000000;">
                    <h4 style="color: #ffc107; margin-top: 0;">🟡 Strategy 2: Semantic Parsing</h4>
                    <p style="color: #000000;"><strong>SQL:</strong></p>
                    <code style="background: #e9ecef; padding: 10px; display: block; border-radius: 4px; white-space: pre-wrap; color: #000000;">{result.strategy_2_sql}</code>
                    <p style="color: #000000;"><strong>Explanation:</strong> {result.strategy_2_explanation}</p>
                    <p style="color: #000000;"><strong>Confidence:</strong> {result.strategy_2_confidence:.2f}</p>
                    <p style="color: #000000;"><strong>Quality Score:</strong> {result.quality_scores['strategy_2']:.1f}/100</p>
                </div>
            </div>
            
            <div style="margin-top: 20px; padding: 15px; background: #e7f3ff; border-radius: 8px; border-left: 4px solid #007bff; color: #000000;">
                <h4 style="margin-top: 0; color: #000000;">💡 Recommendations</h4>
                <ul style="color: #000000;">
                    {"".join(f"<li style='color: #000000;'>{rec}</li>" for rec in result.recommendations)}
                </ul>
            </div>
            
            <div style="margin-top: 15px; font-size: 0.9em; color: #000000;">
                <strong>Execution Times:</strong> 
                Current: {result.execution_times['current']:.3f}s | 
                Strategy 1: {result.execution_times['strategy_1']:.3f}s | 
                Strategy 2: {result.execution_times['strategy_2']:.3f}s
            </div>
        </div>
        """
        return html
    
    def _format_recommendations(self, recommendations: List[str], quality_scores: Dict[str, float]) -> str:
        """Format recommendations as HTML"""
        best_strategy = max(quality_scores.items(), key=lambda x: x[1])
        
        html = f"""
        <div style="padding: 15px; background: #f8f9fa; border-radius: 8px; border: 1px solid #dee2e6; color: #000000;">
            <h4 style="margin-top: 0; color: #000000;">💡 Analysis & Recommendations</h4>
            <p style="color: #666; font-size: 0.9em; margin-bottom: 15px;">Using model: <strong>{self.current_model}</strong></p>
            
            <div style="margin-bottom: 15px; color: #000000;">
                <strong>🏆 Best Performing Strategy:</strong> 
                <span style="color: #28a745; font-weight: bold;">
                    {best_strategy[0].replace('_', ' ').title()} (Score: {best_strategy[1]:.1f}/100)
                </span>
            </div>
            
            <div style="margin-bottom: 15px; color: #000000;">
                <strong>📊 Quality Scores:</strong><br>
                <div style="margin-left: 20px; color: #000000;">
                    Current: {quality_scores['current']:.1f}/100<br>
                    Strategy 1: {quality_scores['strategy_1']:.1f}/100<br>
                    Strategy 2: {quality_scores['strategy_2']:.1f}/100
                </div>
            </div>
            
            {"<div style='color: #000000;'><strong>🔍 Specific Recommendations:</strong><ul style='color: #000000;'>" + "".join(f"<li style='color: #000000;'>{rec}</li>" for rec in recommendations) + "</ul></div>" if recommendations else ""}
        </div>
        """
        return html
    
    def _format_comprehensive_summary(self, results: Dict[str, Any]) -> str:
        """Format comprehensive test summary as HTML"""
        total_queries = results['total_queries']
        strategy_wins = results['strategy_wins']
        avg_scores = results['average_scores']
        avg_times = results['average_times']
        
        # Determine overall winner
        overall_winner = max(strategy_wins.items(), key=lambda x: x[1])
        
        html = f"""
        <div style="padding: 20px; font-family: Arial, sans-serif; color: #000000; background-color: #ffffff;">
            <h2 style="color: #007bff; margin-bottom: 20px;">🏆 Comprehensive Strategy Evaluation Results</h2>
            <p style="color: #666; font-size: 0.9em; margin-bottom: 20px;">Using model: <strong>{self.current_model}</strong></p>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #ffffff; padding: 20px; border-radius: 10px;">
                    <h3 style="margin-top: 0; color: #ffffff;">📊 Overall Performance</h3>
                    <p style="color: #ffffff;"><strong>Total Queries Tested:</strong> {total_queries}</p>
                    <p style="color: #ffffff;"><strong>Overall Winner:</strong> {overall_winner[0].replace('_', ' ').title()}</p>
                    <p style="color: #ffffff;"><strong>Wins:</strong> {overall_winner[1]}/{total_queries}</p>
                </div>
                
                <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: #ffffff; padding: 20px; border-radius: 10px;">
                    <h3 style="margin-top: 0; color: #ffffff;">⚡ Performance Metrics</h3>
                    <p style="color: #ffffff;"><strong>Avg Current Score:</strong> {avg_scores['current']:.1f}/100</p>
                    <p style="color: #ffffff;"><strong>Avg Strategy 1 Score:</strong> {avg_scores['strategy_1']:.1f}/100</p>
                    <p style="color: #ffffff;"><strong>Avg Strategy 2 Score:</strong> {avg_scores['strategy_2']:.1f}/100</p>
                </div>
            </div>
            
            <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; border: 1px solid #dee2e6; color: #000000;">
                <h3 style="margin-top: 0; color: #000000;">📈 Detailed Breakdown</h3>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px; margin-bottom: 15px;">
                    <div style="text-align: center; padding: 15px; background: white; border-radius: 8px; border: 1px solid #007bff; color: #000000;">
                        <h4 style="color: #007bff; margin: 0;">🔵 Current</h4>
                        <p style="margin: 5px 0; color: #000000;"><strong>Wins:</strong> {strategy_wins['current']}</p>
                        <p style="margin: 5px 0; color: #000000;"><strong>Avg Score:</strong> {avg_scores['current']:.1f}</p>
                        <p style="margin: 5px 0; color: #000000;"><strong>Avg Time:</strong> {avg_times['current']:.3f}s</p>
                    </div>
                    
                    <div style="text-align: center; padding: 15px; background: white; border-radius: 8px; border: 1px solid #28a745; color: #000000;">
                        <h4 style="color: #28a745; margin: 0;">🟢 Strategy 1</h4>
                        <p style="margin: 5px 0; color: #000000;"><strong>Wins:</strong> {strategy_wins['strategy_1']}</p>
                        <p style="margin: 5px 0; color: #000000;"><strong>Avg Score:</strong> {avg_scores['strategy_1']:.1f}</p>
                        <p style="margin: 5px 0; color: #000000;"><strong>Avg Time:</strong> {avg_times['strategy_1']:.3f}s</p>
                    </div>
                    
                    <div style="text-align: center; padding: 15px; background: white; border-radius: 8px; border: 1px solid #ffc107; color: #000000;">
                        <h4 style="color: #ffc107; margin: 0;">🟡 Strategy 2</h4>
                        <p style="margin: 5px 0; color: #000000;"><strong>Wins:</strong> {strategy_wins['strategy_2']}</p>
                        <p style="margin: 5px 0; color: #000000;"><strong>Avg Score:</strong> {avg_scores['strategy_2']:.1f}</p>
                        <p style="margin: 5px 0; color: #000000;"><strong>Avg Time:</strong> {avg_times['strategy_2']:.3f}s</p>
                    </div>
                </div>
                
                <div style="margin-top: 20px; padding: 15px; background: #e7f3ff; border-radius: 8px; border-left: 4px solid #007bff; color: #000000;">
                    <h4 style="margin-top: 0; color: #000000;">💡 Key Insights</h4>
                    <ul style="color: #000000;">
                        <li style="color: #000000;"><strong>Performance Leader:</strong> {overall_winner[0].replace('_', ' ').title()} wins {overall_winner[1]} out of {total_queries} tests</li>
                        <li style="color: #000000;"><strong>Quality Improvement:</strong> {"Strategy 1" if avg_scores['strategy_1'] > avg_scores['current'] else "Strategy 2" if avg_scores['strategy_2'] > avg_scores['current'] else "Current"} shows highest average quality score</li>
                        <li style="color: #000000;"><strong>Speed Champion:</strong> {"Current" if avg_times['current'] < min(avg_times['strategy_1'], avg_times['strategy_2']) else "Strategy 1" if avg_times['strategy_1'] < avg_times['strategy_2'] else "Strategy 2"} is fastest on average</li>
                    </ul>
                </div>
            </div>
        </div>
        """
        return html
    
    def _format_detailed_results(self, all_results: List) -> List[List]:
        """Format detailed results for dataframe display"""
        detailed_data = []
        
        for result in all_results:
            # Determine winner
            scores = result.quality_scores
            winner = max(scores.items(), key=lambda x: x[1])[0].replace('_', ' ').title()
            
            # Format recommendations
            rec_summary = "; ".join(result.recommendations[:2]) if result.recommendations else "No specific recommendations"
            if len(rec_summary) > 100:
                rec_summary = rec_summary[:97] + "..."
            
            detailed_data.append([
                result.query,
                f"{scores['current']:.1f}",
                f"{scores['strategy_1']:.1f}",
                f"{scores['strategy_2']:.1f}",
                winner,
                rec_summary
            ])
        
        return detailed_data
    
    def _get_schema_info_display(self) -> str:
        """Get schema information as HTML"""
        if self.current_data is None:
            return "<p style='color: #000000;'>No data loaded</p>"
        
        columns_info = []
        for col in self.current_data.columns:
            dtype = str(self.current_data[col].dtype)
            null_count = self.current_data[col].isnull().sum()
            unique_count = self.current_data[col].nunique()
            
            columns_info.append(f"<tr><td style='color: #000000;'><strong>{col}</strong></td><td style='color: #000000;'>{dtype}</td><td style='color: #000000;'>{unique_count}</td><td style='color: #000000;'>{null_count}</td></tr>")
        
        html = f"""
        <div style="font-family: Arial, sans-serif; color: #000000;">
            <h4 style="color: #000000;">📋 Schema Information</h4>
            <table style="width: 100%; border-collapse: collapse; border: 1px solid #ddd; color: #000000;">
                <thead>
                    <tr style="background-color: #f2f2f2;">
                        <th style="border: 1px solid #ddd; padding: 8px; color: #000000;">Column</th>
                        <th style="border: 1px solid #ddd; padding: 8px; color: #000000;">Type</th>
                        <th style="border: 1px solid #ddd; padding: 8px; color: #000000;">Unique Values</th>
                        <th style="border: 1px solid #ddd; padding: 8px; color: #000000;">Null Count</th>
                    </tr>
                </thead>
                <tbody>
                    {"".join(columns_info)}
                </tbody>
            </table>
        </div>
        """
        return html
    
    def _get_data_stats_display(self) -> str:
        """Get data statistics as HTML"""
        if self.current_data is None:
            return "<p style='color: #000000;'>No data loaded</p>"
        
        numeric_cols = self.current_data.select_dtypes(include=['number']).columns
        stats_info = []
        
        for col in numeric_cols:
            stats = self.current_data[col].describe()
            stats_info.append(f"""
            <div style="margin-bottom: 15px; padding: 10px; border: 1px solid #ddd; border-radius: 5px; color: #000000;">
                <h5 style="margin-top: 0; color: #000000;">{col}</h5>
                <p style="color: #000000;"><strong>Mean:</strong> {stats['mean']:.2f} | <strong>Std:</strong> {stats['std']:.2f}</p>
                <p style="color: #000000;"><strong>Min:</strong> {stats['min']:.2f} | <strong>Max:</strong> {stats['max']:.2f}</p>
            </div>
            """)
        
        html = f"""
        <div style="font-family: Arial, sans-serif; color: #000000;">
            <h4 style="color: #000000;">📊 Numeric Column Statistics</h4>
            {"".join(stats_info) if stats_info else "<p style='color: #000000;'>No numeric columns found</p>"}
        </div>
        """
        return html
