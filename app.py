import gradio as gr
import pandas as pd
import numpy as np
import requests
import json
import io
import base64
import traceback
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import Optional, List, Tuple, Dict
from pathlib import Path
from utils.chat_handler import ChatHandler

# Import the narrative generator (optional)
try:
    from utils.narrative_generator import add_narrative_to_app
    NARRATIVE_AVAILABLE = True
except ImportError:
    NARRATIVE_AVAILABLE = False

# LlamaIndex integration (optional)
try:
    from llamaindex_integration import (
        LlamaIndexFinancialProcessor, 
        create_llamaindex_enhanced_analysis,
        extract_financial_data_from_text
    )
    LLAMAINDEX_AVAILABLE = True
except ImportError:
    LLAMAINDEX_AVAILABLE = False
    print("LlamaIndex not available. Install with: pip install llama-index")

class AriaFinancialChat:
    """Financial data analysis chat powered by Aria Sterling via Ollama"""
    
    def __init__(self):
        self.model_name = "gemma3:latest" # Use Gemma3 model for financial analysis
        self.ollama_url = "http://localhost:11434"
        self.current_data = None
        self.chat_history = []  # Initialize chat history
        self.timescale_shown = False  # Track if timescale analysis has been shown for current dataset
        
        # Initialize chat handler for LLM integration
        self.chat_handler = ChatHandler()
        
        # Initialize timescale analyzer
        self.timescale_analyzer = TimescaleAnalyzer()
        
        # Initialize contribution analyzer
        self.contribution_analyzer = ContributionAnalyzer()
        
        # Add narrative generation if available
        if NARRATIVE_AVAILABLE:
            try:
                from utils.narrative_generator import add_narrative_to_app
                add_narrative_to_app(self)
                print("[SUCCESS] Narrative generation enabled with Aria Sterling persona")
            except Exception as e:
                print(f"[WARNING] Narrative generation initialization failed: {e}")
        
        # Initialize LlamaIndex processor (optional)
        self.llamaindex_processor = None
        if LLAMAINDEX_AVAILABLE:
            try:
                self.llamaindex_processor = LlamaIndexFinancialProcessor()
                print("[SUCCESS] LlamaIndex processor initialized")
            except Exception as e:
                print(f"[WARNING] LlamaIndex initialization failed: {e}")
                self.llamaindex_processor = None
        else:
            print("LlamaIndex not installed. Run: pip install llama-index")
    
    def check_ollama_connection(self) -> bool:
        """Check if Ollama is running and the model is available"""
        try:
            # First check if Ollama is running
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=10)
            if response.status_code == 200:
                models = response.json().get("models", [])
                available_models = [model["name"] for model in models]
                
                # Check if our model is available
                if self.model_name in available_models:
                    print(f"[SUCCESS] Using model: {self.model_name}")
                    return True
                
                # Look specifically for gemma3:latest
                if "gemma3:latest" in available_models:
                    self.model_name = "gemma3:latest"
                    print(f"[SUCCESS] Using model: {self.model_name}")
                    return True
                
                # Look for any gemma3 variant as first priority
                for model_name in available_models:
                    if "gemma3" in model_name:
                        self.model_name = model_name
                        print(f"[SUCCESS] Using gemma3 variant: {self.model_name}")
                        return True
                
                # Only then check for other models (excluding deepseek)
                for model_name in available_models:
                    if any(name in model_name for name in ["phi", "llama", "mistral"]):
                        self.model_name = model_name
                        print(f"[WARNING] Using fallback model: {self.model_name}")
                        return True
                
                print("[ERROR] No suitable LLM models found in Ollama")
                return False
            return False
        except requests.exceptions.Timeout:
            return False
        except requests.exceptions.ConnectionError:
            return False
        except Exception:
            return False
    
    def query_ollama(self, prompt: str) -> str:
        """Query LLM model via Ollama using Aria Sterling persona with full prompt logging"""
        
        # Log the full prompt to console
        print("\n" + "="*80)
        print(f"[PROMPT LOG] Sending prompt to {self.model_name}")
        print("="*80)
        print(prompt)
        print("="*80 + "\n")
        
        try:
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "top_k": 40,
                    "top_p": 0.9,
                    "num_predict": 2048,
                    "num_ctx": 8192  # Increased context window
                }
            }
            
            # Log the payload details
            print(f"[REQUEST LOG] Model: {self.model_name}")
            print(f"[REQUEST LOG] Temperature: {payload['options']['temperature']}")
            print(f"[REQUEST LOG] Context Length: {payload['options']['num_ctx']}")
            print(f"[REQUEST LOG] Max Tokens: {payload['options']['num_predict']}")
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=180  # Extended timeout for large models (3 minutes)
            )
            
            if response.status_code == 200:
                result = response.json()
                llm_response = result.get("response", "").strip()
                
                # Log the response
                print("\n" + "-"*80)
                print(f"[RESPONSE LOG] Response from {self.model_name}")
                print("-"*80)
                print(llm_response)
                print("-"*80 + "\n")
                
                return llm_response
            else:
                error_msg = f"Error: {self.model_name} returned status {response.status_code}"
                print(f"[ERROR LOG] {error_msg}")
                return error_msg
                
        except requests.exceptions.Timeout:
            timeout_msg = f"[WARNING] {self.model_name} is processing your complex financial query. Large models need more time for detailed analysis. The response will appear shortly, or try breaking your question into smaller parts."
            print(f"[TIMEOUT LOG] {timeout_msg}")
            return timeout_msg
        except requests.exceptions.ConnectionError:
            conn_error = "[ERROR] Cannot connect to Ollama. Please ensure Ollama is running with: `ollama serve`"
            print(f"[CONNECTION LOG] {conn_error}")
            return conn_error
        except Exception as e:
            exception_msg = f"Error communicating with {self.model_name}: {str(e)}"
            print(f"[EXCEPTION LOG] {exception_msg}")
            return exception_msg
    
    def create_financial_prompt(self, user_query: str, data_summary: str) -> str:
        """Create optimized prompt for Aria Sterling financial analysis"""
        
        prompt = f"""You are an expert financial analyst with deep expertise in data analysis and Python programming. Analyze the provided financial dataset and respond to the user's question with detailed insights.

DATASET INFORMATION:
{data_summary}

USER QUESTION: {user_query}

Please provide a comprehensive analysis that includes:

## Financial Analysis
- Direct answer to the question with specific insights
- Key metrics and performance indicators
- Trend analysis and variance explanations
- TTM (Trailing Twelve Months) performance where applicable

## Data Patterns & Insights  
- Notable patterns, trends, or anomalies
- Statistical relationships between variables
- Risk factors or opportunities identified
- Year-over-year and period-over-period comparisons

## Business Impact
- Strategic implications of the findings
- Impact on business performance and decisions
- Areas requiring immediate attention
- TTM performance benchmarking

## Recommendations
- Specific actionable steps
- Areas for further investigation
- Risk mitigation strategies
- Performance improvement opportunities based on TTM trends

Provide clear, concise responses using professional financial terminology. Make recommendations data-driven and actionable. Always consider TTM performance when analyzing financial data. DO NOT provide code suggestions or programming examples."""
        
        return prompt
        
    def analyze_data(self, file_data, user_question: str) -> Tuple[str, str]:
        """Analyze uploaded data and answer user questions - with special handling for contribution analysis"""
        
        # Process uploaded file
        if file_data is None:
            return "Please upload a CSV file to analyze.", "[INFO] No data uploaded"

        try:
            # Read CSV file
            if isinstance(file_data, str):
                # If file_data is a file path
                df = pd.read_csv(file_data)
            else:
                # If file_data is file content
                df = pd.read_csv(io.StringIO(file_data.decode('utf-8')))
            
            # Store current data for later use
            self.current_data = df
            
            # Reset timescale shown flag when new data is loaded
            self.timescale_shown = False
            
            # Detect contribution analysis requests
            contribution_keywords = ['contribution analysis', 'pareto', '80/20', '80-20', 'key contributors', 'top contributors']
            user_question_lower = user_question.lower()
            
            if any(keyword in user_question_lower for keyword in contribution_keywords):
                return self._handle_contribution_analysis_request(df, user_question)
            
            # GENERATE COMPREHENSIVE CHAT RESPONSE INCLUDING TIMESCALE ANALYSIS
            chat_response_parts = []
            
            # Add initial processing message for data preparation
            if len(df) > 100:  # For larger datasets, show preparation message
                chat_response_parts.append("🔄 **Preparing your data analysis...**\n")
            
            # 1. Generate ChatHandler response (LLM or rule-based)
            primary_response = self.chat_handler.generate_response(user_question, df)
            chat_response_parts.append(primary_response)
            
            # 2. Generate automatic timescale analysis ONLY on first data load
            timescale_included = False
            if not self.timescale_shown:
                try:
                    timescale_analysis = self.timescale_analyzer.generate_timescale_analysis(df)
                    if timescale_analysis and "No date column found" not in timescale_analysis:
                        chat_response_parts.append("\n" + "="*50)
                        chat_response_parts.append("📈 **AUTOMATIC TIMESCALE ANALYSIS**")
                        chat_response_parts.append("="*50)
                        chat_response_parts.append(timescale_analysis)
                        self.timescale_shown = True  # Mark as shown
                        timescale_included = True
                    else:
                        # Add note about timescale analysis when no date column
                        chat_response_parts.append("\n💡 **Note**: No date column detected for timescale analysis. Upload data with dates for period-over-period insights.")
                        self.timescale_shown = True  # Mark as attempted
                except Exception as e:
                    chat_response_parts.append(f"\n⚠️ **Timescale Analysis**: Could not generate due to: {str(e)}")
                    self.timescale_shown = True  # Mark as attempted
            
            # 3. Combine all parts into final chat response
            final_response = "\n\n".join(chat_response_parts)
            
            # Determine status
            if self.chat_handler.use_llm:
                if timescale_included:
                    status = f"[SUCCESS] Using LLM Analysis + Timescale Analysis"
                else:
                    status = f"[SUCCESS] Using LLM Analysis"
            else:
                if timescale_included:
                    status = "[SUCCESS] Built-in Analysis + Timescale Analysis"
                else:
                    status = "[SUCCESS] Built-in Analysis"
            
            # Add to chat history
            self.chat_history.append({
                "user": user_question,
                "assistant": final_response,
                "timestamp": datetime.now()
            })
            
            return final_response, status
            
        except Exception as e:
            return f"Error processing data: {str(e)}", "[ERROR] Processing Error"
    
    def _handle_contribution_analysis_request(self, df: pd.DataFrame, user_question: str) -> Tuple[str, str]:
        """Handle contribution analysis requests with intelligent column detection"""
        
        try:
            # Detect suitable columns for contribution analysis
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            text_cols = df.select_dtypes(include=['object']).columns.tolist()
            date_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
            
            # Try to detect date columns that might not be datetime type yet
            for col in df.columns:
                if col.lower() in ['date', 'time', 'period', 'period_end'] and col not in date_cols:
                    try:
                        pd.to_datetime(df[col].head(), errors='raise')
                        date_cols.append(col)
                    except:
                        pass
            
            if not numeric_cols or not text_cols:
                return (
                    "❌ **Cannot perform contribution analysis**: Need at least one numeric column and one category column.\n\n" +
                    f"📊 **Your data has**: {len(numeric_cols)} numeric columns, {len(text_cols)} category columns\n\n" +
                    "💡 **Tip**: Ensure your data has categories (like products, regions) and numeric values (like sales, revenue).",
                    "[ERROR] Insufficient columns for contribution analysis"
                )
            
            # Auto-detect the best columns
            value_col = None
            category_col = None
            time_col = None
            
            # Find the best value column (prioritize sales, revenue, amount)
            priority_value_terms = ['sales', 'revenue', 'amount', 'value', 'total', 'sum']
            for term in priority_value_terms:
                for col in numeric_cols:
                    if term in col.lower():
                        value_col = col
                        break
                if value_col:
                    break
            
            # If no priority column found, use the first numeric column
            if not value_col:
                value_col = numeric_cols[0]
            
            # Find the best category column (prioritize product, category, region)
            priority_category_terms = ['product', 'category', 'region', 'customer', 'item', 'name']
            for term in priority_category_terms:
                for col in text_cols:
                    if term in col.lower():
                        category_col = col
                        break
                if category_col:
                    break
            
            # If no priority column found, use the first text column
            if not category_col:
                category_col = text_cols[0]
            
            # Use time column if available (prioritize time-based analysis as requested)
            if date_cols:
                time_col = date_cols[0]
            
            # Initialize contribution analyzer
            if not hasattr(self, 'contribution_analyzer'):
                self.contribution_analyzer = ContributionAnalyzer()
            
            # Perform contribution analysis
            analysis_df, summary, fig = self.contribution_analyzer.perform_contribution_analysis_pandas(
                df=df,
                category_col=category_col,
                value_col=value_col,
                time_col=time_col,  # Automatic time-based prioritization
                threshold=0.8
            )
            
            # Format results for chat display
            chat_response = self.contribution_analyzer.format_contribution_analysis_for_chat(
                analysis_df, summary, category_col, value_col
            )
            
            # Add column selection info to the response
            column_info = f"""
🔍 **AUTO-DETECTED COLUMNS**
• **Category Column**: {category_col}
• **Value Column**: {value_col}
• **Time Column**: {time_col if time_col else 'None detected'}

"""
            
            # Start building comprehensive response
            response_parts = [column_info, chat_response]
            
            # Add time-based note if time column was used
            if time_col:
                response_parts.append(f"""

⏰ **TIME-BASED ANALYSIS NOTE**
Since a time column was detected ({time_col}), this analysis focuses on the most recent period to provide current insights. This follows your preference for time-based prioritization in contribution analysis.
""")
            
            # Combine all parts
            final_response = "\n\n".join(response_parts)
            
            # Add to chat history
            self.chat_history.append({
                "user": user_question,
                "assistant": final_response,
                "timestamp": datetime.now()
            })
            
            # Return appropriate status  
            return final_response, "[SUCCESS] Contribution analysis completed"
            
        except Exception as e:
            error_response = f"❌ **Error performing contribution analysis**: {str(e)}\n\n💡 **Tip**: Try specifying columns explicitly like 'Perform contribution analysis on sales by product'"
            return error_response, "[ERROR] Contribution analysis failed"
    
    def create_data_summary(self, df: pd.DataFrame) -> str:
        """Create comprehensive data summary for Aria Sterling analysis"""
        
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
    
    def fallback_analysis(self, user_query: str) -> str:
        """Fallback analysis when Ollama is not available"""
        
        if self.current_data is None:
            return """[BOT] **Aria Sterling Analysis** (Ollama offline):

Please upload a CSV file to begin analysis.

I'm Aria Sterling, your financial analysis assistant. I can help you analyze financial data, identify trends, calculate metrics, and provide actionable insights.

[INFO] **To enable Ollama**:
1. Ensure Ollama is running: `ollama serve`
2. Verify gemma3 is installed: `ollama list`
3. If missing, install: `ollama pull gemma3:latest`"""
        
        df = self.current_data
        
        response = f"""[BOT] **Aria Sterling Analysis** (Ollama offline):

**Your Question**: {user_query}

**Dataset Overview**:
- {len(df)} rows, {len(df.columns)} columns
- Numeric columns: {len(df.select_dtypes(include=[np.number]).columns)}

**Quick Insights**:
- Data spans from {df.index[0]} to {df.index[-1]}
- Key columns: {', '.join(df.columns[:5])}

As Aria Sterling, your financial analyst, I can provide more insightful analysis when connected to the Ollama language model. Please ensure Ollama is running and reload the application for full functionality.

[INFO] **For enhanced financial analysis with Aria Sterling, ensure Ollama is running with a compatible model.**"""
        
        return response

    def generate_suggested_questions(self, df: pd.DataFrame) -> str:
        """Generate suggested questions based on actual data columns"""
        if df is None or df.empty:
            return self.get_default_suggested_questions()
        
        columns = df.columns.tolist()
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        text_cols = df.select_dtypes(include=['object']).columns.tolist()
        
        # Detect column types and patterns
        date_cols = []
        for col in columns:
            if any(keyword in col.lower() for keyword in ['date', 'time', 'period']):
                date_cols.append(col)
        
        budget_cols = [col for col in columns if 'budget' in col.lower()]
        actual_cols = [col for col in columns if 'actual' in col.lower()]
        variance_cols = [col for col in columns if 'variance' in col.lower()]
        sales_cols = [col for col in columns if 'sales' in col.lower() or 'revenue' in col.lower()]
        profit_cols = [col for col in columns if 'profit' in col.lower() or 'margin' in col.lower()]
        cost_cols = [col for col in columns if 'cost' in col.lower() or 'expense' in col.lower()]
        
        # Geographic columns
        geo_cols = [col for col in columns if any(geo in col.lower() for geo in ['region', 'country', 'state', 'city', 'territory'])]
        
        # Product/Category columns  
        product_cols = [col for col in columns if any(prod in col.lower() for prod in ['product', 'line', 'category', 'segment'])]
        
        suggestions = []
        
        # Basic Analysis Questions
        suggestions.append("**Basic Analysis:**")
        suggestions.append(f'- "Summarize this dataset with {len(df)} rows and {len(columns)} columns"')
        suggestions.append('- "What are the key trends in this data?"')
        suggestions.append('- "Find any anomalies or outliers"')
        
        # Budget vs Actual Analysis (if both exist)
        if budget_cols and actual_cols:
            suggestions.append("\n**Budget vs Actual Analysis:**")
            if any('sales' in col.lower() for col in budget_cols):
                suggestions.append('- "Analyze budget vs actual sales variance"')
            if any('volume' in col.lower() for col in budget_cols):
                suggestions.append('- "Compare budget vs actual volume performance"')
            suggestions.append('- "Which periods/regions had the biggest budget variances?"')
            suggestions.append('- "Calculate variance percentages for all budget vs actual metrics"')
        
        # Regional/Geographic Analysis
        if geo_cols:
            geo_col = geo_cols[0]
            suggestions.append(f"\n**Geographic Analysis:**")
            suggestions.append(f'- "Compare performance by {geo_col}"')
            suggestions.append(f'- "Which {geo_col} has the highest sales/revenue?"')
            suggestions.append(f'- "Show variance analysis by {geo_col}"')
            if sales_cols:
                suggestions.append(f'- "Rank {geo_col} by {sales_cols[0] if sales_cols else "sales"} performance"')
        
        # Product/Category Analysis
        if product_cols:
            prod_col = product_cols[0]
            suggestions.append(f"\n**Product Analysis:**")
            suggestions.append(f'- "Analyze performance by {prod_col}"')
            suggestions.append(f'- "Which {prod_col} is most profitable?"')
            if sales_cols:
                suggestions.append(f'- "Compare {sales_cols[0]} across different {prod_col}"')
        
        # Time Series Analysis
        if date_cols:
            date_col = date_cols[0]
            suggestions.append(f"\n**Time Series Analysis:**")
            suggestions.append(f'- "Show trends over time using {date_col}"')
            suggestions.append(f'- "Identify seasonal patterns in the data"')
            suggestions.append(f'- "Which time periods had the best performance?"')
        
        # Financial Metrics Analysis
        if sales_cols or profit_cols:
            suggestions.append(f"\n**Financial Analysis:**")
            if sales_cols:
                suggestions.append(f'- "Analyze {sales_cols[0]} performance and drivers"')
            if profit_cols:
                suggestions.append(f'- "Calculate profit margins and identify trends"')
            if cost_cols:
                suggestions.append(f'- "Analyze cost structure and efficiency"')
        
        # Advanced Analysis
        suggestions.append(f"\n**Advanced Analysis:**")
        if len(numeric_cols) >= 2:
            suggestions.append(f'- "Show correlation analysis between {numeric_cols[0]} and {numeric_cols[1]}"')
        suggestions.append('- "Generate Python code for statistical analysis"')
        suggestions.append('- "Build a forecasting model for future predictions"')
        
        # Specific Column Questions
        if len(columns) > 0:
            suggestions.append(f"\n**Column-Specific Questions:**")
            suggestions.append(f'- "Explain the relationship between {", ".join(columns[:3])}"')
            if numeric_cols:
                suggestions.append(f'- "What drives the variations in {numeric_cols[0]}?"')
        
        return "\n".join(suggestions)
    
    def get_default_suggested_questions(self) -> str:
        """Default questions when no data is loaded"""
        return """### [TIPS] Sample Questions:

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

[UPLOAD] Upload your CSV file to get personalized suggestions based on your data columns!"""

    def enhanced_analysis_with_llamaindex(self, file_data, user_question: str, context_docs: List[str] = None) -> Tuple[str, str]:
        """Enhanced analysis using both Aria Sterling and LlamaIndex for superior insights"""
        
        # First get standard Aria Sterling analysis
        standard_response, status = self.analyze_data(file_data, user_question)
        
        # Add LlamaIndex enhancement if available
        if self.llamaindex_processor and self.llamaindex_processor.check_availability():
            try:
                # Load the data for LlamaIndex analysis
                if isinstance(file_data, str):
                    df = pd.read_csv(file_data)
                elif hasattr(file_data, 'name'):
                    df = pd.read_csv(file_data.name)
                else:
                    df = pd.read_csv(io.StringIO(file_data.decode('utf-8')))
                
                # Get enhanced analysis using LlamaIndex
                enhanced_response, enhanced_status = create_llamaindex_enhanced_analysis(
                    df, user_question, context_docs
                )
                
                # Combine both analyses
                combined_response = f"""## [BOT] Aria Sterling Financial Analysis:
{standard_response}

---

## [AI] LlamaIndex Enhanced Analysis:
{enhanced_response}

---

### [INSIGHTS] **Synthesis:**
This analysis combines Aria Sterling's financial expertise with LlamaIndex's structured data extraction and knowledge base features for comprehensive financial insights."""
                
                combined_status = f"{status} + {enhanced_status}"
                return combined_response, combined_status
                
            except Exception as e:
                # If LlamaIndex fails, return standard analysis with error note
                fallback_response = f"""{standard_response}

---

[WARNING] **LlamaIndex Enhancement Failed**: {str(e)}
*Falling back to standard Aria Sterling analysis. Ensure LlamaIndex is properly installed and configured.*"""
                
                return fallback_response, f"{status} (LlamaIndex failed)"
        
        # If LlamaIndex not available, return standard analysis with note
        enhanced_note = f"""{standard_response}

---

[INFO] **Enhanced Analysis Available**: Install LlamaIndex for advanced features:
- Structured data extraction from documents
- Multi-document knowledge base queries  
- Cross-temporal financial analysis
- Schema-validated metric extraction

Install with: `pip install llama-index llama-index-llms-ollama`"""
        
        return enhanced_note, f"{status} (Standard mode)"

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
            error_msg = f"Error generating automatic timescale analysis: {str(e)}"
            print(f"Debug: {error_msg}")
            traceback.print_exc()
            return f"""# [WARNING] Automatic Analysis Error

We encountered an issue while analyzing your time series data: {str(e)}

Please try:
1. Ensuring your data contains at least one date/time column
2. Having sufficient data points for meaningful period-over-period analysis
3. Checking that numeric columns contain valid values

You can still ask specific questions about your data using the chat interface."""

    def create_aria_sterling_prompt(self, user_query: str, data_summary: str, auto_analysis: str = None) -> str:
        """Create optimized prompt using the Aria Sterling persona for financial analysis"""
        
        # Aria Sterling system prompt
        aria_system_prompt = """**📌 System Prompt: Financial Analyst Persona**

You are **Aria Sterling**, a world-class financial analyst and strategist. You possess exceptional quantitative reasoning, market intuition, and business acumen. You analyze financial data with precision, distill market signals into actionable insights, and communicate with clarity, confidence, and charisma.

### 🎯 Core Attributes
- **Brilliant and Analytical**: Expert in time series analysis, financial forecasting, valuation, corporate finance, and macroeconomic interpretation.
- **Data-Driven**: Extracts insights from raw data using rigorous statistical and financial techniques. You speak in ratios, deltas, time horizons, and benchmarks.
- **Fluent in Market Language**: Speaks in sharp, well-structured financial commentary—think investor calls, analyst briefings, earnings breakdowns, pitch decks.
- **Human-Centric Communicator**: Makes complex concepts accessible to both CFOs and startup founders. Adjusts tone and vocabulary based on audience's financial fluency.
- **Forward-Looking**: Scans for inflection points, tailwinds/headwinds, and market signals that influence KPIs and company valuations.

### 🧠 Knowledge Domains
- Financial statements, KPIs, profitability analysis
- Forecasting, TTM (Trailing Twelve Months), YoY, QoQ analysis
- Time series analysis and growth metrics (CAGR, MoM, rolling averages)
- TTM calculations and performance benchmarking
- Corporate strategy, M&A basics, capital structure
- Industry benchmarking and competitive analysis
- Equities, credit markets, macroeconomic indicators

### 💬 Communication Style
- Sharp, credible, and confident—yet approachable.
- Speaks in terms like "overdelivered by 14.2%," "driven by margin expansion," or "growth decelerating at a 3-month rolling rate."
- Capable of switching tones: quick elevator pitch, deep-dive analysis, or executive summary."""
        
        # Add automatic analysis to the prompt if available
        auto_analysis_section = ""
        if auto_analysis:
            auto_analysis_section = f"""
AUTOMATIC TIMESCALE ANALYSIS:
{auto_analysis}
"""
        
        # Construct the full prompt with user query, data summary and auto analysis
        prompt = f"""{aria_system_prompt}

DATASET INFORMATION:
{data_summary}
{auto_analysis_section}

USER QUESTION: {user_query if user_query else "Provide a comprehensive analysis of this financial data including key insights, trends, and recommendations."}

As Aria Sterling, analyze this financial data with your characteristic precision and charisma. Identify key trends, calculate relevant metrics, and provide actionable insights. Structure your response with clear sections:

1. **Executive Summary**: Concise overview of the key findings (2-3 bullet points)
2. **Detailed Analysis**: In-depth examination of trends, variances, and metrics
3. **Strategic Implications**: Business impact and forward-looking insights
4. **Actionable Recommendations**: Specific, data-driven next steps

Remember to use precise financial terminology, quantify insights with exact figures, and maintain your confident yet accessible communication style.
"""
        
        return prompt
        
    def generate_automatic_analysis_with_aria(self, df: pd.DataFrame) -> str:
        """Generate an automatic analysis using Aria Sterling persona when data is first loaded"""
        if df is None or df.empty:
            return "Please upload financial data for analysis."
        
        try:
            # Generate automatic timescale analysis
            auto_analysis = self.timescale_analyzer.generate_timescale_analysis(df)
            
            # Create data summary
            data_summary = self.create_data_summary(df)
            
            # Create prompt with Aria Sterling persona
            prompt = self.create_aria_sterling_prompt(
                user_query="Provide an initial overview analysis of this financial dataset, highlighting key metrics, trends, and potential areas for further investigation.",
                data_summary=data_summary,
                auto_analysis=auto_analysis
            )
            
            # Query Ollama
            response = self.query_ollama(prompt)
            
            return response
        except Exception as e:
            import traceback
            error_msg = f"Error generating automatic analysis: {str(e)}"
            print(f"Debug: {error_msg}")
            traceback.print_exc()
            return f"Error generating initial analysis: {str(e)}"
    
    def process_query(self, file, question, history):
        """Process a user query about financial data with proper DataFrame handling"""
        try:
            # Load data if provided - fix the DataFrame boolean issue
            if file and (self.current_data is None):
                try:
                    if hasattr(file, 'name'):
                        df = pd.read_csv(file.name)
                    elif isinstance(file, str):
                        df = pd.read_csv(file)
                    else:
                        df = pd.read_csv(io.StringIO(file.decode('utf-8')))
                    self.current_data = df
                except Exception as e:
                    new_history = (history or []) + [
                        {"role": "user", "content": question},
                        {"role": "assistant", "content": f"Error loading file: {str(e)}"}
                    ]
                    return new_history, [], "Error loading file", None
            
            # Generate response using ChatHandler
            if self.current_data is not None:
                response = self.chat_handler.generate_response(question, self.current_data)
            else:
                response = "Please upload a CSV file to analyze your financial data."
            
            # Update history
            new_history = (history or []) + [
                {"role": "user", "content": question},
                {"role": "assistant", "content": response}
            ]
            
            return new_history, [], "[SUCCESS] Analysis complete", self.current_data
            
        except Exception as e:
            error_msg = f"Error processing query: {str(e)}"
            new_history = (history or []) + [
                {"role": "user", "content": question},
                {"role": "assistant", "content": error_msg}
            ]
            return new_history, [], "[ERROR] Processing Error", None

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
        insights.append("# [ANALYSIS] Automatic Timescale Analysis")
        insights.append("*Analysis generated based on time series patterns in your data*\n")
        
        # Process each time scale
        for time_scale in ["yearly", "quarterly", "monthly", "weekly"]:
            if time_scale not in pop_analysis or not pop_analysis[time_scale]:
                continue
                
            # Add section header
            header_map = {
                "yearly": "## [YEARLY] Year-over-Year (YoY) Analysis",
                "quarterly": "## [QUARTERLY] Quarter-over-Quarter (QoQ) Analysis",
                "monthly": "## [MONTHLY] Month-over-Month (MoM) Analysis",
                "weekly": "## [WEEKLY] Week-over-Week (WoW) Analysis"
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
        insights.append("## [SUMMARY] Executive Summary")
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
        """Generate comprehensive timescale analysis for the given dataframe including TTM"""
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
        
        # Calculate TTM metrics
        ttm_metrics = self.calculate_ttm_metrics(df, date_col, value_cols)
        ttm_analysis = self.generate_ttm_analysis_text(ttm_metrics)
        
        # Prepare aggregations for period-over-period analysis
        aggregations = self.prepare_timescale_aggregations(df, date_col, value_cols)
        
        # Calculate period-over-period analysis
        pop_analysis = self.calculate_period_over_period_analysis(aggregations, value_cols)
        
        # Generate insights
        pop_insights = self._generate_summary_insights(pop_analysis)
        
        # Combine TTM and period-over-period analysis
        combined_analysis = f"""{pop_insights}

{ttm_analysis}

---

### [EXECUTIVE] Executive Summary with TTM Context
*Comprehensive analysis combining period-over-period trends and trailing twelve months performance*

**Key Findings:**
- **Data Coverage**: {len(df)} records from {df[date_col].min().strftime('%Y-%m-%d')} to {df[date_col].max().strftime('%Y-%m-%d')}
- **TTM Period**: {ttm_metrics['period_start'].strftime('%Y-%m-%d')} to {ttm_metrics['period_end'].strftime('%Y-%m-%d')}
- **Analysis Granularity**: {granularity} level data detected"""

        # Add TTM performance summary
        if ttm_metrics["metrics"]:
            yoy_changes = []
            for metric_name, metric_data in ttm_metrics["metrics"].items():
                if metric_data["yoy_change_pct"] is not None:
                    yoy_changes.append(metric_data["yoy_change_pct"])
            
            if yoy_changes:
                avg_yoy = sum(yoy_changes) / len(yoy_changes)
                combined_analysis += f"""
- **TTM Performance**: Average YoY change of {avg_yoy:.1f}% across all metrics
- **TTM Data Quality**: {ttm_metrics['data_points']} data points in trailing twelve months"""
        
        combined_analysis += "\n\n*Use this analysis to understand both short-term trends and long-term performance patterns.*"
        
        return combined_analysis

    def find_date_column(self, df: pd.DataFrame) -> Optional[str]:
        """Find a date column in the dataframe with enhanced detection logic
        
        This method tries multiple approaches to find a date column:
        1. Create a case-insensitive mapping of column names
        2. Look for columns that are already datetime type
        3. Look for columns with date-related names (date, time, period, etc.)
        4. Try to convert object/string columns that might contain dates
        
        Returns:
            str or None: The name of the date column if found, None otherwise
        """
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

    def calculate_ttm_metrics(self, df: pd.DataFrame, date_col: str, value_cols: List[str]) -> Dict:
        """Calculate Trailing Twelve Months (TTM) metrics from the last date in the series"""
        
        # Ensure date column is datetime
        df = df.copy()
        df[date_col] = pd.to_datetime(df[date_col])
        
        # Sort by date and get the last date
        df_sorted = df.sort_values(by=date_col)
        last_date = df_sorted[date_col].max()
        
        print(f"[TTM LOG] Last date in series: {last_date}")
        
        # Calculate TTM start date (12 months before last date)
        ttm_start_date = last_date - pd.DateOffset(months=12)
        
        print(f"[TTM LOG] TTM period: {ttm_start_date} to {last_date}")
        
        # Filter data for TTM period
        ttm_data = df_sorted[
            (df_sorted[date_col] > ttm_start_date) & 
            (df_sorted[date_col] <= last_date)
        ]
        
        print(f"[TTM LOG] TTM data points: {len(ttm_data)} rows")
        
        # Calculate TTM metrics
        ttm_metrics = {
            "period_start": ttm_start_date,
            "period_end": last_date,
            "data_points": len(ttm_data),
            "metrics": {}
        }
        
        for col in value_cols:
            if col in ttm_data.columns:
                ttm_sum = ttm_data[col].sum()
                ttm_mean = ttm_data[col].mean()
                ttm_std = ttm_data[col].std()
                
                # Calculate YoY comparison if we have data from previous year
                yoy_start = ttm_start_date - pd.DateOffset(months=12)
                yoy_end = last_date - pd.DateOffset(months=12)
                
                yoy_data = df_sorted[
                    (df_sorted[date_col] > yoy_start) & 
                    (df_sorted[date_col] <= yoy_end)
                ]
                
                yoy_sum = yoy_data[col].sum() if len(yoy_data) > 0 else None
                yoy_change = ((ttm_sum - yoy_sum) / yoy_sum * 100) if yoy_sum and yoy_sum != 0 else None
                
                ttm_metrics["metrics"][col] = {
                    "ttm_total": ttm_sum,
                    "ttm_average": ttm_mean,
                    "ttm_std_dev": ttm_std,
                    "yoy_comparison": yoy_sum,
                    "yoy_change_pct": yoy_change
                }
                
                print(f"[TTM LOG] {col}: TTM Total = {ttm_sum:,.2f}, YoY Change = {yoy_change:.2f}%" if yoy_change else f"[TTM LOG] {col}: TTM Total = {ttm_sum:,.2f}")
        
        return ttm_metrics
    
    def generate_ttm_analysis_text(self, ttm_metrics: Dict) -> str:
        """Generate natural language analysis of TTM metrics"""
        
        analysis = []
        
        # Add TTM header
        analysis.append("## [TTM] Trailing Twelve Months Analysis")
        analysis.append(f"*Analysis period: {ttm_metrics['period_start'].strftime('%Y-%m-%d')} to {ttm_metrics['period_end'].strftime('%Y-%m-%d')}*")
        analysis.append(f"*Data points: {ttm_metrics['data_points']} records*\n")
        
        if not ttm_metrics["metrics"]:
            analysis.append("- No numeric metrics available for TTM analysis")
            return "\n".join(analysis)
        
        # Analyze each metric
        for metric_name, metric_data in ttm_metrics["metrics"].items():
            analysis.append(f"### {metric_name.replace('_', ' ').title()}")
            
            # TTM totals and averages
            ttm_total = metric_data["ttm_total"]
            ttm_avg = metric_data["ttm_average"]
            
            analysis.append(f"- **TTM Total**: {ttm_total:,.2f}")
            analysis.append(f"- **TTM Monthly Average**: {ttm_avg:,.2f}")
            
            # Year-over-year comparison
            if metric_data["yoy_change_pct"] is not None:
                yoy_change = metric_data["yoy_change_pct"]
                direction = "increased" if yoy_change > 0 else "decreased"
                analysis.append(f"- **YoY Change**: {direction} by {abs(yoy_change):.1f}%")
                
                # Add performance commentary
                if abs(yoy_change) > 20:
                    performance = "significant" if yoy_change > 0 else "concerning"
                    analysis.append(f"  - This represents a **{performance}** year-over-year change")
                elif abs(yoy_change) > 10:
                    performance = "strong" if yoy_change > 0 else "notable"
                    analysis.append(f"  - This shows **{performance}** year-over-year movement")
                else:
                    analysis.append(f"  - This indicates **stable** year-over-year performance")
            else:
                analysis.append("- **YoY Change**: Insufficient historical data for comparison")
            
            # Volatility analysis
            if metric_data["ttm_std_dev"] is not None and ttm_avg != 0:
                cv = (metric_data["ttm_std_dev"] / ttm_avg) * 100
                if cv > 30:
                    volatility = "high"
                elif cv > 15:
                    volatility = "moderate"
                else:
                    volatility = "low"
                analysis.append(f"- **Volatility**: {volatility} (CV: {cv:.1f}%)")
            
            analysis.append("")
        
        # Add TTM summary insights
        analysis.append("### TTM Key Insights")
        insights = []
        
        # Find the best and worst performing metrics
        yoy_changes = {}
        for metric_name, metric_data in ttm_metrics["metrics"].items():
            if metric_data["yoy_change_pct"] is not None:
                yoy_changes[metric_name] = metric_data["yoy_change_pct"]
        
        if yoy_changes:
            best_metric = max(yoy_changes, key=yoy_changes.get)
            worst_metric = min(yoy_changes, key=yoy_changes.get)
            
            insights.append(f"- **Best TTM Performance**: {best_metric.replace('_', ' ').title()} (+{yoy_changes[best_metric]:.1f}% YoY)")
            insights.append(f"- **Weakest TTM Performance**: {worst_metric.replace('_', ' ').title()} ({yoy_changes[worst_metric]:.1f}% YoY)")
            
            # Overall trend assessment
            avg_change = sum(yoy_changes.values()) / len(yoy_changes)
            if avg_change > 5:
                insights.append(f"- **Overall TTM Trend**: Positive growth trajectory (avg +{avg_change:.1f}% YoY)")
            elif avg_change < -5:
                insights.append(f"- **Overall TTM Trend**: Declining performance (avg {avg_change:.1f}% YoY)")
            else:
                insights.append(f"- **Overall TTM Trend**: Stable performance (avg {avg_change:.1f}% YoY)")
        else:
            insights.append("- Insufficient historical data for comprehensive TTM trend analysis")
        
        analysis.extend(insights)
        
        return "\n".join(analysis)

class ContributionAnalyzer:
    """Contribution analysis for financial data - identifies key contributors to metrics"""
    
    def __init__(self):
        pass

    def perform_pareto_analysis(
        self, 
        df: pd.DataFrame, 
        category_col: str, 
        value_col: str, 
        time_col: Optional[str] = None, 
        threshold: float = 0.8
    ) -> Tuple[pd.DataFrame, Optional[go.Figure]]:
        """
        Performs Pareto analysis (80/20 rule) on the given data.

        Args:
            df (pd.DataFrame): The input data.
            category_col (str): The column with categories to analyze (e.g., 'Product').
            value_col (str): The numeric column with the value to analyze (e.g., 'Sales').
            time_col (str, optional): The time column for time-based analysis. Defaults to None.
            threshold (float, optional): The cumulative contribution threshold. Defaults to 0.8.

        Returns:
            Tuple[pd.DataFrame, Optional[go.Figure]]: A DataFrame with the Pareto analysis and a Plotly figure.
        """
        df = df.copy()
        df[value_col] = pd.to_numeric(df[value_col], errors='coerce')
        df.dropna(subset=[value_col], inplace=True)

        if time_col:
            # Group by the time column and apply Pareto analysis to each period
            # This is a simplified approach; for a full implementation, we would loop through each period
            # For now, we'll analyze the most recent period if it's a datetime column
            if pd.api.types.is_datetime64_any_dtype(df[time_col]):
                latest_period = df[time_col].max()
                df = df[df[time_col] == latest_period]

        # Group by category and sum the values
        analysis_df = df.groupby(category_col)[value_col].sum().reset_index()
        analysis_df = analysis_df.sort_values(by=value_col, ascending=False)
        
        # Calculate cumulative sum and percentage
        analysis_df['cumulative_sum'] = analysis_df[value_col].cumsum()
        total_sum = analysis_df[value_col].sum()
        analysis_df['cumulative_pct'] = analysis_df['cumulative_sum'] / total_sum
        
        # Calculate individual contribution percentage
        analysis_df['individual_pct'] = analysis_df[value_col] / total_sum
        
        # Identify key contributors (those that contribute to reaching threshold)
        key_contributors_mask = analysis_df['cumulative_pct'] <= threshold
        if key_contributors_mask.any():
            # Include one more item that crosses the threshold
            threshold_idx = key_contributors_mask.sum()
            if threshold_idx < len(analysis_df):
                key_contributors_mask.iloc[threshold_idx] = True
        
        analysis_df['is_key_contributor'] = key_contributors_mask
        
        # Add ranking
        analysis_df['rank'] = range(1, len(analysis_df) + 1)

        # Generate plot
        fig = self._plot_pareto(analysis_df, category_col, value_col, threshold)

        return analysis_df, fig

    def _plot_pareto(self, analysis_df: pd.DataFrame, category_col: str, value_col: str, threshold: float) -> go.Figure:
        """Generates a Pareto plot using Plotly."""
        
        fig = go.Figure()

        # Bar chart for the values
        fig.add_trace(go.Bar(
            x=analysis_df[category_col],
            y=analysis_df[value_col],
            name=value_col.title(),
            marker_color=['blue' if key else 'lightblue' for key in analysis_df['is_key_contributor']],
            text=[f"{val:,.0f}" for val in analysis_df[value_col]],
            textposition='auto'
        ))

        # Line chart for the cumulative percentage
        fig.add_trace(go.Scatter(
            x=analysis_df[category_col],
            y=analysis_df['cumulative_pct'],
            name='Cumulative Percentage',
            yaxis='y2',
            mode='lines+markers',
            line=dict(color='red', dash='dash', width=2),
            marker=dict(color='red', size=6),
            text=[f"{pct:.1%}" for pct in analysis_df['cumulative_pct']],
            textposition='top center'
        ))

        # Add threshold line
        threshold_line_y = [threshold] * len(analysis_df)
        fig.add_trace(go.Scatter(
            x=analysis_df[category_col],
            y=threshold_line_y,
            name=f'{threshold:.0%} Threshold',
            yaxis='y2',
            mode='lines',
            line=dict(color='green', dash='dot', width=2),
            showlegend=True
        ))

        # Find the key point where threshold is crossed
        threshold_crossed = analysis_df[analysis_df['cumulative_pct'] >= threshold]
        if not threshold_crossed.empty:
            key_point_index = threshold_crossed.index[0]
            key_point_category = analysis_df.loc[key_point_index, category_col]
            key_point_value = analysis_df.loc[key_point_index, 'cumulative_pct']
            
            # Add annotation for the key point
            fig.add_annotation(
                x=key_point_category,
                y=key_point_value,
                yref='y2',
                text=f"Key Point: {key_point_value:.1%}",
                showarrow=True,
                arrowhead=2,
                arrowcolor='green',
                bgcolor='lightgreen',
                bordercolor='green'
            )

        fig.update_layout(
            title=f'Pareto Analysis: {value_col.title()} by {category_col.title()}',
            xaxis_title=category_col.title(),
            yaxis_title=value_col.title(),
            yaxis2=dict(
                title='Cumulative Percentage',
                overlaying='y',
                side='right',
                tickformat='.0%',
                range=[0, 1.05]
            ),
            legend=dict(x=0, y=1.15, orientation='h'),
            height=500,
            template='plotly_white'
        )
        
        return fig
    
    def perform_contribution_analysis_pandas(
        self, 
        df: pd.DataFrame, 
        category_col: str, 
        value_col: str, 
        time_col: Optional[str] = None,
        threshold: float = 0.8
    ) -> Tuple[pd.DataFrame, Dict[str, any], Optional[go.Figure]]:
        """
        Performs contribution analysis using pandas following the 80/20 rule approach.
        Based on the Medium article methodology.

        Args:
            df (pd.DataFrame): The input data.
            category_col (str): The column with categories to analyze.
            value_col (str): The numeric column with values to analyze.
            time_col (str, optional): The time column for time-based analysis.
            threshold (float, optional): The cumulative contribution threshold. Defaults to 0.8.

        Returns:
            Tuple containing:
            - pd.DataFrame: Analysis results with contribution metrics
            - Dict: Summary statistics and key insights  
            - go.Figure: Pareto chart visualization
        """
        df = df.copy()
        df[value_col] = pd.to_numeric(df[value_col], errors='coerce')
        df.dropna(subset=[value_col], inplace=True)

        # Handle time-based analysis
        if time_col and time_col in df.columns:
            # Convert time column to datetime if needed
            if not pd.api.types.is_datetime64_any_dtype(df[time_col]):
                df[time_col] = pd.to_datetime(df[time_col], errors='coerce')
            
            # Use the most recent period for analysis
            latest_period = df[time_col].max()
            df = df[df[time_col] == latest_period]

        # Step 1: Group by category and sum values (following pandas approach)
        data = df.groupby(category_col)[value_col].sum().reset_index()
        
        # Step 2: Sort in descending order
        data = data.sort_values(by=value_col, ascending=False).reset_index(drop=True)
        
        # Step 3: Calculate cumulative sum and contribution percentage
        total_sum = data[value_col].sum()
        data['cumulative_sum'] = data[value_col].cumsum()
        data['contribution'] = data['cumulative_sum'] / total_sum
        data['individual_contribution'] = data[value_col] / total_sum
        
        # Step 4: Identify key contributors (following the pandas approach)
        key_contributors = data[data['contribution'] <= threshold]
        
        # Include the first item that crosses the threshold if exists
        if len(key_contributors) < len(data):
            threshold_crosser_idx = len(key_contributors)
            key_contributors = pd.concat([
                key_contributors, 
                data.iloc[[threshold_crosser_idx]]
            ], ignore_index=True)
        
        # Mark key contributors
        data['is_key_contributor'] = data.index < len(key_contributors)
        
        # Add ranking
        data['rank'] = range(1, len(data) + 1)
        
        # Step 5: Generate summary statistics and insights
        summary = self._generate_contribution_summary(data, category_col, value_col, threshold)
        
        # Step 6: Create visualization
        fig = self._plot_contribution_analysis(data, category_col, value_col, threshold)
        
        return data, summary, fig
    
    def _generate_contribution_summary(self, data: pd.DataFrame, category_col: str, value_col: str, threshold: float) -> Dict[str, any]:
        """Generate summary statistics and insights from contribution analysis."""
        key_contributors = data[data['is_key_contributor']]
        top_contributor = data.iloc[0]
        
        summary = {
            'total_categories': len(data),
            'key_contributors_count': len(key_contributors),
            'key_contributors_percentage': (len(key_contributors) / len(data)) * 100,
            'key_contributors_value_share': key_contributors['individual_contribution'].sum(),
            'key_contributors_list': key_contributors[category_col].tolist(),
            'top_contributor': top_contributor[category_col],
            'top_contributor_share': top_contributor['individual_contribution'] * 100,
            'insights': [
                f"{len(key_contributors)} out of {len(data)} contributors account for {key_contributors['individual_contribution'].sum():.1%} of total value",
                "Distribution follows Pareto principle pattern",
                f"Top contributor: {top_contributor[category_col]} ({top_contributor['individual_contribution']:.1%})"
            ]
        }
        
        return summary
    
    def _plot_contribution_analysis(self, data: pd.DataFrame, category_col: str, value_col: str, threshold: float) -> go.Figure:
        """Create an interactive Pareto chart for contribution analysis."""
        # Create figure with secondary y-axis
        fig = go.Figure()
        
        # Add bar chart for individual values
        fig.add_trace(
            go.Bar(
                x=data[category_col],
                y=data[value_col],
                name=f'{value_col}',
                marker_color=['red' if is_key else 'lightblue' for is_key in data['is_key_contributor']],
                hovertemplate=f'<b>%{{x}}</b><br>{value_col}: %{{y:,.0f}}<br>Share: %{{customdata:.1%}}<extra></extra>',
                customdata=data['individual_contribution'],
                yaxis='y'
            )
        )
        
        # Add line chart for cumulative percentage
        fig.add_trace(
            go.Scatter(
                x=data[category_col],
                y=data['contribution'],
                mode='lines+markers',
                name='Cumulative %',
                line=dict(color='red', width=3),
                marker=dict(size=8),
                hovertemplate='<b>%{x}</b><br>Cumulative: %{y:.1%}<extra></extra>',
                yaxis='y2'
            )
        )
        
        # Add threshold line
        fig.add_hline(
            y=threshold,
            line_dash="dash",
            line_color="orange",
            annotation_text=f"{threshold:.0%} Threshold",
            annotation_position="bottom right",
            yref='y2'
        )
        
        # Update layout
        fig.update_layout(
            title=f'Contribution Analysis - {category_col} by {value_col} (80/20 Pareto)',
            xaxis_title=category_col,
            yaxis=dict(
                title=f'{value_col}',
                side='left'
            ),
            yaxis2=dict(
                title='Cumulative Contribution (%)',
                side='right',
                overlaying='y',
                tickformat='.0%',
                range=[0, 1.05]
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            height=600,
            template='plotly_white',
            hovermode='x unified'
        )
        
        return fig
    
    def format_contribution_analysis_for_chat(
        self, 
        analysis_df: pd.DataFrame, 
        summary: Dict[str, any], 
        category_col: str, 
        value_col: str
    ) -> str:
        """
        Format contribution analysis results for chat display.
        
        Args:
            analysis_df: The analyzed data with contributions
            summary: Summary statistics from analysis
            category_col: Name of the category column
            value_col: Name of the value column
            
        Returns:
            Formatted string for chat display
        """
        try:
            # Header
            response = f"""📊 **CONTRIBUTION ANALYSIS RESULTS** (80/20 Pareto Principle)

🎯 **ANALYSIS SUMMARY**
• **Total {category_col.title()}s**: {summary['total_categories']}
• **Key Contributors**: {summary['key_contributors_count']} ({summary['key_contributors_percentage']:.1f}%)
• **Value Share of Key Contributors**: {summary['key_contributors_value_share']:.1%}
• **Top Contributor**: {summary['top_contributor']} ({summary['top_contributor_share']:.1%})

"""

            # Top contributors table
            key_contributors = analysis_df[analysis_df['is_key_contributor']].head(10)
            
            response += f"""📈 **TOP CONTRIBUTORS** (Key 80/20 Players)

{'Rank':<4} {'Category':<20} {'Value':<12} {'Share':<8} {'Cumulative':<12}
{'-'*4} {'-'*20} {'-'*12} {'-'*8} {'-'*12}
"""
            
            for idx, row in key_contributors.iterrows():
                rank = idx + 1
                category = str(row[category_col])[:18]  # Truncate long names
                value = f"{row[value_col]:,.0f}"
                share = f"{row['individual_contribution']:.1%}"
                cumulative = f"{row['contribution']:.1%}"
                
                response += f"{rank:<4} {category:<20} {value:<12} {share:<8} {cumulative:<12}\n"
            
            response += "\n\n"
            
            # Insights based on Pareto analysis
            concentration_level = "Strong" if summary['key_contributors_value_share'] > 0.8 else "Moderate" if summary['key_contributors_value_share'] > 0.6 else "Weak"
            
            response += f"""🔍 **KEY INSIGHTS** (Following 80/20 Pareto Principle)

• **Concentration**: {concentration_level} concentration pattern detected
• **Pareto Efficiency**: {summary['key_contributors_percentage']:.1f}% of {category_col.lower()}s drive {summary['key_contributors_value_share']:.1%} of total {value_col.lower()}
• **Strategic Focus**: Top 3 contributors account for {analysis_df.head(3)['contribution'].iloc[-1]:.1%} of total value

"""

            # Business recommendations
            if summary['key_contributors_value_share'] > 0.8:
                response += f"""💡 **STRATEGIC RECOMMENDATIONS**

🎯 **HIGH PRIORITY**:
• Focus resources on top {min(3, summary['key_contributors_count'])} contributors
• Protect and expand relationships with key {category_col.lower()}s
• Analyze success factors of top performers

⚠️ **RISK MANAGEMENT**:
• High concentration creates dependency risk
• Diversification strategy may be needed
• Monitor top contributor stability closely

"""
            else:
                response += f"""💡 **STRATEGIC RECOMMENDATIONS**

📊 **BALANCED PORTFOLIO**:
• More evenly distributed contribution pattern
• Opportunities for growth across multiple {category_col.lower()}s
• Consider targeted improvement initiatives

🚀 **OPTIMIZATION OPPORTUNITIES**:
• Identify potential for top performers to increase share
• Analyze underperforming {category_col.lower()}s for improvement potential
• Balanced growth strategy recommended

"""

            # Bottom performers section
            bottom_performers = analysis_df[~analysis_df['is_key_contributor']]
            if not bottom_performers.empty:
                response += f"""⚠️ **UNDERPERFORMING {category_col.upper()}S** ({len(bottom_performers)} items)

Bottom 3 contributors account for only {bottom_performers.tail(3)['individual_contribution'].sum():.1%} of total {value_col.lower()}

Consider:
• Performance improvement programs
• Resource reallocation decisions  
• Cost-benefit analysis for continued investment

"""

            response += f"""---
✅ **Analysis Complete** | Following pandas-based 80/20 methodology from Medium article
📊 Data sorted by {value_col.lower()} in descending order | Cumulative percentages calculated using pandas cumsum()
🎯 Key contributors identified at 80% threshold | Charts available for visual analysis
"""

            return response
            
        except Exception as e:
            return f"❌ Error formatting contribution analysis: {str(e)}"

# Initialize the chat system
chat_system = AriaFinancialChat()

def process_query(file, question, history):
    """Process user query and return response"""
    
    if not question.strip():
        return history, history, "Please enter a question about your financial data.", None
    
    # Analyze data and get response
    response, status = chat_system.analyze_data(file, question)
    
    # Update chat history
    history.append({"role": "user", "content": question})
    history.append({"role": "assistant", "content": response})
    
    # Return current data for grid display
    current_data = chat_system.current_data if chat_system.current_data is not None else None
    
    return history, history, status, current_data

def process_query_enhanced(file, question, history, use_llamaindex=False):
    """Enhanced process query with optional LlamaIndex integration"""
    
    if not question.strip():
        return history, history, "Please enter a question about your financial data.", None
    
    # Choose analysis method based on user preference
    if use_llamaindex and LLAMAINDEX_AVAILABLE:
        # Use enhanced analysis with LlamaIndex
        response, status = chat_system.enhanced_analysis_with_llamaindex(file, question)
    else:
        # Use standard Aria Sterling analysis
        response, status = chat_system.analyze_data(file, question)
    
    # Update chat history
    history.append({"role": "user", "content": question})
    history.append({"role": "assistant", "content": response})
    
    # Return current data for grid display
    current_data = chat_system.current_data if chat_system.current_data is not None else None
    
    return history, history, status, current_data

def load_data_for_grid(file):
    """Load data specifically for grid display"""
    print(f"[DEBUG] load_data_for_grid called with file: {file}")
    print(f"[DEBUG] File type: {type(file)}")
    
    if file is None:
        print("[DEBUG] load_data_for_grid received None file")
        return None
    
    try:
        if hasattr(file, 'name'):
            print(f"[DEBUG] Loading from file path: {file.name}")
            df = pd.read_csv(file.name)
        elif isinstance(file, str):
            print(f"[DEBUG] Loading from string path: {file}")
            df = pd.read_csv(file)
        else:
            print(f"[DEBUG] Loading from file content (decoded)")
            df = pd.read_csv(io.StringIO(file.decode('utf-8')))
        
        
        print(f"[SUCCESS] Successfully loaded DataFrame - Shape: {df.shape}, Columns: {list(df.columns)}")
        
        # Store in chat system for analysis
        chat_system.current_data = df
        return df
    except Exception as e:
        print(f"[ERROR] Error loading data: {e}")
        import traceback
        traceback.print_exc()
        return None


def check_system_status():
    """Check system status including LlamaIndex availability"""
    ollama_available = chat_system.check_ollama_connection()
    llamaindex_available = (
        LLAMAINDEX_AVAILABLE and 
        chat_system.llamaindex_processor and 
        chat_system.llamaindex_processor.check_availability()
    )
    
    status_parts = []
    
    # Ollama status
    if ollama_available:
        status_parts.append("[SUCCESS] **Gemma3** Active")
    else:
        status_parts.append("[WARNING] **Gemma3** Offline (Run: `ollama serve`)")
    
    # LlamaIndex status
    if llamaindex_available:
        status_parts.append("[SUCCESS] **LlamaIndex** Ready")
    elif LLAMAINDEX_AVAILABLE:
        status_parts.append("[WARNING] **LlamaIndex** Available but not connected")
    else:
        status_parts.append("[INFO] **LlamaIndex** Not installed (`pip install llama-index`)")
    
    # Enhancement note
    if ollama_available and llamaindex_available:
        enhancement = "\n\n[ENHANCED] **Full Enhancement Mode**: Both Gemma3 conversational AI and LlamaIndex structured extraction available for maximum analytical power!"
    elif ollama_available:
        enhancement = "\n\n[BOT] **Standard Mode**: Gemma3 conversational analysis active. Install LlamaIndex for enhanced document processing."
    else:
        enhancement = "\n\n[BASIC] **Basic Mode**: Using built-in analysis. Enable Gemma3 and LlamaIndex for full AI capabilities."
    
    return " | ".join(status_parts) + enhancement

# Create Gradio interface
def create_interface():
    """Create the Gradio interface - Pure chat-focused with all analysis inline"""
    
    with gr.Blocks(
        title="VariancePro - Financial Analysis Chat",
        theme=gr.themes.Soft(),
        css="""
        .container { max-width: 1000px; margin: auto; }
        .chat-container { height: 600px; overflow-y: auto; }
        """
    ) as interface:
        
        gr.Markdown("# 🚀 VariancePro - Financial Analysis Chat")
        gr.Markdown("### 📊 Powered by Gemma3 via Ollama | All analysis appears in chat conversation")
        
        # Single column layout - pure chat interface
        with gr.Column():
            # File upload at the top
            file_input = gr.File(
                label="📁 Upload Financial Data (CSV) - Analysis will appear in chat below",
                file_types=[".csv"],
                type="filepath",
                file_count="single"
            )
            
            # Main chat interface - all analysis appears here
            chatbot = gr.Chatbot(
                label="💬 Financial Analysis Chat - All results appear here inline",
                height=600,
                show_label=True,
                type="messages",
                elem_classes=["chat-container"]
            )
            
            # User input
            user_input = gr.Textbox(
                label="💭 Ask about your financial data:",
                placeholder="e.g., 'Perform contribution analysis', 'Analyze sales variance by region', 'Show 80/20 Pareto analysis'",
                lines=2
            )
            
            # Buttons row
            with gr.Row():
                submit_btn = gr.Button("🔍 Analyze", variant="primary")
                clear_btn = gr.Button("🗑️ Clear Chat")
                status_btn = gr.Button("📊 System Status")
            
            # Tips section - compact
            gr.Markdown("""
            💡 **Tips**: Upload CSV → Ask questions → All analysis (including contribution analysis, charts, insights) appears in chat above
            
            🎯 **Sample Questions**: "Perform contribution analysis", "Show me 80/20 analysis", "Analyze budget vs actual", "Generate Python code"
            """)
        
        # State for chat history only - all analysis goes into chat
        chat_state = gr.State([])
        
        # Event handlers - ALL ANALYSIS APPEARS IN CHAT
        def submit_query(file, question, history, chat_state):
            """Handle user queries - all results appear in chat conversation"""
            try:
                # Process the query using existing logic
                new_history, new_chat_state, status, current_data = process_query(file, question, chat_state)
                
                # All analysis appears in the new_history (chat conversation)
                # No separate panels needed
                return new_history, "", new_chat_state
                
            except Exception as e:
                error_msg = f"❌ Error processing query: {str(e)}"
                updated_history = (history or []) + [
                    {"role": "user", "content": question},
                    {"role": "assistant", "content": error_msg}
                ]
                return updated_history, "", chat_state
        
        def clear_chat():
            """Clear chat history"""
            chat_system.chat_history = []
            return [], []
        
        def show_system_status():
            """Show system status in chat"""
            status = check_system_status()
            status_message = f"""
📊 **System Status Check**

{status}

✅ **Interface**: Pure chat mode - all analysis appears inline
💡 **Tip**: Upload CSV and ask for contribution analysis, 80/20 Pareto analysis, or any financial insights
"""
            return [{"role": "assistant", "content": status_message}], [{"role": "assistant", "content": status_message}]
        
        def initialize_chat_with_analysis(file):
            """Initialize chat with immediate comprehensive analysis when file is uploaded"""
            if file is None:
                return [], []
                
            try:
                # Load the data for analysis
                df = load_data_for_grid(file)
                if df is None:
                    error_msg = "❌ **Error**: Could not load CSV file. Please check the file format."
                    return [{"role": "assistant", "content": error_msg}], [{"role": "assistant", "content": error_msg}]
                
                # Generate comprehensive initial analysis including contribution analysis
                initial_analysis = f"""
📁 **File Uploaded Successfully!**

📊 **Dataset Overview**:
- **Rows**: {len(df):,}
- **Columns**: {len(df.columns)}
- **Numeric Columns**: {len(df.select_dtypes(include=[np.number]).columns)}
- **Text Columns**: {len(df.select_dtypes(include=['object']).columns)}
- **Date Columns**: {len(df.select_dtypes(include=['datetime64']).columns)}

🔍 **Column Names**: {', '.join(df.columns.tolist())}

---

🤖 **Automatic Analysis Ready**

I'm **Aria Sterling**, your financial analyst. I've loaded your data and I'm ready to perform comprehensive analysis including:

• 📈 **Contribution Analysis** (80/20 Pareto analysis)
• 📊 **Time-series Analysis** (if date columns detected)
• 💰 **Budget vs Actual Variance** (if budget/actual columns found)
• 📋 **Statistical Summary** 
• 🐍 **Python Code Generation**

🎯 **Try These Questions**:
- "Perform contribution analysis"
- "Show me 80/20 Pareto analysis" 
- "Analyze budget vs actual variance"
- "Generate Python code for this data"
- "What are the key trends?"

💡 **What would you like to analyze first?**
"""
                
                # Try to auto-detect and suggest specific analysis based on columns
                columns = df.columns.tolist()
                suggestions = []
                
                # Check for contribution analysis opportunities
                numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
                text_cols = df.select_dtypes(include=['object']).columns.tolist()
                
                if len(numeric_cols) > 0 and len(text_cols) > 0:
                    suggestions.append(f"🎯 **Suggested**: Try 'Perform contribution analysis on {numeric_cols[0]} by {text_cols[0]}'")
                
                # Check for sales/revenue columns
                sales_cols = [col for col in columns if any(term in col.lower() for term in ['sales', 'revenue', 'income'])]
                if sales_cols:
                    suggestions.append(f"💰 **Suggested**: Analyze sales patterns: 'Show contribution analysis for {sales_cols[0]}'")
                
                # Check for budget/actual columns
                budget_cols = [col for col in columns if 'budget' in col.lower()]
                actual_cols = [col for col in columns if 'actual' in col.lower()]
                if budget_cols and actual_cols:
                    suggestions.append(f"📊 **Suggested**: Variance analysis: 'Compare {budget_cols[0]} vs {actual_cols[0]}'")
                
                if suggestions:
                    initial_analysis += "\n\n🔍 **Smart Suggestions Based on Your Data**:\n" + "\n".join(suggestions)
                
                # AUTOMATICALLY GENERATE AND INCLUDE TIMESCALE ANALYSIS IN INITIAL UPLOAD
                try:
                    # Initialize chat system for this analysis
                    if not hasattr(chat_system, 'timescale_analyzer'):
                        chat_system.timescale_analyzer = TimescaleAnalyzer()
                    
                    # Generate timescale analysis
                    timescale_analysis = chat_system.timescale_analyzer.generate_timescale_analysis(df)
                    
                    if timescale_analysis and "No date column found" not in timescale_analysis:
                        initial_analysis += "\n\n" + "="*50
                        initial_analysis += "\n📈 **AUTOMATIC TIMESCALE ANALYSIS**"
                        initial_analysis += "\n" + "="*50
                        initial_analysis += "\n" + timescale_analysis
                    else:
                        initial_analysis += "\n\n💡 **Note**: No date column detected for timescale analysis. Your data will still get comprehensive analysis!"
                        
                except Exception as e:
                    initial_analysis += f"\n\n⚠️ **Timescale Analysis**: Could not generate automatically due to: {str(e)}"
                
                initial_chat = [{"role": "assistant", "content": initial_analysis}]
                return initial_chat, initial_chat
                
            except Exception as e:
                error_msg = f"❌ **Error analyzing uploaded file**: {str(e)}"
                print(f"Error initializing chat: {error_msg}")
                initial_chat = [{"role": "assistant", "content": error_msg}]
                return initial_chat, initial_chat
        
        # Connect events - simplified for chat-only interface
        submit_btn.click(
            submit_query,
            inputs=[file_input, user_input, chatbot, chat_state],
            outputs=[chatbot, user_input, chat_state]
        )
        
        user_input.submit(
            submit_query,
            inputs=[file_input, user_input, chatbot, chat_state],
            outputs=[chatbot, user_input, chat_state]
        )
        
        # Initialize chat with comprehensive analysis on file upload
        file_input.upload(
            initialize_chat_with_analysis,
            inputs=[file_input],
            outputs=[chatbot, chat_state]
        )
        
        clear_btn.click(
            clear_chat,
            outputs=[chatbot, chat_state]
        )
        
        status_btn.click(
            show_system_status,
            outputs=[chatbot, chat_state]
        )
        
        # Initial welcome message
        def show_welcome():
            welcome_msg = """
🚀 **Welcome to VariancePro Financial Analysis Chat!**

I'm **Aria Sterling**, your AI financial analyst. 

📋 **How it works**:
1. 📁 **Upload** your CSV financial data above
2. 💬 **Ask** questions in the chat box
3. 📊 **Get** comprehensive analysis with charts, insights, and Python code

🎯 **I specialize in**:
• 📈 **Contribution Analysis** (80/20 Pareto principle)
• 📊 **Budget vs Actual Variance Analysis** 
• 📈 **Time-series Trends & Forecasting**
• 🐍 **Python Code Generation**
• 💡 **Business Insights & Recommendations**

🔥 **All analysis appears right here in this chat - no separate panels!**

**Ready to get started? Upload your CSV file above! 📁⬆️**
"""
            return [{"role": "assistant", "content": welcome_msg}]
        
        interface.load(
            show_welcome,
            outputs=[chatbot]
        )
    
    return interface

if __name__ == "__main__":
    # Create and launch the interface
    demo = create_interface()
    
    print("Starting VariancePro Financial Chat with Gemma3...")
    print("Upload your CSV data and start asking questions!")
    
    demo.launch(
        server_name="0.0.0.0",    # Listen on all network interfaces
        server_port=7865,         # Changed port to avoid conflict
        share=False,
        debug=False,
        show_error=True
    )
