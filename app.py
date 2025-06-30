#!/usr/bin/env python3
"""
VariancePro Financial Analysis App - FIXED VERSION WITH ONLY 2 TABS
"""

import gradio as gr
import pandas as pd
import numpy as np
import io
import json
import requests
from datetime import datetime
from typing import List, Dict, Optional

class SimpleFinancialChat:
    """Simplified financial data analysis chat"""
    
    def __init__(self):
        self.current_data = None
        self.chat_history = []
        
        # Initialize timescale analyzer
        self.timescale_analyzer = TimescaleAnalyzer()
    
    def get_default_suggested_questions(self):
        """Get default suggested questions when no data is loaded"""
        return """### 💡 Suggested Questions

**Getting Started:**
- "How can I analyze financial variances?"
- "What metrics can I track for financial performance?"
- "How to identify trends in financial data?"

**Code Assistance:**
- "Generate dashboard code for financial data"
- "Help me build a forecasting model"

📁 Upload your CSV file to get personalized suggestions based on your data columns!"""

    def get_default_system_prompt(self):
        """Get the default system prompt for the chat"""
        prompt = """I am VariancePro, your financial analysis assistant. 

I can help you analyze your financial data, identify trends, calculate metrics, and provide insights. 

Upload your financial data (CSV file) and I'll assist you with:
- Variance analysis and trend identification
- Period-over-period comparisons
- Statistical analysis and financial metrics
- Python code for detailed analysis

How can I help with your financial data today?"""
        return prompt
    
    def generate_automatic_timescale_analysis(self, df: pd.DataFrame) -> str:
        """Generate automatic timescale analysis when data is loaded"""
        if df is None or df.empty:
            return "No data available for timescale analysis. Please upload financial data."
        
        try:
            # Use the timescale analyzer to generate insights
            analysis_text = self.timescale_analyzer.generate_timescale_analysis(df)
            
            # Add footer with guidance
            footer = """
---

*This analysis was automatically generated based on the time patterns in your data. For more specific insights, ask detailed questions about trends, variances, or period-over-period comparisons.*"""
            return analysis_text + footer
        except Exception as e:
            import traceback
            error_msg = f"Error generating automatic timescale analysis: {str(e)}"
            print(f"Debug: {error_msg}")
            traceback.print_exc()
            return f"""# ⚠️ Automatic Analysis Error

We encountered an issue while analyzing your time series data: {str(e)}

Please try:
1. Ensuring your data contains at least one date/time column
2. Having sufficient data points for meaningful period-over-period analysis
3. Checking that your date format is consistent and can be parsed

If issues persist, you can still explore your data manually or ask specific questions."""
    
    def process_query(self, file, question, history):
        """Process a user query about financial data"""
        try:
            # Load data if provided
            if file and not self.current_data:
                try:
                    df = pd.read_csv(file)
                    self.current_data = df
                except Exception as e:
                    new_history = (history or []) + [
                        {"role": "user", "content": question},
                        {"role": "assistant", "content": f"Error loading file: {str(e)}"}
                    ]
                    return new_history, [], "Error loading file", None
            
            # Simple response for testing
            response = f"You asked: {question}\n\nThis is a simplified test response. In the real app, we would analyze your data and provide insights."
            
            # Update history
            new_history = (history or []) + [
                {"role": "user", "content": question},
                {"role": "assistant", "content": response}
            ]
            
            return new_history, new_history, "Data processed successfully", self.current_data
            
        except Exception as e:
            import traceback
            error_msg = f"Error: {str(e)}\n{traceback.format_exc()}"
            new_history = (history or []) + [
                {"role": "user", "content": question},
                {"role": "assistant", "content": f"Error: {str(e)}"}
            ]
            return new_history, [], error_msg, None

def load_data_for_grid(file_path):
    """Load data for the data grid view"""
    if file_path is None:
        return None
    
    try:
        df = pd.read_csv(file_path)
        return df
    except Exception as e:
        print(f"Error loading file: {str(e)}")
        return None

def check_system_status():
    """Check system status"""
    return "✅ System is ready. You can upload financial data and start asking questions."

def create_interface():
    """Create the Gradio interface"""
    
    # Initialize chat system
    global chat_system
    chat_system = SimpleFinancialChat()
    
    def process_query(file, question, chat_state):
        """Process a query using the chat system"""
        history = chat_state if chat_state else []
        new_history, new_chat_state, status, current_data = chat_system.process_query(file, question, history)
        return new_history, new_chat_state, status, current_data
    
    with gr.Blocks(
        title="VariancePro - Financial Chat",
        theme=gr.themes.Soft(),
        css="""
        .container { max-width: 1200px; margin: auto; }
        .status-box { background: #f0f8ff; padding: 10px; border-radius: 5px; margin: 10px 0; }
        .chat-container { height: 400px; overflow-y: auto; }
        .data-grid { max-height: 500px; overflow: auto; }
        """
    ) as interface:
        
        gr.Markdown("# 🚀 VariancePro - Financial Data Analysis")
        gr.Markdown("### FIXED VERSION WITH ONLY 2 TABS")
        
        # Create tabs for different views - ONLY 2 TABS
        with gr.Tabs():
            # Chat Analysis Tab
            with gr.TabItem("💬 Chat Analysis"):
                with gr.Row():
                    with gr.Column(scale=2):
                        # File upload
                        file_input = gr.File(
                            label="📁 Upload Financial Data (CSV)",
                            file_types=[".csv"],
                            type="filepath",
                            file_count="single"
                        )
                        
                        # Chat interface
                        chatbot = gr.Chatbot(
                            label="💬 Financial Analysis Chat",
                            height=400,
                            show_label=True,
                            type="messages"
                        )
                        
                        # User input
                        user_input = gr.Textbox(
                            label="Ask about your financial data:",
                            placeholder="e.g., 'Analyze sales variance by region'",
                            lines=2
                        )
                        
                        # Buttons
                        with gr.Row():
                            submit_btn = gr.Button("🔍 Analyze", variant="primary")
                            clear_btn = gr.Button("🗑️ Clear Chat")
                    
                    with gr.Column(scale=1):
                        # Status panel
                        status_display = gr.Textbox(
                            label="🤖 System Status",
                            value=check_system_status(),
                            interactive=False,
                            lines=2
                        )
                        
                        # Suggested questions
                        suggested_questions = gr.Markdown(
                            value=chat_system.get_default_suggested_questions(),
                            label="💡 Suggested Questions"
                        )
            
            # Data Grid Tab
            with gr.TabItem("📊 Data View"):
                with gr.Row():
                    with gr.Column(scale=1):
                        # Data info panel
                        data_info = gr.Textbox(
                            label="📋 Dataset Information",
                            value="No data loaded yet. Please upload a CSV file in the Chat Analysis tab.",
                            interactive=False,
                            lines=3
                        )
                        
                        # Data grid
                        data_grid = gr.DataFrame(
                            label="📈 Data Grid",
                            interactive=False,
                            wrap=True,
                            elem_classes=["data-grid"]
                        )
                    
                    with gr.Column(scale=1):
                        # Automatic timescale analysis
                        gr.Markdown("### 🚀 Automatic Timescale Analysis")
                        gr.Markdown("*Comprehensive period-over-period analysis generated automatically*")
                        
                        auto_analysis_display = gr.Markdown(
                            label="📈 Automatic Analysis",
                            value="Please upload data to see automatic analysis.",
                            elem_classes=["analysis-display"]
                        )
        
        # State for chat history and data
        chat_state = gr.State([])
        
        # Event handlers
        def submit_query(file, question, history, chat_state):
            new_history, new_chat_state, status, current_data = process_query(file, question, chat_state)
            
            # Update data info and grid
            if current_data is not None:
                info_text = f"""📊 Dataset Loaded: {len(current_data)} rows × {len(current_data.columns)} columns
                
🔢 Numeric Columns: {len(current_data.select_dtypes(include=[np.number]).columns)}
📝 Text Columns: {len(current_data.select_dtypes(include=['object']).columns)}
📅 Date Columns: {len(current_data.select_dtypes(include=['datetime64']).columns)}"""
                return new_history, "", new_chat_state, status, info_text, current_data
            else:
                return new_history, "", new_chat_state, status, data_info.value, None
        
        def update_data_view(file):
            """Update data view when file is uploaded - includes automatic timescale analysis"""
            if file is None:
                return "No data loaded yet. Please upload a CSV file.", None, "Please upload data to see automatic analysis."
            
            df = load_data_for_grid(file)
            if df is not None:
                # Basic data info
                info_text = f"""📊 Dataset Loaded: {len(df)} rows × {len(df.columns)} columns
                
🔢 Numeric Columns: {len(df.select_dtypes(include=[np.number]).columns)}
📝 Text Columns: {len(df.select_dtypes(include=['object']).columns)}
📅 Date Columns: {len(df.select_dtypes(include=['datetime64']).columns)}

💾 Memory Usage: {df.memory_usage(deep=True).sum() / 1024:.1f} KB

📋 Column Names: {', '.join(df.columns.tolist())}"""
                
                # Generate automatic timescale analysis
                print("🚀 Generating automatic timescale analysis...")
                auto_analysis = chat_system.generate_automatic_timescale_analysis(df)
                
                return info_text, df, auto_analysis
            else:
                return "Error loading data. Please check the file format.", None, "Unable to generate analysis due to data loading error."
                return "Error loading data. Please check the file format.", None
        
        def clear_chat_history():
            """Clear chat history"""
            return [], []
        
        def initialize_chat_with_system_message(file):
            """Initialize the chat with a system message when a file is uploaded"""
            if file is None:
                return [], []
                
            try:
                df = load_data_for_grid(file)
                if df is None:
                    return [], []
                    
                # Generate initial system message
                system_message = chat_system.generate_initial_system_message(df)
                
                # Return the chat history with just the system message
                initial_chat = [system_message]
                
                return initial_chat, initial_chat
            except Exception as e:
                print(f"Error initializing chat: {str(e)}")
                return [], []
        
        # Connect event handlers
        submit_btn.click(
            submit_query,
            inputs=[file_input, user_input, chatbot, chat_state],
            outputs=[chatbot, user_input, chat_state, status_display, data_info, data_grid]
        )
        
        clear_btn.click(
            clear_chat_history,
            inputs=[],
            outputs=[chatbot, chat_state]
        )
        
        file_input.change(
            update_data_view,
            inputs=[file_input],
            outputs=[data_info, data_grid, auto_analysis_display]
        )
        
        # Add event to initialize chat with system message
        file_input.change(
            initialize_chat_with_system_message,
            inputs=[file_input],
            outputs=[chatbot, chat_state]
        )
        
        file_input.upload(
            initialize_chat_with_system_message,
            inputs=[file_input],
            outputs=[chatbot, chat_state]
        )
    
    return interface

class TimescaleAnalyzer:
    """Automatic timescale analysis for financial data - mimics junior analyst work"""
    
    def __init__(self):
        self.analysis_cache = {}
    
    def detect_time_granularity(self, df: pd.DataFrame, date_col: str) -> str:
        """Detect the granularity of time series data"""
        if date_col not in df.columns:
            return "unknown"
        
        # Convert to datetime if needed
        dates = pd.to_datetime(df[date_col]).sort_values()
        
        # Calculate differences between consecutive dates
        diffs = dates.diff().dropna()
        mode_diff = diffs.mode().iloc[0] if len(diffs) > 0 else pd.Timedelta(days=1)
        
        # Determine granularity
        if mode_diff <= pd.Timedelta(hours=1):
            return "hourly"
        elif mode_diff <= pd.Timedelta(days=1):
            return "daily"
        elif mode_diff <= pd.Timedelta(days=7):
            return "weekly"
        elif mode_diff <= pd.Timedelta(days=31):
            return "monthly"
        elif mode_diff <= pd.Timedelta(days=92):
            return "quarterly"
        else:
            return "yearly"
    
    def prepare_timescale_aggregations(self, df: pd.DataFrame, date_col: str, value_cols: List[str]) -> Dict:
        """Pre-compute aggregations at different time scales"""
        if date_col not in df.columns:
            return {}
        
        # Ensure date column is datetime
        df = df.copy()
        df[date_col] = pd.to_datetime(df[date_col])
        
        # Sort by date
        df = df.sort_values(by=date_col)
        
        # Initialize aggregations dictionary
        aggregations = {
            "weekly": {},
            "monthly": {},
            "quarterly": {},
            "yearly": {}
        }
        
        # Filter only numeric columns if value_cols not specified
        if not value_cols:
            value_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            # Remove date column if it's somehow in the numeric columns
            if date_col in value_cols:
                value_cols.remove(date_col)
        
        # Weekly aggregation
        df['week'] = df[date_col].dt.to_period('W').astype(str)
        weekly = df.groupby('week')[value_cols].sum().reset_index()
        aggregations["weekly"]["data"] = weekly
        aggregations["weekly"]["periods"] = weekly['week'].tolist()
        
        # Monthly aggregation
        df['month'] = df[date_col].dt.to_period('M').astype(str)
        monthly = df.groupby('month')[value_cols].sum().reset_index()
        aggregations["monthly"]["data"] = monthly
        aggregations["monthly"]["periods"] = monthly['month'].tolist()
        
        # Quarterly aggregation
        df['quarter'] = df[date_col].dt.to_period('Q').astype(str)
        quarterly = df.groupby('quarter')[value_cols].sum().reset_index()
        aggregations["quarterly"]["data"] = quarterly
        aggregations["quarterly"]["periods"] = quarterly['quarter'].tolist()
        
        # Yearly aggregation
        df['year'] = df[date_col].dt.to_period('Y').astype(str)
        yearly = df.groupby('year')[value_cols].sum().reset_index()
        aggregations["yearly"]["data"] = yearly
        aggregations["yearly"]["periods"] = yearly['year'].tolist()
        
        return aggregations
    
    def calculate_period_over_period_analysis(self, aggregations: Dict, value_cols: List[str]) -> Dict:
        """Calculate period-over-period metrics for different time scales"""
        result = {
            "weekly": {},
            "monthly": {},
            "quarterly": {},
            "yearly": {}
        }
        
        # Process each time scale
        for time_scale in ["weekly", "monthly", "quarterly", "yearly"]:
            if time_scale not in aggregations or "data" not in aggregations[time_scale]:
                continue
                
            data = aggregations[time_scale]["data"]
            time_col = data.columns[0]  # First column is the time period
            
            # Calculate period-over-period metrics for each value column
            for value_col in value_cols:
                if value_col not in data.columns:
                    continue
                
                # Calculate absolute and percentage changes
                data[f'{value_col}_prev'] = data[value_col].shift(1)
                data[f'{value_col}_abs_change'] = data[value_col] - data[f'{value_col}_prev']
                data[f'{value_col}_pct_change'] = (data[value_col] / data[f'{value_col}_prev'] - 1) * 100
                
                # Calculate summary statistics
                total_periods = len(data)
                positive_changes = sum(data[f'{value_col}_abs_change'] > 0)
                negative_changes = sum(data[f'{value_col}_abs_change'] < 0)
                
                # Store results
                result[time_scale][value_col] = {
                    "periods": data[time_col].tolist(),
                    "values": data[value_col].tolist(),
                    "abs_changes": data[f'{value_col}_abs_change'].tolist(),
                    "pct_changes": data[f'{value_col}_pct_change'].tolist(),
                    "summary": {
                        "total_periods": total_periods,
                        "positive_periods": positive_changes,
                        "negative_periods": negative_changes,
                        "avg_pct_change": data[f'{value_col}_pct_change'].mean(),
                        "max_pct_change": data[f'{value_col}_pct_change'].max(),
                        "min_pct_change": data[f'{value_col}_pct_change'].min(),
                        "latest_value": data[value_col].iloc[-1] if total_periods > 0 else None,
                        "latest_change": data[f'{value_col}_pct_change'].iloc[-1] if total_periods > 0 else None
                    }
                }
        
        return result
    
    def _generate_summary_insights(self, pop_analysis: Dict) -> str:
        """Generate natural language insights from the period-over-period analysis"""
        insights = []
        
        # Add header
        insights.append("# 📊 Automatic Timescale Analysis")
        insights.append("*Analysis generated based on time series patterns in your data*\n")
        
        # Process each time scale
        for time_scale in ["yearly", "quarterly", "monthly", "weekly"]:
            if time_scale not in pop_analysis or not pop_analysis[time_scale]:
                continue
                
            # Add section header
            header_map = {
                "yearly": "## 📅 Year-over-Year (YoY) Analysis",
                "quarterly": "## 📊 Quarter-over-Quarter (QoQ) Analysis",
                "monthly": "## 📆 Month-over-Month (MoM) Analysis",
                "weekly": "## 📈 Week-over-Week (WoW) Analysis"
            }
            insights.append(header_map[time_scale])
            
            # Process each metric
            for metric, data in pop_analysis[time_scale].items():
                summary = data["summary"]
                periods = data["periods"]
                
                # Only process if we have enough data
                if summary["total_periods"] < 2:
                    insights.append(f"*Insufficient {time_scale} data for {metric} analysis*\n")
                    continue
                
                # Add metric header
                insights.append(f"### {metric.replace('_', ' ').title()}")
                
                # Latest period change
                latest_period = periods[-1]
                latest_change = summary["latest_change"]
                if pd.notna(latest_change):
                    change_direction = "increased" if latest_change > 0 else "decreased"
                    insights.append(f"- **Latest {time_scale} ({latest_period})**: {change_direction} by {abs(latest_change):.2f}%")
                
                # Overall trend
                trend_ratio = summary["positive_periods"] / summary["total_periods"]
                if trend_ratio > 0.6:
                    trend = "mostly increasing"
                elif trend_ratio < 0.4:
                    trend = "mostly decreasing"
                else:
                    trend = "fluctuating"
                
                insights.append(f"- **Overall trend**: {trend} over {summary['total_periods']} periods")
                
                # Extreme periods
                if summary["max_pct_change"] > 0:
                    max_idx = data["pct_changes"].index(summary["max_pct_change"])
                    max_period = periods[max_idx]
                    insights.append(f"- **Largest increase**: {summary['max_pct_change']:.2f}% in {max_period}")
                
                if summary["min_pct_change"] < 0:
                    min_idx = data["pct_changes"].index(summary["min_pct_change"])
                    min_period = periods[min_idx]
                    insights.append(f"- **Largest decrease**: {summary['min_pct_change']:.2f}% in {min_period}")
                
                # Average change
                insights.append(f"- **Average change**: {summary['avg_pct_change']:.2f}% per {time_scale[:-2]}")
                
                # Add spacer
                insights.append("")
        
        # Executive summary
        insights.append("## 📋 Executive Summary")
        insights.append("*Key takeaways from the automatic time series analysis:*\n")
        
        # Extract key metrics from different time scales for the executive summary
        exec_points = []
        
        # Check for notable yearly trends
        if "yearly" in pop_analysis and pop_analysis["yearly"]:
            for metric, data in pop_analysis["yearly"].items():
                summary = data["summary"]
                if summary["total_periods"] >= 2:
                    latest_change = summary["latest_change"]
                    if pd.notna(latest_change) and abs(latest_change) > 10:
                        direction = "growth" if latest_change > 0 else "decline"
                        exec_points.append(f"**Annual {direction}**: {metric.replace('_', ' ').title()} shows {abs(latest_change):.1f}% YoY {direction}")
        
        # Check for quarterly acceleration/deceleration
        if "quarterly" in pop_analysis and pop_analysis["quarterly"]:
            for metric, data in pop_analysis["quarterly"].items():
                if len(data["pct_changes"]) >= 3:
                    # Get last 3 changes
                    recent_changes = [c for c in data["pct_changes"][-3:] if pd.notna(c)]
                    if len(recent_changes) >= 2:
                        if all(c > 0 for c in recent_changes) and recent_changes[-1] > recent_changes[0]:
                            exec_points.append(f"**Accelerating growth**: {metric.replace('_', ' ').title()} shows increasing QoQ growth rates")
                        elif all(c < 0 for c in recent_changes) and recent_changes[-1] < recent_changes[0]:
                            exec_points.append(f"**Deepening decline**: {metric.replace('_', ' ').title()} shows worsening QoQ decline")
        
        # Add executive points
        if exec_points:
            insights.extend(exec_points)
        else:
            insights.append("- Insufficient time series data for executive insights")
        
        # Return the formatted insights
        return "\n".join(insights)
    
    def generate_timescale_analysis(self, df: pd.DataFrame) -> str:
        """Generate comprehensive timescale analysis for the given dataframe"""
        # Find date column using our helper method
        date_col = self.find_date_column(df)
        
        if not date_col:
            return "No date column found in the data. Cannot perform timescale analysis."
        
        # Convert the date column to datetime
        df = df.copy()
        try:
            df[date_col] = pd.to_datetime(df[date_col])
        except Exception as e:
            return f"Error converting {date_col} to datetime: {str(e)}"
        
        # Detect granularity
        granularity = self.detect_time_granularity(df, date_col)
        
        # Get numeric columns for analysis
        value_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if date_col in value_cols:
            value_cols.remove(date_col)
        
        # Prepare aggregations
        aggregations = self.prepare_timescale_aggregations(df, date_col, value_cols)
        
        # Calculate period-over-period analysis
        pop_analysis = self.calculate_period_over_period_analysis(aggregations, value_cols)
        
        # Generate insights
        insights = self._generate_summary_insights(pop_analysis)
        
        return insights

    def find_date_column(self, df: pd.DataFrame) -> Optional[str]:
        """Find a date column in the dataframe with enhanced detection logic"""
        # Create a case-insensitive mapping of column names
        col_lower_map = {col.lower(): col for col in df.columns}
        
        # First, check common date column names case-insensitively
        common_date_cols = ['date', 'time', 'period_end', 'period', 'timestamp']
        for date_col in common_date_cols:
            if date_col in col_lower_map:
                return col_lower_map[date_col]
        
        # Next, look for columns that are already datetime
        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                return col
        
        # Look for columns with date-related names (case-insensitive)
        date_related_keywords = ['date', 'time', 'period', 'year', 'month', 'day', 'quarter', 'fiscal']
        for col in df.columns:
            col_lower = col.lower()
            if any(keyword in col_lower for keyword in date_related_keywords):
                try:
                    # Try to convert to datetime
                    sample = df[col].dropna().head(5)
                    if not sample.empty:
                        # Special handling for quarter notation like "Q1 2023"
                        if any('q' in str(x).lower() for x in sample):
                            return col
                        
                        # Try to convert
                        test_conversion = pd.to_datetime(sample, errors='coerce')
                        if not test_conversion.isna().all():
                            return col
                except Exception:
                    # Conversion failed, but still return the column if it has date-related name
                    if any(keyword in col_lower for keyword in ['date', 'time', 'period']):
                        return col
                    continue
        
        # Last resort: try to convert any string column that might be a date
        for col in df.select_dtypes(include=['object']).columns:
            try:
                # Try to convert sample of values to datetime
                sample = df[col].dropna().head(15)  # Increased sample size for mixed formats
                if not sample.empty:
                    # Special handling for quarter notation
                    if any('q' in str(x).lower() for x in sample):
                        return col
                    
                    # Handle mixed date formats
                    test_conversion = pd.to_datetime(sample, errors='coerce')
                    if not test_conversion.isna().all() and test_conversion.notna().sum() >= len(sample) * 0.5:  # At least 50% valid
                        return col
            except Exception:
                continue
        
        # No date column found
        return None

    def generate_initial_system_message(self, df=None):
        """Generate the initial system message to start the chat"""
        if df is None or df.empty:
            # No data yet, provide general welcome message
            return {"role": "assistant", "content": self.get_default_system_prompt()}
        
        # If we have data, create an automatic analysis
        try:
            # Count rows and columns
            row_count = len(df)
            col_count = len(df.columns)
            
            # Get column types
            numeric_cols = len(df.select_dtypes(include=[np.number]).columns)
            text_cols = len(df.select_dtypes(include=['object']).columns)
            date_cols = len(df.select_dtypes(include=['datetime64']).columns)
            
            # Get column names (limited to first 5)
            col_names = df.columns.tolist()[:5]
            col_sample = ", ".join(col_names)
            
            # Create initial message
            message = f"""# 👋 Welcome to VariancePro Financial Analysis

I've detected your uploaded data with **{row_count:,} rows** and **{col_count} columns**.

**Dataset Overview:**
- 🔢 {numeric_cols} numeric columns
- 📝 {text_cols} text columns
- 📅 {date_cols} datetime columns

**Sample columns:** {col_sample}{", ..." if len(df.columns) > 5 else ""}

## 🚀 What would you like to know?

Try asking questions like:
- "Analyze the trends in this data"
- "Compare performance across regions"
- "Calculate month-over-month growth"
- "Show me Python code to analyze this dataset"

I'm ready to help with your financial analysis!"""
            
            return {"role": "assistant", "content": message}
        except Exception as e:
            # Fallback to default prompt if there's an error
            print(f"Error generating initial system message: {str(e)}")
            return {"role": "assistant", "content": self.get_default_system_prompt()}

# Global variable for chat system
chat_system = None

if __name__ == "__main__":
    # Create and launch the interface
    demo = create_interface()
    
    print("🚀 Starting VariancePro Financial Chat FIXED VERSION...")
    print("📊 Upload your CSV data and start asking questions!")
    print("⚠️ This is the fixed version with ONLY 2 TABS (no visualization)")
    
    demo.launch(
        server_name="127.0.0.1",
        server_port=7866,
        share=False,
        debug=False,
        show_error=True
    )
