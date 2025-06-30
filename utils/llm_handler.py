import requests
import json
import os
from typing import Optional, Dict, Any
import pandas as pd
import numpy as np

class LLMHandler:
    """Handles integration with various LLM models via multiple backends"""
    
    def __init__(self, backend="ollama", model_name="deepseek-coder:6.7b"):
        self.backend = backend
        self.model_name = model_name
        self.base_url = "http://localhost:11434"  # Default Ollama port
        self.session = requests.Session()
        
        # Model-specific configurations
        self.model_configs = {
            "phi3": {
                "temperature": 0.3,
                "top_k": 40,
                "top_p": 0.9,
                "num_predict": 500,
                "system_prompt": "You are a professional financial data analyst assistant."
            },
            "deepseek-coder:6.7b": {
                "temperature": 0.1,
                "top_k": 40,
                "top_p": 0.9,
                "num_predict": 1024,
                "system_prompt": "You are an expert financial data analyst with deep knowledge of financial metrics and market analysis."
            }
        }
        
    def is_available(self) -> bool:
        """Check if the LLM backend is available"""
        try:
            if self.backend == "ollama":
                response = self.session.get(f"{self.base_url}/api/tags", timeout=5)
                return response.status_code == 200
            return False
        except:
            return False
    
    def generate_financial_response(self, user_query: str, data_context: str, data_summary: Dict[str, Any]) -> str:
        """Generate intelligent response using LLM with financial data context"""
        
        if not self.is_available():
            return self._fallback_response(user_query, data_context, data_summary)
        
        # Create a comprehensive prompt for financial analysis
        prompt = self._create_financial_prompt(user_query, data_context, data_summary)
        
        try:
            if self.backend == "ollama":
                return self._query_ollama(prompt)
            else:
                return self._fallback_response(user_query, data_context, data_summary)
        except Exception as e:
            print(f"LLM Error: {e}")
            return self._fallback_response(user_query, data_context, data_summary)
    def _create_financial_prompt(self, user_query: str, data_context: str, data_summary: Dict[str, Any]) -> str:
        """Create a comprehensive prompt optimized for financial analysis"""
        
        config = self.model_configs.get(self.model_name, self.model_configs["deepseek-coder:6.7b"])
        system_prompt = config["system_prompt"]
        
        # Enhanced prompt for LLM with code-focused analysis
        prompt = f"""{system_prompt}

You are analyzing financial data and can provide both analytical insights and code suggestions for deeper analysis.

DATASET CONTEXT:
{data_context}

DATASET SUMMARY:
- Total Records: {data_summary.get('total_rows', 'N/A')}
- Columns: {data_summary.get('total_columns', 'N/A')} 
- Numeric Fields: {data_summary.get('numeric_columns', 'N/A')}
- Key Metrics: {data_summary.get('key_metrics', 'N/A')}
- Date Range: {data_summary.get('date_range', 'N/A')}

USER QUESTION: {user_query}

Please provide:
1. **Direct Answer**: Address the specific question with data-driven insights
2. **Key Findings**: Highlight the most important patterns or trends
3. **Business Impact**: Explain what these findings mean for business decisions
4. **Code Suggestions** (if applicable): Suggest Python/pandas code for deeper analysis
5. **Recommendations**: Actionable next steps based on the analysis

Format your response with clear sections and use financial terminology appropriately. If the question involves technical analysis, provide relevant code snippets using pandas/numpy.

ANALYSIS:"""
        
        return prompt
    def _query_ollama(self, prompt: str) -> str:
        """Query Ollama API with model-specific configurations"""
        try:
            config = self.model_configs.get(self.model_name, self.model_configs["deepseek-coder:6.7b"])
            
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": config["temperature"],
                    "top_k": config["top_k"], 
                    "top_p": config["top_p"],
                    "num_predict": config["num_predict"]
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=45  # Longer timeout for complex financial analysis
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "").strip()
            else:
                return f"Error: Unable to get response from {self.model_name} (Status: {response.status_code})"
                
        except Exception as e:
            return f"Error communicating with {self.model_name}: {str(e)}"
    def _fallback_response(self, user_query: str, data_context: str, data_summary: Dict[str, Any]) -> str:
        """Fallback response when LLM is not available"""
        return f"""🤖 **Enhanced Analysis** (LLM offline - using built-in intelligence):

**Your Question**: {user_query}

**Data Overview**: 
- Dataset: {data_summary.get('total_rows', 0)} rows, {data_summary.get('total_columns', 0)} columns
- Numeric fields: {data_summary.get('numeric_columns', 0)}

**Quick Insights**:
{data_context[:300]}...

💡 **Note**: For AI-powered analysis with code suggestions, ensure Ollama is running with the appropriate model.
To enable: Run `ollama pull deepseek-coder:6.7b` in terminal, then restart the app.

🔧 **Available Models**: deepseek-coder:6.7b (recommended), phi3"""

    def get_model_status(self) -> Dict[str, Any]:
        """Get current model status and available models"""
        if not self.is_available():
            return {
                "status": "offline",
                "backend": self.backend,
                "message": "LLM backend not available. Install Ollama and pull deepseek-coder:6.7b model."
            }
        
        try:
            if self.backend == "ollama":
                response = self.session.get(f"{self.base_url}/api/tags")
                models = response.json().get("models", [])
                model_names = [model["name"] for model in models]
                
                return {
                    "status": "online",
                    "backend": self.backend,
                    "available_models": model_names,
                    "current_model": self.model_name,
                    "model_loaded": self.model_name in model_names
                }
        except:
            pass
        
        return {
            "status": "error", 
            "backend": self.backend,
            "message": "Unable to get model status"
        }

class DataContextBuilder:
    """Builds context from pandas DataFrame for LLM analysis"""
    
    @staticmethod
    def build_context(df: pd.DataFrame, max_rows: int = 5) -> tuple[str, Dict[str, Any]]:
        """Build comprehensive context from DataFrame"""
        
        if df is None or df.empty:
            return "No data available", {}
        
        # Basic info
        total_rows = len(df)
        total_columns = len(df.columns)
        
        # Column analysis
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        text_cols = df.select_dtypes(include=['object']).columns.tolist()
        date_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
        
        # Sample data
        sample_data = df.head(max_rows).to_string()
        
        # Summary statistics for numeric columns
        numeric_summary = ""
        if numeric_cols:
            stats = df[numeric_cols].describe()
            numeric_summary = stats.to_string()
        
        # Build context string
        context = f"""
COLUMN STRUCTURE:
- Numeric Columns ({len(numeric_cols)}): {', '.join(numeric_cols)}
- Text Columns ({len(text_cols)}): {', '.join(text_cols)}
- Date Columns ({len(date_cols)}): {', '.join(date_cols)}

SAMPLE DATA (first {max_rows} rows):
{sample_data}

NUMERIC STATISTICS:
{numeric_summary}
"""
        
        # Build summary dictionary
        summary = {
            "total_rows": total_rows,
            "total_columns": total_columns,
            "numeric_columns": len(numeric_cols),
            "text_columns": len(text_cols),
            "date_columns": len(date_cols),
            "column_names": df.columns.tolist(),
            "numeric_column_names": numeric_cols,
            "text_column_names": text_cols
        }
        
        # Add date range if date columns exist
        if date_cols:
            try:
                date_col = date_cols[0]
                min_date = df[date_col].min()
                max_date = df[date_col].max()
                summary["date_range"] = f"{min_date} to {max_date}"
            except:
                summary["date_range"] = "Unable to determine"
        
        # Add key metrics for financial data
        key_metrics = []
        financial_keywords = ['price', 'volume', 'close', 'open', 'high', 'low']
        for col in numeric_cols:
            if any(keyword in col.lower() for keyword in financial_keywords):
                try:
                    mean_val = df[col].mean()
                    key_metrics.append(f"{col}: avg={mean_val:.2f}")
                except:
                    pass
        
        summary["key_metrics"] = ", ".join(key_metrics) if key_metrics else "No financial metrics detected"
        
        return context.strip(), summary
