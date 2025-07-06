"""
Quick Action Handler for VariancePro v2.0

This module handles all quick action button functionality including:
- Summary analysis
- Trends analysis
- Top/Bottom N analysis
- Action routing and processing
- Response formatting

Extracted from app_v2.py to follow modular design principles.
"""

from datetime import datetime
from typing import List, Dict, Any

from handlers.timestamp_handler import TimestampHandler


class QuickActionHandler:
    """
    Handles quick action button processing and analysis.
    
    This class encapsulates all quick action functionality to keep
    the main application code clean and focused.
    """
    
    def __init__(self, app_core):
        """
        Initialize the quick action handler.
        
        Args:
            app_core: Reference to the main application core for data access
        """
        self.app_core = app_core
        self.timestamp_handler = TimestampHandler()
    
    def handle_action(self, action: str, history: List[Dict]) -> List[Dict]:
        """
        Handle quick action button clicks by creating a proper user-assistant interaction.
        
        Args:
            action (str): The action to perform (summary, trends, top5, etc.)
            history (List[Dict]): The current chat history
            
        Returns:
            List[Dict]: Updated chat history with the action and response
        """
        print(f"[DEBUG] Quick action triggered: {action}")
        
        # Generate timestamp for browser local time
        current_timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Create a user message for the action
        user_message = f"Please provide {action} analysis"
        
        # Add timestamped user message to history
        timestamped_user_message = {
            "role": "user", 
            "content": self.timestamp_handler.add_timestamp_to_message(user_message, current_timestamp)
        }
        history.append(timestamped_user_message)
        
        # Check if data is available
        if not self.app_core.has_data():
            response = "⚠️ **Please upload a CSV file first** to use quick analysis features."
        else:
            # Route to appropriate action handler
            response = self._route_action(action)
        
        # Add the timestamped assistant response to chat history
        timestamped_assistant_message = {
            "role": "assistant", 
            "content": self.timestamp_handler.add_timestamp_to_message(response, current_timestamp)
        }
        history.append(timestamped_assistant_message)
        return history
    
    def _route_action(self, action: str) -> str:
        """
        Route the action to the appropriate handler.
        
        Args:
            action (str): The action to perform
            
        Returns:
            str: The analysis response
        """
        action_lower = action.lower()
        
        if action_lower == "summary":
            return self._handle_summary_action()
        elif action_lower == "trends":
            return self._handle_trends_action()
        elif action_lower == "variance":
            return self._handle_variance_action()
        elif "top" in action_lower or "bottom" in action_lower:
            return self._handle_top_bottom_action(action)
        else:
            return f"🔍 **{action.title()} Analysis**\n\nThis feature is being implemented. You can ask questions about your data in the chat!"
    
    def _handle_summary_action(self) -> str:
        """
        Handle summary quick action.
        
        Returns:
            str: Summary analysis response
        """
        current_data, data_summary = self.app_core.get_current_data()
        
        if data_summary:
            return f"📊 **Data Summary**\n\n{data_summary}"
        else:
            # Generate basic summary if no cached summary
            row_count = len(current_data)
            col_count = len(current_data.columns)
            columns = ', '.join(current_data.columns[:5])
            if len(current_data.columns) > 5:
                columns += "..."
            
            return f"""📊 **Quick Summary**

**Dataset Overview**: {row_count:,} rows × {col_count} columns

**Columns**: {columns}

**Data Types**: {len(current_data.select_dtypes(include=['number']).columns)} numeric, {len(current_data.select_dtypes(include=['object']).columns)} text

💡 **Next Steps**: Try trends analysis or ask specific questions about your data!"""
    
    def _handle_trends_action(self) -> str:
        """
        Handle trends quick action.
        
        Returns:
            str: Trends analysis response
        """
        if self.app_core.timescale_analyzer is None:
            return "⚠️ **Trends Analysis**: Timescale analyzer not available. Please check the system configuration."
        
        try:
            current_data, _ = self.app_core.get_current_data()
            
            # Detect date columns for trends analysis
            date_columns = self._detect_date_columns(current_data)
            
            if not date_columns:
                return "⚠️ **Trends Analysis**: No date columns detected in your data. Trends analysis requires time-based data."
            
            # Get numeric columns
            numeric_columns = current_data.select_dtypes(include=['number']).columns.tolist()
            
            if not numeric_columns:
                return "⚠️ **Trends Analysis**: No numeric columns found. Trends analysis requires numerical data to analyze."
            
            # Perform the analysis
            self.app_core.timescale_analyzer.analyze(
                data=current_data,
                date_col=date_columns[0],
                value_cols=numeric_columns[:3]  # Limit to first 3 columns
            )
            
            if self.app_core.timescale_analyzer.status == "completed":
                return f"📈 **Trends Analysis**\n\n{self.app_core.timescale_analyzer.format_for_chat()}"
            else:
                return f"❌ **Trends Analysis Failed**: {self.app_core.timescale_analyzer.status}"
                
        except Exception as e:
            return f"❌ **Trends Analysis Error**: {str(e)}"
    
    def _handle_variance_action(self) -> str:
        """
        Handle variance analysis quick action.
        
        Returns:
            str: Variance analysis response
        """
        try:
            current_data, _ = self.app_core.get_current_data()
            
            # Import the variance analyzer
            from analyzers.variance_analyzer import VarianceAnalyzer
            
            variance_analyzer = VarianceAnalyzer()
            
            # Try to detect common variance comparison patterns
            columns = current_data.columns.tolist()
            
            # Look for common variance column patterns
            variance_pairs = variance_analyzer.detect_variance_pairs(columns)
            
            if not variance_pairs:
                return """⚠️ **Variance Analysis**: No obvious variance comparison pairs detected.

**Expected column patterns:**
• Actual vs Planned (e.g., 'Actual Sales', 'Planned Sales')
• Budget vs Actual (e.g., 'Budget', 'Actual')
• Budget vs Sales (e.g., 'Budget Revenue', 'Sales Revenue')

**Available columns**: """ + ", ".join(columns[:10]) + ("..." if len(columns) > 10 else "") + """

💡 **Tip**: Ask me specific questions like "compare actual vs planned" or manually specify columns for variance analysis."""
            
            # Perform variance analysis on the first detected pair
            first_pair = variance_pairs[0]
            result = variance_analyzer.calculate_variance(
                data=current_data,
                actual_col=first_pair['actual'],
                planned_col=first_pair['planned'],
                analysis_type=first_pair.get('type', 'absolute')
            )
            
            return f"""📊 **Variance Analysis Results**

**Comparison**: {first_pair['actual']} vs {first_pair['planned']}

{result}

💡 **Additional Pairs Detected**: {len(variance_pairs) - 1} more variance comparison opportunities available."""
            
        except Exception as e:
            return f"❌ **Variance Analysis Error**: {str(e)}"
    
    def _handle_top_bottom_action(self, action: str) -> str:
        """
        Handle top/bottom N analysis actions.
        
        Args:
            action (str): The action (top5, bottom10, etc.)
            
        Returns:
            str: Analysis response
        """
        try:
            current_data, _ = self.app_core.get_current_data()
            
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
            numeric_columns = current_data.select_dtypes(include=['number']).columns.tolist()
            
            if not numeric_columns:
                return f"⚠️ **{direction.title()} {n} Analysis**: No numeric columns found in your data."
            
            # Get categorical columns for grouping
            categorical_columns = current_data.select_dtypes(include=['object']).columns.tolist()
            
            # Use the first numeric column for values
            value_col = numeric_columns[0]
            
            # Use the first categorical column for categories (if available)
            if categorical_columns:
                category_col = categorical_columns[0]
                
                # Group by category and sum values
                grouped_data = current_data.groupby(category_col)[value_col].sum().reset_index()
                
                # Sort and get top/bottom N
                if direction == "top":
                    result_data = grouped_data.nlargest(n, value_col)
                else:
                    result_data = grouped_data.nsmallest(n, value_col)
                    
                # Format results
                result_text = ""
                for idx, row in result_data.iterrows():
                    result_text += f"• **{row[category_col]}**: {row[value_col]:,.2f}\n"
                
                return f"""🔍 **{direction.title()} {n} Analysis**

{result_text}

💡 **Insight**: These are the {direction} performing categories when grouped by {category_col} and summed by {value_col}."""
            
            else:
                # No categorical columns, just sort by the numeric column
                if direction == "top":
                    result_data = current_data.nlargest(n, value_col)
                else:
                    result_data = current_data.nsmallest(n, value_col)
                
                # Create a simple display
                result_text = ""
                for idx, row in result_data.head(n).iterrows():
                    result_text += f"• Row {idx + 1}: {row[value_col]:,.2f}\n"
                
                return f"""🔍 **{direction.title()} {n} Analysis**

{result_text}

💡 **Insight**: These are the {direction} {n} values from the {value_col} column."""
                
        except Exception as e:
            return f"❌ **{action.title()} Analysis Error**: {str(e)}"
    
    def _detect_date_columns(self, df) -> List[str]:
        """
        Detect potential date columns in the DataFrame.
        
        Args:
            df: The DataFrame to analyze
            
        Returns:
            List[str]: List of potential date column names
        """
        date_columns = []
        
        for col in df.columns:
            col_lower = col.lower()
            # Check for common date column names
            if any(date_word in col_lower for date_word in ['date', 'time', 'day', 'month', 'year']):
                date_columns.append(col)
                continue
            
            # Check if the column can be parsed as dates
            try:
                import pandas as pd
                pd.to_datetime(df[col].dropna().head(10), errors='raise')
                date_columns.append(col)
            except:
                continue
        
        return date_columns
