import gradio as gr
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import requests
import json
import io
import base64
from datetime import datetime
from typing import Optional, List, Tuple

class StarCoderFinancialChat:
    """Financial data analysis chat powered by StarCoder2 via Ollama"""
    
    def __init__(self):
        self.ollama_url = "http://localhost:11434"
        self.model_name = "starcoder2"
        self.current_data = None
        self.chat_history = []
        
    def check_ollama_connection(self) -> bool:
        """Check if Ollama is running and StarCoder2 is available"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                available_models = [model["name"] for model in models]
                return any("starcoder2" in model for model in available_models)
            return False
        except:
            return False
    
    def query_starcoder(self, prompt: str) -> str:
        """Query StarCoder2 model via Ollama"""
        try:
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.2,
                    "top_k": 40,
                    "top_p": 0.95,
                    "num_predict": 1000
                }
            }
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                return response.json().get("response", "").strip()
            else:
                return f"Error: StarCoder2 returned status {response.status_code}"
                
        except Exception as e:
            return f"Error communicating with StarCoder2: {str(e)}"
    
    def create_financial_prompt(self, user_query: str, data_summary: str) -> str:
        """Create optimized prompt for StarCoder2 financial analysis"""
        
        prompt = f"""You are an expert financial data analyst and Python programmer. You have access to a financial dataset and need to provide comprehensive analysis with code suggestions.

CURRENT DATASET:
{data_summary}

USER QUESTION: {user_query}

Please provide a comprehensive response that includes:

1. **FINANCIAL ANALYSIS**: Direct answer to the question with key insights
2. **KEY PATTERNS**: Important trends, outliers, or relationships in the data
3. **BUSINESS IMPACT**: What these findings mean for business decisions
4. **PYTHON CODE**: Relevant pandas/numpy code for deeper analysis (if applicable)
5. **RECOMMENDATIONS**: Actionable next steps

Format your response clearly with headers and use financial terminology appropriately. If providing code, make it practical and executable.

RESPONSE:"""
        
        return prompt
    
    def analyze_data(self, file_data, user_question: str) -> Tuple[str, str]:
        """Analyze uploaded data and answer user questions"""
        
        # Check StarCoder2 availability
        if not self.check_ollama_connection():
            return self.fallback_analysis(user_question), "⚠️ StarCoder2 offline - using built-in analysis"
        
        # Process uploaded file
        if file_data is None:
            return "Please upload a CSV file to analyze.", "📁 No data uploaded"
        
        try:
            # Read CSV file
            if isinstance(file_data, str):
                # If file_data is a file path
                df = pd.read_csv(file_data)
            else:
                # If file_data is file content
                df = pd.read_csv(io.StringIO(file_data.decode('utf-8')))
            
            self.current_data = df
            
            # Create data summary
            data_summary = self.create_data_summary(df)
            
            # Create prompt for StarCoder2
            prompt = self.create_financial_prompt(user_question, data_summary)
            
            # Get StarCoder2 response
            starcoder_response = self.query_starcoder(prompt)
            
            # Add to chat history
            self.chat_history.append({
                "user": user_question,
                "assistant": starcoder_response,
                "timestamp": datetime.now()
            })
            
            return starcoder_response, f"✅ StarCoder2 Analysis | Dataset: {len(df)} rows, {len(df.columns)} columns"
            
        except Exception as e:
            return f"Error processing data: {str(e)}", "❌ Processing Error"
    
    def create_data_summary(self, df: pd.DataFrame) -> str:
        """Create comprehensive data summary for StarCoder2"""
        
        summary = f"""
DATASET OVERVIEW:
- Rows: {len(df)}
- Columns: {len(df.columns)}
- Date Range: {self.get_date_range(df)}

COLUMN STRUCTURE:
{self.get_column_info(df)}

SAMPLE DATA:
{df.head(3).to_string()}

STATISTICAL SUMMARY:
{df.describe().round(2).to_string() if len(df.select_dtypes(include=[np.number]).columns) > 0 else "No numeric columns"}
"""
        return summary
    
    def get_date_range(self, df: pd.DataFrame) -> str:
        """Extract date range from dataframe"""
        date_cols = df.select_dtypes(include=['datetime64']).columns
        if len(date_cols) == 0:
            # Try to find date-like columns
            for col in df.columns:
                if 'date' in col.lower() or 'time' in col.lower():
                    try:
                        date_series = pd.to_datetime(df[col])
                        return f"{date_series.min()} to {date_series.max()}"
                    except:
                        continue
            return "No date columns detected"
        else:
            date_col = date_cols[0]
            return f"{df[date_col].min()} to {df[date_col].max()}"
    
    def get_column_info(self, df: pd.DataFrame) -> str:
        """Get detailed column information"""
        info = []
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        text_cols = df.select_dtypes(include=['object']).columns
        date_cols = df.select_dtypes(include=['datetime64']).columns
        
        if len(numeric_cols) > 0:
            info.append(f"Numeric ({len(numeric_cols)}): {', '.join(numeric_cols[:5])}{'...' if len(numeric_cols) > 5 else ''}")
        
        if len(text_cols) > 0:
            info.append(f"Text ({len(text_cols)}): {', '.join(text_cols[:5])}{'...' if len(text_cols) > 5 else ''}")
            
        if len(date_cols) > 0:
            info.append(f"Date ({len(date_cols)}): {', '.join(date_cols)}")
        
        return "\n".join(info)
    
    def fallback_analysis(self, user_question: str) -> str:
        """Fallback analysis when StarCoder2 is not available"""
        
        if self.current_data is None:
            return """🤖 **Built-in Analysis** (StarCoder2 offline):

Please upload a CSV file to begin analysis.

💡 **To enable StarCoder2**:
1. Ensure Ollama is running: `ollama serve`
2. Verify StarCoder2 is installed: `ollama list`
3. If missing, install: `ollama pull starcoder2`"""
        
        df = self.current_data
        
        response = f"""🤖 **Built-in Analysis** (StarCoder2 offline):

**Your Question**: {user_question}

**Dataset Overview**:
- {len(df)} rows, {len(df.columns)} columns
- Numeric columns: {len(df.select_dtypes(include=[np.number]).columns)}

**Quick Insights**:
- Data spans from {df.index[0]} to {df.index[-1]}
- Key columns: {', '.join(df.columns[:5])}

💡 **For enhanced AI analysis with code suggestions, ensure StarCoder2 is running via Ollama.**"""
        
        return response
    
    def create_visualization(self, df: pd.DataFrame, chart_type: str = "summary") -> Optional[str]:
        """Create plotly visualizations"""
        
        if df is None or df.empty:
            return None
        
        try:
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            
            if chart_type == "summary" and len(numeric_cols) >= 2:
                # Create correlation heatmap
                fig = px.imshow(
                    df[numeric_cols].corr().round(2),
                    title="Correlation Matrix",
                    color_continuous_scale="RdBu",
                    aspect="auto"
                )
                return fig.to_html()
            
            elif chart_type == "trends" and len(numeric_cols) >= 1:
                # Create line chart for first numeric column
                fig = px.line(
                    df.reset_index(), 
                    x=df.index, 
                    y=numeric_cols[0],
                    title=f"{numeric_cols[0]} Over Time"
                )
                return fig.to_html()
            
        except Exception as e:
            return f"Visualization error: {str(e)}"
        
        return None

# Initialize the chat system
chat_system = StarCoderFinancialChat()

def process_query(file, question, history):
    """Process user query and return response"""
    
    if not question.strip():
        return history, history, "Please enter a question about your financial data."
    
    # Analyze data and get response
    response, status = chat_system.analyze_data(file, question)
    
    # Update chat history
    history.append([question, response])
    
    return history, history, status

def check_system_status():
    """Check system status"""
    starcoder_available = chat_system.check_ollama_connection()
    
    if starcoder_available:
        return "✅ StarCoder2 Active - AI-enhanced analysis enabled"
    else:
        return "⚠️ StarCoder2 Offline - Using built-in analysis. Run: ollama serve"

# Create Gradio interface
def create_interface():
    """Create the Gradio interface"""
    
    with gr.Blocks(
        title="VariancePro - StarCoder2 Financial Chat",
        theme=gr.themes.Soft(),
        css="""
        .container { max-width: 1200px; margin: auto; }
        .status-box { background: #f0f8ff; padding: 10px; border-radius: 5px; margin: 10px 0; }
        .chat-container { height: 400px; overflow-y: auto; }
        """
    ) as interface:
        
        gr.Markdown("# 🚀 VariancePro - Financial Data Analysis Chat")
        gr.Markdown("### Powered by StarCoder2 via Ollama")
        
        with gr.Row():
            with gr.Column(scale=2):
                # File upload
                file_input = gr.File(
                    label="📁 Upload Financial Data (CSV)",
                    file_types=[".csv"],
                    type="filepath"
                )
                
                # Chat interface
                chatbot = gr.Chatbot(
                    label="💬 Financial Analysis Chat",
                    height=400,
                    show_label=True
                )
                
                # User input
                user_input = gr.Textbox(
                    label="Ask about your financial data:",
                    placeholder="e.g., 'Analyze sales variance by region and suggest Python code'",
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
                
                # Sample questions
                gr.Markdown("""
                ### 💡 Sample Questions:
                
                **Basic Analysis:**
                - "Summarize this dataset"
                - "What are the key trends?"
                - "Find any anomalies or outliers"
                
                **Advanced Analysis:**
                - "Analyze budget vs actual variance"
                - "Compare performance by region"
                - "Show Python code for correlation analysis"
                
                **Code Assistance:**
                - "Generate dashboard code for this data"
                - "Help me build a forecasting model"
                - "Create visualization code"
                """)
                
                # Refresh status button
                refresh_btn = gr.Button("🔄 Refresh Status")
        
        # State for chat history
        chat_state = gr.State([])
        
        # Event handlers
        def submit_query(file, question, history, chat_state):
            new_history, new_chat_state, status = process_query(file, question, chat_state)
            return new_history, "", new_chat_state, status
        
        def clear_chat():
            chat_system.chat_history = []
            return [], []
        
        # Connect events
        submit_btn.click(
            submit_query,
            inputs=[file_input, user_input, chatbot, chat_state],
            outputs=[chatbot, user_input, chat_state, status_display]
        )
        
        user_input.submit(
            submit_query,
            inputs=[file_input, user_input, chatbot, chat_state],
            outputs=[chatbot, user_input, chat_state, status_display]
        )
        
        clear_btn.click(
            clear_chat,
            outputs=[chatbot, chat_state]
        )
        
        refresh_btn.click(
            check_system_status,
            outputs=[status_display]
        )
        
        # Initial status check
        interface.load(
            check_system_status,
            outputs=[status_display]
        )
    
    return interface

if __name__ == "__main__":
    # Create and launch the interface
    demo = create_interface()
    
    print("🚀 Starting VariancePro Financial Chat with StarCoder2...")
    print("📊 Upload your CSV data and start asking questions!")
    
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=True,
        show_error=True
    )
