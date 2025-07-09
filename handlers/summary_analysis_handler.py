"""
Summary Analysis Handler for VariancePro v2.0

This module handles summary analysis functionality including:
- Data summary generation
- RAG-enhanced summary analysis
- Summary formatting and presentation

Following modular design principles to keep files focused and maintainable.
"""

import pandas as pd
from typing import Dict, Any


class SummaryAnalysisHandler:
    """
    Handles summary analysis with RAG enhancement.
    
    This class focuses solely on summary-related functionality
    to maintain single responsibility principle.
    """
    
    def __init__(self, app_core, rag_manager=None, rag_analyzer=None):
        """
        Initialize the summary analysis handler.
        
        Args:
            app_core: Reference to the main application core for data access
            rag_manager: RAG Document Manager for document context (optional)
            rag_analyzer: RAG Enhanced Analyzer for enhanced analysis (optional)
        """
        self.app_core = app_core
        self.rag_manager = rag_manager
        self.rag_analyzer = rag_analyzer
    
    def handle_summary_analysis(self) -> str:
        """
        Handle summary analysis with RAG enhancement.
        
        Returns:
            str: Summary analysis response with RAG context if available
        """
        current_data, data_summary = self.app_core.get_current_data()
        
        # Generate a human-readable summary from the data
        if data_summary and isinstance(data_summary, dict):
            # Convert the data_summary dict to a readable format
            base_summary = self._format_data_summary_dict(data_summary, current_data)
        elif isinstance(data_summary, str):
            # If it's already a string, use it directly
            base_summary = f"📊 **Data Summary**\n\n{data_summary}"
        else:
            # Generate basic summary if no cached summary
            base_summary = self._generate_basic_summary(current_data)
        
        # Enhance with RAG if available
        if self.rag_manager and self.rag_analyzer and self.rag_manager.has_documents():
            return self._enhance_with_rag(base_summary, current_data)
        
        return base_summary
    
    def _generate_basic_summary(self, current_data: pd.DataFrame) -> str:
        """
        Generate a basic summary when no cached summary is available.
        
        Args:
            current_data: The pandas DataFrame to summarize
            
        Returns:
            str: Basic summary text
        """
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
    
    def _enhance_with_rag(self, base_summary: str, current_data: pd.DataFrame) -> str:
        """
        Enhance summary with RAG context.
        
        Args:
            base_summary: The base summary to enhance
            current_data: The pandas DataFrame
            
        Returns:
            str: RAG-enhanced summary
        """
        try:
            print("🔍 Enhancing summary with RAG context...")
            
            row_count = len(current_data)
            col_count = len(current_data.columns)
            
            # Create analysis context for RAG enhancement
            analysis_context = f"""
Data Summary Analysis:
- Dataset: {row_count:,} rows × {col_count} columns
- Key columns: {', '.join(current_data.columns[:10])}
- Data types: {len(current_data.select_dtypes(include=['number']).columns)} numeric, {len(current_data.select_dtypes(include=['object']).columns)} categorical
"""
            
            # Enhance with RAG
            enhanced_result = self.rag_analyzer.enhance_general_analysis(
                analysis_data={'summary': base_summary, 'context': analysis_context},
                analysis_type='summary',
                query_context="dataset summary and overview analysis"
            )
            
            if enhanced_result.get('success'):
                print(f"✅ RAG-enhanced summary generated with {enhanced_result.get('documents_used', 0)} document(s)")
                
                # Log the prompt being used for validation
                if 'prompt_used' in enhanced_result:
                    print("📝 PROMPT USED FOR RAG ENHANCEMENT:")
                    print("=" * 50)
                    print(enhanced_result['prompt_used'])
                    print("=" * 50)
                
                return f"""{base_summary}

{enhanced_result['enhanced_analysis']}

---
🔍 **RAG Enhancement**: Analysis enhanced with {enhanced_result.get('documents_used', 0)} document(s)"""
            else:
                print(f"⚠️ RAG enhancement failed: {enhanced_result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ RAG enhancement error: {str(e)}")
        
        return base_summary
    
    def _format_data_summary_dict(self, data_summary: dict, current_data: pd.DataFrame) -> str:
        """
        Convert data summary dictionary to human-readable format.
        
        Args:
            data_summary: Dictionary containing data analysis results
            current_data: The pandas DataFrame
            
        Returns:
            str: Formatted, human-readable summary
        """
        try:
            # Extract key information from the dictionary
            row_count = data_summary.get('row_count', len(current_data))
            col_count = data_summary.get('column_count', len(current_data.columns))
            columns = data_summary.get('columns', list(current_data.columns))
            basic_stats = data_summary.get('basic_stats', {})
            
            # Start building the summary
            summary_parts = [
                "📊 **Data Summary**",
                "",
                f"**Dataset Overview**: {row_count:,} rows × {col_count} columns",
                ""
            ]
            
            # Add column information
            if columns:
                display_cols = columns[:5]
                if len(columns) > 5:
                    display_cols.append("...")
                summary_parts.append(f"**Columns**: {', '.join(display_cols)}")
                summary_parts.append("")
            
            # Add data types info
            column_types = data_summary.get('column_types', {})
            if column_types:
                numeric_cols = sum(1 for dtype in column_types.values() if 'int' in str(dtype).lower() or 'float' in str(dtype).lower())
                text_cols = sum(1 for dtype in column_types.values() if 'object' in str(dtype).lower())
                summary_parts.append(f"**Data Types**: {numeric_cols} numeric, {text_cols} text")
                summary_parts.append("")
            
            # Add key statistics for numeric columns
            if basic_stats:
                summary_parts.append("**Key Statistics**:")
                for col, stats in list(basic_stats.items())[:3]:  # Show first 3 numeric columns
                    if isinstance(stats, dict) and 'mean' in stats:
                        summary_parts.append(f"• **{col}**: Avg ${stats['mean']:,.0f}, Range ${stats['min']:,.0f}-${stats['max']:,.0f}")
                summary_parts.append("")
            
            # Add data quality insights
            data_quality = data_summary.get('data_quality', {})
            if data_quality:
                null_columns = [col for col, quality in data_quality.items() if quality.get('null_count', 0) > 0]
                if null_columns:
                    summary_parts.append(f"**Data Quality**: {len(null_columns)} columns have missing values")
                else:
                    summary_parts.append("**Data Quality**: No missing values detected")
                summary_parts.append("")
            
            # Add suggested actions
            summary_parts.extend([
                "**Suggested Actions**:",
                "• Try trends analysis for time-based insights",
                "• Use variance analysis for performance gaps",
                "• Ask questions like 'show me the top performers'"
            ])
            
            return "\n".join(summary_parts)
            
        except Exception as e:
            print(f"[DEBUG] Error formatting data summary: {e}")
            # Fallback to basic summary
            row_count = len(current_data)
            col_count = len(current_data.columns)
            return f"""📊 **Data Summary**

**Dataset Overview**: {row_count:,} rows × {col_count} columns

**Columns**: {', '.join(current_data.columns[:5])}{"..." if len(current_data.columns) > 5 else ""}

💡 **Note**: Summary formatting issue occurred. You can still analyze your data!"""
