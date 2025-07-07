"""
SQL Insight UI - Interactive Interface for AI-Powered SQL Analysis
Provides field picker, query builder, and comprehensive insight display
"""

import gradio as gr
import pandas as pd
import json
from typing import List, Dict, Any, Optional, Tuple
from analyzers.sql_insight_engine import SQLInsightEngine

class SQLInsightUI:
    """
    Interactive UI for SQL Insight Engine with field picker and AI analysis
    
    Features:
    1. Visual field picker with AI-inferred types
    2. SQL query editor with syntax highlighting
    3. Real-time query results display
    4. AI-powered insights generation
    5. Query template management
    """
    
    def __init__(self):
        """Initialize the SQL Insight UI"""
        self.engine = SQLInsightEngine()
        self.current_dataset = None
        self.field_picker_data = []
        print("🎨 SQL Insight UI initialized")
    
    def create_interface(self) -> gr.Interface:
        """
        Create the complete Gradio interface for SQL insights
        
        Returns:
            Configured Gradio interface
        """
        with gr.Blocks(
            title="SQL Insight Engine - AI-Powered Query Analysis",
            theme=gr.themes.Soft()
        ) as interface:
            
            gr.Markdown("""
            # 🧠 SQL Insight Engine
            ### AI-Powered Query Analysis with Smart Field Detection
            
            Upload your CSV data, explore fields with AI-powered type detection, 
            write SQL queries, and get comprehensive AI insights!
            """)
            
            with gr.Row():
                with gr.Column(scale=2):
                    # File upload section
                    gr.Markdown("## 📁 Data Upload")
                    file_upload = gr.File(
                        label="Upload CSV File",
                        file_types=[".csv"],
                        type="filepath"
                    )
                    
                    upload_status = gr.Textbox(
                        label="Upload Status",
                        value="Ready to upload CSV file...",
                        interactive=False
                    )
                
                with gr.Column(scale=1):
                    # Dataset info
                    gr.Markdown("## 📊 Dataset Info")
                    dataset_info = gr.JSON(
                        label="Dataset Summary",
                        value={}
                    )
            
            # Field picker section
            gr.Markdown("## 🎯 Smart Field Picker")
            gr.Markdown("*Fields automatically analyzed with AI-powered type detection*")
            
            with gr.Row():
                field_picker = gr.Dataframe(
                    headers=["Field Name", "AI Type", "Description", "Sample Values"],
                    datatype=["str", "str", "str", "str"],
                    label="Available Fields (AI-Analyzed)",
                    interactive=False,
                    max_rows=10
                )
            
            # Query section
            gr.Markdown("## ✍️ SQL Query Builder")
            
            with gr.Row():
                with gr.Column(scale=2):
                    query_input = gr.Code(
                        label="SQL Query",
                        language="sql",
                        placeholder="SELECT * FROM dataset LIMIT 10",
                        lines=8
                    )
                    
                    with gr.Row():
                        execute_btn = gr.Button("🚀 Execute Query", variant="primary")
                        execute_with_insights_btn = gr.Button("🧠 Execute + AI Insights", variant="secondary")
                        clear_btn = gr.Button("🗑️ Clear", variant="stop")
                
                with gr.Column(scale=1):
                    gr.Markdown("### 💡 Smart Suggestions")
                    suggestions_display = gr.HTML(value="Upload data to see query suggestions")
                    
                    gr.Markdown("### 🔄 Quick Actions")
                    load_suggestion_btn = gr.Button("📋 Load Suggestion")
                    save_template_btn = gr.Button("💾 Save as Template")
            
            # Results section
            gr.Markdown("## 📊 Query Results")
            
            with gr.Tabs():
                with gr.TabItem("🔍 Data Results"):
                    results_display = gr.Dataframe(
                        label="Query Results",
                        interactive=False,
                        max_rows=20
                    )
                    
                    results_info = gr.Textbox(
                        label="Execution Info",
                        value="No query executed yet",
                        interactive=False
                    )
                
                with gr.TabItem("🧠 AI Insights"):
                    insights_display = gr.Markdown(
                        value="Execute a query with AI insights to see analysis here...",
                        label="AI-Generated Insights"
                    )
                    
                    insights_status = gr.Textbox(
                        label="Insights Status",
                        value="Ready for analysis",
                        interactive=False
                    )
            
            # Query management section
            with gr.Accordion("📚 Query Templates & History", open=False):
                with gr.Tabs():
                    with gr.TabItem("💾 Saved Templates"):
                        templates_display = gr.Dataframe(
                            headers=["Name", "Query", "Created"],
                            label="Saved Query Templates"
                        )
                        
                        with gr.Row():
                            template_name = gr.Textbox(label="Template Name", placeholder="My Analysis Query")
                            template_desc = gr.Textbox(label="Description", placeholder="Optional description")
                    
                    with gr.TabItem("📝 Query History"):
                        history_display = gr.Dataframe(
                            headers=["Time", "Query", "Status", "Rows"],
                            label="Query Execution History"
                        )
            
            # Event handlers
            file_upload.change(
                fn=self.handle_file_upload,
                inputs=[file_upload],
                outputs=[upload_status, dataset_info, field_picker, suggestions_display]
            )
            
            execute_btn.click(
                fn=self.execute_query,
                inputs=[query_input],
                outputs=[results_display, results_info, history_display]
            )
            
            execute_with_insights_btn.click(
                fn=self.execute_query_with_insights,
                inputs=[query_input],
                outputs=[results_display, results_info, insights_display, insights_status, history_display]
            )
            
            clear_btn.click(
                fn=lambda: ("", "", "Ready for next query"),
                outputs=[query_input, results_info, insights_status]
            )
            
            save_template_btn.click(
                fn=self.save_query_template,
                inputs=[query_input, template_name, template_desc],
                outputs=[templates_display, template_name, template_desc]
            )
            
            # Load initial data
            interface.load(
                fn=self.initialize_interface,
                outputs=[suggestions_display, history_display, templates_display]
            )
        
        return interface
    
    def handle_file_upload(self, file_path: str) -> Tuple[str, Dict, List[List], str]:
        """
        Handle CSV file upload with AI-powered field analysis
        
        Args:
            file_path: Path to uploaded CSV file
            
        Returns:
            Tuple of (status, dataset_info, field_picker_data, suggestions_html)
        """
        if not file_path:
            return "No file selected", {}, [], "Upload data to see suggestions"
        
        try:
            # Load the CSV file
            df = pd.read_csv(file_path)
            self.current_dataset = df
            
            # Analyze with AI
            dataset_info = self.engine.load_dataset(df, "dataset")
            
            if dataset_info["status"] == "success":
                # Prepare field picker data
                field_data = []
                for field in dataset_info["field_picker_data"]:
                    field_data.append([
                        field["name"],
                        field["type"],
                        field["description"],
                        ", ".join(str(v) for v in field["sample_values"][:3])
                    ])
                
                self.field_picker_data = field_data
                
                # Generate suggestions HTML
                suggestions_html = self._generate_suggestions_html()
                
                status = f"✅ Dataset loaded successfully! {dataset_info['row_count']} rows, {dataset_info['column_count']} columns analyzed with AI."
                
                return status, dataset_info, field_data, suggestions_html
            
            else:
                return f"❌ Error: {dataset_info['message']}", {}, [], "Upload error"
                
        except Exception as e:
            return f"❌ Failed to load file: {str(e)}", {}, [], "Upload error"
    
    def execute_query(self, query: str) -> Tuple[pd.DataFrame, str, List[List]]:
        """
        Execute SQL query without insights
        
        Args:
            query: SQL query to execute
            
        Returns:
            Tuple of (results_df, info_text, history_data)
        """
        if not query.strip():
            return pd.DataFrame(), "Please enter a SQL query", self._get_history_data()
        
        if self.current_dataset is None:
            return pd.DataFrame(), "Please upload a CSV file first", self._get_history_data()
        
        # Execute query
        result = self.engine.execute_sql_query(query, generate_insights=False)
        
        if result["status"] == "success":
            results_df = pd.DataFrame(result["data"])
            info_text = f"✅ Query executed successfully! {result['row_count']} rows returned."
            
            return results_df, info_text, self._get_history_data()
        else:
            return pd.DataFrame(), f"❌ Query failed: {result['message']}", self._get_history_data()
    
    def execute_query_with_insights(self, query: str) -> Tuple[pd.DataFrame, str, str, str, List[List]]:
        """
        Execute SQL query with AI insights generation
        
        Args:
            query: SQL query to execute
            
        Returns:
            Tuple of (results_df, info_text, insights_markdown, insights_status, history_data)
        """
        if not query.strip():
            return pd.DataFrame(), "Please enter a SQL query", "No insights available", "Query required", self._get_history_data()
        
        if self.current_dataset is None:
            return pd.DataFrame(), "Please upload a CSV file first", "No insights available", "Data required", self._get_history_data()
        
        # Execute query with insights
        result = self.engine.execute_sql_query(query, generate_insights=True)
        
        if result["status"] == "success":
            results_df = pd.DataFrame(result["data"])
            info_text = f"✅ Query executed successfully! {result['row_count']} rows returned."
            
            # Process insights
            if "insights" in result and result["insights"]["status"] == "success":
                insights_markdown = self._format_insights_for_display(result["insights"]["insights_text"])
                insights_status = "✅ AI insights generated successfully"
            elif "insights" in result and result["insights"]["status"] == "fallback":
                insights_markdown = self._format_insights_for_display(result["insights"]["insights_text"])
                insights_status = "⚠️ Using statistical analysis (AI unavailable)"
            else:
                insights_markdown = "❌ Failed to generate insights"
                insights_status = "Insights generation failed"
            
            return results_df, info_text, insights_markdown, insights_status, self._get_history_data()
        else:
            return pd.DataFrame(), f"❌ Query failed: {result['message']}", "No insights available", "Query failed", self._get_history_data()
    
    def save_query_template(self, query: str, name: str, description: str) -> Tuple[List[List], str, str]:
        """
        Save query as a template
        
        Args:
            query: SQL query to save
            name: Template name
            description: Template description
            
        Returns:
            Tuple of (templates_data, cleared_name, cleared_description)
        """
        if not query.strip() or not name.strip():
            return self._get_templates_data(), name, description
        
        result = self.engine.save_query_template(name, query, description)
        
        if result["status"] == "success":
            return self._get_templates_data(), "", ""  # Clear inputs on success
        else:
            return self._get_templates_data(), name, description  # Keep inputs on failure
    
    def initialize_interface(self) -> Tuple[str, List[List], List[List]]:
        """
        Initialize interface with default data
        
        Returns:
            Tuple of (suggestions_html, history_data, templates_data)
        """
        suggestions_html = "Upload a CSV file to see smart query suggestions"
        history_data = self._get_history_data()
        templates_data = self._get_templates_data()
        
        return suggestions_html, history_data, templates_data
    
    def _generate_suggestions_html(self) -> str:
        """
        Generate HTML for query suggestions
        
        Returns:
            HTML string with suggestions
        """
        suggestions = self.engine.get_query_suggestions()
        
        if not suggestions:
            return "No suggestions available"
        
        html_parts = ["<div style='font-family: Arial, sans-serif;'>"]
        
        for suggestion in suggestions[:5]:  # Show top 5 suggestions
            html_parts.append(f"""
            <div style='margin: 10px 0; padding: 10px; border: 1px solid #ddd; border-radius: 5px; background: #f9f9f9;'>
                <strong>{suggestion['title']}</strong>
                <p style='margin: 5px 0; color: #666; font-size: 0.9em;'>{suggestion['description']}</p>
                <code style='background: #e9e9e9; padding: 2px 5px; border-radius: 3px; font-size: 0.8em;'>{suggestion['query']}</code>
            </div>
            """)
        
        html_parts.append("</div>")
        
        return "".join(html_parts)
    
    def _format_insights_for_display(self, insights_text: str) -> str:
        """
        Format insights text for Markdown display
        
        Args:
            insights_text: Raw insights text from LLM
            
        Returns:
            Formatted markdown text
        """
        if not insights_text:
            return "No insights available"
        
        # Add some basic formatting if not already present
        formatted_text = insights_text
        
        # Ensure proper markdown formatting
        if not formatted_text.startswith("#"):
            formatted_text = "## 🧠 AI Analysis Results\n\n" + formatted_text
        
        return formatted_text
    
    def _get_history_data(self) -> List[List]:
        """
        Get query history data for display
        
        Returns:
            List of history records
        """
        history = self.engine.get_query_history()
        
        history_data = []
        for record in history[-10:]:  # Last 10 queries
            timestamp = record.get("timestamp", "")[:19]  # Truncate timestamp
            query = record.get("query", "")[:50] + "..." if len(record.get("query", "")) > 50 else record.get("query", "")
            status = "✅ Success" if record.get("status") == "success" else "❌ Error"
            rows = str(record.get("row_count", record.get("error", "N/A")))
            
            history_data.append([timestamp, query, status, rows])
        
        return history_data
    
    def _get_templates_data(self) -> List[List]:
        """
        Get saved templates data for display
        
        Returns:
            List of template records
        """
        templates = self.engine.get_saved_templates()
        
        templates_data = []
        for template in templates:
            name = template.get("name", "Unnamed")
            query = template.get("query", "")[:50] + "..." if len(template.get("query", "")) > 50 else template.get("query", "")
            created = template.get("created_at", "")[:10]  # Date only
            
            templates_data.append([name, query, created])
        
        return templates_data

def create_sql_insight_interface() -> gr.Interface:
    """
    Create and return the SQL Insight interface
    
    Returns:
        Configured Gradio interface
    """
    ui = SQLInsightUI()
    return ui.create_interface()

if __name__ == "__main__":
    # Create and launch the interface
    interface = create_sql_insight_interface()
    interface.launch(
        server_name="0.0.0.0",
        server_port=7875,
        share=False,
        debug=True
    )
