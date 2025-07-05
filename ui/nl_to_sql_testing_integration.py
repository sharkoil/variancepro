"""
NL-to-SQL Testing Integration for VariancePro
Adds testing framework as a new tab in the main application
"""

import gradio as gr
import pandas as pd
import os
from typing import Optional

# Import existing components
from ui.nl_to_sql_testing_ui import NLToSQLTestingUI


def add_testing_tab_to_app(demo_interface, data_file_path: str = None, llm_interpreter=None):
    """
    Add NL-to-SQL testing tab to existing Gradio interface
    
    Args:
        demo_interface: Existing Gradio interface
        data_file_path: Path to CSV data file
        llm_interpreter: LLM interpreter instance
        
    Returns:
        Modified interface with testing tab
    """
    
    # Initialize testing UI
    testing_ui = NLToSQLTestingUI(data_file_path, llm_interpreter)
    
    # Add testing tab to existing interface
    with demo_interface:
        with gr.Tab("🧪 NL-to-SQL Testing") as testing_tab:
            gr.Markdown("""
            # 🧪 **NL-to-SQL Strategy Testing Framework**
            
            **Purpose:** Safely test and compare different NL-to-SQL translation strategies without affecting production queries.
            
            **Available Strategies:**
            - 🔵 **Current Implementation:** Your existing enhanced translator
            - 🟢 **Strategy 1: LLM-Enhanced:** Uses LLM for better intent understanding and systematic WHERE clause building
            - 🟡 **Strategy 2: Semantic Parsing:** Advanced pattern recognition with context learning
            
            Choose a tab below to start testing:
            """)
            
            with gr.Tab("📝 Quick Test"):
                create_quick_test_interface(testing_ui)
            
            with gr.Tab("⚖️ Strategy Comparison"):
                create_comparison_interface(testing_ui)
            
            with gr.Tab("📊 Comprehensive Analysis"):
                create_comprehensive_interface(testing_ui)
            
            with gr.Tab("📋 Data Info"):
                create_data_info_interface(testing_ui)
    
    return demo_interface


def create_quick_test_interface(testing_ui: NLToSQLTestingUI):
    """Create quick test interface"""
    
    gr.Markdown("## 🚀 Quick Single Query Test")
    gr.Markdown("Test any natural language query against all three strategies instantly.")
    
    with gr.Row():
        with gr.Column(scale=1):
            query_input = gr.Textbox(
                label="Enter your natural language query",
                placeholder="e.g., Show me sales where region is North and actual > 15000",
                lines=3,
                info="Try queries with filtering conditions to see the difference!"
            )
            
            test_button = gr.Button("🧪 Test All Strategies", variant="primary", size="lg")
            
            gr.Markdown("### 💡 Try these example queries:")
            
            example_queries = [
                ("🎯 Basic Filter", "Show me sales where region is North"),
                ("📈 Numeric Comparison", "Find records where actual sales > 15000"),
                ("📅 Date Filter", "Get data for Q1 2024"),
                ("🏆 Top N", "Show top 3 regions by sales"),
                ("🔍 Complex Filter", "List products with variance greater than 800"),
                ("📊 Range Query", "Show sales between 12000 and 18000"),
                ("🎪 Multiple Conditions", "Find North region products with sales > 14000")
            ]
            
            for label, query in example_queries:
                example_btn = gr.Button(f"{label}: {query}", size="sm", variant="secondary")
                example_btn.click(lambda q=query: q, outputs=query_input)
        
        with gr.Column(scale=2):
            results_output = gr.HTML(label="Test Results")
    
    test_button.click(
        testing_ui.test_single_query,
        inputs=[query_input],
        outputs=[results_output]
    )


def create_comparison_interface(testing_ui: NLToSQLTestingUI):
    """Create side-by-side comparison interface"""
    
    gr.Markdown("## ⚖️ Detailed Strategy Comparison")
    gr.Markdown("See exactly how each strategy handles your query with detailed breakdown.")
    
    with gr.Row():
        query_input = gr.Textbox(
            label="Query for Detailed Comparison",
            placeholder="Enter your query to see detailed comparison",
            lines=2
        )
        compare_button = gr.Button("⚖️ Compare in Detail", variant="primary")
    
    with gr.Row():
        with gr.Column():
            gr.Markdown("### 🔵 **Current Implementation**")
            with gr.Group():
                current_sql = gr.Code(label="Generated SQL", language="sql", lines=4)
                current_explanation = gr.Textbox(label="Explanation", lines=2)
                current_confidence = gr.Number(label="Confidence Score", precision=2)
        
        with gr.Column():
            gr.Markdown("### 🟢 **Strategy 1: LLM-Enhanced**")
            with gr.Group():
                strategy1_sql = gr.Code(label="Generated SQL", language="sql", lines=4)
                strategy1_explanation = gr.Textbox(label="Explanation", lines=2)
                strategy1_confidence = gr.Number(label="Confidence Score", precision=2)
        
        with gr.Column():
            gr.Markdown("### 🟡 **Strategy 2: Semantic Parsing**")
            with gr.Group():
                strategy2_sql = gr.Code(label="Generated SQL", language="sql", lines=4)
                strategy2_explanation = gr.Textbox(label="Explanation", lines=2)
                strategy2_confidence = gr.Number(label="Confidence Score", precision=2)
    
    with gr.Row():
        recommendations_output = gr.HTML(label="Analysis & Recommendations")
    
    compare_button.click(
        testing_ui.compare_strategies,
        inputs=[query_input],
        outputs=[
            current_sql, current_explanation, current_confidence,
            strategy1_sql, strategy1_explanation, strategy1_confidence,
            strategy2_sql, strategy2_explanation, strategy2_confidence,
            recommendations_output
        ]
    )


def create_comprehensive_interface(testing_ui: NLToSQLTestingUI):
    """Create comprehensive testing interface"""
    
    gr.Markdown("## 📊 Comprehensive Strategy Evaluation")
    gr.Markdown("Run a full test suite to determine which strategy performs best overall.")
    
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("""
            ### 🎯 **What This Test Does:**
            
            - Tests **10 different query types** across all strategies
            - Measures **quality scores** based on:
              - Presence of WHERE clauses
              - Appropriate SELECT statements  
              - Correct aggregations
              - Confidence levels
            - Provides **performance timing**
            - Generates **actionable recommendations**
            
            **Estimated Time:** ~30-60 seconds
            """)
            
            run_button = gr.Button("🚀 Run Full Evaluation", variant="primary", size="lg")
            
            gr.Markdown("""
            ### 📝 **Test Queries Include:**
            - Basic filtering conditions
            - Numeric comparisons  
            - Date/time filtering
            - Top N queries
            - Range queries
            - Complex multi-condition filters
            """)
        
        with gr.Column(scale=2):
            summary_output = gr.HTML(label="Evaluation Summary")
    
    with gr.Row():
        detailed_results_output = gr.Dataframe(
            label="Detailed Results by Query",
            headers=["Query", "Current Score", "Strategy 1 Score", "Strategy 2 Score", "Winner", "Key Issues"],
            wrap=True
        )
    
    run_button.click(
        testing_ui.run_comprehensive_test,
        outputs=[summary_output, detailed_results_output]
    )


def create_data_info_interface(testing_ui: NLToSQLTestingUI):
    """Create data information interface"""
    
    gr.Markdown("## 📋 Data Context & Schema Information")
    gr.Markdown("Understanding your data structure helps interpret the testing results.")
    
    if testing_ui.current_data is not None:
        with gr.Row():
            gr.Markdown(f"""
            ### 📊 **Dataset Overview**
            - **Rows:** {testing_ui.current_data.shape[0]:,}
            - **Columns:** {testing_ui.current_data.shape[1]}
            - **Data Type:** Financial/Sales Data
            """)
        
        with gr.Row():
            with gr.Column():
                data_preview = gr.Dataframe(
                    value=testing_ui.current_data.head(10),
                    label="Data Preview (First 10 rows)",
                    wrap=True
                )
            
            with gr.Column():
                schema_info = testing_ui._get_schema_info_display()
                gr.HTML(schema_info, label="Schema Details")
        
        with gr.Row():
            stats_info = testing_ui._get_data_stats_display()
            gr.HTML(stats_info, label="Statistical Summary")
    
    else:
        gr.Markdown("⚠️ **No data loaded.** The testing framework will use sample data.")


def integrate_testing_with_existing_app():
    """
    Integration function to add testing framework to your existing app
    Call this from your main app.py file
    """
    
    # Determine data file path
    data_file_paths = [
        "sample_variance_data.csv",
        "sample_data/sample_variance_data.csv",
        "sample_data/comprehensive_sales_data.csv"
    ]
    
    data_file_path = None
    for path in data_file_paths:
        if os.path.exists(path):
            data_file_path = path
            break
    
    return data_file_path


# Example integration code for your main app
def add_testing_to_main_app(existing_interface, llm_interpreter=None):
    """
    Example function showing how to integrate testing into your main app
    
    Usage in your app.py:
    ```python
    from ui.nl_to_sql_testing_integration import add_testing_to_main_app
    
    # After creating your main interface
    demo = add_testing_to_main_app(demo, llm_interpreter)
    ```
    """
    
    # Find data file
    data_file_path = integrate_testing_with_existing_app()
    
    # Add testing functionality
    enhanced_interface = add_testing_tab_to_app(
        existing_interface, 
        data_file_path, 
        llm_interpreter
    )
    
    return enhanced_interface
