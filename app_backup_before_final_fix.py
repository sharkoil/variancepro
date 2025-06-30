import gradio as gr
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import requests
import json
import io
import base64
import traceback
from datetime import datetime, timedelta
from typing import Optional, List, Tuple, Dict
from pathlib import Path

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

class Phi4FinancialChat:
    """Financial data analysis chat powered by Phi4 via Ollama"""
    
    def __init__(self):
        self.model_name = "deepseek-coder:6.7b"
        self.ollama_url = "http://localhost:11434"
        self.current_data = None
        self.chat_history = []  # Initialize chat history
        
        # Initialize timescale analyzer
        self.timescale_analyzer = TimescaleAnalyzer()
        
        # Add narrative generation if available
        if NARRATIVE_AVAILABLE:
            try:
                from utils.narrative_generator import add_narrative_to_app
                add_narrative_to_app(self)
                print("✅ Narrative generation enabled with Aria Sterling persona")
            except Exception as e:
                print(f"⚠️ Narrative generation initialization failed: {e}")
        
        # Initialize LlamaIndex processor (optional)
        self.llamaindex_processor = None
        if LLAMAINDEX_AVAILABLE:
            try:
                self.llamaindex_processor = LlamaIndexFinancialProcessor()
                print("✅ LlamaIndex processor initialized")
            except Exception as e:
                print(f"⚠️ LlamaIndex initialization failed: {e}")
                self.llamaindex_processor = None
        else:
            print("LlamaIndex not installed. Run: pip install llama-index")
    
    def check_ollama_connection(self) -> bool:
        """Check if Ollama is running and Phi4 is available"""
        try:
            # First check if Ollama is running
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=10)
            if response.status_code == 200:
                models = response.json().get("models", [])
                available_models = [model["name"] for model in models]
                # Check for exact match or pattern match
                return any(
                    model_name for model_name in available_models 
                    if "phi4" in model_name or model_name == "phi4"
                )
            return False
        except requests.exceptions.Timeout:
            return False
        except requests.exceptions.ConnectionError:
            return False
        except Exception:
            return False
    
    def query_phi4(self, prompt: str) -> str:
        """Query DeepSeek Coder model via Ollama"""
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
            return "⚠️ Phi4 is processing your complex financial query. Large models need more time for detailed analysis. The response will appear shortly, or try breaking your question into smaller parts."
        except requests.exceptions.ConnectionError:
            return "❌ Cannot connect to Ollama. Please ensure Ollama is running with: `ollama serve`"
        except Exception as e:
            return f"Error communicating with Phi4: {str(e)}"
    
    def create_financial_prompt(self, user_query: str, data_summary: str) -> str:
        """Create optimized prompt for Phi4 financial analysis"""
        
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
- Data visualization suggestions
- Statistical analysis methods

## Recommendations
- Specific actionable steps
- Areas for further investigation
- Risk mitigation strategies

Provide clear, concise responses using professional financial terminology. Make recommendations data-driven and actionable."""
        
        return prompt
    
    def analyze_data(self, file_data, user_question: str) -> Tuple[str, str]:
        """Analyze uploaded data and answer user questions"""
        
        # Check Phi4 availability
        if not self.check_ollama_connection():
            return self.fallback_analysis(user_question), "⚠️ Phi4 offline - using built-in analysis"
        
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
            
            # Create prompt for Phi4
            prompt = self.create_financial_prompt(user_question, data_summary)
            
            # Get Phi4 response
            phi4_response = self.query_phi4(prompt)
            
            # Add to chat history
            self.chat_history.append({
                "user": user_question,
                "assistant": phi4_response,
                "timestamp": datetime.now()
            })
            
            return phi4_response, f"✅ Phi4 Analysis | Dataset: {len(df)} rows, {len(df.columns)} columns"
            
        except Exception as e:
            return f"Error processing data: {str(e)}", "❌ Processing Error"
    
    def create_data_summary(self, df: pd.DataFrame) -> str:
        """Create comprehensive data summary for Phi4"""
        
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
        """Fallback analysis when Phi4 is not available"""
        
        if self.current_data is None:
            return """🤖 **Built-in Analysis** (DeepSeek Coder offline):

Please upload a CSV file to begin analysis.

💡 **To enable Phi4**:
1. Ensure Ollama is running: `ollama serve`
2. Verify Phi4 is installed: `ollama list`
3. If missing, install: `ollama pull phi4`"""
        
        df = self.current_data
        
        response = f"""🤖 **Built-in Analysis** (DeepSeek Coder offline):

**Your Question**: {user_query}

**Dataset Overview**:
- {len(df)} rows, {len(df.columns)} columns
- Numeric columns: {len(df.select_dtypes(include=[np.number]).columns)}

**Quick Insights**:
- Data spans from {df.index[0]} to {df.index[-1]}
- Key columns: {', '.join(df.columns[:5])}

💡 **For enhanced AI analysis with code suggestions, ensure DeepSeek Coder is running via Ollama.**"""
        
        return response
    
    def analyze_visualization_structure(self, df: pd.DataFrame) -> dict:
        """Use Phi4 to analyze data structure for optimal visualization"""
        
        if not self.check_ollama_connection():
            return self.fallback_visualization_analysis(df)
        
        # Create a prompt for the LLM to analyze the data structure
        columns_info = []
        for col in df.columns:
            dtype = str(df[col].dtype)
            sample_values = df[col].dropna().head(3).tolist()
            unique_count = df[col].nunique()
            columns_info.append(f"- {col}: {dtype}, {unique_count} unique values, samples: {sample_values}")
        
        prompt = f"""Analyze this dataset for time series visualization. Return a JSON response with the optimal configuration.

DATASET COLUMNS:
{chr(10).join(columns_info)}

SAMPLE DATA:
{df.head(3).to_string()}

Task: Identify the best configuration for a vertical bar chart time series visualization.

Requirements:
1. X-axis: Must be a time/date column (identify the best one)
2. Y-axis: Numeric columns to plot (select 1-3 most important)
3. Grouping: Categorical fields for grouping (max 3, order by importance)

Return ONLY a JSON object with this exact structure:
{{
    "x_axis": "column_name",
    "y_axis": ["numeric_column1", "numeric_column2"],
    "grouping": ["category1", "category2"],
    "reasoning": "Brief explanation of choices"
}}

Focus on:
- Time/date patterns in column names and data
- Meaningful numeric metrics for business analysis
- Categorical fields that provide useful grouping"""

        try:
            response = self.query_phi4(prompt)
            
            # Try to extract JSON from the response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                config = json.loads(json_match.group())
                
                # Validate the configuration
                if self.validate_viz_config(config, df):
                    return config
            
            # If parsing fails, fall back to automatic analysis
            return self.fallback_visualization_analysis(df)
            
        except Exception as e:
            print(f"LLM analysis failed: {e}")
            return self.fallback_visualization_analysis(df)
    
    def validate_viz_config(self, config: dict, df: pd.DataFrame) -> bool:
        """Validate the LLM-generated visualization configuration"""
        try:
            # Check if all specified columns exist
            all_cols = [config.get('x_axis')] + config.get('y_axis', []) + config.get('grouping', [])
            return all(col in df.columns for col in all_cols if col)
        except:
            return False
    
    def fallback_visualization_analysis(self, df: pd.DataFrame) -> dict:
        """Fallback method to analyze data structure when LLM is unavailable"""
        
        # Find time/date columns
        time_col = None
        for col in df.columns:
            if any(keyword in col.lower() for keyword in ['date', 'time', 'period', 'month', 'year', 'day']):
                time_col = col
                break
        
        if not time_col:
            # Try to find columns that can be converted to datetime
            for col in df.columns:
                try:
                    pd.to_datetime(df[col].head(10))
                    time_col = col
                    break
                except:
                    continue
        
        # Find numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        y_axis = numeric_cols[:2] if len(numeric_cols) >= 2 else numeric_cols
        
        # Find categorical columns
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        if time_col in categorical_cols:
            categorical_cols.remove(time_col)
        grouping = categorical_cols[:3]
        
        return {
            "x_axis": time_col,
            "y_axis": y_axis,
            "grouping": grouping,
            "reasoning": "Automatic analysis - LLM unavailable"
        }
    
    def create_time_series_visualization(self, df: pd.DataFrame) -> tuple:
        """Create intelligent time series visualization using Chart.js"""
        
        if df is None or df.empty:
            return None, "No data available for visualization"
        
        try:
            print(f"Debug: Starting Chart.js visualization with {len(df)} rows, {len(df.columns)} columns")
            
            # Use deterministic analysis to find columns for visualization
            viz_config = self.fallback_visualization_analysis(df)
            print(f"Debug: Determined viz config: {viz_config}")
            
            x_col = viz_config.get('x_axis')
            y_cols = viz_config.get('y_axis', [])
            group_cols = viz_config.get('grouping', [])
            
            print(f"Debug: x_col={x_col}, y_cols={y_cols}, group_cols={group_cols}")
            
            if not x_col or not y_cols:
                error_msg = f"Could not identify suitable columns. x_col='{x_col}', y_cols={y_cols}"
                print(f"Debug: {error_msg}")
                return None, error_msg
            
            # Check if columns exist in dataframe
            missing_cols = []
            if x_col not in df.columns:
                missing_cols.append(x_col)
            for col in y_cols:
                if col not in df.columns:
                    missing_cols.append(col)
            
            if missing_cols:
                error_msg = f"Missing columns in dataset: {missing_cols}. Available columns: {list(df.columns)}"
                print(f"Debug: {error_msg}")
                return None, error_msg
            
            # Prepare the data
            df_viz = df.copy()
            print(f"Debug: Data preparation - original shape: {df_viz.shape}")
            
            # Convert x-axis to datetime if it isn't already
            try:
                if df_viz[x_col].dtype == 'object':
                    df_viz[x_col] = pd.to_datetime(df_viz[x_col])
                    print(f"Debug: Converted {x_col} to datetime")
                else:
                    print(f"Debug: {x_col} already in datetime format")
            except Exception as e:
                error_msg = f"Could not convert {x_col} to datetime format: {str(e)}"
                print(f"Debug: {error_msg}")
                return None, error_msg
            
            # Sort by time and remove any NaN values
            df_viz = df_viz.dropna(subset=[x_col] + y_cols)
            df_viz = df_viz.sort_values(x_col)
            print(f"Debug: After cleaning - shape: {df_viz.shape}")
            
            if df_viz.empty:
                return None, "No valid data remaining after cleaning"
            
            # Generate Chart.js HTML
            chart_html = self.generate_chartjs_html(df_viz, x_col, y_cols, group_cols, viz_config)
            print(f"Debug: Chart.js HTML generated, length: {len(chart_html)} characters")
            
            config_info = f"""📊 **Visualization Configuration (Chart.js):**
- **X-axis (Time):** {x_col}
- **Y-axis (Metrics):** {', '.join(y_cols)}
- **Grouping:** {', '.join(group_cols) if group_cols else 'None'}
- **Analysis:** {viz_config.get('reasoning', 'AI-generated configuration')}

🔍 **Data Summary:**
- **Records processed:** {len(df_viz)}
- **Date range:** {df_viz[x_col].min()} to {df_viz[x_col].max()}
- **Chart type:** Interactive time series chart (Chart.js)
- **Features:** Responsive, tooltips, zoom, hover effects"""
            
            return chart_html, config_info
                
        except Exception as e:
            error_msg = f"Visualization error: {str(e)}"
            print(f"Debug: {error_msg}")
            import traceback
            traceback.print_exc()
            return None, error_msg
    
    def create_chartjs_template(self, labels: list, data_dict: dict, chart_title: str, x_axis_title: str, y_axis_title: str) -> str:
        """Create Chart.js HTML template following examples.txt pattern"""
        
        # Define consistent color palette (from examples.txt)
        chart_colors = {
            'red': 'rgb(255, 99, 132)',
            'orange': 'rgb(255, 159, 64)', 
            'yellow': 'rgb(255, 205, 86)',
            'green': 'rgb(75, 192, 192)',
            'blue': 'rgb(54, 162, 235)',
            'purple': 'rgb(153, 102, 255)',
            'grey': 'rgb(201, 203, 207)'
        }
        
        color_names = ['blue', 'red', 'green', 'orange', 'purple', 'yellow', 'grey']
        
        # Build datasets array
        datasets = []
        for i, (series_name, data_array) in enumerate(data_dict.items()):
            color_name = color_names[i % len(color_names)]
            color = chart_colors[color_name]
            
            dataset = {
                'label': series_name,
                'data': data_array,
                'backgroundColor': color.replace('rgb', 'rgba').replace(')', ', 0.5)'),
                'borderColor': color,
                'borderWidth': 2
            }
            datasets.append(dataset)
        
        # Create chart data structure following examples.txt pattern
        chart_data = {
            'labels': labels,
            'datasets': datasets
        }
        
        html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <title>VariancePro Financial Chart</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f8f9fa;
        }}
        .chart-container {{
            position: relative;
            width: 100%;
            height: 600px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 20px;
            margin: 0 auto;
        }}
        .chart-title {{
            text-align: center;
            font-size: 24px;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 30px;
        }}
        #chartCanvas {{
            width: 100% !important;
            height: 500px !important;
        }}
    </style>
</head>
<body>
    <div class="chart-container">
        <div class="chart-title">{chart_title}</div>
        <canvas id="chartCanvas"></canvas>
    </div>

    <script>
        console.log('🔍 VariancePro Chart.js Debug Info:');
        console.log('📍 Document location:', window.location.href);
        console.log('📍 Chart.js available:', typeof Chart !== 'undefined');
        
        // Wait for Chart.js to load
        function initChart() {{
            if (typeof Chart === 'undefined') {{
                console.error('❌ Chart.js not available, retrying in 500ms...');
                setTimeout(initChart, 500);
                return;
            }}
            
            console.log('✅ Chart.js loaded, version:', Chart.version);
        
            // Data structure following examples.txt pattern
            const chartData = {json.dumps(chart_data, indent=2)};
        
        console.log('📊 Chart Data structure:', chartData);
        if (chartData.labels) console.log('📊 Labels:', chartData.labels);
        if (chartData.datasets) console.log('📈 Number of datasets:', chartData.datasets.length);
        
        // Validate data
        if (!chartData.labels || chartData.labels.length === 0) {{
            console.error('❌ No labels provided');
            document.querySelector('.chart-container').innerHTML = '<div style="text-align: center; padding: 50px; color: #ff6b6b;"><h3>❌ No Labels</h3><p>Chart labels are missing or empty</p></div>';
            return;
        }}
        
        if (!chartData.datasets || chartData.datasets.length === 0) {{
            console.error('❌ No datasets provided'); 
            document.querySelector('.chart-container').innerHTML = '<div style="text-align: center; padding: 50px; color: #ff6b6b;"><h3>❌ No Data</h3><p>Chart datasets are missing or empty</p></div>';
            return;
        }}
        
        // Validate dataset lengths
        for (let i = 0; i < chartData.datasets.length; i++) {{
            const dataset = chartData.datasets[i];
            if (dataset.data.length !== chartData.labels.length) {{
                console.error(`❌ Dataset ${{i}} length (${{dataset.data.length}}) doesn\'t match labels length (${{chartData.labels.length}})`);
                document.querySelector('.chart-container').innerHTML = '<div style="text-align: center; padding: 50px; color: #ff6b6b;"><h3>❌ Data Mismatch</h3><p>Dataset lengths don\'t match labels</p></div>';
                return;
            }}
        }}
        
        console.log('✅ Data validation passed');
        
        // Chart configuration following examples.txt pattern
        const config = {{
            type: 'bar',
            data: chartData,
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        display: true,
                        position: 'top'
                    }},
                    tooltip: {{
                        backgroundColor: 'rgba(0,0,0,0.8)',
                        titleColor: 'white',
                        bodyColor: 'white',
                        callbacks: {{
                            label: function(context) {{
                                return context.dataset.label + ': ' + 
                                       new Intl.NumberFormat('en-US', {{
                                           minimumFractionDigits: 0,
                                           maximumFractionDigits: 2
                                       }}).format(context.parsed.y);
                            }}
                        }}
                    }}
                }},
                scales: {{
                    x: {{
                        title: {{
                            display: true,
                            text: '{x_axis_title}'
                        }}
                    }},
                    y: {{
                        beginAtZero: false,
                        title: {{
                            display: true,
                            text: '{y_axis_title}'
                        }}
                    }}
                }}
            }}
        }};
        
        console.log('🔧 Chart config created');
        
        // Create chart following examples.txt pattern
        const ctx = document.getElementById('chartCanvas');
        if (!ctx) {{
            console.error('❌ Canvas element not found');
            return;
        }}
        
        try {{

            const chart = new Chart(ctx, config);
            console.log('✅ Chart created successfully');
            
            // Log final state
            setTimeout(() => {{
                console.log('📊 Final chart state:');
                console.log('  Labels count:', chart.data.labels.length);
                console.log('  Datasets count:', chart.data.datasets.length);
                console.log('  Chart rendered:', chart.canvas.clientHeight > 0);
            }}, 100);
            
        }} catch (error) {{
            console.error('❌ Chart creation failed:', error);
            document.querySelector('.chart-container').innerHTML = `
                <div style="text-align: center; padding: 50px; color: #ff6b6b;">
                    <h3>❌ Chart Error</h3>
                    <p>${{error.message}}</p>
                </div>
            `;
        }}
        
        }} // End initChart function
        
        // Start chart initialization
        if (document.readyState === 'loading') {{
            document.addEventListener('DOMContentLoaded', initChart);
        }} else {{
            initChart();
        }}
    </script>
</body>
</html>
"""
        return html_template
    
    def generate_chartjs_html(self, df: pd.DataFrame, x_col: str, y_cols: List[str], group_cols: List[str], viz_config: dict) -> str:
        """Generate complete HTML with Chart.js visualization using clean data approach"""
        
        print(f"Debug: generate_chartjs_html called with df shape: {df.shape}")
        print(f"Debug: x_col='{x_col}', y_cols={y_cols}, group_cols={group_cols}")
        
        # Use the new clean data generation approach
        labels, data_dict = self.generate_chart_data(df, x_col, y_cols, group_cols)
        
        # Validate the generated data
        if not self.validate_chart_data(labels, data_dict):
            print("Debug: ERROR - Chart data validation failed!")
            return self.generate_error_chart_html("Generated chart data failed validation")
        
        print(f"Debug: Clean chart data - Labels: {len(labels)}, Series: {list(data_dict.keys())}")
        
        # Create chart title and axis labels
        chart_title = f"{y_cols[0]} Analysis"
        if len(y_cols) > 1:
            chart_title = f"Financial Metrics Analysis"
        if group_cols and group_cols[0] in df.columns:
            chart_title += f" by {group_cols[0]}"
            
        x_axis_title = x_col.replace('_', ' ').title()
        y_axis_title = "Value"
        if len(y_cols) == 1:
            y_axis_title = y_cols[0].replace('_', ' ').title()
        
        print(f"Debug: Chart title: '{chart_title}'")
        print(f"Debug: Axis titles: X='{x_axis_title}', Y='{y_axis_title}'")
        
        # Generate the Chart.js HTML using the clean template
        return self.create_chartjs_template(labels, data_dict, chart_title, x_axis_title, y_axis_title)
    
    def generate_chart_data(self, df: pd.DataFrame, x_col: str, y_cols: List[str], group_cols: List[str]) -> tuple[list, dict]:
        """Generate clean labels and data arrays for Chart.js - ONLY returns labels and data arrays"""
        
        print(f"Debug: Generating chart data for {len(df)} rows")
        
        # Sort by x column first
        df_sorted = df.sort_values(x_col)
        
        # Generate clean labels array
        labels = []
        data_dict = {}
        
        if group_cols and group_cols[0] in df.columns:
            # Grouped data approach - multiple datasets
            group_col = group_cols[0]
            groups = sorted(df_sorted[group_col].unique())
            
            # Get all unique x values for consistent labeling
            unique_x_values = sorted(df_sorted[x_col].unique())
            
            # Create labels array
            for x_val in unique_x_values:
                if hasattr(x_val, 'strftime'):
                    labels.append(x_val.strftime('%Y-%m-%d'))
                else:
                    labels.append(str(x_val))
            
            # Create data arrays for each group
            for group in groups:
                group_data = df_sorted[df_sorted[group_col] == group]
                data_values = []
                
                # Align data with labels
                for x_val in unique_x_values:
                    matching_rows = group_data[group_data[x_col] == x_val]
                    if len(matching_rows) > 0:
                        # Use first y_col for grouped data
                        value = matching_rows[y_cols[0]].iloc[0]
                        # Ensure numeric value
                        if pd.isna(value):
                            data_values.append(0)
                        else:
                            data_values.append(float(value))
                    else:
                        data_values.append(0)
                
                data_dict[str(group)] = data_values
                
        else:
            # Multiple y-columns as separate datasets
            unique_x_values = sorted(df_sorted[x_col].unique())
            
            # Create labels array
            for x_val in unique_x_values:
                if hasattr(x_val, 'strftime'):
                    labels.append(x_val.strftime('%Y-%m-%d'))
                else:
                    labels.append(str(x_val))
            
            # Create data arrays for each y column
            for y_col in y_cols:
                data_values = []
                for x_val in unique_x_values:
                    matching_rows = df_sorted[df_sorted[x_col] == x_val]
                    if len(matching_rows) > 0:
                        value = matching_rows[y_col].iloc[0]
                        # Ensure numeric value
                        if pd.isna(value):
                            data_values.append(0)
                        else:
                            data_values.append(float(value))
                    else:
                        data_values.append(0)
                
                # Clean up column name for display
                clean_name = y_col.replace('_', ' ').title()
                data_dict[clean_name] = data_values
        
        print(f"Debug: Generated {len(labels)} labels and {len(data_dict)} data series")
        for series_name, data_array in data_dict.items():
            print(f"Debug: Series '{series_name}': {len(data_array)} values")
        
        return labels, data_dict
    
    def validate_chart_data(self, labels: list, data_dict: dict) -> bool:
        """Strict validation for chart data arrays following examples.txt pattern"""
        
        # Check labels array
        if not isinstance(labels, list):
            print("Debug: Validation failed - labels must be a list")
            return False
        
        if len(labels) == 0:
            print("Debug: Validation failed - labels array cannot be empty")
            return False
        
        # Validate all labels are strings
        for i, label in enumerate(labels):
            if not isinstance(label, str):
                print(f"Debug: Validation failed - label at index {i} must be a string, got {type(label)}")
                return False
        
        # Check data_dict structure
        if not isinstance(data_dict, dict):
            print("Debug: Validation failed - data_dict must be a dictionary")
            return False
        
        if len(data_dict) == 0:
            print("Debug: Validation failed - data_dict cannot be empty")
            return False
        
        labels_count = len(labels);
        
        # Validate each data series
        for series_name, data_array in data_dict.items():
            # Check series name is string
            if not isinstance(series_name, str):
                print(f"Debug: Validation failed - series name must be string, got {type(series_name)}")
                return False
            
            # Check data array is list
            if not isinstance(data_array, list):
                print(f"Debug: Validation failed - data for '{series_name}' must be a list")
                return False
            
            # Check length matches labels
            if len(data_array) != labels_count:
                print(f"Debug: Validation failed - data series '{series_name}' length ({len(data_array)}) doesn't match labels length ({labels_count})")
                return False
            
            # Check all values are numeric
            for i, value in enumerate(data_array):
                if not isinstance(value, (int, float)):
                    print(f"Debug: Validation failed - data value at index {i} in series '{series_name}' must be numeric, got {type(value)}: {value}")
                    return False
                
                # Check for invalid numbers
                if pd.isna(value) or not np.isfinite(value):
                    print(f"Debug: Validation failed - invalid numeric value at index {i} in series '{series_name}': {value}")
                    return False
        
        print(f"Debug: Validation passed - {len(labels)} labels, {len(data_dict)} series")
        return True

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
        suggestions.append('- "Create a dashboard visualization of key metrics"')
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
        return """### 💡 Sample Questions:

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

📁 Upload your CSV file to get personalized suggestions based on your data columns!"""

    def enhanced_analysis_with_llamaindex(self, file_data, user_question: str, context_docs: List[str] = None) -> Tuple[str, str]:
        """Enhanced analysis using both Phi4 and LlamaIndex for superior insights"""
        
        # First get standard Phi4 analysis
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
                combined_response = f"""## 🤖 Phi4 Financial Analysis:
{standard_response}

---

## 🧠 LlamaIndex Enhanced Analysis:
{enhanced_response}

---

### 🎯 **Synthesis:**
This analysis combines Phi4's conversational AI capabilities with LlamaIndex's structured data extraction and knowledge base features for comprehensive financial insights."""
                
                combined_status = f"{status} + {enhanced_status}"
                return combined_response, combined_status
                
            except Exception as e:
                # If LlamaIndex fails, return standard analysis with error note
                fallback_response = f"""{standard_response}

---

⚠️ **LlamaIndex Enhancement Failed**: {str(e)}
*Falling back to standard Phi4 analysis. Ensure LlamaIndex is properly installed and configured.*"""
                
                return fallback_response, f"{status} (LlamaIndex failed)"
        
        # If LlamaIndex not available, return standard analysis with note
        enhanced_note = f"""{standard_response}

---

💡 **Enhanced Analysis Available**: Install LlamaIndex for advanced features:
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
            return f"""# ⚠️ Automatic Analysis Error

We encountered an issue while analyzing your time series data: {str(e)}

Please try:
1. Ensuring your data contains at least one date/time column
2. Having sufficient data points for meaningful period-over-period analysis
3. Checking that numeric columns contain valid values

You can still ask specific questions about your data using the chat interface."""

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
        """Generate comprehensive time series analysis based on available data"""
        if df is None or df.empty:
            return "No data available for analysis."
            
        # Check if dataset has only one row
        if len(df) <= 1:
            return """# ⚠️ Insufficient Data for Time Series Analysis

This dataset contains only a single data point, which is insufficient for performing period-over-period analysis.

To perform meaningful time series analysis, please provide data with:
- Multiple time periods
- At least two data points
- Consistent time intervals

You can still use the chat interface to ask questions about this single data point."""

        # Detect date column
        date_col = self.detect_date_column(df)
        if not date_col:
            return "No date column detected in the data. Please ensure your data includes a column with dates."
        
        # Detect numeric columns for analysis
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if not numeric_cols:
            return "No numeric columns detected for analysis. Please ensure your data includes numeric values to analyze."
        
        # Use cache if available
        cache_key = f"{id(df)}_{date_col}_{'_'.join(numeric_cols)}"
        if cache_key in self.analysis_cache:
            return self.analysis_cache[cache_key]
        
        # Prepare time-scale aggregations
        aggregations = self.prepare_timescale_aggregations(df, date_col, numeric_cols)
        if not aggregations:
            return "Unable to generate time-based aggregations. Please check your date column format."
        
        # Calculate period-over-period analysis
        pop_analysis = self.calculate_period_over_period_analysis(aggregations, numeric_cols)
        
        # Generate summary insights
        analysis_text = self._generate_summary_insights(pop_analysis)
        
        # Cache the result
        self.analysis_cache[cache_key] = analysis_text
        
        return analysis_text

    def detect_date_column(self, df: pd.DataFrame) -> Optional[str]:
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
chat_system = Phi4FinancialChat()

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
        # Use standard Phi4 analysis
        response, status = chat_system.analyze_data(file, question)
    
    # Update chat history
    history.append({"role": "user", "content": question})
    history.append({"role": "assistant", "content": response})
    
    # Return current data for grid display
    current_data = chat_system.current_data if chat_system.current_data is not None else None
    
    return history, history, status, current_data

def load_data_for_grid(file):
    """Load data specifically for grid display"""
    print(f"📂 DEBUG: load_data_for_grid called with file: {file}")
    print(f"📂 DEBUG: File type: {type(file)}")
    
    if file is None:
        print("❌ DEBUG: load_data_for_grid received None file")
        return None
    
    try:
        if hasattr(file, 'name'):
            print(f"📂 DEBUG: Loading from file path: {file.name}")
            df = pd.read_csv(file.name)
        elif isinstance(file, str):
            print(f"📂 DEBUG: Loading from string path: {file}")
            df = pd.read_csv(file)
        else:
            print(f"📂 DEBUG: Loading from file content (decoded)")
            df = pd.read_csv(io.StringIO(file.decode('utf-8')))
        
        print(f"✅ DEBUG: Successfully loaded DataFrame - Shape: {df.shape}, Columns: {list(df.columns)}")
        
        # Store in chat system for analysis
        chat_system.current_data = df
        return df
    except Exception as e:
        print(f"❌ DEBUG: Error loading data: {e}")
        import traceback
        traceback.print_exc()
        return None

def generate_visualization(file):
    """Generate time series visualization using LLM analysis"""
    print(f"🎯 DEBUG: generate_visualization called with file: {file}")
    
    if file is None:
        print("❌ DEBUG: No data provided to generate_visualization")
        return None, "No data uploaded. Please upload a CSV file first."
    
    print(f"📁 DEBUG: File details - Name: {getattr(file, 'name', 'Unknown')}, Type: {type(file)}")
    
    df = load_data_for_grid(file)
    print(f"📊 DEBUG: Loaded DataFrame - Shape: {df.shape if df is not None else 'None'}")
    
    if df is not None:
        print(f"📈 DEBUG: Calling create_time_series_visualization with {len(df)} rows")
        chart_html, config_info = chat_system.create_time_series_visualization(df)
        
        if chart_html:
            print(f"✅ DEBUG: Chart HTML generated successfully, length: {len(chart_html)}")
        else:
            print(f"❌ DEBUG: Chart HTML is None or empty")
            
        print(f"📋 DEBUG: Config info: {config_info[:100]}..." if config_info else "❌ No config info")
        
        return chart_html, config_info
    else:
        print("❌ DEBUG: DataFrame is None - failed to load data")
        return None, "Error loading data for visualization."

def check_system_status():
    """Check system status including LlamaIndex availability"""
    phi4_available = chat_system.check_ollama_connection()
    llamaindex_available = (
        LLAMAINDEX_AVAILABLE and 
        chat_system.llamaindex_processor and 
        chat_system.llamaindex_processor.check_availability()
    )
    
    status_parts = []
    
    # Phi4 status
    if phi4_available:
        status_parts.append("✅ **DeepSeek Coder** Active")
    else:
        status_parts.append("⚠️ **DeepSeek Coder** Offline (Run: `ollama serve`)")
    
    # LlamaIndex status
    if llamaindex_available:
        status_parts.append("✅ **LlamaIndex** Ready")
    elif LLAMAINDEX_AVAILABLE:
        status_parts.append("⚠️ **LlamaIndex** Available but not connected")
    else:
        status_parts.append("💡 **LlamaIndex** Not installed (`pip install llama-index`)")
    
    # Enhancement note
    if phi4_available and llamaindex_available:
        enhancement = "\n\n🎯 **Full Enhancement Mode**: Both DeepSeek Coder conversational AI and LlamaIndex structured extraction available for maximum analytical power!"
    elif phi4_available:
        enhancement = "\n\n🤖 **Standard Mode**: DeepSeek Coder conversational analysis active. Install LlamaIndex for enhanced document processing."
    else:
        enhancement = "\n\n⚙️ **Basic Mode**: Using built-in analysis. Enable DeepSeek Coder and LlamaIndex for full AI capabilities."
    
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
        .viz-container { width: 100%; height: 100%; }
        .chart-container { width: 100%; max-width: 100%; height: 600px; }
        """
    ) as interface:
        
        gr.Markdown("# 🚀 VariancePro - Financial Data Analysis Chat")
        gr.Markdown("### Powered by DeepSeek Coder via Ollama")
        
        # Create tabs for different views
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
                        
                        # Dynamic sample questions based on data
                        suggested_questions = gr.Markdown(
                            value=chat_system.get_default_suggested_questions(),
                            label="💡 Suggested Questions"
                        )
                        
                        # Refresh status button
                        refresh_btn = gr.Button("🔄 Refresh Status")
            
            # Data Grid Tab
            with gr.TabItem("📊 Data View"):
                with gr.Row():
                    with gr.Column(scale=1):
                        # File upload for data view (shared with chat)
                        gr.Markdown("### 📁 Data Overview")
                        gr.Markdown("Upload a CSV file in the Chat Analysis tab to view the data here.")
                        
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
            
            # Visualizations Tab
            with gr.TabItem("📈 Visualizations"):
                with gr.Column():
                    gr.Markdown("### 🤖 AI-Powered Time Series Visualization")
                    gr.Markdown("Upload CSV data and the AI will automatically create optimal time series visualizations.")
                    
                    with gr.Row():
                        with gr.Column(scale=3):
                            # Visualization configuration info
                            viz_config_info = gr.Textbox(
                                label="🔧 Visualization Configuration",
                                value="Upload data to see AI-generated visualization configuration.",
                                interactive=False,
                                lines=6
                            )
                        
                        with gr.Column(scale=1):
                            # Generate button
                            generate_viz_btn = gr.Button("🎨 Generate Visualization", variant="primary", size="lg")
                            
                            gr.Markdown("""
                            **AI Features:**
                            - 🤖 Automatic time axis detection
                            - 📊 Smart metric selection  
                            - 🎯 Intelligent grouping
                            - 📅 Date format conversion
                            - 🎨 Optimized bar charts
                            """)
                    
                    # Visualization display
                    viz_display = gr.HTML(
                        label="📊 Time Series Visualization",
                        value="<div style='text-align: center; padding: 50px; color: #666;'>No visualization generated yet. Upload data and click 'Generate Visualization'.</div>",
                        elem_classes=["viz-container"]
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
📅 Date Columns: {len(current_data.select_dtypes(include=['datetime64']).columns)}

💾 Memory Usage: {current_data.memory_usage(deep=True).sum() / 1024:.1f} KB"""
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
                return "Error loading data. Please check your CSV file.", None, "Unable to generate analysis due to data loading error."
        
        def clear_chat():
            chat_system.chat_history = []
            return [], []
        
        def handle_generate_viz(file):
            """Handle visualization generation"""
            if file is None:
                return "No data uploaded. Please upload a CSV file first.", "<div style='text-align: center; padding: 50px; color: #666;'>Please upload a CSV file first.</div>"
            
            chart_html, config_info = generate_visualization(file)
            if chart_html:
                return config_info, chart_html
            else:
                return config_info, "<div style='text-align: center; padding: 50px; color: #666;'>Failed to generate visualization. Please check your data format.</div>"
        
        def update_suggested_questions(file):
            """Update suggested questions based on uploaded data"""
            if file is None:
                return chat_system.get_default_suggested_questions()
            
            df = load_data_for_grid(file)
            if df is not None:
                return chat_system.generate_suggested_questions(df)
            else:
                return chat_system.get_default_suggested_questions()
        
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
        
        # Generate visualization
        generate_viz_btn.click(
            handle_generate_viz,
            inputs=[file_input],
            outputs=[viz_config_info, viz_display]
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
    
    print("🚀 Starting VariancePro Financial Chat with DeepSeek Coder...")
    print("📊 Upload your CSV data and start asking questions!")
    
    demo.launch(
        server_name="127.0.0.1",
        server_port=7863,
        share=False,
        debug=False,
        show_error=True
    )
