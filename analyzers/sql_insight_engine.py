"""
Enhanced SQL Insight Engine - AI-Powered SQL Query Analysis with Smart Field Detection
Provides SQL query execution with LLM-powered field type inference and comprehensive insights
"""

import pandas as pd
import json
import uuid
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import requests
from io import StringIO
import re

class SQLInsightEngine:
    """
    Enhanced SQL Insight Engine with AI-powered field detection and analysis
    
    This class provides:
    1. AI-powered field type inference using Ollama/Gemma
    2. Safe SQL query execution on CSV data
    3. LLM-powered insight generation from query results
    4. Interactive field picker for query building
    5. Query template management and reusability
    """
    
    def __init__(self):
        """Initialize the Enhanced SQL Insight Engine"""
        self.data: Optional[pd.DataFrame] = None
        self.table_name: str = "dataset"
        self.schema: Dict[str, str] = {}
        self.field_metadata: Dict[str, Dict] = {}
        self.saved_queries: Dict[str, Dict] = {}
        self.query_history: List[Dict] = []
        print("🧠 Enhanced SQL Insight Engine initialized with AI-powered field detection")
    
    def load_dataset(self, df: pd.DataFrame, dataset_name: str = "dataset") -> Dict[str, Any]:
        """
        Load a dataset with AI-powered field analysis
        
        Args:
            df: The pandas DataFrame to analyze
            dataset_name: Name for the dataset table
            
        Returns:
            Dict containing schema information and field picker data
        """
        try:
            self.data = df.copy()
            self.table_name = dataset_name
            
            # Generate enhanced schema with AI
            print("🔍 Analyzing dataset structure with AI...")
            self.schema = self._ai_analyze_schema(df)
            self.field_metadata = self._generate_field_metadata(df)
            
            schema_info = {
                "status": "success",
                "table_name": self.table_name,
                "row_count": len(df),
                "column_count": len(df.columns),
                "schema": self.schema,
                "field_metadata": self.field_metadata,
                "sample_data": df.head(3).to_dict('records'),
                "field_picker_data": self._generate_field_picker_data()
            }
            
            print(f"📊 Dataset loaded with AI analysis: {len(df)} rows, {len(df.columns)} columns")
            return schema_info
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to load dataset: {str(e)}"
            }
    
    def _ai_analyze_schema(self, df: pd.DataFrame) -> Dict[str, str]:
        """
        Use AI to analyze DataFrame schema with intelligent type inference
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            Dictionary mapping column names to AI-inferred data types
        """
        # Get basic pandas types first as fallback
        basic_schema = {}
        for col in df.columns:
            dtype = df[col].dtype
            
            if pd.api.types.is_numeric_dtype(dtype):
                if pd.api.types.is_integer_dtype(dtype):
                    basic_schema[col] = "INTEGER"
                else:
                    basic_schema[col] = "REAL"
            elif pd.api.types.is_datetime64_any_dtype(dtype):
                basic_schema[col] = "DATE"
            else:
                basic_schema[col] = "TEXT"
        
        # Use AI for enhanced type inference
        try:
            enhanced_schema = self._llm_enhanced_schema_analysis(df, basic_schema)
            print("✅ AI schema analysis completed successfully")
            return enhanced_schema
        except Exception as e:
            print(f"⚠️ AI schema analysis failed, using basic types: {e}")
            return basic_schema
    
    def _llm_enhanced_schema_analysis(self, df: pd.DataFrame, basic_schema: Dict[str, str]) -> Dict[str, str]:
        """
        Use LLM to enhance schema analysis with semantic understanding
        
        Args:
            df: DataFrame to analyze
            basic_schema: Basic pandas-inferred schema
            
        Returns:
            Enhanced schema with LLM insights
        """
        # Prepare sample data for LLM analysis
        sample_data = {}
        for col in df.columns[:10]:  # Limit to first 10 columns for performance
            sample_values = df[col].dropna().head(5).astype(str).tolist()
            sample_data[col] = {
                "sample_values": sample_values,
                "pandas_type": basic_schema[col],
                "null_count": int(df[col].isnull().sum()),
                "unique_count": int(df[col].nunique()),
                "total_count": len(df[col])
            }
        
        prompt = f"""
        Analyze these dataset columns and suggest appropriate SQL data types based on semantic meaning.
        Look at the sample values and patterns to determine the best type.
        
        Column Analysis:
        {json.dumps(sample_data, indent=2)}
        
        For each column, suggest one of these SQL types:
        - INTEGER (whole numbers, counts, IDs)
        - REAL (decimal numbers, prices, measurements)
        - TEXT (names, descriptions, free text)
        - DATE (dates, timestamps, time values)
        - CURRENCY (monetary amounts)
        - PERCENTAGE (percentage values)
        - CATEGORY (limited set of categorical values)
        - ID (unique identifiers)
        
        Consider:
        - Sample values and their patterns
        - Column names (hint at meaning)
        - Data distribution (unique count vs total)
        
        Respond ONLY with valid JSON in this exact format:
        {{"column_name": "TYPE", "column_name2": "TYPE"}}
        """
        
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "gemma2:latest",
                    "prompt": prompt,
                    "stream": False
                },
                timeout=20
            )
            
            if response.status_code == 200:
                result = response.json()
                llm_response = result.get('response', '{}').strip()
                
                # Extract JSON from response
                try:
                    # Find JSON in response
                    start_idx = llm_response.find('{')
                    end_idx = llm_response.rfind('}') + 1
                    if start_idx >= 0 and end_idx > start_idx:
                        json_str = llm_response[start_idx:end_idx]
                        enhanced_types = json.loads(json_str)
                        
                        # Validate and merge with basic schema
                        final_schema = {}
                        for col in df.columns:
                            if col in enhanced_types and enhanced_types[col] in [
                                "INTEGER", "REAL", "TEXT", "DATE", "CURRENCY", 
                                "PERCENTAGE", "CATEGORY", "ID"
                            ]:
                                final_schema[col] = enhanced_types[col]
                            else:
                                final_schema[col] = basic_schema[col]
                        
                        return final_schema
                except json.JSONDecodeError as e:
                    print(f"JSON decode error: {e}")
                    
        except Exception as e:
            print(f"LLM request failed: {e}")
        
        # Fallback to basic schema
        return basic_schema
    
    def _generate_field_metadata(self, df: pd.DataFrame) -> Dict[str, Dict]:
        """
        Generate comprehensive metadata for each field
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            Field metadata dictionary
        """
        metadata = {}
        
        for col in df.columns:
            col_data = df[col]
            
            # Basic statistics
            stats = {
                "name": col,
                "type": self.schema.get(col, "TEXT"),
                "null_count": int(col_data.isnull().sum()),
                "unique_count": int(col_data.nunique()),
                "total_count": len(col_data),
                "sample_values": col_data.dropna().head(3).astype(str).tolist()
            }
            
            # Type-specific analysis
            if pd.api.types.is_numeric_dtype(col_data):
                stats.update({
                    "min_value": float(col_data.min()) if not col_data.empty else None,
                    "max_value": float(col_data.max()) if not col_data.empty else None,
                    "mean_value": float(col_data.mean()) if not col_data.empty else None,
                    "is_numeric": True
                })
            else:
                stats.update({
                    "max_length": int(col_data.astype(str).str.len().max()) if not col_data.empty else 0,
                    "is_numeric": False
                })
            
            # Categorization hints
            unique_ratio = stats["unique_count"] / stats["total_count"] if stats["total_count"] > 0 else 0
            stats["is_likely_category"] = unique_ratio < 0.1 and stats["unique_count"] < 50
            stats["is_likely_id"] = unique_ratio > 0.9 and stats["unique_count"] > stats["total_count"] * 0.9
            
            metadata[col] = stats
        
        return metadata
    
    def _generate_field_picker_data(self) -> List[Dict]:
        """
        Generate field picker data for UI
        
        Returns:
            List of field picker items
        """
        picker_data = []
        
        for col, metadata in self.field_metadata.items():
            picker_item = {
                "name": col,
                "type": metadata["type"],
                "display_name": col.replace("_", " ").title(),
                "description": self._generate_field_description(metadata),
                "is_numeric": metadata.get("is_numeric", False),
                "sample_values": metadata["sample_values"],
                "unique_count": metadata["unique_count"],
                "null_count": metadata["null_count"]
            }
            picker_data.append(picker_item)
        
        return sorted(picker_data, key=lambda x: x["name"])
    
    def _generate_field_description(self, metadata: Dict) -> str:
        """
        Generate a human-readable description for a field
        
        Args:
            metadata: Field metadata
            
        Returns:
            Description string
        """
        desc_parts = []
        
        # Type description
        type_desc = {
            "INTEGER": "Whole numbers",
            "REAL": "Decimal numbers", 
            "TEXT": "Text data",
            "DATE": "Date/time values",
            "CURRENCY": "Monetary amounts",
            "PERCENTAGE": "Percentage values",
            "CATEGORY": "Categorical data",
            "ID": "Unique identifiers"
        }
        desc_parts.append(type_desc.get(metadata["type"], "Data"))
        
        # Stats
        if metadata["is_numeric"]:
            if metadata.get("min_value") is not None:
                desc_parts.append(f"Range: {metadata['min_value']:.2f} - {metadata['max_value']:.2f}")
        else:
            if metadata.get("max_length"):
                desc_parts.append(f"Max length: {metadata['max_length']}")
        
        # Quality info
        if metadata["null_count"] > 0:
            desc_parts.append(f"{metadata['null_count']} nulls")
        
        desc_parts.append(f"{metadata['unique_count']} unique values")
        
        return " | ".join(desc_parts)
    
    def execute_sql_query(self, query: str, generate_insights: bool = True) -> Dict[str, Any]:
        """
        Execute SQL query with optional AI insight generation
        
        Args:
            query: SQL query string to execute
            generate_insights: Whether to generate AI insights
            
        Returns:
            Dictionary containing query results and insights
        """
        if self.data is None:
            return {
                "status": "error",
                "message": "No dataset loaded. Please upload a CSV file first."
            }
        
        # Validate query safety
        safety_check = self._validate_query_safety(query)
        if not safety_check["is_safe"]:
            return {
                "status": "error",
                "message": f"Query validation failed: {safety_check['reason']}"
            }
        
        try:
            # Create in-memory SQLite database
            conn = sqlite3.connect(':memory:')
            
            # Load data into SQLite
            self.data.to_sql(self.table_name, conn, index=False, if_exists='replace')
            
            # Execute query
            result_df = pd.read_sql_query(query, conn)
            conn.close()
            
            # Prepare results
            query_results = {
                "status": "success",
                "query_id": str(uuid.uuid4())[:8],
                "data": result_df.to_dict('records'),
                "columns": list(result_df.columns),
                "row_count": len(result_df),
                "execution_time": datetime.now().isoformat(),
                "query": query
            }
            
            # Generate AI insights if requested
            if generate_insights:
                print("🧠 Generating AI insights from query results...")
                insights_result = self.generate_ai_insights(query, query_results)
                query_results["insights"] = insights_result
            
            # Store in history
            self.query_history.append({
                "id": query_results["query_id"],
                "timestamp": query_results["execution_time"],
                "query": query,
                "row_count": len(result_df),
                "status": "success",
                "has_insights": generate_insights
            })
            
            return query_results
            
        except Exception as e:
            # Store failed query in history
            error_id = str(uuid.uuid4())[:8]
            self.query_history.append({
                "id": error_id,
                "timestamp": datetime.now().isoformat(),
                "query": query,
                "error": str(e),
                "status": "error"
            })
            
            return {
                "status": "error",
                "message": f"Query execution failed: {str(e)}",
                "query_id": error_id,
                "query": query
            }
    
    def generate_ai_insights(self, query: str, query_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive AI-powered insights from query results
        
        Args:
            query: The SQL query that was executed
            query_results: Results from query execution
            
        Returns:
            Dictionary containing AI-generated insights
        """
        if query_results["status"] != "success":
            return {
                "status": "error",
                "message": "Cannot generate insights for failed query"
            }
        
        try:
            # Prepare comprehensive data summary
            data_summary = self._prepare_comprehensive_data_summary(query_results)
            
            # Create detailed prompt for LLM
            prompt = self._create_comprehensive_insight_prompt(query, data_summary, query_results)
            
            # Get insights from Ollama
            insights_text = self._query_ollama_for_insights(prompt)
            
            return {
                "status": "success",
                "insights_text": insights_text,
                "data_summary": data_summary,
                "generated_at": datetime.now().isoformat(),
                "query_analyzed": query
            }
            
        except Exception as e:
            print(f"⚠️ AI insights generation failed: {e}")
            # Fallback to statistical insights
            statistical_insights = self._generate_statistical_insights(query_results["data"])
            
            return {
                "status": "fallback",
                "insights_text": statistical_insights,
                "message": f"AI insights unavailable, using statistical analysis: {str(e)}",
                "generated_at": datetime.now().isoformat(),
                "query_analyzed": query
            }
    
    def _prepare_comprehensive_data_summary(self, query_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare comprehensive summary for LLM analysis
        
        Args:
            query_results: Query execution results
            
        Returns:
            Comprehensive data summary
        """
        data = query_results["data"]
        if not data:
            return {"row_count": 0, "summary": "No data returned"}
        
        df = pd.DataFrame(data)
        
        summary = {
            "row_count": len(df),
            "column_count": len(df.columns),
            "columns": list(df.columns),
            "sample_rows": data[:5],  # First 5 rows
            "numeric_stats": {},
            "text_stats": {},
            "data_quality": {}
        }
        
        # Analyze numeric columns
        numeric_cols = df.select_dtypes(include=['number']).columns
        for col in numeric_cols:
            if col in df.columns:
                summary["numeric_stats"][col] = {
                    "mean": float(df[col].mean()),
                    "median": float(df[col].median()),
                    "min": float(df[col].min()),
                    "max": float(df[col].max()),
                    "std": float(df[col].std())
                }
        
        # Analyze text columns
        text_cols = df.select_dtypes(include=['object']).columns
        for col in text_cols:
            if col in df.columns:
                summary["text_stats"][col] = {
                    "unique_count": int(df[col].nunique()),
                    "most_common": df[col].value_counts().head(3).to_dict(),
                    "avg_length": float(df[col].astype(str).str.len().mean())
                }
        
        # Data quality assessment
        for col in df.columns:
            null_count = df[col].isnull().sum()
            summary["data_quality"][col] = {
                "null_count": int(null_count),
                "null_percentage": float(null_count / len(df) * 100) if len(df) > 0 else 0
            }
        
        return summary
    
    def _create_comprehensive_insight_prompt(self, query: str, data_summary: Dict, query_results: Dict) -> str:
        """
        Create comprehensive prompt for LLM insight generation
        
        Args:
            query: Original SQL query
            data_summary: Summary of the data
            query_results: Full query results
            
        Returns:
            Formatted prompt string for insights
        """
        prompt = f"""
        As a financial data analyst, analyze this SQL query and its results to provide actionable business insights.

        SQL QUERY EXECUTED:
        {query}

        RESULTS SUMMARY:
        - Total rows returned: {data_summary['row_count']}
        - Columns: {', '.join(data_summary['columns'])}

        SAMPLE DATA (first 5 rows):
        {json.dumps(data_summary['sample_rows'], indent=2)}

        NUMERIC ANALYSIS:
        {json.dumps(data_summary['numeric_stats'], indent=2)}

        TEXT DATA ANALYSIS:
        {json.dumps(data_summary['text_stats'], indent=2)}

        DATA QUALITY:
        {json.dumps(data_summary['data_quality'], indent=2)}

        Please provide a comprehensive analysis including:

        1. **EXECUTIVE SUMMARY**: What does this data tell us? (2-3 sentences)

        2. **KEY FINDINGS**: 
           - Most significant patterns or trends
           - Notable outliers or anomalies
           - Statistical insights

        3. **BUSINESS IMPLICATIONS**:
           - What this means for business decisions
           - Potential opportunities or risks identified
           - Recommended actions

        4. **DATA QUALITY ASSESSMENT**:
           - Completeness and reliability of the data
           - Any limitations to consider

        5. **NEXT STEPS**:
           - Suggested follow-up analyses
           - Additional data that might be needed

        Format your response as clear, professional analysis suitable for business stakeholders. 
        Use bullet points for key findings. Keep it under 400 words but comprehensive.
        """
        
        return prompt
    
    def _query_ollama_for_insights(self, prompt: str) -> str:
        """
        Query Ollama for comprehensive AI-generated insights
        
        Args:
            prompt: The prompt to send to Ollama
            
        Returns:
            AI-generated insights text
        """
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "gemma2:latest",
                    "prompt": prompt,
                    "stream": False
                },
                timeout=45  # Longer timeout for comprehensive analysis
            )
            
            if response.status_code == 200:
                result = response.json()
                insights = result.get('response', 'No insights generated')
                
                # Clean up the response
                insights = insights.strip()
                if insights:
                    return insights
                else:
                    return "No insights could be generated from the query results."
            else:
                raise Exception(f"Ollama API returned status {response.status_code}")
                
        except Exception as e:
            raise Exception(f"Failed to get AI insights: {str(e)}")
    
    def _validate_query_safety(self, query: str) -> Dict[str, Any]:
        """
        Validate SQL query for safety (read-only operations only)
        
        Args:
            query: SQL query to validate
            
        Returns:
            Dictionary with validation results
        """
        # Clean and normalize query
        clean_query = query.strip().upper()
        
        # Remove comments
        clean_query = re.sub(r'--.*$', '', clean_query, flags=re.MULTILINE)
        clean_query = re.sub(r'/\*.*?\*/', '', clean_query, flags=re.DOTALL)
        
        # Check for dangerous keywords
        dangerous_keywords = [
            'INSERT', 'UPDATE', 'DELETE', 'DROP', 'ALTER', 'CREATE',
            'TRUNCATE', 'REPLACE', 'MERGE', 'EXEC', 'EXECUTE'
        ]
        
        for keyword in dangerous_keywords:
            if keyword in clean_query:
                return {
                    "is_safe": False,
                    "reason": f"Query contains dangerous keyword: {keyword}"
                }
        
        # Must start with SELECT
        if not clean_query.startswith('SELECT'):
            return {
                "is_safe": False,
                "reason": "Query must start with SELECT"
            }
        
        return {"is_safe": True, "reason": "Query passed safety validation"}
    
    def _generate_statistical_insights(self, data: List[Dict]) -> str:
        """
        Generate fallback statistical insights when AI is unavailable
        
        Args:
            data: Query result data
            
        Returns:
            Statistical insights text
        """
        if not data:
            return "**No data available for analysis.**"
        
        df = pd.DataFrame(data)
        insights = []
        
        insights.append("## **STATISTICAL ANALYSIS SUMMARY**\n")
        insights.append(f"📊 **Dataset Overview:**")
        insights.append(f"- Total records analyzed: {len(df)}")
        insights.append(f"- Number of fields: {len(df.columns)}")
        insights.append(f"- Data completeness: {((df.count().sum() / (len(df) * len(df.columns))) * 100):.1f}%\n")
        
        # Analyze numeric columns
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            insights.append("📈 **Numeric Field Analysis:**")
            for col in numeric_cols[:3]:  # Top 3 numeric columns
                mean_val = df[col].mean()
                median_val = df[col].median()
                std_val = df[col].std()
                insights.append(f"- **{col}**: Mean {mean_val:.2f}, Median {median_val:.2f}, Std Dev {std_val:.2f}")
            insights.append("")
        
        # Categorical analysis
        cat_cols = df.select_dtypes(include=['object']).columns
        if len(cat_cols) > 0:
            insights.append("🏷️ **Categorical Data:**")
            for col in cat_cols[:2]:
                unique_count = df[col].nunique()
                most_common = df[col].value_counts().head(1)
                if len(most_common) > 0:
                    insights.append(f"- **{col}**: {unique_count} unique values, most common: '{most_common.index[0]}'")
            insights.append("")
        
        # Data quality insights
        insights.append("🔍 **Data Quality Observations:**")
        
        # Check for missing data
        null_counts = df.isnull().sum()
        high_null_cols = null_counts[null_counts > len(df) * 0.1]
        if len(high_null_cols) > 0:
            insights.append(f"- Columns with significant missing data: {', '.join(high_null_cols.index)}")
        else:
            insights.append("- Data completeness: Good (minimal missing values)")
        
        # Dataset size assessment
        if len(df) > 1000:
            insights.append("- Dataset size: Large sample, results are statistically significant")
        elif len(df) > 100:
            insights.append("- Dataset size: Medium sample, conclusions should be interpreted carefully")
        else:
            insights.append("- Dataset size: Small sample, limited statistical power")
        
        insights.append("\n**Note:** This is automated statistical analysis. For deeper business insights, ensure AI analysis is available.")
        
        return "\n".join(insights)
    
    def get_field_picker_data(self) -> List[Dict]:
        """
        Get field picker data for UI
        
        Returns:
            List of field data for picker interface
        """
        return self._generate_field_picker_data()
    
    def get_query_suggestions(self) -> List[Dict[str, str]]:
        """
        Generate smart SQL query suggestions based on current schema
        
        Returns:
            List of suggested queries with descriptions
        """
        if not self.schema:
            return []
        
        suggestions = []
        
        # Basic exploration queries
        suggestions.append({
            "title": "📋 Data Overview",
            "query": f"SELECT * FROM {self.table_name} LIMIT 10",
            "description": "View first 10 rows of the dataset",
            "category": "exploration"
        })
        
        suggestions.append({
            "title": "📊 Record Count",
            "query": f"SELECT COUNT(*) as total_rows FROM {self.table_name}",
            "description": "Get total number of records",
            "category": "summary"
        })
        
        # Smart suggestions based on field types
        numeric_cols = [col for col, dtype in self.schema.items() if dtype in ['INTEGER', 'REAL', 'CURRENCY']]
        if numeric_cols:
            col = numeric_cols[0]
            suggestions.append({
                "title": f"📈 {col} Statistics",
                "query": f"SELECT MIN({col}) as min_val, MAX({col}) as max_val, AVG({col}) as avg_val, COUNT(*) as count FROM {self.table_name}",
                "description": f"Statistical summary of {col}",
                "category": "analysis"
            })
            
            suggestions.append({
                "title": f"🔝 Top 5 by {col}",
                "query": f"SELECT * FROM {self.table_name} ORDER BY {col} DESC LIMIT 5",
                "description": f"Highest values in {col}",
                "category": "ranking"
            })
        
        # Category analysis
        category_cols = [col for col, dtype in self.schema.items() if dtype == 'CATEGORY']
        if category_cols:
            col = category_cols[0]
            suggestions.append({
                "title": f"🏷️ {col} Distribution",
                "query": f"SELECT {col}, COUNT(*) as count FROM {self.table_name} GROUP BY {col} ORDER BY count DESC",
                "description": f"Distribution of {col} values",
                "category": "distribution"
            })
        
        # Date analysis if available
        date_cols = [col for col, dtype in self.schema.items() if dtype == 'DATE']
        if date_cols:
            col = date_cols[0]
            suggestions.append({
                "title": f"📅 Date Range - {col}",
                "query": f"SELECT MIN({col}) as earliest, MAX({col}) as latest, COUNT(*) as total FROM {self.table_name}",
                "description": f"Date range analysis for {col}",
                "category": "temporal"
            })
        
        return suggestions
    
    def save_query_template(self, name: str, query: str, description: str = "") -> Dict[str, Any]:
        """
        Save a query as a reusable template with schema compatibility
        
        Args:
            name: Template name
            query: SQL query
            description: Template description
            
        Returns:
            Save operation results
        """
        try:
            template_id = str(uuid.uuid4())[:8]
            
            template = {
                "id": template_id,
                "name": name,
                "query": query,
                "description": description,
                "schema_signature": self._get_schema_signature(),
                "created_at": datetime.now().isoformat(),
                "compatible_schemas": [self._get_schema_signature()],
                "field_count": len(self.schema),
                "field_types": dict(self.schema)
            }
            
            self.saved_queries[template_id] = template
            
            return {
                "status": "success",
                "template_id": template_id,
                "message": f"Template '{name}' saved successfully"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to save template: {str(e)}"
            }
    
    def _get_schema_signature(self) -> str:
        """
        Generate a schema signature for compatibility checking
        
        Returns:
            Schema signature string
        """
        if not self.schema:
            return ""
        
        # Create sorted signature of column names and types
        sorted_schema = sorted(self.schema.items())
        signature_parts = [f"{col}:{dtype}" for col, dtype in sorted_schema]
        return "|".join(signature_parts)
    
    def get_compatible_templates(self) -> List[Dict]:
        """
        Get query templates compatible with current dataset schema
        
        Returns:
            List of compatible templates
        """
        if not self.schema:
            return []
        
        current_signature = self._get_schema_signature()
        compatible = []
        
        for template in self.saved_queries.values():
            if current_signature in template.get("compatible_schemas", []):
                compatible.append(template)
        
        return compatible
    
    def get_query_history(self) -> List[Dict]:
        """
        Get query execution history
        
        Returns:
            List of query history records
        """
        return sorted(self.query_history, key=lambda x: x["timestamp"], reverse=True)
    
    def get_saved_templates(self) -> List[Dict]:
        """
        Get all saved query templates
        
        Returns:
            List of saved templates
        """
        return list(self.saved_queries.values())
