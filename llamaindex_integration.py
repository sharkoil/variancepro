"""
LlamaIndex Integration for VariancePro Financial Analysis
Advanced document processing and structured data extraction
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
import json
import tempfile
import os
from datetime import datetime
from pathlib import Path

try:
    from llama_index.core import Document, VectorStoreIndex, Settings
    from llama_index.core.extractors import (
        SummaryExtractor,
        QuestionsAnsweredExtractor, 
        TitleExtractor,
        KeywordExtractor
    )
    from llama_index.core.node_parser import SimpleNodeParser
    from llama_index.core.schema import BaseNode
    from llama_index.core.output_parsers import PydanticOutputParser
    from llama_index.core.query_engine import BaseQueryEngine
    from llama_index.llms.ollama import Ollama
    from pydantic import BaseModel, Field
    LLAMAINDEX_AVAILABLE = True
except ImportError:
    # Create dummy classes when LlamaIndex is not available
    LLAMAINDEX_AVAILABLE = False
    
    class BaseModel:
        pass
    
    def Field(**kwargs):
        return None
    
    print("LlamaIndex not installed. Run: pip install llama-index")

class FinancialMetric(BaseModel):
    """Structured financial metric extraction model"""
    metric_name: str = Field(description="Name of the financial metric (e.g., 'Revenue', 'EBITDA')")
    value: float = Field(description="Numerical value of the metric")
    period: str = Field(description="Time period (e.g., 'Q1 2024', 'FY 2023')")
    currency: Optional[str] = Field(description="Currency if specified (e.g., 'USD', 'EUR')")
    unit: Optional[str] = Field(description="Unit of measurement (e.g., 'millions', 'thousands')")
    growth_rate: Optional[float] = Field(description="Growth rate if mentioned (as percentage)")

class FinancialDocument(BaseModel):
    """Complete financial document structure"""
    document_type: str = Field(description="Type of document (e.g., 'Income Statement', 'Balance Sheet')")
    company_name: Optional[str] = Field(description="Company name if mentioned")
    reporting_period: str = Field(description="Reporting period")
    metrics: List[FinancialMetric] = Field(description="List of extracted financial metrics")
    key_insights: List[str] = Field(description="Key business insights from the document")
    data_quality_score: float = Field(description="Quality score of extracted data (0-1)")

if LLAMAINDEX_AVAILABLE:
    class LlamaIndexFinancialProcessor:
        """Advanced financial document processing with LlamaIndex"""
        
        def __init__(self, model_name: str = "gemma3:latest"):
            self.model_name = model_name
            self.llm = Ollama(model=model_name, base_url="http://localhost:11434")
            
            # Use new Settings API instead of deprecated ServiceContext
            Settings.llm = self.llm
            Settings.chunk_size = 512
            Settings.chunk_overlap = 50
            self.financial_index = None
            self.documents_indexed = []
            
        def check_availability(self) -> bool:
            """Check if LlamaIndex and Ollama are available"""
            try:
                # Test LLM connection
                response = self.llm.complete("Test")
                return True
            except Exception as e:
                print(f"LlamaIndex/Ollama not available: {e}")
                return False
    
    def extract_structured_financial_data(self, text_content: str) -> FinancialDocument:
        """Extract structured financial data from text using LlamaIndex"""
        
        if not self.check_availability():
            raise RuntimeError("LlamaIndex/Ollama not available")
        
        # Create document
        document = Document(text=text_content)
        
        # Set up structured extraction
        parser = PydanticOutputParser(output_cls=FinancialDocument)
        
        # Create extraction prompt
        extraction_prompt = f"""
        You are a financial data extraction expert. Analyze the following financial document text and extract structured information.

        Extract all financial metrics, company information, and insights according to the specified schema.
        Be precise with numbers and ensure all extracted data is accurate.

        Document Text:
        {text_content}

        Return the extracted data in the exact JSON format specified by the schema.
        """
        
        try:
            # Get structured response
            response = self.llm.complete(extraction_prompt)
            extracted_data = parser.parse(response.text)
            return extracted_data
        except Exception as e:
            print(f"Extraction error: {e}")
            # Return minimal structure if extraction fails
            return FinancialDocument(
                document_type="Unknown",
                reporting_period="Unknown", 
                metrics=[],
                key_insights=[f"Extraction failed: {str(e)}"],
                data_quality_score=0.0
            )
    
    def create_financial_dataframe(self, financial_doc: FinancialDocument) -> pd.DataFrame:
        """Convert extracted financial document to pandas DataFrame"""
        
        if not financial_doc.metrics:
            return pd.DataFrame()
        
        data = []
        for metric in financial_doc.metrics:
            row = {
                'Date': metric.period,
                'Metric': metric.metric_name,
                'Value': metric.value,
                'Currency': metric.currency or 'USD',
                'Unit': metric.unit or '',
                'Growth_Rate': metric.growth_rate,
                'Document_Type': financial_doc.document_type,
                'Company': financial_doc.company_name or 'Unknown'
            }
            data.append(row)
        
        df = pd.DataFrame(data)
        
        # Try to parse dates
        try:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        except:
            pass
            
        return df
    
    def build_financial_knowledge_base(self, documents: List[str]) -> VectorStoreIndex:
        """Build a searchable knowledge base from financial documents"""
        
        if not self.check_availability():
            raise RuntimeError("LlamaIndex not available")
        
        # Create Document objects
        docs = [Document(text=doc) for doc in documents]
        
        # Set up extractors for better indexing
        extractors = [
            TitleExtractor(nodes=5),
            QuestionsAnsweredExtractor(questions=3),
            SummaryExtractor(summaries=["prev", "self"]),
            KeywordExtractor(keywords=10)
        ]
        
        # Configure node parser with extractors
        node_parser = SimpleNodeParser.from_defaults(extractors=extractors)
        
        # Build index
        self.financial_index = VectorStoreIndex.from_documents(
            docs, 
            node_parser=node_parser
        )
        
        self.documents_indexed = documents
        return self.financial_index
    
    def query_financial_knowledge_base(self, query: str) -> str:
        """Query the financial knowledge base"""
        
        if not self.financial_index:
            return "No financial knowledge base available. Index documents first."
        
        try:
            query_engine = self.financial_index.as_query_engine(
                response_mode="tree_summarize"
            )
            
            response = query_engine.query(query)
            return str(response)
            
        except Exception as e:
            return f"Query error: {str(e)}"
    
    def analyze_financial_trends(self, df_list: List[pd.DataFrame], query: str) -> str:
        """Analyze trends across multiple financial datasets"""
        
        if not df_list:
            return "No data provided for analysis"
        
        # Combine all dataframes
        combined_analysis = []
        
        for i, df in enumerate(df_list):
            if df.empty:
                continue
                
            # Create summary of each dataset
            summary = f"""
Dataset {i+1}:
- Rows: {len(df)}
- Columns: {', '.join(df.columns)}
- Date Range: {self._get_date_range(df)}
- Key Metrics: {', '.join(df.select_dtypes(include=[np.number]).columns[:5])}

Sample Data:
{df.head(3).to_string()}
"""
            combined_analysis.append(summary)
        
        # Create comprehensive analysis prompt
        analysis_prompt = f"""
You are a financial analyst examining multiple related datasets. Analyze the following data and answer the specific question.

DATASETS:
{chr(10).join(combined_analysis)}

QUESTION: {query}

Provide a comprehensive analysis including:
1. Cross-dataset trends and patterns
2. Key performance indicators across time periods
3. Anomalies or notable changes
4. Strategic insights and recommendations
5. Data quality assessment

Focus on answering the specific question while providing broader context from all datasets.
"""
        
        try:
            response = self.llm.complete(analysis_prompt)
            return response.text
        except Exception as e:
            return f"Analysis error: {str(e)}"
    
    def _get_date_range(self, df: pd.DataFrame) -> str:
        """Helper to extract date range from dataframe"""
        date_cols = df.select_dtypes(include=['datetime64']).columns
        if len(date_cols) > 0:
            date_col = date_cols[0]
            return f"{df[date_col].min()} to {df[date_col].max()}"
        return "No dates detected"
    
    def generate_financial_insights_report(self, df: pd.DataFrame, context_docs: List[str] = None) -> str:
        """Generate comprehensive financial insights report"""
        
        # Build knowledge base if context documents provided
        if context_docs and len(context_docs) > 0:
            self.build_financial_knowledge_base(context_docs)
        
        # Analyze the dataframe
        data_summary = f"""
FINANCIAL DATA ANALYSIS:
- Dataset Size: {len(df)} rows, {len(df.columns)} columns
- Date Range: {self._get_date_range(df)}
- Numeric Columns: {', '.join(df.select_dtypes(include=[np.number]).columns)}
- Categorical Columns: {', '.join(df.select_dtypes(include=['object']).columns)}

STATISTICAL SUMMARY:
{df.describe().round(2).to_string() if len(df.select_dtypes(include=[np.number]).columns) > 0 else "No numeric data"}

SAMPLE DATA:
{df.head(5).to_string()}
"""
        
        # Generate insights using LLM
        insights_prompt = f"""
As a senior financial analyst, provide a comprehensive analysis of this financial dataset.

{data_summary}

Generate a detailed report including:

## Executive Summary
- Key financial highlights
- Overall performance assessment
- Critical areas requiring attention

## Trend Analysis
- Growth patterns and trajectories
- Seasonal variations
- Performance volatility

## Risk Assessment
- Potential financial risks identified
- Variance analysis and explanations
- Early warning indicators

## Strategic Recommendations
- Immediate action items
- Long-term strategic considerations
- Areas for deeper investigation

## Data Quality & Reliability
- Assessment of data completeness
- Confidence level in findings
- Recommendations for data improvement

Provide specific, actionable insights based on the financial data patterns observed.
"""
        
        try:
            response = self.llm.complete(insights_prompt)
            
            # If we have a knowledge base, add contextual insights
            if self.financial_index:
                context_query = "What additional context from historical documents is relevant to this analysis?"
                contextual_insights = self.query_financial_knowledge_base(context_query)
                
                full_report = f"""
{response.text}

## Historical Context & Background
{contextual_insights}

---
*Analysis powered by LlamaIndex with Phi4 • {datetime.now().strftime('%Y-%m-%d %H:%M')}*
"""
                return full_report
            
            return response.text
            
        except Exception as e:
            return f"Report generation error: {str(e)}"

else:
    # Create dummy class when LlamaIndex is not available
    class LlamaIndexFinancialProcessor:
        def __init__(self, model_name: str = "phi4:latest"):
            pass
        
        def check_availability(self) -> bool:
            return False

# Integration functions for VariancePro
def create_llamaindex_enhanced_analysis(df: pd.DataFrame, user_question: str, context_docs: List[str] = None) -> Tuple[str, str]:
    """Enhanced analysis using LlamaIndex structured extraction"""
    
    if not LLAMAINDEX_AVAILABLE:
        return ("LlamaIndex not installed. Install with: `pip install llama-index llama-index-llms-ollama`", 
               "❌ LlamaIndex Not Available")
    
    try:
        processor = LlamaIndexFinancialProcessor()
        
        if not processor.check_availability():
            return ("LlamaIndex integration not available. Ensure Ollama is running with phi4 model.", 
                   "❌ LlamaIndex Offline")
        
        # Generate comprehensive analysis
        if context_docs:
            # With context documents
            analysis = processor.generate_financial_insights_report(df, context_docs)
            
            # Answer specific question with context
            specific_answer = processor.query_financial_knowledge_base(
                f"Based on the financial data and documents, {user_question}"
            )
            
            combined_response = f"""
## 🎯 Specific Answer:
{specific_answer}

## 📊 Comprehensive Financial Analysis:
{analysis}
"""
            status = f"✅ LlamaIndex Enhanced Analysis | {len(df)} rows + {len(context_docs)} documents"
            
        else:
            # Data-only analysis
            analysis = processor.analyze_financial_trends([df], user_question)
            status = f"✅ LlamaIndex Analysis | {len(df)} rows processed"
            combined_response = analysis
        
        return combined_response, status
        
    except Exception as e:
        return f"LlamaIndex analysis error: {str(e)}", "❌ LlamaIndex Error"

def extract_financial_data_from_text(text_content: str) -> pd.DataFrame:
    """Extract structured financial data from text using LlamaIndex"""
    
    if not LLAMAINDEX_AVAILABLE:
        return pd.DataFrame()
    
    try:
        processor = LlamaIndexFinancialProcessor()
        
        if not processor.check_availability():
            return pd.DataFrame()
        
        # Extract structured data
        financial_doc = processor.extract_structured_financial_data(text_content)
        
        # Convert to DataFrame
        df = processor.create_financial_dataframe(financial_doc)
        
        return df
        
    except Exception as e:
        print(f"Text extraction error: {e}")
        return pd.DataFrame()

if __name__ == "__main__":
    # Example usage
    if LLAMAINDEX_AVAILABLE:
        try:
            processor = LlamaIndexFinancialProcessor()
            print("LlamaIndex Financial Processor Ready!")
            print(f"Available: {processor.check_availability()}")
        except Exception as e:
            print(f"LlamaIndex processor failed: {e}")
    else:
        print("LlamaIndex not installed. Run: pip install llama-index")
