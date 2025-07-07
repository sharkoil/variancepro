"""
VariancePro v2.0 - Focused Financial Data Analysis
Clean implementation with Ollama integration and intelligent CSV analysis
"""

import gradio as gr
import pandas as pd
import requests
import uuid
import json
from datetime import datetime
from typing import List, Dict, Tuple, Optional
import os

# Import analyzers for OOB analysis
from analyzers.timescale_analyzer import TimescaleAnalyzer
from analyzers.base_analyzer import AnalysisError
from analyzers.nl2sql_function_caller import NL2SQLFunctionCaller
from config.settings import Settings


class VarianceProApp:
    """Main application class for VariancePro v2.0"""
    
    def __init__(self):
        """Initialize the application"""
        # Generate session ID
        self.session_id = str(uuid.uuid4())[:8]
        
        # Application state
        self.current_data = None
        self.data_summary = None
        
        # Initialize Ollama connection
        self.ollama_url = "http://localhost:11434"
        self.model_name = "gemma3:latest"
        
        # Initialize analyzers for OOB analysis
        try:
            self.settings = Settings()
            self.timescale_analyzer = TimescaleAnalyzer(self.settings)
            self.nl2sql_engine = NL2SQLFunctionCaller(self.ollama_url, self.model_name)
            print(f"[DEBUG] Analyzers initialized successfully")
        except Exception as e:
            print(f"[DEBUG] Warning: Could not initialize analyzers: {e}")
            self.timescale_analyzer = None
            self.nl2sql_engine = None
        
        # Check connections on startup
        self.ollama_status = self._check_ollama_connection()
        self.gradio_status = "Running"
        
        print(f"🚀 VariancePro v2.0 initialized")
        print(f"📝 Session ID: {self.session_id}")
        print(f"🤖 Ollama Status: {self.ollama_status}")
    
    def _check_ollama_connection(self) -> str:
        """Check if Ollama is running and model is available"""
        try:
            # Check if Ollama is running
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [model['name'] for model in models]
                
                if self.model_name in model_names:
                    return f"✅ Connected ({self.model_name})"
                else:
                    return f"⚠️ Model {self.model_name} not found"
            else:
                return "❌ Ollama not responding"
                
        except requests.exceptions.RequestException:
            return "❌ Ollama not running"
    
    def _call_ollama(self, prompt: str) -> str:
        """Call Ollama API with the given prompt"""
        try:
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False
            }
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', 'No response from model')
            else:
                return f"Error: Ollama API returned status {response.status_code}"
                
        except requests.exceptions.RequestException as e:
            return f"Error calling Ollama: {str(e)}"
    
    def validate_csv_file(self, file_path: str) -> Tuple[bool, str, Optional[pd.DataFrame]]:
        """Validate CSV file and return status"""
        if not file_path:
            return False, "No file provided", None
        
        try:
            # Basic file checks
            if not os.path.exists(file_path):
                return False, "File not found", None
            
            if not file_path.lower().endswith('.csv'):
                return False, "Please upload a CSV file (.csv extension required)", None
            
            # Try to read the CSV
            try:
                df = pd.read_csv(file_path)
            except pd.errors.EmptyDataError:
                return False, "The CSV file is empty. Please upload a file with data.", None
            except pd.errors.ParserError as e:
                return False, f"CSV format error: {str(e)}. Please check your file format.", None
            except UnicodeDecodeError:
                # Try different encodings
                try:
                    df = pd.read_csv(file_path, encoding='latin1')
                except:
                    return False, "Unable to read file. Please ensure it's a valid CSV with UTF-8 or Latin1 encoding.", None
            
            # Validate data content
            if df.empty:
                return False, "The CSV file contains no data rows. Please upload a file with actual data.", None
            
            if len(df.columns) == 0:
                return False, "The CSV file has no columns. Please check your file format.", None
            
            if len(df.columns) == 1 and df.columns[0].count(',') > 0:
                return False, "It looks like your CSV might have formatting issues. Please ensure proper comma separation.", None
            
            return True, "File validation successful", df
            
        except Exception as e:
            return False, f"Unexpected error reading file: {str(e)}", None
    
    def analyze_csv_data(self, df: pd.DataFrame) -> Dict:
        """Analyze CSV data and create summary for LLM"""
        analysis = {
            'row_count': len(df),
            'column_count': len(df.columns),
            'columns': list(df.columns),
            'column_types': {},
            'sample_data': {},
            'basic_stats': {}
        }
        
        # Analyze each column
        for col in df.columns:
            # Get column type
            dtype = str(df[col].dtype)
            analysis['column_types'][col] = dtype
            
            # Get sample values (first 10 non-null values)
            sample_values = df[col].dropna().head(10).tolist()
            analysis['sample_data'][col] = sample_values
            
            # Basic statistics for numeric columns
            if df[col].dtype in ['int64', 'float64']:
                try:
                    stats = {
                        'min': float(df[col].min()),
                        'max': float(df[col].max()),
                        'mean': float(df[col].mean()),
                        'null_count': int(df[col].isnull().sum())
                    }
                    analysis['basic_stats'][col] = stats
                except:
                    pass
        
        # Get sample rows
        sample_rows = df.head(10).to_dict('records')
        analysis['sample_rows'] = sample_rows
        
        return analysis
    
    def generate_data_summary(self, analysis: Dict) -> str:
        """Generate LLM summary of the data"""
        prompt = f"""
You are a financial data analyst. A user has uploaded a CSV file with the following characteristics:

DATASET OVERVIEW:
- Rows: {analysis['row_count']:,}
- Columns: {analysis['column_count']}
- Column Names: {', '.join(analysis['columns'])}

COLUMN DETAILS:
"""
        
        for col, dtype in analysis['column_types'].items():
            prompt += f"\n- {col}: {dtype}"
            if col in analysis['sample_data']:
                sample_vals = analysis['sample_data'][col][:5]  # First 5 samples
                prompt += f" (samples: {sample_vals})"
        
        if analysis['basic_stats']:
            prompt += f"\n\nNUMERIC STATISTICS:"
            for col, stats in analysis['basic_stats'].items():
                prompt += f"\n- {col}: min={stats['min']}, max={stats['max']}, avg={stats['mean']:.2f}"
        
        prompt += f"""

SAMPLE DATA (first few rows):
{analysis['sample_rows'][:3]}

Please provide a concise, friendly summary of this dataset. Focus on:
1. What type of data this appears to be (financial, sales, etc.)
2. What analyses might be useful
3. Any notable patterns or insights
4. Suggested questions the user might ask

Keep the response conversational and under 200 words.
"""
        
        # Call Ollama
        if self.ollama_status.startswith("✅"):
            return self._call_ollama(prompt)
        else:
            # Fallback summary without LLM
            return f"""📊 **Dataset Loaded Successfully**

**Overview**: {analysis['row_count']:,} rows × {analysis['column_count']} columns

**Columns**: {', '.join(analysis['columns'][:5])}{'...' if len(analysis['columns']) > 5 else ''}

⚠️ **LLM Analysis Unavailable**: {self.ollama_status}

**Suggested Actions**:
• Ask questions about your data
• Try queries like "summarize the data" or "show me trends"
• Use the analysis features to explore patterns

*Upload successful! You can now analyze your data.*"""
    
    def upload_csv(self, file, history: List[Dict]) -> Tuple[str, List[Dict]]:
        """Handle CSV file upload with validation and analysis"""
        if file is None:
            return "Please select a CSV file to upload.", history
        
        print(f"[DEBUG] Processing file: {file.name}")
        
        # Validate file
        is_valid, message, df = self.validate_csv_file(file.name)
        
        if not is_valid:
            error_timestamp = datetime.now().strftime("%H:%M:%S")
            error_msg = f"❌ **Upload Failed**\n\n{message}\n\n**Tips**:\n• Ensure your file is a valid CSV\n• Check that data is properly formatted\n• Try opening the file in Excel to verify structure"
            # Add timestamped error to chat as well
            timestamped_error_message = {
                "role": "assistant", 
                "content": self._add_timestamp_to_message(f"❌ **CSV Upload Failed**\n\n{message}", error_timestamp)
            }
            history.append(timestamped_error_message)
            return error_msg, history
        
        # Store the data
        self.current_data = df
        
        # Analyze the data
        print(f"[DEBUG] Analyzing data: {df.shape}")
        analysis = self.analyze_csv_data(df)
        self.data_summary = analysis
        
        # Generate LLM summary
        print(f"[DEBUG] Generating summary via LLM")
        summary = self.generate_data_summary(analysis)
        
        # Create comprehensive analysis message for chat
        current_timestamp = datetime.now().strftime("%H:%M:%S")
        
        analysis_message = f"""✅ **CSV Data Successfully Analyzed!**

📊 **Dataset Overview:**
• **Rows**: {analysis['row_count']:,}
• **Columns**: {analysis['column_count']}
• **File**: {file.name.split('/')[-1]}

📋 **Column Details:**
{self._format_column_info(analysis)}

🤖 **AI Summary:**
{summary}

Ready to answer questions about your data! Try asking about trends, calculations, or specific insights."""

        # Add timestamped analysis message to chat history
        timestamped_analysis_message = {
            "role": "assistant", 
            "content": self._add_timestamp_to_message(analysis_message, current_timestamp)
        }
        history.append(timestamped_analysis_message)
        
        # Perform OOB (Out-of-the-Box) Timescale Analysis
        oob_analysis = self.perform_oob_analysis(df)
        if oob_analysis:
            # Add timestamp to OOB analysis as well
            oob_timestamp = datetime.now().strftime("%H:%M:%S")
            timestamped_oob_message = {
                "role": "assistant", 
                "content": self._add_timestamp_to_message(oob_analysis, oob_timestamp)
            }
            history.append(timestamped_oob_message)
        
        # Return both upload status and updated chat
        upload_status = f"✅ **File Uploaded Successfully**\n\n{summary}"
        return upload_status, history
    
    def _format_column_info(self, analysis: Dict) -> str:
        """Format column information for display"""
        lines = []
        for col, dtype in analysis['column_types'].items():
            # Simplify data type names
            if 'int' in dtype.lower():
                type_display = "Integer"
            elif 'float' in dtype.lower():
                type_display = "Decimal"
            elif 'datetime' in dtype.lower():
                type_display = "Date/Time"
            else:
                type_display = "Text"
            
            lines.append(f"• **{col}**: {type_display}")
        
        return '\n'.join(lines)
    
    def perform_oob_analysis(self, df: pd.DataFrame) -> Optional[str]:
        """
        Perform Out-of-the-Box (OOB) analysis automatically after CSV upload
        Focuses on timescale analysis to provide immediate insights
        """
        if self.timescale_analyzer is None:
            print("[DEBUG] Timescale analyzer not available, skipping OOB analysis")
            return None
        
        try:
            print("[DEBUG] Starting OOB Timescale Analysis...")
            
            # Auto-detect date columns
            date_columns = self._detect_date_columns(df)
            
            if not date_columns:
                print("[DEBUG] No date columns detected, skipping timescale analysis")
                return "🔍 **Automatic Analysis**: No date columns detected. Upload data with dates for time-series insights."
            
            # Use the first date column found
            date_col = date_columns[0]
            print(f"[DEBUG] Using date column: {date_col}")
            
            # Auto-detect numeric columns for analysis
            numeric_columns = df.select_dtypes(include=['number']).columns.tolist()
            
            if not numeric_columns:
                print("[DEBUG] No numeric columns found for timescale analysis")
                return "🔍 **Automatic Analysis**: Date column detected but no numeric data found for time-series analysis."
            
            # Limit to first 3 numeric columns to avoid overwhelming output
            value_cols = numeric_columns[:3]
            print(f"[DEBUG] Using value columns: {value_cols}")
            
            # Perform timescale analysis
            self.timescale_analyzer.analyze(
                data=df,
                date_col=date_col,
                value_cols=value_cols
            )
            
            # Format results for chat
            if self.timescale_analyzer.status == "completed":
                print("[DEBUG] OOB Timescale Analysis completed successfully")
                
                # Create OOB analysis header
                oob_message = f"""🚀 **Automatic Time-Series Analysis**

*I've automatically analyzed your data's time patterns. Here's what I found:*

{self.timescale_analyzer.format_for_chat()}

💡 **Next Steps**: Ask me about specific time periods, trends, or comparisons!"""
                
                return oob_message
            else:
                print(f"[DEBUG] OOB Analysis failed with status: {self.timescale_analyzer.status}")
                return "🔍 **Automatic Analysis**: Time-series analysis attempted but encountered issues. You can manually request analysis using 'analyze trends'."
        
        except AnalysisError as e:
            print(f"[DEBUG] OOB Analysis error: {e}")
            return f"🔍 **Automatic Analysis**: {str(e)}"
        except Exception as e:
            print(f"[DEBUG] Unexpected OOB Analysis error: {e}")
            return "🔍 **Automatic Analysis**: Time-series analysis encountered an issue. You can manually request analysis using 'analyze trends'."
    
    def _detect_date_columns(self, df: pd.DataFrame) -> List[str]:
        """
        Detect potential date columns in the DataFrame
        
        Returns:
            List of column names that appear to contain dates
        """
        date_columns = []
        
        for col in df.columns:
            # Check column name patterns
            col_lower = col.lower()
            if any(date_word in col_lower for date_word in ['date', 'time', 'timestamp', 'created', 'updated', 'day', 'month', 'year']):
                date_columns.append(col)
                continue
            
            # Check data type
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                date_columns.append(col)
                continue
            
            # Try to parse as date (sample first few non-null values)
            sample_values = df[col].dropna().head(10)
            if len(sample_values) > 0:
                try:
                    # Try to parse a few values as dates
                    parsed_count = 0
                    for value in sample_values:
                        try:
                            pd.to_datetime(str(value), infer_datetime_format=True)
                            parsed_count += 1
                        except:
                            pass
                    
                    # If most samples parse as dates, consider it a date column
                    if parsed_count >= len(sample_values) * 0.7:  # 70% success rate
                        date_columns.append(col)
                except:
                    pass
        
        print(f"[DEBUG] Detected date columns: {date_columns}")
        return date_columns
    
    def _add_timestamp_to_message(self, message: str, timestamp: str) -> str:
        """
        Add a timestamp to a chat message in a subtle, professional format.
        
        Args:
            message (str): The original message content
            timestamp (str): The timestamp in HH:MM:SS format based on browser local time
            
        Returns:
            str: Message with timestamp prefix
        """
        # Add timestamp as a subtle prefix with light styling
        timestamp_prefix = f"<span style='color: #888; font-size: 0.85em; opacity: 0.7;'>[{timestamp}]</span> "
        return timestamp_prefix + message
    
    def chat_response(self, message: str, history: List[Dict]) -> Tuple[List[Dict], str]:
        """Handle chat messages with NL2SQL integration and browser-local timestamps"""
        if not message.strip():
            return history, ""
        
        # Generate timestamp for browser local time
        current_timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Add user message with timestamp
        user_message = {
            "role": "user", 
            "content": self._add_timestamp_to_message(message, current_timestamp)
        }
        history.append(user_message)
        
        # Process the message
        if self.current_data is None:
            response = "Please upload a CSV file first to start analyzing your data."
        else:
            # Check for Top N/Bottom N patterns in natural language
            if self._is_top_bottom_query(message):
                response = self._handle_top_bottom_query(message)
            elif "summary" in message.lower():
                response = self._generate_summary_response()
            elif "help" in message.lower():
                response = self._generate_help_response()
            elif self.nl2sql_engine and self.ollama_status.startswith("✅"):
                # Use NL2SQL for complex queries
                response = self._handle_nl2sql_query(message)
            else:
                response = f"I understand you asked: '{message}'. I can help analyze your data! Try asking for a 'summary' or use the quick action buttons."
        
        # Add assistant response with timestamp
        assistant_message = {
            "role": "assistant", 
            "content": self._add_timestamp_to_message(response, current_timestamp)
        }
        history.append(assistant_message)
        
        return history, ""
    
    def _is_top_bottom_query(self, message: str) -> bool:
        """Check if the message is asking for top/bottom analysis"""
        message_lower = message.lower()
        top_bottom_indicators = [
            'top 5', 'top 10', 'bottom 5', 'bottom 10',
            'highest', 'lowest', 'best', 'worst', 'largest', 'smallest'
        ]
        return any(indicator in message_lower for indicator in top_bottom_indicators)
    
    def _handle_top_bottom_query(self, message: str) -> str:
        """Handle top/bottom queries using base analyzer"""
        try:
            from analyzers.base_analyzer import BaseAnalyzer
            
            # Create a temporary base analyzer instance
            base_analyzer = BaseAnalyzer()
            
            # Parse the query to extract N and direction
            message_lower = message.lower()
            
            # Determine direction and N
            if any(word in message_lower for word in ['top', 'highest', 'best', 'largest']):
                direction = 'top'
            else:
                direction = 'bottom'
            
            # Extract number
            import re
            numbers = re.findall(r'\d+', message)
            n = int(numbers[0]) if numbers else 5
            
            # Get numeric columns for analysis
            numeric_columns = self.current_data.select_dtypes(include=['number']).columns.tolist()
            
            if not numeric_columns:
                return "⚠️ **Top/Bottom Analysis**: No numeric columns found in your data."
            
            # Use the first numeric column
            value_col = numeric_columns[0]
            
            # Perform analysis
            if direction == 'top':
                result = base_analyzer.perform_top_n_analysis(
                    data=self.current_data,
                    value_column=value_col,
                    n=n
                )
            else:
                result = base_analyzer.perform_bottom_n_analysis(
                    data=self.current_data,
                    value_column=value_col,
                    n=n
                )
            
            return f"🔍 **{direction.title()} {n} Analysis**\n\n{result}"
            
        except Exception as e:
            return f"❌ **Top/Bottom Analysis Error**: {str(e)}"
    
    def _handle_nl2sql_query(self, message: str) -> str:
        """Handle natural language queries using NL2SQL function calling"""
        try:
            result = self.nl2sql_engine.process_query(message, self.current_data)
            return result
        except Exception as e:
            return f"❌ **Query Processing Error**: {str(e)}"
    
    def _generate_summary_response(self) -> str:
        """Generate a summary of current data"""
        if self.data_summary:
            return f"""📊 **Data Summary**

**Dataset**: {self.data_summary['row_count']:,} rows × {self.data_summary['column_count']} columns

**Columns**: {', '.join(self.data_summary['columns'])}

**Data Types**: {len([c for c, t in self.data_summary['column_types'].items() if 'int' in t or 'float' in t])} numeric, {len([c for c, t in self.data_summary['column_types'].items() if 'object' in t])} text columns

*Ask me specific questions about your data or use the quick action buttons!*"""
        else:
            return "No data loaded yet. Please upload a CSV file first."
    
    def _generate_help_response(self) -> str:
        """Generate help message"""
        return """🤝 **How to Use VariancePro v2.0**

**Getting Started**:
1. Upload your CSV file using the file upload area
2. Wait for the AI to analyze your data
3. Ask questions about your data

**Current Features**:
• CSV upload and validation
• Intelligent data analysis via Gemma3
• Top N/Bottom N analysis
• Natural Language to SQL queries
• Automatic time-series analysis

**Example Queries**:
• "Show me the top 10 values"
• "What are the trends in this data?"
• "Summarize the data"

*This is VariancePro v2.0 - focused and powerful!*"""
    
    def _quick_action(self, action: str, history: List[Dict]) -> List[Dict]:
        """Handle quick action button clicks by creating a proper user-assistant interaction with timestamps"""
        print(f"[DEBUG] Quick action triggered: {action}")
        
        # Generate timestamp for browser local time
        current_timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Create a user message for the action
        user_message = f"Please provide {action} analysis"
        
        # Add timestamped user message to history
        timestamped_user_message = {
            "role": "user", 
            "content": self._add_timestamp_to_message(user_message, current_timestamp)
        }
        history.append(timestamped_user_message)
        
        if self.current_data is None:
            response = "⚠️ **Please upload a CSV file first** to use quick analysis features."
        else:
            # Handle different quick actions
            if action.lower() == "summary":
                response = self._generate_summary_response()
            elif action.lower() == "trends":
                response = self._handle_trends_action()
            elif "top" in action.lower():
                response = self._handle_top_bottom_action(action)
            elif "bottom" in action.lower():
                response = self._handle_top_bottom_action(action)
            else:
                response = f"🔍 **{action.title()} Analysis**\n\nThis feature is being implemented. You can ask questions about your data in the chat!"
        
        # Add the timestamped assistant response to chat history
        timestamped_assistant_message = {
            "role": "assistant", 
            "content": self._add_timestamp_to_message(response, current_timestamp)
        }
        history.append(timestamped_assistant_message)
        return history
    
    def _handle_trends_action(self) -> str:
        """Handle trends quick action"""
        if self.timescale_analyzer is None:
            return "⚠️ **Trends Analysis**: Timescale analyzer not available. Please check the system configuration."
        
        try:
            # Detect date columns for trends analysis
            date_columns = self._detect_date_columns(self.current_data)
            
            if not date_columns:
                return "⚠️ **Trends Analysis**: No date columns detected in your data. Trends analysis requires time-based data."
            
            # Get numeric columns
            numeric_columns = self.current_data.select_dtypes(include=['number']).columns.tolist()
            
            if not numeric_columns:
                return "⚠️ **Trends Analysis**: No numeric columns found. Trends analysis requires numerical data to analyze."
            
            # Perform the analysis
            self.timescale_analyzer.analyze(
                data=self.current_data,
                date_col=date_columns[0],
                value_cols=numeric_columns[:3]  # Limit to first 3 columns
            )
            
            if self.timescale_analyzer.status == "completed":
                return f"📈 **Trends Analysis**\n\n{self.timescale_analyzer.format_for_chat()}"
            else:
                return f"❌ **Trends Analysis Failed**: {self.timescale_analyzer.status}"
                
        except Exception as e:
            return f"❌ **Trends Analysis Error**: {str(e)}"
    
    def _handle_top_bottom_action(self, action: str) -> str:
        """Handle top/bottom N analysis actions"""
        try:
            # Parse the action to get N and direction
            action_lower = action.lower()
            
            if "top" in action_lower:
                direction = "top"
                if "5" in action_lower:
                    n = 5
                elif "10" in action_lower:
                    n = 10
                else:
                    n = 5  # default
            elif "bottom" in action_lower:
                direction = "bottom"
                if "5" in action_lower:
                    n = 5
                elif "10" in action_lower:
                    n = 10
                else:
                    n = 5  # default
            else:
                return f"❌ **Analysis Error**: Unrecognized action '{action}'"
            
            # Get numeric columns for analysis
            numeric_columns = self.current_data.select_dtypes(include=['number']).columns.tolist()
            
            if not numeric_columns:
                return f"⚠️ **{action.title()} Analysis**: No numeric columns found in your data. This analysis requires numerical data."
            
            # Use the first numeric column for analysis
            value_col = numeric_columns[0]
            
            # Get category columns (non-numeric, non-date)
            category_columns = []
            for col in self.current_data.columns:
                if col not in numeric_columns and col not in self._detect_date_columns(self.current_data):
                    category_columns.append(col)
            
            if not category_columns:
                # If no category columns, create a simple ranking by index
                if direction == "top":
                    result_df = self.current_data.nlargest(n, value_col)
                else:
                    result_df = self.current_data.nsmallest(n, value_col)
                
                result_text = result_df.to_string(index=False, max_rows=n)
                
                return f"""🔍 **{action.title()} Analysis**

**Showing {direction} {n} records by {value_col}**

```
{result_text}
```

💡 **Insight**: These are the {direction} {n} records ranked by {value_col} values."""
            
            else:
                # Group by first category column and aggregate
                category_col = category_columns[0]
                
                # Group and sum by category
                grouped = self.current_data.groupby(category_col)[value_col].sum().reset_index()
                
                if direction == "top":
                    result_df = grouped.nlargest(n, value_col)
                else:
                    result_df = grouped.nsmallest(n, value_col)
                
                result_text = result_df.to_string(index=False, max_rows=n)
                
                return f"""🔍 **{action.title()} Analysis**

**Showing {direction} {n} {category_col} by total {value_col}**

```
{result_text}
```

💡 **Insight**: These are the {direction} performing categories when grouped by {category_col} and summed by {value_col}."""
                
        except Exception as e:
            return f"❌ **{action.title()} Analysis Error**: {str(e)}"
    
    def create_interface(self):
        """Create the Gradio interface"""
        with gr.Blocks(title="VariancePro v2.0", theme=gr.themes.Soft()) as interface:
            # Header
            gr.Markdown("# 📊 VariancePro v2.0")
            gr.Markdown("*AI-Powered Financial Data Analysis with Gemma3*")
            
            with gr.Row():
                with gr.Column(scale=1):
                    # File upload
                    gr.Markdown("### 📁 Upload Data")
                    file_input = gr.File(
                        label="CSV File",
                        file_types=[".csv"],
                        type="filepath"
                    )
                    
                    # Upload status
                    upload_status = gr.Textbox(
                        label="Upload Status",
                        value="Ready to upload CSV file...",
                        lines=8,
                        interactive=False
                    )
                
                with gr.Column(scale=2):
                    # Chat interface
                    gr.Markdown("### 💬 Analysis Chat")
                    
                    chatbot = gr.Chatbot(
                        label="AI Assistant",
                        height=400,
                        type="messages",
                        value=[{"role": "assistant", "content": "👋 Welcome to VariancePro v2.0! Upload your CSV file and I'll analyze it for you."}]
                    )
                    
                    with gr.Row():
                        chat_input = gr.Textbox(
                            placeholder="Ask about your data...",
                            label="Your Message",
                            scale=4
                        )
                        send_btn = gr.Button("Send 📤", scale=1, variant="primary")
                    
                    # Quick Analysis Buttons
                    gr.Markdown("**Quick Analysis:**")
                    with gr.Row():
                        summary_btn = gr.Button("📋 Summary", size="sm")
                        trends_btn = gr.Button("📈 Trends", size="sm")
                        
                    # Top N / Bottom N Buttons
                    gr.Markdown("**Top/Bottom Analysis:**")
                    with gr.Row():
                        top5_btn = gr.Button("🔝 Top 5", size="sm", variant="secondary")
                        bottom5_btn = gr.Button("🔻 Bottom 5", size="sm", variant="secondary")
                        top10_btn = gr.Button("📊 Top 10", size="sm", variant="secondary")
                        bottom10_btn = gr.Button("📉 Bottom 10", size="sm", variant="secondary")
            
            # Footer with status
            with gr.Row():
                gr.Markdown(f"""
**Session**: `{self.session_id}` | **Ollama**: {self.ollama_status} | **Gradio**: {self.gradio_status} | **Model**: {self.model_name}
                """)
            
            # Event bindings
            file_input.change(
                fn=self.upload_csv,
                inputs=[file_input, chatbot],
                outputs=[upload_status, chatbot]
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
            
            # Quick Analysis button events
            summary_btn.click(
                fn=lambda h: self._quick_action("summary", h),
                inputs=[chatbot],
                outputs=[chatbot]
            )
            
            trends_btn.click(
                fn=lambda h: self._quick_action("trends", h),
                inputs=[chatbot],
                outputs=[chatbot]
            )
            
            # Top N / Bottom N button events
            top5_btn.click(
                fn=lambda h: self._quick_action("top 5", h),
                inputs=[chatbot],
                outputs=[chatbot]
            )
            
            bottom5_btn.click(
                fn=lambda h: self._quick_action("bottom 5", h),
                inputs=[chatbot],
                outputs=[chatbot]
            )
            
            top10_btn.click(
                fn=lambda h: self._quick_action("top 10", h),
                inputs=[chatbot],
                outputs=[chatbot]
            )
            
            bottom10_btn.click(
                fn=lambda h: self._quick_action("bottom 10", h),
                inputs=[chatbot],
                outputs=[chatbot]
            )
        
        return interface


def main():
    """Main entry point"""
    print("🚀 Starting VariancePro v2.0...")
    
    app = VarianceProApp()
    interface = app.create_interface()
    
    print("✅ Application ready")
    print(f"🌐 Access at: http://localhost:7873")
    
    interface.launch(
        server_name="0.0.0.0",
        server_port=7873,
        share=False,
        debug=True,
        show_error=True
    )


if __name__ == "__main__":
    main()
