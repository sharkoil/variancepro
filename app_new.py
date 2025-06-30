"""
Fresh Financial Chat App - Gradio + Ollama + StarCoder2
A clean, multi-turn chat application for financial data analysis
"""

import gradio as gr
import pandas as pd
import requests
import json
import io
import time
from typing import List, Tuple, Optional, Dict, Any

class OllamaStarCoder:
    """Clean Ollama client for StarCoder2 interactions"""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "starcoder2:latest"):
        self.base_url = base_url
        self.model = model
        self.is_available = self._check_availability()
    
    def _check_availability(self) -> bool:
        """Check if Ollama and StarCoder2 are available"""
        try:
            # Check Ollama service
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code != 200:
                return False
            
            # Check if StarCoder2 model is available
            models = response.json().get('models', [])
            model_names = [model.get('name', '') for model in models]
            return any(self.model.split(':')[0] in name for name in model_names)
        except:
            return False
    
    def generate_response(self, prompt: str, context: str = "") -> str:
        """Generate response using StarCoder2"""
        if not self.is_available:
            return "❌ Ollama/StarCoder2 not available. Please ensure Ollama is running and StarCoder2 is installed."
        
        try:
            # Construct the full prompt with context
            full_prompt = self._build_prompt(prompt, context)
            
            # Make request to Ollama
            payload = {
                "model": self.model,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_tokens": 2048
                }
            }
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', 'No response generated')
            else:
                return f"❌ Error: {response.status_code} - {response.text}"
                
        except Exception as e:
            return f"❌ Error generating response: {str(e)}"
    
    def _build_prompt(self, user_query: str, data_context: str = "") -> str:
        """Build a comprehensive prompt for financial analysis"""
        base_prompt = """You are a financial data analyst AI assistant. You help users analyze financial data, provide insights, and suggest code solutions.

Key capabilities:
- Analyze financial datasets (revenue, costs, profits, etc.)
- Provide data insights and trends
- Suggest Python/pandas code for analysis
- Answer financial and business questions

Guidelines:
- Be concise but thorough
- Provide actionable insights
- Include relevant code examples when helpful
- Focus on practical business value
"""
        
        if data_context:
            base_prompt += f"\n\nCurrent dataset context:\n{data_context}\n"
        
        base_prompt += f"\n\nUser question: {user_query}\n\nResponse:"
        
        return base_prompt

class FinancialChatApp:
    """Main Gradio application class"""
    
    def __init__(self):
        self.llm = OllamaStarCoder()
        self.current_data = None
        self.data_summary = ""
    
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
    
    def _generate_data_summary(self, df: pd.DataFrame) -> str:
        """Generate a summary of the dataset for context"""
        summary = f"""Dataset Summary:
- Shape: {df.shape[0]} rows, {df.shape[1]} columns
- Columns: {', '.join(df.columns.tolist())}
"""
        
        # Add numeric column stats
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            summary += f"- Numeric columns: {', '.join(numeric_cols)}\n"
        
        # Add date columns if any
        date_cols = df.select_dtypes(include=['datetime']).columns
        if len(date_cols) > 0:
            summary += f"- Date columns: {', '.join(date_cols)}\n"
        
        return summary
    
    def chat_response(self, message: str, history: List[Tuple[str, str]]) -> Tuple[List[Tuple[str, str]], str]:
        """Handle chat interactions with context"""
        if not message.strip():
            return history, ""
        
        # Generate response using LLM
        response = self.llm.generate_response(message, self.data_summary)
        
        # Add to history
        history.append((message, response))
        
        return history, ""
    
    def get_status(self) -> str:
        """Get current system status"""
        status = "🔍 **System Status**\n\n"
        
        # Ollama status
        if self.llm.is_available:
            status += "✅ Ollama + StarCoder2: Ready\n"
        else:
            status += "❌ Ollama + StarCoder2: Not available\n"
        
        # Data status
        if self.current_data is not None:
            status += f"✅ Dataset: Loaded ({self.current_data.shape[0]} rows)\n"
        else:
            status += "⏳ Dataset: No data loaded\n"
        
        return status
    
    def create_interface(self):
        """Create the Gradio interface"""
        
        with gr.Blocks(title="Financial Chat App - StarCoder2", theme=gr.themes.Soft()) as interface:
            
            gr.HTML("""
            <h1 style="text-align: center; color: #2E86AB;">💼 Financial Chat App</h1>
            <p style="text-align: center; font-size: 18px;">
                Upload your financial data and chat with StarCoder2 for insights and analysis
            </p>
            """)
            
            with gr.Row():
                with gr.Column(scale=1):
                    # Status panel
                    status_display = gr.Markdown(value=self.get_status())
                    refresh_btn = gr.Button("🔄 Refresh Status", size="sm")
                    
                    # File upload
                    gr.Markdown("### 📊 Upload Data")
                    file_input = gr.File(
                        label="Upload CSV File",
                        file_types=[".csv"],
                        type="filepath"
                    )
                    
                    # Data preview
                    data_preview = gr.Textbox(
                        label="Data Preview",
                        value="No data loaded",
                        lines=8,
                        max_lines=15,
                        interactive=False
                    )
                
                with gr.Column(scale=2):
                    # Chat interface
                    gr.Markdown("### 💬 Chat with StarCoder2")
                    
                    chatbot = gr.Chatbot(
                        label="Financial Assistant",
                        height=400,
                        show_label=True
                    )
                    
                    with gr.Row():
                        chat_input = gr.Textbox(
                            placeholder="Ask about your data, request analysis, or get code suggestions...",
                            label="Your Message",
                            lines=2,
                            scale=4
                        )
                        send_btn = gr.Button("Send 📤", scale=1, variant="primary")
                    
                    # Quick action buttons
                    with gr.Row():
                        gr.Button("📈 Analyze Trends", size="sm")
                        gr.Button("💰 Financial Summary", size="sm")
                        gr.Button("📋 Generate Code", size="sm")
            
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
        
        return interface

def main():
    """Main entry point"""
    print("🚀 Starting Financial Chat App...")
    
    app = FinancialChatApp()
    interface = app.create_interface()
    
    print("✅ App ready! Starting Gradio interface...")
    
    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=True
    )

if __name__ == "__main__":
    main()
