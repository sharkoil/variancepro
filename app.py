import gradio as gr
import pandas as pd
import numpy as np
import requests
import json
import io
import base64
import traceback
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
        self.model_name = "deepseek-coder:6.7b" # Use locally available deepseek-coder model
        self.ollama_url = "http://localhost:11434"
        self.current_data = None
        self.chat_history = []  # Initialize chat history
        
        # Initialize chat handler for DeepSeek integration
        self.chat_handler = ChatHandler()
        
        # Initialize timescale analyzer
        self.timescale_analyzer = TimescaleAnalyzer()
        
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
                
                # Look specifically for deepseek-coder:6.7b
                if "deepseek-coder:6.7b" in available_models:
                    self.model_name = "deepseek-coder:6.7b"
                    print(f"[SUCCESS] Using model: {self.model_name}")
                    return True
                
                # Also check for any model containing deepseek, phi, llama, or mistral as fallbacks
                for model_name in available_models:
                    if any(name in model_name for name in ["deepseek", "phi", "llama", "mistral"]):
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
        """Query LLM model via Ollama using Aria Sterling persona"""
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
                    "num_ctx": 8192  # Increased context window for DeepSeek Coder
                }
            }
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=180  # Extended timeout for large Phi4 model (3 minutes)
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "").strip()
            else:
                return f"Error: Phi4 returned status {response.status_code}"
                
        except requests.exceptions.Timeout:
            return "[WARNING] Phi4 is processing your complex financial query. Large models need more time for detailed analysis. The response will appear shortly, or try breaking your question into smaller parts."
        except requests.exceptions.ConnectionError:
            return "[ERROR] Cannot connect to Ollama. Please ensure Ollama is running with: `ollama serve`"
        except Exception as e:
            return f"Error communicating with Phi4: {str(e)}"
    
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

## Data Patterns & Insights  
- Notable patterns, trends, or anomalies
- Statistical relationships between variables
- Risk factors or opportunities identified

## Business Impact
- Strategic implications of the findings
- Impact on business performance and decisions
- Areas requiring immediate attention

## Python Code (if relevant)
- Practical code snippets for deeper analysis
- Statistical analysis methods

## Recommendations
- Specific actionable steps
- Areas for further investigation
- Risk mitigation strategies

Provide clear, concise responses using professional financial terminology. Make recommendations data-driven and actionable."""
        
        return prompt
    
    def analyze_data(self, file_data, user_question: str) -> Tuple[str, str]:
        """Analyze uploaded data and answer user questions using ChatHandler"""
        
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
            
            # Use ChatHandler to generate response
            response = self.chat_handler.generate_response(user_question, df)
            
            if self.chat_handler.use_llm:
                status = f"[SUCCESS] Using DeepSeek LLM"
            else:
                status = "[WARNING] LLM not available - using built-in analysis"
            
            # Add to chat history
            self.chat_history.append({
                "user": user_question,
                "assistant": response,
                "timestamp": datetime.now()
            })
            
            return response, status
            
        except Exception as e:
            return f"Error processing data: {str(e)}", "[ERROR] Processing Error"
    
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
2. Verify deepseek-coder is installed: `ollama list`
3. If missing, install: `ollama pull deepseek-coder:6.7b`"""
        
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
        
        # Product/category columns  
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
        aria_system_prompt = """**[SYSTEM] System Prompt: Financial Analyst Persona**

You are **Aria Sterling**, a world-class financial analyst and strategist. You possess exceptional quantitative reasoning, market intuition, and business acumen. You analyze financial data with precision, distill market signals into actionable insights, and communicate with clarity, confidence, and charisma.

### [CORE] Core Attributes
- **Brilliant and Analytical**: Expert in time series analysis, financial forecasting, valuation, corporate finance, and macroeconomic interpretation.
- **Data-Driven**: Extracts insights from raw data using rigorous statistical and financial techniques. You speak in ratios, deltas, time horizons, and benchmarks.
- **Fluent in Market Language**: Speaks in sharp, well-structured financial commentary—think investor calls, analyst briefings, earnings breakdowns, pitch decks.
- **Human-Centric Communicator**: Makes complex concepts accessible to both CFOs and startup founders. Adjusts tone and vocabulary based on audience's financial fluency.
- **Forward-Looking**: Scans for inflection points, tailwinds/headwinds, and market signals that influence KPIs and company valuations.

### [KNOWLEDGE] Knowledge Domains
- Financial statements, KPIs, profitability analysis
- Forecasting, TTM, YoY, QoQ analysis
- Time series analysis and growth metrics (CAGR, MoM, rolling averages)
- Corporate strategy, M&A basics, capital structure
- Industry benchmarking and competitive analysis
- Equities, credit markets, macroeconomic indicators

### [STYLE] Communication Style
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
        status_parts.append("[SUCCESS] **DeepSeek Coder** Active")
    else:
        status_parts.append("[WARNING] **DeepSeek Coder** Offline (Run: `ollama serve`)")
    
    # LlamaIndex status
    if llamaindex_available:
        status_parts.append("[SUCCESS] **LlamaIndex** Ready")
    elif LLAMAINDEX_AVAILABLE:
        status_parts.append("[WARNING] **LlamaIndex** Available but not connected")
    else:
        status_parts.append("[INFO] **LlamaIndex** Not installed (`pip install llama-index`)")
    
    # Enhancement note
    if ollama_available and llamaindex_available:
        enhancement = "\n\n[ENHANCED] **Full Enhancement Mode**: Both DeepSeek Coder conversational AI and LlamaIndex structured extraction available for maximum analytical power!"
    elif ollama_available:
        enhancement = "\n\n[BOT] **Standard Mode**: DeepSeek Coder conversational analysis active. Install LlamaIndex for enhanced document processing."
    else:
        enhancement = "\n\n[BASIC] **Basic Mode**: Using built-in analysis. Enable DeepSeek Coder and LlamaIndex for full AI capabilities."
    
    return " | ".join(status_parts) + enhancement

# Create Gradio interface
def create_interface():
    """Create the Gradio interface"""
    
    with gr.Blocks(
        title="VariancePro - DeepSeek Financial Chat",
        theme=gr.themes.Soft(),
        css="""
        .container { max-width: 1200px; margin: auto; }
        .status-box { background: #f0f8ff; padding: 10px; border-radius: 5px; margin: 10px 0; }
        .chat-container { height: 400px; overflow-y: auto; }
        .data-grid { max-height: 500px; overflow: auto; }
        """
    ) as interface:
        
        gr.Markdown("# VariancePro - Financial Data Analysis Chat")
        gr.Markdown("### Powered by DeepSeek Coder via Ollama")
        
        # Create tabs for different views - ONLY 2 TABS
        with gr.Tabs():
            # Chat Analysis Tab
            with gr.TabItem("[CHAT] Chat Analysis"):
                with gr.Row():
                    with gr.Column(scale=2):
                        # File upload
                        file_input = gr.File(
                            label="[UPLOAD] Upload Financial Data (CSV)",
                            file_types=[".csv"],
                            type="filepath",
                            file_count="single"
                        )
                        
                        # Chat interface
                        chatbot = gr.Chatbot(
                            label="[CHAT] Financial Analysis Chat",
                            height=400,
                            show_label=True,
                            type="messages"
                        )
                        
                        # User input
                        user_input = gr.Textbox(
                            label="Ask about your financial data:",
                            placeholder="e.g., 'Analyze sales variance by region and suggest Python code'",
                            lines=2
                        )
                        
                        # Buttons
                        with gr.Row():
                            submit_btn = gr.Button("[SEARCH] Analyze", variant="primary")
                            clear_btn = gr.Button("[CLEAR] Clear Chat")
                    
                    with gr.Column(scale=1):
                        # Status panel
                        status_display = gr.Textbox(
                            label="[STATUS] System Status",
                            value=check_system_status(),
                            interactive=False,
                            lines=2
                        )
                        
                        # Dynamic sample questions based on data
                        suggested_questions = gr.Markdown(
                            value=chat_system.get_default_suggested_questions(),
                            label="[TIPS] Suggested Questions"
                        )
                        
                        # Refresh status button
                        refresh_btn = gr.Button("[REFRESH] Refresh Status")
            
            # Data Grid Tab
            with gr.TabItem("[DATA] Data View"):
                with gr.Row():
                    with gr.Column(scale=1):
                        # File upload for data view (shared with chat)
                        gr.Markdown("### [INFO] Data Overview")
                        gr.Markdown("Upload a CSV file in the Chat Analysis tab to view the data here.")
                        
                        # Data info panel
                        data_info = gr.Textbox(
                            label="[INFO] Dataset Information",
                            value="No data loaded yet. Please upload a CSV file in the Chat Analysis tab.",
                            interactive=False,
                            lines=3
                        )
                        
                        # Data grid
                        data_grid = gr.DataFrame(
                            label="[GRID] Data Grid",
                            interactive=False,
                            wrap=True,
                            elem_classes=["data-grid"]
                        )
                    
                    with gr.Column(scale=1):
                        # Automatic timescale analysis
                        gr.Markdown("### Automatic Timescale Analysis")
                        gr.Markdown("*Comprehensive period-over-period analysis generated automatically*")
                        
                        auto_analysis_display = gr.Markdown(
                            label="[AUTO] Automatic Analysis",
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
                info_text = f"""[DATA] Dataset Loaded: {len(current_data)} rows × {len(current_data.columns)} columns

[NUMERIC] Numeric Columns: {len(current_data.select_dtypes(include=[np.number]).columns)}
[TEXT] Text Columns: {len(current_data.select_dtypes(include=['object']).columns)}
[DATE] Date Columns: {len(current_data.select_dtypes(include=['datetime64']).columns)}

[MEMORY] Memory Usage: {current_data.memory_usage(deep=True).sum() / 1024:.1f} KB"""
                return new_history, "", new_chat_state, status, info_text, current_data
            else:
                return new_history, "", new_chat_state, status, "No data loaded", None
        
        def update_data_view(file):
            """Update data view when file is uploaded - includes automatic timescale analysis"""
            if file is None:
                return "No data loaded yet. Please upload a CSV file.", None, "Please upload data to see automatic analysis."
            
            df = load_data_for_grid(file)
            if df is not None:
                # Basic data info
                info_text = f"""[DATA] Dataset Loaded: {len(df)} rows × {len(df.columns)} columns
                
[NUMERIC] Numeric Columns: {len(df.select_dtypes(include=[np.number]).columns)}
[TEXT] Text Columns: {len(df.select_dtypes(include=['object']).columns)}
[DATE] Date Columns: {len(df.select_dtypes(include=['datetime64']).columns)}

[MEMORY] Memory Usage: {df.memory_usage(deep=True).sum() / 1024:.1f} KB

[COLUMNS] Column Names: {', '.join(df.columns.tolist())}"""
                
                # Generate automatic timescale analysis
                print("Generating automatic timescale analysis...")
                auto_analysis = chat_system.generate_automatic_timescale_analysis(df)
                
                return info_text, df, auto_analysis
            else:
                return "Error loading data. Please check your CSV file.", None, "Unable to generate analysis due to data loading error."
        
        def clear_chat():
            chat_system.chat_history = []
            return [], []
        
        def update_suggested_questions(file):
            """Update suggested questions based on uploaded data"""
            if file is None:
                return chat_system.get_default_suggested_questions()
            
            df = load_data_for_grid(file)
            if df is not None:
                return chat_system.generate_suggested_questions(df)
            else:
                return chat_system.get_default_suggested_questions()
        
        def initialize_chat_with_system_message(file):
            """Initialize the chat with immediate LLM analysis when a file is uploaded"""
            if file is None:
                return [], []
                
            try:
                # Read the CSV file as raw text and pass directly to LLM
                if hasattr(file, 'name'):
                    with open(file.name, 'r', encoding='utf-8') as f:
                        csv_content = f.read()
                elif isinstance(file, str):
                    with open(file, 'r', encoding='utf-8') as f:
                        csv_content = f.read()
                else:
                    csv_content = file.decode('utf-8')
                
                # Create system prompt for immediate preliminary analysis
                system_prompt = """You are **Aria Sterling**, a world-class financial analyst. A CSV file has just been uploaded. Please provide immediate preliminary analysis of this financial data.

UPLOADED CSV DATA:
""" + csv_content + """

Please provide:
1. **Quick Overview**: What type of financial data is this?
2. **Key Columns**: Identify the main financial metrics
3. **Data Quality**: Any obvious issues or patterns?
4. **Initial Insights**: 3-4 immediate observations
5. **Suggested Questions**: What should we analyze next?

Respond as Aria Sterling with your characteristic financial expertise and confidence."""
                
                # Get immediate LLM response
                if chat_system.chat_handler.use_llm:
                    aria_analysis = chat_system.query_ollama(system_prompt)
                else:
                    aria_analysis = "[UPLOAD] **File Uploaded Successfully!**\n\nI've received your CSV file and I'm ready to analyze it. Since the LLM is not available, please ask specific questions about your data and I'll provide built-in analysis.\n\n[TIP] **Tip**: Try asking 'Summarize this dataset' or upload the file and ask specific questions about trends, variances, or metrics."
                
                # Return the chat history with the immediate analysis
                initial_chat = [{"role": "assistant", "content": aria_analysis}]
                
                return initial_chat, initial_chat
            except Exception as e:
                error_msg = f"Error analyzing uploaded file: {str(e)}"
                print(f"Error initializing chat: {error_msg}")
                initial_chat = [{"role": "assistant", "content": error_msg}]
                return initial_chat, initial_chat
        
        # Connect events
        submit_btn.click(
            submit_query,
            inputs=[file_input, user_input, chatbot, chat_state],
            outputs=[chatbot, user_input, chat_state, status_display, data_info, data_grid]
        )
        
        user_input.submit(
            submit_query,
            inputs=[file_input, user_input, chatbot, chat_state],
            outputs=[chatbot, user_input, chat_state, status_display, data_info, data_grid]
        )
        
        def update_all_data_views(file):
            """Update all data-related views when file is uploaded"""
            data_info, data_grid, auto_analysis = update_data_view(file)
            questions = update_suggested_questions(file)
            return data_info, data_grid, questions, auto_analysis
        
        # Update data view and suggested questions when file is uploaded
        file_input.upload(
            update_all_data_views,
            inputs=[file_input],
            outputs=[data_info, data_grid, suggested_questions, auto_analysis_display]
        )
        
        # Initialize chat with system message on file upload
        file_input.upload(
            initialize_chat_with_system_message,
            inputs=[file_input],
            outputs=[chatbot, chat_state]
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
    
    print("Starting VariancePro Financial Chat with DeepSeek Coder...")
    print("Upload your CSV data and start asking questions!")
    
    demo.launch(
        server_name="127.0.0.1",
        server_port=7864,
        share=False,
        debug=False,
        show_error=True
    )
