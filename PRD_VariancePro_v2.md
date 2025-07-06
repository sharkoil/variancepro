# Product Requirements Document (PRD) - VariancePro v2.0

## **Executive Summary**
VariancePro v2.0 is a focused, robust Gradio-based financial data analysis tool that provides intelligent CSV analysis and natural language SQL querying through local Ollama/Gemma3 integration.

## **Product Vision**
Create a simple, powerful tool that allows financial professionals to upload CSV data and get immediate AI-powered insights without complex setup or cloud dependencies.

---

## **Phase 1: Core Foundation (IMPLEMENTED)**

### **1.1 Application Initialization**
**Requirements:**
- ✅ Generate unique session ID on startup
- ✅ Display session ID in footer
- ✅ Check Ollama connection status
- ✅ Verify Gemma3:latest model availability
- ✅ Display all status information in footer

**Implementation:**
- Session ID format: 8-character UUID
- Footer shows: Session ID | Ollama Status | Gradio Status | Model Name
- Real-time connection validation with friendly status messages

### **1.2 CSV File Upload & Validation**
**Requirements:**
- ✅ Robust CSV validation with friendly error messages
- ✅ File format checking (.csv extension)
- ✅ Encoding detection (UTF-8, Latin1)
- ✅ Empty file detection
- ✅ Structure validation (columns, rows)
- ✅ Clear error messaging for common issues

**Implementation:**
- Multi-encoding support for international data
- Detailed validation with specific error messages
- Prevention of common CSV format issues

### **1.3 Data Analysis & LLM Integration**
**Requirements:**
- ✅ Row and column counting
- ✅ Column type detection
- ✅ Sample data extraction (10 rows)
- ✅ Basic statistics for numeric columns
- ✅ LLM-generated data summary via Gemma3
- ✅ Fallback summary when LLM unavailable

**Implementation:**
- Comprehensive data profiling

### **1.4 Top N/Bottom N Analysis (IMPLEMENTED)**
**Requirements:**
- ✅ Top 5/Bottom 5 buttons in UI
- ✅ Top 10/Bottom 10 buttons in UI
- ✅ Natural language chat support ("top 5", "bottom 10", etc.)
- ✅ Number extraction from queries ("show me top 3")
- ✅ Analysis across all numeric columns
- ✅ Date dimension support (exclude date columns from ranking)
- ✅ Formatted results for chat display

**Implementation:**
- Button-based quick actions
- Natural language parsing with regex number extraction
- Integration with base_analyzer.py methods
- Smart column filtering (excludes dates from numeric analysis)
- Intelligent prompt engineering for data summaries
- Graceful degradation when Ollama is unavailable

---

## **Phase 2: Advanced NL2SQL with Gemma3 Function Calling (NEXT)**

### **2.1 Enhanced Data Context System**
**Requirements:**
- 🔄 Advanced column type detection (text, numeric, date, categorical)
- 🔄 Sample value analysis for better context
- 🔄 Relationship detection between columns
- 🔄 Schema generation with field metadata
- 🔄 Constraint detection (ranges, categories, formats)

**Implementation Strategy:**
- Enhance existing `analyze_csv_data()` with deeper analysis
- Create schema context for LLM function calls
- Build column relationship maps

### **2.2 Gemma3 Function Calling for NL2SQL**
**Requirements:**
- 🔄 Function calling integration with Gemma3
- 🔄 Structured query generation (not just SQL strings)
- 🔄 Field validation before query execution
- 🔄 Query optimization and safety checking
- 🔄 Natural language query parsing with intent detection

**Target Queries:**
- "Show me sales by region"
- "Find customers with revenue > $10,000"
- "What are the top 5 products by sales in Q1?"
- "Filter data where date is after January 2024"
- "Compare budget vs actual by department"

**Function Calling Architecture:**
```python
def generate_query(
    intent: str,          # "filter", "aggregate", "sort", "compare"
    columns: List[str],   # Target columns
    conditions: List[Dict], # WHERE clauses with operators
    aggregations: List[Dict], # SUM, COUNT, AVG, etc.
    order_by: List[Dict], # Sorting specifications
    limit: Optional[int]  # Row limits
) -> QueryResult
```

### **2.3 Progressive Implementation Plan**

**Step 1: Function Schema Setup (Small Change)**
- Create function definitions for Gemma3
- Basic query intent classification
- Simple SELECT queries

**Step 2: WHERE Clause Intelligence (Small Change)**
- Smart operator detection (>, <, =, LIKE, BETWEEN)
- Date range parsing ("last month", "Q1 2024")
- Numeric comparison handling

**Step 3: Aggregation & Grouping (Small Change)**
- GROUP BY detection
- SUM, COUNT, AVG operations
- HAVING clause support

**Step 4: Advanced Features (Small Change)**
- Multiple table joins (if multiple CSVs)
- Complex filtering combinations
- Query optimization

---

## **Phase 3: Advanced Analytics (PLANNED)**

### **3.1 Financial Analysis Functions**
- Variance analysis (actual vs budget)
- Trend analysis and forecasting
- Contribution analysis (Pareto)
- Financial ratios and KPIs

### **3.2 Interactive Visualizations**
- Dynamic charts based on queries
- Financial dashboards
- Export capabilities

---

## **Technical Architecture**

### **Core Components**
1. **VarianceProApp**: Main application class
2. **CSV Validator**: Robust file validation
3. **Data Analyzer**: Statistical analysis engine
4. **LLM Interface**: Ollama/Gemma3 integration
5. **Chat Handler**: Conversation management

### **Technology Stack**
- **Frontend**: Gradio (Python-based UI)
- **Backend**: Python with Pandas for data processing
- **AI/LLM**: Ollama with Gemma3:latest model
- **Data**: CSV file processing with pandas

### **Dependencies**
- gradio
- pandas
- requests
- uuid (built-in)
- datetime (built-in)

---

## **Current Implementation Status**

### **✅ COMPLETED (Phase 1)**
- Clean, focused application architecture
- Session management with unique IDs
- Comprehensive CSV validation
- Ollama connection management
- Intelligent data analysis and LLM summaries
- Professional Gradio interface
- Real-time status monitoring

### **🔄 IN TESTING**
- File upload and validation flow
- LLM integration and response handling
- Error handling and user feedback

### **📋 NEXT STEPS**
Ready for your approval and feedback on Phase 1 before proceeding to Phase 2 (NL2SQL implementation).

---

## **Success Metrics**
1. **Reliability**: 99% successful CSV upload and validation
2. **User Experience**: <5 seconds from upload to AI summary
3. **Error Handling**: Clear, actionable error messages
4. **Performance**: Handle files up to 100MB efficiently

---

## **Current Demo**
The Phase 1 implementation is running at `http://localhost:7873` with:
- Session ID: `91a558ec`
- Ollama Status: ✅ Connected (gemma3:latest)
- Full CSV validation and AI-powered analysis

**Ready for your review and approval to proceed to Phase 2!**
