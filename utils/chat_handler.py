import pandas as pd
import numpy as np
from datetime import datetime
import re
from .llm_handler import LLMHandler, DataContextBuilder

class ChatHandler:
    """Handles chat interactions and generates responses for financial data queries"""
    
    def __init__(self):
        self.context_memory = []
        self.llm_handler = None
        self.use_llm = False
          # Try to initialize LLM handler
        try:
            from .llm_handler import LLMHandler, DataContextBuilder
            self.llm_handler = LLMHandler(backend="ollama", model_name="starcoder2")
            self.data_context_builder = DataContextBuilder()
            self.use_llm = self.llm_handler.is_available()
        except ImportError:
            print("LLM handler not available - using fallback responses")
        
        self.financial_keywords = {
            'analysis': ['analyze', 'analysis', 'trend', 'pattern', 'insight'],
            'statistics': ['mean', 'average', 'median', 'std', 'statistics', 'summary'],
            'comparison': ['compare', 'comparison', 'versus', 'vs', 'difference'],            'visualization': ['chart', 'graph', 'plot', 'visualize', 'show'],
            'filtering': ['filter', 'where', 'select', 'find', 'search'],
            'calculation': ['calculate', 'compute', 'sum', 'total', 'count'],
            'time_series': ['time', 'date', 'period', 'monthly', 'yearly', 'daily']        }
    
    def generate_response(self, user_input, data=None):
        """Generate a response based on user input and available data"""
        
        # Store the conversation context
        self.context_memory.append({
            'user_input': user_input,
            'timestamp': datetime.now(),
            'has_data': data is not None
        })
        
        # If no data is available
        if data is None or data.empty:
            return self._handle_no_data_response(user_input)
        
        # Try LLM-enhanced response first
        if self.use_llm and self.llm_handler:
            try:
                # Build data context for LLM
                data_context, data_summary = self.data_context_builder.build_context(data)
                
                # Get LLM response
                llm_response = self.llm_handler.generate_financial_response(
                    user_input, data_context, data_summary
                )
                
                if llm_response and not llm_response.startswith("Error"):
                    return f"🤖 **AI-Enhanced Analysis**:\n\n{llm_response}"
            except Exception as e:
                print(f"LLM error: {e}")
                # Fall back to rule-based system
        
        # Fallback to rule-based analysis
        intent = self._analyze_intent(user_input)
        
        # Generate appropriate response based on intent
        if intent == 'greeting':
            return self._generate_greeting_response(data)
        elif intent == 'analysis':
            return self._generate_analysis_response(user_input, data)
        elif intent == 'statistics':
            return self._generate_statistics_response(user_input, data)
        elif intent == 'columns':
            return self._generate_columns_response(data)
        elif intent == 'summary':
            return self._generate_summary_response(data)
        elif intent == 'help':
            return self._generate_help_response()
        elif intent == 'question':
            return self._generate_question_response(user_input, data)
        elif intent == 'comparison':
            return self._generate_comparison_response(user_input, data)
        else:
            return self._generate_general_response(user_input, data)
    
    def _analyze_intent(self, user_input):
        """Analyze user input to determine intent"""
        user_input_lower = user_input.lower()
        
        # Greeting patterns
        greeting_patterns = ['hello', 'hi', 'hey', 'good morning', 'good afternoon']
        if any(pattern in user_input_lower for pattern in greeting_patterns):
            return 'greeting'
        
        # Help patterns
        help_patterns = ['help', 'what can you do', 'commands', 'options']
        if any(pattern in user_input_lower for pattern in help_patterns):
            return 'help'
        
        # Column information patterns
        column_patterns = ['columns', 'fields', 'what data', 'data structure']
        if any(pattern in user_input_lower for pattern in column_patterns):
            return 'columns'
        
        # Summary patterns
        summary_patterns = ['summary', 'overview', 'describe', 'info']
        if any(pattern in user_input_lower for pattern in summary_patterns):
            return 'summary'
        
        # Specific question patterns
        question_patterns = ['what is', 'how much', 'how many', 'when', 'which', 'where']
        if any(pattern in user_input_lower for pattern in question_patterns):
            return 'question'
        
        # Comparison patterns
        comparison_patterns = ['compare', 'vs', 'versus', 'difference between', 'higher', 'lower', 'better', 'worse']
        if any(pattern in user_input_lower for pattern in comparison_patterns):
            return 'comparison'
        
        # Check for specific financial analysis keywords
        for category, keywords in self.financial_keywords.items():
            if any(keyword in user_input_lower for keyword in keywords):
                return category
        
        return 'general'
    
    def _handle_no_data_response(self, user_input):
        """Handle responses when no data is available"""
        responses = [
            "I'd love to help you analyze your financial data! Please upload a CSV file first using the sidebar.",
            "To get started, please upload your financial data file (CSV format) using the file uploader on the left.",
            "I need some data to work with. Please upload a CSV file containing your financial data and I'll help you analyze it!",
            "Once you upload your financial data, I can help you with analysis, statistics, trends, and insights!"
        ]
        
        # Return a relevant response
        if 'upload' in user_input.lower():
            return "Use the file uploader in the sidebar to upload your CSV file. I support various financial data formats!"
        else:
            return responses[len(self.context_memory) % len(responses)]
    
    def _generate_greeting_response(self, data):
        """Generate a greeting response with data context"""
        row_count = len(data)
        col_count = len(data.columns)
        
        return f"Hello! I'm your financial data assistant. I can see you have {row_count} rows and {col_count} columns of data loaded. I can help you analyze trends, calculate statistics, and provide insights. What would you like to explore?"
    
    def _generate_analysis_response(self, user_input, data):
        """Generate analysis-focused responses"""
        responses = []
        
        # Basic data overview
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            responses.append(f"I found {len(numeric_cols)} numeric columns in your data: {', '.join(numeric_cols[:3])}{'...' if len(numeric_cols) > 3 else ''}")
            
            # Quick statistics for first numeric column
            first_col = numeric_cols[0]
            mean_val = data[first_col].mean()
            responses.append(f"For {first_col}: Average = {mean_val:.2f}, Min = {data[first_col].min():.2f}, Max = {data[first_col].max():.2f}")
        
        # Look for date columns for trend analysis
        date_cols = [col for col in data.columns if any(keyword in col.lower() for keyword in ['date', 'time'])]
        if date_cols:
            responses.append(f"I also detected time-based data in column '{date_cols[0]}' which we can use for trend analysis.")
        
        # Check for missing values
        missing_values = data.isnull().sum().sum()
        if missing_values > 0:
            responses.append(f"Note: Your data has {missing_values} missing values that might affect the analysis.")
        
        return " ".join(responses) if responses else "I can analyze your data for trends, patterns, and insights. What specific aspect would you like to explore?"
    
    def _generate_statistics_response(self, user_input, data):
        """Generate statistics-focused responses"""
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) == 0:
            return "I don't see any numeric columns in your data for statistical analysis. Your data appears to be mostly text-based."
        
        # Generate statistics for the first few numeric columns
        stats_info = []
        for col in numeric_cols[:2]:  # Limit to first 2 columns
            mean_val = data[col].mean()
            median_val = data[col].median()
            std_val = data[col].std()
            
            stats_info.append(f"**{col}**: Mean = {mean_val:.2f}, Median = {median_val:.2f}, Std Dev = {std_val:.2f}")
        
        response = "Here are the key statistics for your numeric data:\n\n" + "\n".join(stats_info)
        
        if len(numeric_cols) > 2:
            response += f"\n\nI can also analyze {len(numeric_cols) - 2} other numeric columns. Just ask about a specific column!"
        
        return response
    
    def _generate_columns_response(self, data):
        """Generate response about data structure"""
        response = f"Your dataset has {len(data.columns)} columns:\n\n"
        
        # Categorize columns
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        text_cols = data.select_dtypes(include=['object']).columns
        date_cols = data.select_dtypes(include=['datetime64']).columns
        
        if len(numeric_cols) > 0:
            response += f"**Numeric columns ({len(numeric_cols)})**: {', '.join(numeric_cols)}\n\n"
        
        if len(text_cols) > 0:
            response += f"**Text columns ({len(text_cols)})**: {', '.join(text_cols)}\n\n"
        
        if len(date_cols) > 0:
            response += f"**Date columns ({len(date_cols)})**: {', '.join(date_cols)}\n\n"
        
        response += "I can help you analyze any of these columns. What would you like to explore?"
        
        return response
    
    def _generate_summary_response(self, data):
        """Generate a comprehensive summary of the data"""
        summary_parts = []
        
        # Basic info
        summary_parts.append(f"📊 **Dataset Overview**: {len(data)} rows × {len(data.columns)} columns")
        
        # Column types
        numeric_cols = len(data.select_dtypes(include=[np.number]).columns)
        text_cols = len(data.select_dtypes(include=['object']).columns)
        summary_parts.append(f"📈 **Column Types**: {numeric_cols} numeric, {text_cols} text")
        
        # Missing data
        missing_total = data.isnull().sum().sum()
        missing_pct = (missing_total / (len(data) * len(data.columns))) * 100
        summary_parts.append(f"🔍 **Data Quality**: {missing_total} missing values ({missing_pct:.1f}%)")
        
        # Quick insights
        if numeric_cols > 0:
            first_numeric = data.select_dtypes(include=[np.number]).columns[0]
            avg_val = data[first_numeric].mean()
            summary_parts.append(f"💰 **Sample Insight**: Average {first_numeric} = {avg_val:.2f}")
        
        summary_parts.append("💬 **Next Steps**: Ask me about trends, statistics, or specific columns!")
        
        return "\n\n".join(summary_parts)
    
    def _generate_help_response(self):
        """Generate help information"""
        help_text = """
🤖 **I can help you with:**

📊 **Data Analysis**
- "Analyze my data" - Get insights and trends
- "Show me statistics" - Calculate means, medians, etc.
- "What are the columns?" - View data structure

📈 **Specific Queries**
- "Tell me about [column name]"
- "Compare [column1] vs [column2]"
- "Show trends over time"

🔍 **Data Exploration**
- "Summarize my data"
- "Find outliers"
- "What patterns do you see?"

💡 **Tips**: Be specific about what you want to analyze, and I'll provide detailed insights!
        """
        return help_text
    
    def _generate_general_response(self, user_input, data):
        """Generate a general response for unclear queries"""
        # Try to extract column names from the input
        mentioned_columns = [col for col in data.columns if col.lower() in user_input.lower()]
        
        if mentioned_columns:
            col = mentioned_columns[0]
            if data[col].dtype in ['int64', 'float64']:
                mean_val = data[col].mean()
                return f"I see you're asking about '{col}'. It's a numeric column with an average value of {mean_val:.2f}. Would you like more detailed statistics or analysis?"
            else:
                unique_count = data[col].nunique()
                return f"I see you're asking about '{col}'. It's a text column with {unique_count} unique values. The most common value is '{data[col].mode().iloc[0] if not data[col].mode().empty else 'N/A'}'."
        
        # Default response
        responses = [
            "I'm here to help analyze your financial data! Try asking about trends, statistics, or specific columns.",
            "Could you be more specific? I can help with data analysis, statistics, or insights about your dataset.",
            "I can analyze your data in many ways. Try asking: 'What are the main trends?' or 'Show me statistics for [column name]'."
        ]
        
        return responses[len(self.context_memory) % len(responses)]
    
    def _generate_question_response(self, user_input, data):
        """Generate response for specific questions about data"""
        user_input_lower = user_input.lower()
        
        # Extract column names mentioned in the question
        mentioned_columns = [col for col in data.columns if col.lower() in user_input_lower]
        
        # Handle different types of questions
        if 'how many' in user_input_lower:
            if mentioned_columns:
                col = mentioned_columns[0]
                unique_count = data[col].nunique()
                return f"There are {unique_count} unique values in the '{col}' column."
            else:
                return f"Your dataset has {len(data)} total rows."
        
        elif 'what is' in user_input_lower and 'average' in user_input_lower:
            if mentioned_columns:
                col = mentioned_columns[0]
                if data[col].dtype in ['int64', 'float64']:
                    avg_val = data[col].mean()
                    return f"The average {col} is {avg_val:.2f}"
                else:
                    return f"'{col}' is not a numeric column, so I can't calculate an average."
            else:
                numeric_cols = data.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) > 0:
                    first_col = numeric_cols[0]
                    avg_val = data[first_col].mean()
                    return f"The average {first_col} is {avg_val:.2f}"
        
        elif 'highest' in user_input_lower or 'maximum' in user_input_lower or 'max' in user_input_lower:
            if mentioned_columns:
                col = mentioned_columns[0]
                if data[col].dtype in ['int64', 'float64']:
                    max_val = data[col].max()
                    max_row = data[data[col] == max_val].iloc[0]
                    return f"The highest {col} is {max_val:.2f}. " + self._format_row_info(max_row, data.columns)
                else:
                    return f"'{col}' is not a numeric column."
        
        elif 'lowest' in user_input_lower or 'minimum' in user_input_lower or 'min' in user_input_lower:
            if mentioned_columns:
                col = mentioned_columns[0]
                if data[col].dtype in ['int64', 'float64']:
                    min_val = data[col].min()
                    min_row = data[data[col] == min_val].iloc[0]
                    return f"The lowest {col} is {min_val:.2f}. " + self._format_row_info(min_row, data.columns)
                else:
                    return f"'{col}' is not a numeric column."
        
        # Default question response
        return self._generate_general_response(user_input, data)
    
    def _generate_comparison_response(self, user_input, data):
        """Generate response for comparison questions"""
        user_input_lower = user_input.lower()
        mentioned_columns = [col for col in data.columns if col.lower() in user_input_lower]
        
        if len(mentioned_columns) >= 2:
            col1, col2 = mentioned_columns[0], mentioned_columns[1]
            
            # Check if both columns are numeric
            if data[col1].dtype in ['int64', 'float64'] and data[col2].dtype in ['int64', 'float64']:
                avg1 = data[col1].mean()
                avg2 = data[col2].mean()
                
                comparison = "higher" if avg1 > avg2 else "lower" if avg1 < avg2 else "equal to"
                difference = abs(avg1 - avg2)
                
                response = f"Comparing {col1} vs {col2}:\n"
                response += f"• {col1} average: {avg1:.2f}\n"
                response += f"• {col2} average: {avg2:.2f}\n"
                response += f"• {col1} is {comparison} {col2} by {difference:.2f}"
                
                return response
            else:
                return f"I can only compare numeric columns. {col1} and {col2} need to be numeric for comparison."
        
        elif len(mentioned_columns) == 1:
            col = mentioned_columns[0]
            if data[col].dtype in ['int64', 'float64']:
                stats = data[col].describe()
                return f"Statistics for {col}:\n• Mean: {stats['mean']:.2f}\n• Min: {stats['min']:.2f}\n• Max: {stats['max']:.2f}\n• Std Dev: {stats['std']:.2f}"
        
        return "Please specify which columns you'd like to compare. For example: 'Compare price vs volume'"
    
    def _format_row_info(self, row, columns):
        """Format row information for display"""
        info_parts = []
        for col in columns[:3]:  # Show first 3 columns
            info_parts.append(f"{col}: {row[col]}")
        return "(" + ", ".join(info_parts) + ")"
