# LlamaIndex Integration Guide for VariancePro

## 🚀 Transform Your Financial Analysis with LlamaIndex

LlamaIndex is a powerful framework for building LLM applications with advanced data indexing, retrieval, and **structured extraction** capabilities. Here's how it can revolutionize your VariancePro financial analysis app:

## 🎯 Key Benefits for VariancePro:

### 1. **Structured Data Extraction** 📊
- **Automatic Schema Validation**: Extract financial data according to predefined schemas
- **Pydantic Models**: Ensure data consistency and type safety
- **Multi-Format Support**: Process PDFs, text files, financial reports
- **Quality Scoring**: Automatic assessment of extraction reliability

### 2. **Advanced RAG (Retrieval Augmented Generation)** 🔍
- **Financial Knowledge Base**: Index historical reports and documents
- **Context-Aware Responses**: AI answers based on your specific financial history
- **Cross-Document Analysis**: Find patterns across multiple time periods
- **Semantic Search**: Natural language queries across all financial data

### 3. **Multi-Document Intelligence** 📄
- **Trend Analysis**: Compare performance across quarters/years
- **Comprehensive Reporting**: Generate insights from multiple data sources
- **Historical Context**: Provide background for current financial situations
- **Data Relationship Discovery**: Identify connections between different reports

## 🛠️ Technical Implementation:

### Core Components Created:

1. **FinancialMetric Model**: Structured extraction of individual metrics
2. **FinancialDocument Model**: Complete document structure with validation
3. **LlamaIndexFinancialProcessor**: Main processing engine
4. **Knowledge Base Builder**: Creates searchable document indexes

### Example Usage:

```python
# Extract structured data from financial text
processor = LlamaIndexFinancialProcessor()
financial_doc = processor.extract_structured_financial_data(text_content)

# Convert to DataFrame for analysis
df = processor.create_financial_dataframe(financial_doc)

# Build knowledge base from multiple documents
processor.build_financial_knowledge_base(document_list)

# Query with context
insights = processor.query_financial_knowledge_base("What drove Q3 revenue growth?")
```

## 📋 Setup Instructions:

### 1. Install LlamaIndex
```bash
# Install LlamaIndex with all dependencies
pip install llama-index

# Additional packages for enhanced functionality
pip install llama-index-llms-ollama
pip install llama-index-embeddings-ollama
```

### 2. Update Your requirements.txt
```
llama-index>=0.9.0
llama-index-llms-ollama>=0.1.0
pydantic>=2.0.0
```

### 3. Integrate with Your App
Add to your `app.py`:

```python
# Add import
try:
    from llamaindex_integration import (
        LlamaIndexFinancialProcessor, 
        create_llamaindex_enhanced_analysis,
        extract_financial_data_from_text
    )
    LLAMAINDEX_AVAILABLE = True
except ImportError:
    LLAMAINDEX_AVAILABLE = False

# Enhance your Phi4FinancialChat class
class Phi4FinancialChat:
    def __init__(self):
        # ...existing code...
        self.llamaindex_processor = None
        if LLAMAINDEX_AVAILABLE:
            try:
                self.llamaindex_processor = LlamaIndexFinancialProcessor()
            except Exception as e:
                print(f"LlamaIndex initialization failed: {e}")
    
    def enhanced_analysis_with_llamaindex(self, file_data, user_question: str, context_docs: List[str] = None):
        """Enhanced analysis using LlamaIndex structured extraction"""
        
        # Process data normally
        standard_response, status = self.analyze_data(file_data, user_question)
        
        # Add LlamaIndex enhancement if available
        if self.llamaindex_processor and self.llamaindex_processor.check_availability():
            try:
                df = pd.read_csv(file_data.name) if hasattr(file_data, 'name') else pd.read_csv(file_data)
                
                # Get enhanced analysis
                enhanced_response, enhanced_status = create_llamaindex_enhanced_analysis(
                    df, user_question, context_docs
                )
                
                # Combine responses
                combined_response = f"""
## 🤖 Phi4 Analysis:
{standard_response}

## 🧠 LlamaIndex Enhanced Analysis:
{enhanced_response}
"""
                return combined_response, f"{status} + {enhanced_status}"
                
            except Exception as e:
                return f"{standard_response}\n\n⚠️ LlamaIndex enhancement failed: {str(e)}", status
        
        return standard_response, status
```

## 🌟 Advanced Features:

### 1. **Structured Financial Data Extraction**

```python
# Define your financial schema
class QuarterlyReport(BaseModel):
    revenue: float = Field(description="Total revenue")
    expenses: float = Field(description="Total expenses") 
    net_income: float = Field(description="Net income")
    quarter: str = Field(description="Quarter (e.g., Q1 2024)")

# Extract with validation
processor = LlamaIndexFinancialProcessor()
extracted_data = processor.extract_structured_financial_data(report_text)
```

### 2. **Multi-Document Knowledge Base**

```python
# Build comprehensive financial knowledge base
documents = [
    "Q1 2024 financial report text...",
    "Q2 2024 financial report text...", 
    "Annual strategy document text..."
]

processor.build_financial_knowledge_base(documents)

# Query with full context
answer = processor.query_financial_knowledge_base(
    "How did our Q2 performance compare to Q1 and what factors contributed?"
)
```

### 3. **Advanced Trend Analysis**

```python
# Analyze multiple datasets together
dataframes = [q1_df, q2_df, q3_df, q4_df]

analysis = processor.analyze_financial_trends(
    dataframes, 
    "What are the key trends across all quarters?"
)
```

## 🎮 Real-World Use Cases:

### 1. **Quarterly Report Processing**
- Upload PDF quarterly reports
- Extract structured financial metrics automatically
- Build searchable knowledge base of all reports
- Query across multiple quarters for trend analysis

### 2. **Budget vs Actual Analysis**
- Extract budget data from planning documents
- Compare with actual performance data
- Generate variance explanations using historical context
- Identify patterns from previous budget cycles

### 3. **Investment Committee Preparation**
- Process multiple financial documents
- Generate comprehensive performance summaries
- Provide historical context for current decisions
- Create data-driven investment recommendations

### 4. **Regulatory Compliance**
- Extract required metrics from financial statements
- Validate data consistency across documents
- Generate compliance reports with proper documentation
- Maintain audit trail of data sources

## 🔧 Integration with Your Current App:

### Enhanced Gradio Interface:

```python
# Add document upload capability
with gr.Tabs():
    with gr.TabItem("Enhanced Analysis"):
        doc_upload = gr.File(
            label="Upload Financial Documents (PDF, TXT)",
            file_types=[".pdf", ".txt", ".docx"],
            file_count="multiple"
        )
        
        enhanced_analysis_btn = gr.Button("Generate Enhanced Analysis")
        enhanced_output = gr.Markdown()

# Connect LlamaIndex processing
enhanced_analysis_btn.click(
    process_documents_with_llamaindex,
    inputs=[file_input, doc_upload, message_input],
    outputs=[enhanced_output]
)
```

### Enhanced Visualization with Context:

```python
def create_contextualized_visualization(df, user_query, context_docs):
    """Create charts with LlamaIndex-enhanced insights"""
    
    # Generate standard chart
    chart_html, config_info = chat_system.create_time_series_visualization(df)
    
    # Add LlamaIndex contextual analysis
    if chat_system.llamaindex_processor:
        contextual_insights = chat_system.llamaindex_processor.query_financial_knowledge_base(
            f"Provide context for this visualization: {user_query}"
        )
        
        enhanced_config = f"""
{config_info}

## 📚 Historical Context:
{contextual_insights}
"""
        return chart_html, enhanced_config
    
    return chart_html, config_info
```

## 🚀 Next Steps:

1. **Install Dependencies**: `pip install llama-index llama-index-llms-ollama`
2. **Test Basic Integration**: Try the structured extraction example
3. **Add Document Upload**: Enhance your Gradio interface
4. **Build Knowledge Base**: Start indexing your financial documents
5. **Advanced Queries**: Implement cross-document analysis

## 💡 Pro Tips:

- **Start Small**: Begin with structured extraction before building knowledge bases
- **Schema Design**: Carefully design your Pydantic models for your specific financial data
- **Quality Scores**: Use the data quality scoring to filter unreliable extractions
- **Chunking Strategy**: For large documents, configure appropriate node parsing
- **Memory Management**: Consider persistent storage for large knowledge bases

With LlamaIndex integration, VariancePro becomes a **truly intelligent financial analysis platform** that can understand, extract, and analyze financial data at an enterprise level!

## 🔗 Useful Resources:

- [LlamaIndex Documentation](https://docs.llamaindex.ai/)
- [Structured Extraction Guide](https://docs.llamaindex.ai/en/stable/understanding/extraction/structured_llms/)
- [Pydantic Models](https://docs.pydantic.dev/)
- [Ollama Integration](https://docs.llamaindex.ai/en/stable/examples/llm/ollama/)
