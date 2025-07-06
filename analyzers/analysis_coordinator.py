"""
Analysis Coordinator for VariancePro
Coordinates all analysis operations and query routing
"""

from typing import Dict, Any, List, Tuple
from analyzers.enhanced_nl_to_sql_translator import TranslationResult
import pandas as pd


class AnalysisCoordinator:
    """Coordinates all analysis operations for the VariancePro application"""
    
    def __init__(self, app):
        """Initialize coordinator with reference to main app"""
        self.app = app
    
    def process_user_query(self, query: str) -> str:
        """Process user query with intelligent routing"""
        query_lower = query.lower()
        
        try:
            # Check for SQL-like queries or natural language that can be translated to SQL
            sql_indicators = [
                'show', 'find', 'get', 'list', 'top', 'bottom', 'where', 'greater than', 
                'less than', 'above', 'below', 'highest', 'lowest', 'count', 'sum', 
                'average', 'by region', 'by product', 'by channel', 'with'
            ]
            
            if any(indicator in query_lower for indicator in sql_indicators):
                # Try SQL-based analysis first
                sql_response = self.process_sql_query(query)
                if not sql_response.startswith("❌"):
                    return sql_response
            
            # Fallback to existing analysis patterns
            if any(word in query_lower for word in ['contribution', 'pareto', '80/20', 'top contributors']):
                return self.perform_contribution_analysis(query)
            
            elif any(word in query_lower for word in ['variance', 'budget', 'actual']):
                return self.perform_variance_analysis(query)
            
            elif any(word in query_lower for word in ['trend', 'time', 'ttm']):
                return self.perform_trend_analysis(query)
            
            elif any(word in query_lower for word in ['summary', 'overview', 'describe']):
                return self.generate_data_overview()
            
            else:
                # Try SQL query as last resort
                return self.process_sql_query(query)
                
        except Exception as e:
            return f"❌ **Analysis Error**: {str(e)}"
    
    def perform_contribution_analysis(self, query: str) -> str:
        """Perform contribution analysis"""
        try:
            if not self.app.column_suggestions:
                return "⚠️ **Data analysis not ready**. Please try uploading your file again."
            
            category_cols = self.app.column_suggestions.get('category_columns', [])
            value_cols = self.app.column_suggestions.get('value_columns', [])
            
            if not category_cols or not value_cols:
                return "⚠️ **Contribution analysis requires category and value columns**"
            
            # Use the analyzers
            results = self.app.contributor_analyzer.analyze(
                data=self.app.current_data,
                category_col=category_cols[0],
                value_col=value_cols[0]
            )
            
            return self.app.contributor_analyzer.format_for_chat()
            
        except Exception as e:
            return f"❌ **Contribution Analysis Error**: {str(e)}"
    
    def perform_variance_analysis(self, query: str) -> str:
        """Perform variance analysis"""
        try:
            budget_vs_actual = self.app.column_suggestions.get('budget_vs_actual', {})
            
            if not budget_vs_actual:
                return "⚠️ **Variance analysis requires budget and actual columns**"
            
            budget_col = list(budget_vs_actual.keys())[0]
            actual_col = budget_vs_actual[budget_col]
            
            results = self.app.financial_analyzer.analyze(
                data=self.app.current_data,
                budget_col=budget_col,
                actual_col=actual_col
            )
            
            return self.app.financial_analyzer.format_for_chat()
            
        except Exception as e:
            return f"❌ **Variance Analysis Error**: {str(e)}"
    
    def perform_trend_analysis(self, query: str) -> str:
        """Perform trend analysis"""
        try:
            date_cols = self.app.csv_loader.column_info.get('date_columns', [])
            numeric_cols = self.app.csv_loader.column_info.get('numeric_columns', [])
            
            if not date_cols or not numeric_cols:
                return "⚠️ **Trend analysis requires date and numeric columns**"
            
            results = self.app.timescale_analyzer.analyze(
                data=self.app.current_data,
                date_col=date_cols[0],
                value_cols=numeric_cols[:3]  # Limit to first 3 numeric columns
            )
            
            return self.app.timescale_analyzer.format_for_chat()
            
        except Exception as e:
            return f"❌ **Trend Analysis Error**: {str(e)}"
    
    def generate_data_overview(self) -> str:
        """Generate comprehensive data overview"""
        if not self.app.data_summary:
            return "⚠️ **No data summary available**. Please upload a file first."
        
        overview_parts = [
            "📊 **DATA OVERVIEW**",
            "",
            self.app.data_summary,
            "",
            f"📋 **Shape**: {len(self.app.current_data):,} rows × {len(self.app.current_data.columns)} columns",
            "",
            "🎯 **Available Analyses:**"
        ]
        
        # Add available analysis types
        if self.app.column_suggestions:
            if self.app.column_suggestions.get('category_columns') and self.app.column_suggestions.get('value_columns'):
                overview_parts.append("✅ Contribution Analysis")
            if self.app.column_suggestions.get('budget_vs_actual'):
                overview_parts.append("✅ Variance Analysis")
            if self.app.csv_loader.column_info.get('date_columns'):
                overview_parts.append("✅ Trend Analysis")
        
        return "\n".join(overview_parts)
    
    def generate_basic_response(self, query: str) -> str:
        """Generate basic response for unrecognized queries"""
        return f"""
💬 **I can help you analyze your data!**

Here are some things you can try:
• **"analyze contribution"** - Find top performers (80/20 analysis)
• **"analyze variance"** - Compare budget vs actual
• **"analyze trends"** - Look at time-based patterns
• **"summary"** - Get a data overview

Your data has **{len(self.app.current_data):,} rows** and **{len(self.app.current_data.columns)} columns**.

What would you like to explore?
"""
    
    def get_available_analyses(self) -> list:
        """Get list of available analysis types based on current data"""
        available = []
        
        if not self.app.column_suggestions:
            return available
        
        if self.app.column_suggestions.get('category_columns') and self.app.column_suggestions.get('value_columns'):
            available.append("Contribution Analysis")
        
        if self.app.column_suggestions.get('budget_vs_actual'):
            available.append("Variance Analysis")
        
        if self.app.csv_loader.column_info.get('date_columns'):
            available.append("Trend Analysis")
        
        return available
    
    def process_sql_query(self, query: str) -> str:
        """Process SQL-based queries using enhanced NL-to-SQL translation"""
        try:
            if self.app.current_data is None:
                return "⚠️ **Please upload a CSV file first** to start analyzing your data."
            
            # Try enhanced NL-to-SQL translator first
            result = self.app.enhanced_nl_to_sql.translate_to_sql(query)
            
            if result.success:
                # Execute SQL query on the data
                try:
                    # Use pandas query or SQL-like operations
                    import sqlite3
                    import tempfile
                    import os
                    
                    # Create temporary SQLite database
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.db', delete=False) as tmp:
                        db_path = tmp.name
                    
                    conn = sqlite3.connect(db_path)
                    
                    # Load data into SQLite
                    self.app.current_data.to_sql('data', conn, if_exists='replace', index=False)
                    
                    # Execute the generated SQL
                    query_result = pd.read_sql_query(result.sql_query, conn)
                    
                    conn.close()
                    os.unlink(db_path)  # Clean up temp file
                    
                    # Format the response
                    response_parts = [
                        f"🔍 **SQL Query Analysis**",
                        f"**Query**: {query}",
                        f"**Generated SQL**: `{result.sql_query}`",
                        f"**Explanation**: {result.explanation}",
                        f"**Confidence**: {result.confidence:.1%}",
                        "",
                        "📊 **Results**:",
                        "```",
                        query_result.to_string(index=False, max_rows=20),
                        "```"
                    ]
                    
                    if len(query_result) > 20:
                        response_parts.append(f"*Showing first 20 of {len(query_result)} results*")
                    
                    return "\n".join(response_parts)
                    
                except Exception as sql_error:
                    return f"❌ **SQL Execution Error**: {str(sql_error)}\n**Generated SQL**: `{result.sql_query}`"
            
            else:
                # Fallback to LLM-enhanced strategy
                llm_result = self.app.llm_enhanced_sql.translate_to_sql(query)
                
                if llm_result.success:
                    return f"🔍 **LLM-Enhanced SQL Translation**\n**Query**: {query}\n**Generated SQL**: `{llm_result.sql_query}`\n**Explanation**: {llm_result.explanation}"
                else:
                    return f"❌ **SQL Translation Failed**: {llm_result.error_message or 'Unable to translate query to SQL'}"
        
        except Exception as e:
            return f"❌ **SQL Query Error**: {str(e)}"
    
    def process_export_request(self, query: str) -> str:
        """Process export-related requests"""
        query_lower = query.lower()
        
        try:
            if self.app.current_data is None:
                return "⚠️ **Please upload a CSV file first** before exporting data."
            
            if "export to csv" in query_lower or "download csv" in query_lower:
                return self._export_to_csv()
            
            elif "export analysis" in query_lower or "export results" in query_lower:
                return self._export_analysis_results()
            
            elif "export summary" in query_lower or "summary report" in query_lower:
                return self._export_summary_report()
            
            else:
                return self._show_export_options()
                
        except Exception as e:
            return f"❌ **Export Error**: {str(e)}"
    
    def _export_to_csv(self) -> str:
        """Export current data to CSV"""
        try:
            import tempfile
            import os
            from datetime import datetime
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"variancepro_data_{timestamp}.csv"
            filepath = os.path.join(tempfile.gettempdir(), filename)
            
            self.app.current_data.to_csv(filepath, index=False)
            
            return f"✅ **CSV Export Complete**\n\n📄 **File**: {filename}\n📁 **Location**: {filepath}\n📊 **Records**: {len(self.app.current_data):,} rows\n📋 **Columns**: {len(self.app.current_data.columns)}\n\n*File saved to your system's temporary directory*"
            
        except Exception as e:
            return f"❌ **CSV Export Failed**: {str(e)}"
    
    def _export_analysis_results(self) -> str:
        """Export analysis results"""
        try:
            results = []
            
            # Perform quick analyses
            if self.app.column_suggestions:
                # Contribution analysis
                if self.app.column_suggestions.get('category_columns') and self.app.column_suggestions.get('value_columns'):
                    contrib_result = self.perform_contribution_analysis("contribution analysis")
                    results.append("## Contribution Analysis\n" + contrib_result)
                
                # Variance analysis
                variance_result = self.perform_variance_analysis("variance analysis")
                results.append("## Variance Analysis\n" + variance_result)
            
            if results:
                return "📊 **Analysis Export Ready**\n\n" + "\n\n".join(results)
            else:
                return "⚠️ **No analysis results to export**. Try running some analyses first."
                
        except Exception as e:
            return f"❌ **Analysis Export Failed**: {str(e)}"
    
    def _export_summary_report(self) -> str:
        """Export comprehensive summary report"""
        try:
            from datetime import datetime
            
            report_parts = [
                "# 📊 VariancePro Data Summary Report",
                f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "",
                "## 📈 Dataset Overview",
                f"- **Total Rows**: {len(self.app.current_data):,}",
                f"- **Total Columns**: {len(self.app.current_data.columns)}",
                f"- **Memory Usage**: {self.app.current_data.memory_usage(deep=True).sum() / 1024**2:.2f} MB",
                ""
            ]
            
            # Column information
            report_parts.append("## 📋 Column Details")
            for col in self.app.current_data.columns:
                dtype = str(self.app.current_data[col].dtype)
                null_count = self.app.current_data[col].isnull().sum()
                unique_count = self.app.current_data[col].nunique()
                report_parts.append(f"- **{col}**: {dtype} | {null_count} nulls | {unique_count} unique values")
            
            # Numeric statistics
            numeric_cols = self.app.current_data.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                report_parts.extend([
                    "",
                    "## 🔢 Numeric Statistics",
                    "```",
                    str(self.app.current_data[numeric_cols].describe()),
                    "```"
                ])
            
            return "\n".join(report_parts)
            
        except Exception as e:
            return f"❌ **Summary Report Failed**: {str(e)}"
    
    def _show_export_options(self) -> str:
        """Show available export options"""
        return """💾 **Export Options Available**

**Available Commands**:
• `export to csv` - Download data as CSV file
• `export analysis` - Export current analysis results
• `export summary` - Generate comprehensive data report

**Quick Actions**:
• Use the 💾 Export button for more options
• Visit the Export & Reports tab for advanced features

**Supported Formats**:
• CSV, Excel, JSON
• Analysis reports (TXT/MD)
• Visualization exports"""
