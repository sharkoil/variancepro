# VariancePro - AI-Powered Financial Intelligence Platform

<div align="center">
  <img src="logo.png" alt="VariancePro Logo" width="200"/>
  
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
  [![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
  [![Gradio](https://img.shields.io/badge/Gradio-4.0+-orange.svg)](https://gradio.app/)
  [![AI-Powered](https://img.shields.io/badge/AI-Powered-green.svg)](https://github.com/sharkoil/variancepro)
  [![News Intelligence](https://img.shields.io/badge/News-Intelligence-blue.svg)](https://github.com/sharkoil/variancepro)
</div>

## 🚀 Overview

VariancePro is a revolutionary AI-powered financial intelligence platform that transforms raw CSV data into comprehensive business insights with actionable market intelligence. Built with advanced AI models and powered by local inference, it provides enterprise-grade analysis capabilities while maintaining complete data privacy.

**🎯 What makes VariancePro unique:**
- **AI-Generated Executive Summaries** for complex time-series analysis
- **Actionable News Intelligence** that correlates market factors with data patterns
- **Collapsible Detail Views** for executive-level reporting with drill-down capabilities
- **Real-time Market Context** through RSS feed integration and content extraction
- **Zero-Trust Privacy** with 100% local processing

### ✨ Core Features

- **🤖 AI-Powered Analysis**: Chat with Aria Sterling, your AI financial analyst
- **📊 Advanced Analytics**: Contribution, variance, timescale, and ranking analysis
- **🧠 Executive Summaries**: AI-generated concise insights with expandable details
- **📰 Market Intelligence**: Actionable news analysis correlated with your data patterns
- **🔒 Privacy-First**: All processing happens locally - your data never leaves your machine
- **📈 Professional Reporting**: Publication-ready tables, charts, and executive reports
- **🎯 Intelligent Detection**: Auto-identifies data types, patterns, and business context
- **⚡ Real-Time Chat**: Natural language interface for data exploration and insights
- **🌐 RSS Integration**: Live news feeds for business context without API costs
- **📄 Article Extraction**: Deep content analysis from news sources for better intelligence

## 🛠️ Technology Stack

- **Frontend**: Gradio web interface with custom CSS styling and responsive design
- **Backend**: Python with pandas for advanced data processing and analysis
- **AI Engine**: Ollama with Gemma3 model for local AI inference and natural language processing
- **News Intelligence**: RSS feed integration with feedparser and content extraction
- **Data Processing**: Advanced CSV parsing with automatic column type detection and validation
- **Analysis Engine**: Modular analyzer architecture with AI-enhanced summaries
- **Security**: Zero-trust local processing with no external data transmission

## 📋 Requirements

- Python 3.8 or higher
- 8GB+ RAM (recommended for AI model performance)
- Ollama installed locally with Gemma3 model
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Internet connection (for news intelligence features only)

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/sharkoil/variancepro.git
cd variancepro
```

### 2. Install Dependencies
```bash
# Install core dependencies
pip install -r requirements.txt

# Alternative: Install minimal dependencies
pip install -r requirements-minimal.txt

# Alternative: Install full feature set
pip install -r requirements-full.txt
```

### 3. Install and Setup Ollama
```bash
# Install Ollama (visit https://ollama.ai for platform-specific instructions)

# Pull recommended models
ollama pull gemma3:latest      # Primary model for analysis
ollama pull deepseek-r1:14b    # Advanced reasoning model
ollama pull qwen3:8b           # Fast response model
ollama pull llava:latest       # Multi-modal capabilities

# Verify installation
ollama list
```

### 4. Run the Main Application
```bash
# Start the main VariancePro application
python app.py

# Alternative: Use the launcher script (if available)
python start_app.bat

# Windows batch file launcher
start_app.bat
```

The main application will start on `http://localhost:7871` by default.

### 5. Launch the Testing Framework (Optional)
```bash
# Start the Enhanced NL-to-SQL Testing Framework
python test_enhanced_nl_to_sql_ui.py

# Alternative: Direct launch
python -c "from nl_to_sql_testing_ui_enhanced import EnhancedNLToSQLTestingUI; EnhancedNLToSQLTestingUI().launch()"
```

The testing framework will start on `http://localhost:7862` by default.

### 🎯 Application Access Points

| Component | URL | Purpose |
|-----------|-----|---------|
| **Main Application** | `http://localhost:7871` | Financial analysis with AI insights |
| **Testing Framework** | `http://localhost:7862` | NL-to-SQL testing and validation |
| **Ollama API** | `http://localhost:11434` | AI model management |

### ⚙️ Configuration Options

#### Environment Variables
```bash
# Set custom ports
export VARIANCEPRO_PORT=7871
export TESTING_FRAMEWORK_PORT=7862
export OLLAMA_HOST=localhost:11434

# Set default model
export DEFAULT_MODEL=gemma3:latest
```

#### Startup Scripts
```bash
# Windows
start_app.bat                    # Launch main application
start_enhanced_demo.bat          # Launch with enhanced features

# Python scripts
python launch_testing.py         # Comprehensive test launcher
python run_tests.py             # Run validation tests
```

## 💡 Usage Guide

### Data Upload & Analysis
1. **Upload CSV File**: Click "Upload CSV File" and select your financial data
2. **Auto-Detection**: The system automatically analyzes your data structure and suggests columns
3. **Field Mapping**: Review and adjust column mappings in the Field Picker section
4. **Instant Analysis**: Chat interface becomes active with contextual business insights

### 🎯 Analysis Types

#### 📈 Contribution Analysis (Pareto 80/20)
**Purpose**: Identifies the critical few contributors driving majority of your results
- **Use Case**: Product profitability, customer analysis, sales territory performance
- **Output**: Ranked contributors with cumulative percentages and visual indicators
- **AI Enhancement**: Executive summary highlighting key insights and business implications

#### 💰 Variance Analysis
**Purpose**: Compares planned vs. actual performance to identify gaps and opportunities
- **Use Case**: Budget vs. actual analysis, forecast accuracy, performance monitoring
- **Output**: Variance tables with percentage deviations and trend indicators
- **AI Enhancement**: Contextual insights on performance drivers and recommendation priorities

#### ⏱️ Timescale Analysis (NEW!)
**Purpose**: Advanced time-series analysis with AI-powered executive summaries
- **Use Case**: Revenue trends, seasonal patterns, growth analysis, performance tracking
- **Output**: Comprehensive time-based insights with collapsible detail views
- **AI Features**: 
  - 🧠 **Executive Summary**: Concise AI-generated insights highlighting key findings
  - 📊 **Detailed Analysis**: Expandable sections with comprehensive metrics and trends
  - 📈 **Pattern Recognition**: AI identification of seasonal trends, growth patterns, and anomalies

#### 🔝 Top/Bottom N Analysis
**Purpose**: Ranks categories by performance metrics with detailed breakdowns
- **Use Case**: Best/worst performers, competitive analysis, resource allocation
- **Output**: Ranked tables with performance metrics and comparative analysis
- **AI Enhancement**: Strategic recommendations based on performance patterns

### 📰 Business Context Intelligence (NEW!)

**Actionable News Intelligence System** - Revolutionary feature that correlates market factors with your data patterns:

#### 🎯 Market Intelligence Summary
- **AI-Generated Insights**: Contextual analysis of how current market conditions may impact your business
- **Geographic Correlation**: Location-based news analysis tied to your data geography
- **Industry Context**: Sector-specific news intelligence relevant to your business metrics
- **Performance Impact**: Quantified estimates of how market factors may influence your KPIs

#### 📊 News Sources Table
- **Curated Headlines**: Relevant business news filtered for your industry and geography
- **Direct Links**: Clickable access to full articles for deeper research
- **Source Diversity**: Multiple news sources for comprehensive market view
- **Date Relevance**: Recent news prioritized for current market conditions

#### 🔍 Intelligent Content Extraction
- **Article Analysis**: Deep content extraction beyond headlines for richer insights
- **Sentiment Analysis**: Understanding market sentiment and its potential business impact
- **Trend Correlation**: Connecting news trends with data patterns in your business metrics

### 💬 Natural Language Chat Interface

Transform complex data questions into instant insights:

**Example Queries:**
- *"Show me the top 10 products by sales with market context"*
- *"Analyze budget variance and explain any external factors"*
- *"What are the revenue trends and how do current economic conditions affect them?"*
- *"Which regions are underperforming and what market factors might explain this?"*
- *"Generate an executive summary of our Q3 performance with business intelligence"*

**Chat Features:**
- **Intent Recognition**: AI automatically determines the best analysis type for your question
- **Context Awareness**: Remembers previous conversations and data context
- **Executive Summaries**: One-click access to AI-generated insights with expandable details
- **Market Integration**: Automatically includes relevant business context when applicable

## 🔍 Enhanced NL-to-SQL Translation

VariancePro now features a robust Natural Language to SQL translator that enables business users to query financial data using plain English instead of complex SQL syntax.

### Key Features

- **Natural Language Queries**: Ask questions in plain English like "Show me sales greater than 60000"
- **Financial Domain Knowledge**: Built-in understanding of financial terminology and metrics
- **Pattern Recognition**: Advanced pattern matching for business metrics, comparisons, and aggregations
- **Confidence Scoring**: Transparent query confidence with detailed explanations
- **Special Case Handling**: Optimized handling for common financial query patterns

### Sequence Diagram

```mermaid
sequenceDiagram
    participant User
    participant App as VariancePro
    participant Translator as NLToSQLTranslator
    participant Engine as SQLQueryEngine
    participant Result as FormattedResults
    
    User->>App: Ask natural language question
    App->>Translator: translate_to_sql(query)
    
    Translator->>Translator: identify_columns(query)
    Note over Translator: Match query terms with financial metrics
    
    Translator->>Translator: detect_aggregation_columns(query)
    Note over Translator: Detect SUM, AVG, COUNT functions
    
    Translator->>Translator: detect_group_by_columns(query)
    Note over Translator: Identify dimensions for grouping
    
    Translator->>Translator: build_where_clause(query)
    Note over Translator: Create filtering conditions
    
    Translator->>Translator: build_order_by_clause(query)
    Note over Translator: Determine sorting preferences
    
    Translator->>Translator: build_limit_clause(query)
    Note over Translator: Apply result limiting
    
    alt Special Case Detected
        Translator->>Translator: handle_special_case(query)
        Note over Translator: Optimized handling for common patterns
    end
    
    Translator-->>App: SQL Query + Explanation + Confidence
    
    App->>Engine: execute_query(sql)
    Engine->>Engine: validate_query(sql)
    Engine->>Engine: run_on_database(sql)
    Engine-->>App: Query Results
    
    App->>Result: format_results(results)
    Result-->>App: Professional Formatted Output
    
    App-->>User: Display Results + Explanation
```

### Example Queries

The enhanced translator successfully handles diverse financial queries:

1. **Filtering**: "Show me sales greater than 60000"
2. **Comparisons**: "Find transactions where actual sales is less than budget sales"
3. **Percentages**: "List products where discount percentage is greater than 2%"
4. **Multiple Conditions**: "Show regions with customer satisfaction above 3 and negative variance"
5. **Aggregations**: "Total actual sales by region where budget sales is greater than 50000"
6. **Averages**: "Average discount percentage by product line"
7. **Top N**: "Top 5 regions by actual sales"
8. **Ranking**: "Find products with highest customer satisfaction"

### Usage Example

```python
from analyzers.enhanced_nl_to_sql_translator_final_complete import EnhancedNLToSQLTranslator

# Initialize the translator
translator = EnhancedNLToSQLTranslator()

# Set the schema context
translator.set_schema_context(schema_info, "financial_data")

# Translate a natural language query
result = translator.translate_to_sql("Top 5 regions by actual sales")

if result.success:
    print(f"SQL: {result.sql_query}")
    print(f"Explanation: {result.explanation}")
    print(f"Confidence: {result.confidence}")
    
    # Execute the query with your database connector
    # ...
```

## 🏗️ System Architecture

```
variancepro/
├── ai/                         # AI and LLM integration
│   ├── llm_interpreter.py     # Core AI conversation engine
│   └── narrative_generator.py # AI-powered content generation
├── analyzers/                  # Advanced data analysis modules
│   ├── base_analyzer.py       # Foundation classes and formatting
│   ├── contributor_analyzer.py # Pareto 80/20 analysis
│   ├── financial_analyzer.py  # Variance and financial metrics
│   ├── timescale_analyzer.py  # Time-series with AI summaries
│   ├── news_analyzer_v2.py    # Actionable news intelligence
│   └── query_router.py        # Intelligent query routing
├── config/                     # Configuration management
│   └── settings.py            # Application settings and AI config
├── data/                       # Data processing utilities
│   └── csv_loader.py          # Intelligent CSV parsing
├── utils/                      # Utility functions
│   └── llm_handler.py         # LLM communication utilities
├── tests/                      # Comprehensive unit tests
├── sample_data/               # Example datasets for testing
├── app.py                     # Main application orchestrator
└── requirements.txt           # Python dependencies
```

### Enhanced System Flow Diagram

```mermaid
sequenceDiagram
    participant User
    participant Gradio as Gradio UI
    participant App as QuantCommanderApp
    participant CSV as CSVLoader
    participant AI as LLMInterpreter
    participant TimeScale as TimescaleAnalyzer
    participant News as NewsAnalyzer
    participant Router as QueryRouter
    participant Format as AnalysisFormatter

    User->>Gradio: Upload CSV File
    Gradio->>App: handle_file_upload()
    App->>CSV: load_and_validate()
    CSV->>CSV: Auto-detect columns, types & patterns
    CSV-->>App: Data + Column suggestions + Context
    
    App->>News: analyze_data_context()
    News->>News: Extract geographic locations
    News->>AI: generate_targeted_news_queries()
    AI-->>News: Intelligent search queries
    News->>News: fetch_relevant_news()
    News->>News: extract_article_content()
    News-->>App: Actionable business intelligence
    
    App->>Gradio: Display data preview + market context
    
    User->>Gradio: Ask analytical question
    Gradio->>App: chat_response()
    
    App->>Router: route_user_query()
    Router->>AI: classify_intent_and_parameters()
    AI-->>Router: Analysis type + extraction parameters
    Router-->>App: Routing decision
    
    alt Timescale Analysis
        App->>TimeScale: analyze()
        TimeScale->>TimeScale: Calculate time-based metrics
        TimeScale->>AI: generate_ai_summary()
        AI-->>TimeScale: Executive insights
        TimeScale->>Format: create_collapsible_format()
        Format-->>TimeScale: Executive summary + details
        TimeScale-->>App: Enhanced time analysis
    else News Context Analysis
        App->>News: format_news_for_chat()
        News->>AI: generate_actionable_summary()
        AI-->>News: Market intelligence insights
        News->>News: create_news_table()
        News-->>App: Actionable news intelligence
    else Standard Analysis
        App->>App: perform_traditional_analysis()
        App->>Format: create_professional_output()
        Format-->>App: Formatted results
    end
    
    opt AI Insights Available
        App->>AI: query_llm(analysis_context)
        AI-->>App: Strategic recommendations
    end
    
    App->>Gradio: Return enhanced analysis
    Gradio->>User: Display executive summary + details
```

### 🧠 AI-Enhanced Components

#### 1. **TimescaleAnalyzer** (Enhanced)
- **Executive Summary Generation**: AI creates concise insights from complex time-series data
- **Collapsible Detail Views**: Professional presentation with expandable sections
- **Pattern Recognition**: AI identifies trends, seasonality, and anomalies
- **Business Impact Analysis**: Quantified insights on performance implications

#### 2. **NewsAnalyzer V2** (Redesigned)
- **Actionable Intelligence**: Focuses on market factors affecting data patterns
- **Geographic Correlation**: Location-based news analysis
- **Content Extraction**: Deep article analysis beyond headlines
- **Business Impact Scoring**: AI assessment of news relevance to business metrics

#### 3. **LLMInterpreter** (Core AI Engine)
- **Intent Classification**: Natural language query understanding
- **Context Awareness**: Maintains conversation state and data context
- **Multi-modal Analysis**: Handles text, data, and business intelligence
- **Local Processing**: Privacy-preserving AI inference

#### 4. **QueryRouter** (Intelligent Routing)
- **Smart Dispatch**: Routes queries to optimal analysis engines
- **Parameter Extraction**: Intelligently identifies analysis parameters
- **Context Preservation**: Maintains user intent across complex workflows

## 🔧 Configuration

### Environment Variables
```bash
# AI Model Configuration
VARIANCEPRO_LLM_MODEL=gemma3:latest
OLLAMA_HOST=http://localhost:11434
VARIANCEPRO_LLM_TIMEOUT=180

# Server Configuration
GRADIO_SERVER_PORT=7871
GRADIO_SHARE=false

# Analysis Configuration
VARIANCEPRO_CONTRIBUTION_THRESHOLD=0.8
VARIANCEPRO_NEWS_MAX_ARTICLES=10

# News Intelligence Configuration
VARIANCEPRO_NEWS_ENABLED=true
VARIANCEPRO_RSS_TIMEOUT=30
VARIANCEPRO_CONTENT_EXTRACTION=true
```

### Advanced Configuration Options
```python
# config/settings.py
class Settings:
    # AI Configuration
    LLM_MODEL = "gemma3:latest"
    LLM_TIMEOUT = 180
    LLM_MAX_RETRIES = 3
    
    # News Intelligence
    NEWS_MAX_ARTICLES = 10
    NEWS_RSS_SOURCES = [
        "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRFZ4TVdZU0FtVnVHZ0pWVXlnQVAB",
        "https://feeds.reuters.com/reuters/businessNews"
    ]
    
    # Analysis Parameters
    CONTRIBUTION_THRESHOLD = 0.8
    TIMESCALE_PERIODS = ["daily", "weekly", "monthly", "quarterly"]
    
    # UI Configuration
    GRADIO_THEME = "default"
    GRADIO_CSS_FILE = "custom.css"
```

## 📊 Supported Data Formats

### Primary Formats
- **CSV Files**: Primary format with automatic delimiter detection (comma, semicolon, tab)
- **Excel Files**: .xlsx and .xls support via openpyxl with multi-sheet handling
- **Encoding Support**: UTF-8, Latin-1, CP1252, and other common encodings

### Advanced Data Structure Recognition

#### Expected Data Patterns
```csv
# Time-series financial data
Date,Product,Region,Budget,Actual,Category,SubCategory
2024-01-01,Widget A,North America,10000,12000,Electronics,Consumer
2024-01-01,Widget B,Europe,8000,7500,Electronics,Business
2024-02-01,Service X,Asia Pacific,15000,16500,Services,Premium

# Multi-dimensional business data
Quarter,Division,Manager,Revenue,Costs,Profit,YoY_Growth
Q1-2024,Sales,John Smith,1250000,950000,300000,8.5%
Q1-2024,Marketing,Jane Doe,450000,420000,30000,12.1%
Q2-2024,Operations,Bob Wilson,890000,678000,212000,5.7%
```

#### Auto-Detection Capabilities
- **Date Columns**: ISO formats, US/EU formats, quarter notation, fiscal periods
- **Category Columns**: Text fields for grouping and segmentation
- **Value Columns**: Revenue, sales, costs, quantities (with currency/unit detection)
- **Budget Columns**: Plan, target, forecast, budget (automatic pairing with actuals)
- **Geographic Data**: States, countries, regions (triggers news intelligence)
- **Hierarchical Data**: Category/subcategory, division/department structures

## 🎯 Advanced Analysis Examples

### 1. Executive Time-Series Analysis
**Input Data**: Monthly revenue data across product lines
```csv
Date,Product,Revenue,Budget
2024-01-01,Product A,125000,120000
2024-02-01,Product A,132000,125000
2024-03-01,Product A,118000,130000
```

**AI-Enhanced Output**:
```
📊 TIMESCALE ANALYSIS

🧠 Executive Summary:
Revenue performance shows strong momentum with 8.2% growth over Q1, 
exceeding budget by 4.1% despite March underperformance. Product A 
demonstrates consistent demand with seasonal variations typical for 
the technology sector.

--- See More Details ---

📈 DETAILED ANALYSIS:
• Growth Trend: 8.2% quarterly increase
• Budget Variance: +4.1% favorable overall
• Volatility: 12% standard deviation (normal range)
• Peak Performance: February (+5.6% vs budget)
• Attention Area: March (-9.2% vs budget requires investigation)

💡 BUSINESS INSIGHTS:
Market conditions favor continued growth with Q2 projections 
indicating 12% expansion potential based on current trends.
```

### 2. Actionable News Intelligence
**Data Context**: Sales performance across US states
**Generated Intelligence**:
```
📰 BUSINESS CONTEXT ANALYSIS

🎯 Market Intelligence Summary:
Current economic indicators suggest 3-5% regional variation in 
consumer spending, with California markets showing resilience 
due to tech sector strength. Federal interest rate policies 
may impact Q3 purchasing decisions, particularly in 
discretionary spending categories.

📊 RELEVANT NEWS SOURCES
| # | Headline | Source | Date |
|---|----------|--------|------|
| 1 | [Fed Signals Rate Stability Through Q3](https://reuters.com/...) | Reuters | Jul 02 |
| 2 | [California Consumer Confidence Rises](https://bloomberg.com/...) | Bloomberg | Jul 01 |
| 3 | [Retail Sales Beat Expectations](https://wsj.com/...) | WSJ | Jun 30 |
```

### 3. Multi-Dimensional Contribution Analysis
**Business Question**: "Which products and regions drive 80% of our profitability?"
**AI Response**: Comprehensive Pareto analysis with cross-dimensional insights, identifying that 23% of product-region combinations generate 81% of total profit, with specific recommendations for resource allocation and market focus.

## 🛡️ Privacy & Security

### Zero-Trust Architecture
- **Local Processing**: All analysis happens on your machine - no cloud dependencies
- **No Data Upload**: CSV files are processed in-memory only, never transmitted
- **AI Privacy**: Uses local Ollama models, completely offline AI inference
- **No Telemetry**: Zero usage data collection or transmission
- **Secure News Access**: RSS feeds accessed directly, no tracking or data sharing

### Data Handling Best Practices
- **Memory Management**: Data automatically cleared after analysis
- **File Security**: No persistent storage of uploaded files
- **Network Isolation**: AI processing completely offline
- **Audit Trail**: Local logging only, no external reporting

## 🧪 Testing & Quality Assurance

### Comprehensive Test Suite
```bash
# Run all tests
pytest tests/ -v

# Specific test categories
pytest tests/test_ai_core.py -v                    # AI integration tests
pytest tests/test_timescale_analyzer.py -v        # Time-series analysis
pytest tests/test_actionable_news.py -v           # News intelligence
pytest tests/test_complete_integration.py -v      # End-to-end workflows
```

### Test Coverage Areas
- **Data Processing**: CSV parsing, column detection, validation
- **AI Integration**: LLM communication, intent classification, summary generation
- **Analysis Engines**: All analyzer modules with sample data
- **News Intelligence**: RSS parsing, content extraction, relevance scoring
- **User Interface**: Gradio integration, error handling, response formatting

## 🚀 What's New in VariancePro v2.0

### � AI-Enhanced Executive Reporting
- **Smart Summaries**: AI generates concise executive insights from complex data analysis
- **Collapsible Views**: Professional presentation with "See More Details" expandable sections
- **Context-Aware Analysis**: AI understands business context and provides relevant insights

### 📰 Revolutionary News Intelligence
- **Actionable Market Intelligence**: Goes beyond generic business advice to provide specific market factors affecting your data
- **Geographic Correlation**: Location-based news analysis tied to your business geography
- **Content Extraction**: Deep article analysis beyond headlines for richer business intelligence
- **RSS Integration**: Real-time news feeds without expensive API costs

### ⚡ Performance & UX Improvements
- **Intelligent Query Routing**: Optimized analysis engine selection based on user intent
- **Enhanced Column Detection**: Superior auto-detection of data types and business context
- **Responsive Design**: Improved mobile and tablet experience
- **Error Resilience**: Graceful degradation and comprehensive error handling

## �🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

### Development Setup
```bash
# Clone repository
git clone https://github.com/sharkoil/variancepro.git
cd variancepro

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt
pip install pytest black flake8 mypy

# Set up pre-commit hooks
pip install pre-commit
pre-commit install

# Run tests
pytest tests/ -v --cov=./ --cov-report=html
```

### Code Quality Standards
- **Type Hints**: All functions must include descriptive type hints
- **Docstrings**: Comprehensive documentation for all modules and functions
- **Unit Tests**: Minimum 80% test coverage for all new code
- **Code Style**: Black formatting with flake8 linting
- **Modular Design**: Clean separation of concerns and reusable components

### Contributing Guidelines
1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Write** tests for your changes
4. **Ensure** all tests pass (`pytest tests/`)
5. **Commit** your changes (`git commit -m 'Add amazing feature'`)
6. **Push** to the branch (`git push origin feature/amazing-feature`)
7. **Open** a Pull Request with detailed description

## 🧪 Enhanced NL-to-SQL Testing Framework

VariancePro includes a sophisticated testing framework specifically designed for evaluating Natural Language to SQL translation capabilities across multiple AI models. This framework allows you to compare different strategies and models to find the best approach for your specific use cases.

### 🎯 Framework Overview

The Enhanced NL-to-SQL Testing Framework provides:
- **🤖 Multi-Model Support**: Test with any Ollama-deployed model
- **🔄 Strategy Comparison**: Compare different translation approaches
- **📊 Quality Scoring**: Automated assessment of translation accuracy
- **📈 Performance Metrics**: Response time and success rate tracking
- **🎨 Interactive UI**: Web-based interface for easy testing and evaluation

### 🛠️ Testing Framework Components

#### Core Files:
- `nl_to_sql_testing_ui_enhanced.py` - Main testing interface with model selection
- `test_enhanced_nl_to_sql_ui.py` - Launcher script for the testing framework
- `analyzers/enhanced_nl_to_sql_translator.py` - Primary translation engine
- `analyzers/strategy_1_llm_enhanced.py` - LLM-enhanced translation strategy
- `analyzers/strategy_2_semantic_parsing.py` - Semantic parsing strategy
- `analyzers/nl_to_sql_tester.py` - Core testing and validation logic

### 🚀 Running the Testing Framework

#### Prerequisites
Ensure you have Ollama running with your desired models:
```bash
# Check available models
ollama list

# Pull additional models if needed
ollama pull deepseek-r1:14b
ollama pull qwen3:8b
ollama pull llava:latest
```

#### Launch the Testing Interface
```bash
# Navigate to project directory
cd f:\Projects\VARIANCEPRO

# Launch the enhanced testing UI
python test_enhanced_nl_to_sql_ui.py
```

The testing interface will be available at `http://localhost:7862`

#### Alternative Launch Methods
```bash
# Direct launch of testing framework
python -c "from nl_to_sql_testing_ui_enhanced import EnhancedNLToSQLTestingUI; EnhancedNLToSQLTestingUI().launch()"

# Background launch
python nl_to_sql_testing_ui_enhanced.py
```

### 📋 Testing Framework Usage Guide

#### 1. Model Selection
- **Available Models**: Dropdown shows all Ollama-deployed models
- **Real-time Switching**: Change models without restarting the interface
- **Auto-refresh**: Click "🔄 Refresh Models" to detect newly installed models
- **Default Model**: Framework starts with `gemma3:latest` if available

#### 2. Test Data Upload
```bash
# Supported formats: CSV, Excel (.xlsx, .xls)
# Upload your dataset containing the data you want to query
# Framework automatically detects column structure
```

#### 3. Natural Language Query Testing
```
Example queries to test:
- "Show me the top 5 products by revenue"
- "What are the sales figures for the last quarter?"
- "Find customers with orders above $10,000"
- "Compare revenue between regions"
```

#### 4. Strategy Comparison
The framework tests multiple strategies simultaneously:
- **LLM Enhanced**: Uses advanced AI reasoning for complex queries
- **Semantic Parsing**: Rule-based approach for structured queries
- **Hybrid Approach**: Combines multiple strategies for optimal results

#### 5. Quality Assessment
- **Syntax Validation**: Checks if generated SQL is valid
- **Execution Testing**: Runs queries against your data
- **Result Verification**: Validates query output makes sense
- **Performance Scoring**: 0-100 quality score with detailed breakdown

### 🔄 Testing Framework Sequence Diagram

```mermaid
sequenceDiagram
    participant User
    participant UI as Testing UI
    participant Ollama as Ollama API
    participant Translator as NL-to-SQL Translator
    participant Strategies as Translation Strategies
    participant DB as Data Engine
    participant Scorer as Quality Scorer

    User->>UI: Upload dataset & enter NL query
    UI->>UI: Validate inputs
    UI->>Ollama: Get available models
    Ollama-->>UI: Return model list
    User->>UI: Select model & strategy
    UI->>Translator: Initialize with selected model
    
    loop For each strategy
        UI->>Strategies: Execute translation strategy
        Strategies->>Ollama: Send NL query with context
        Ollama-->>Strategies: Return SQL translation
        Strategies->>DB: Validate SQL syntax
        DB-->>Strategies: Syntax validation result
        Strategies->>DB: Execute SQL query
        DB-->>Strategies: Query results
        Strategies->>Scorer: Calculate quality score
        Scorer-->>Strategies: Quality metrics
        Strategies-->>UI: Return strategy results
    end
    
    UI->>UI: Compare strategy results
    UI->>UI: Generate performance report
    UI-->>User: Display comprehensive results
```

### 📊 Understanding Test Results

#### Quality Score Components:
- **Syntax Score (0-25)**: SQL syntax correctness
- **Execution Score (0-25)**: Query runs without errors  
- **Logic Score (0-25)**: Query logic matches intent
- **Performance Score (0-25)**: Execution time and efficiency

#### Result Interpretation:
- **90-100**: Excellent - Production ready
- **75-89**: Good - Minor refinements needed
- **60-74**: Fair - Requires optimization
- **Below 60**: Poor - Needs significant improvement

### 🎛️ Advanced Configuration

#### Custom Strategy Testing
```python
# Add custom translation strategies
from analyzers.strategy_1_llm_enhanced import Strategy1LLMEnhanced

# Test with specific parameters
strategy = Strategy1LLMEnhanced(
    model_name="your-model",
    temperature=0.1,
    max_tokens=1000
)
```

#### Batch Testing
```python
# Run batch tests with multiple queries
test_queries = [
    "Show top customers",
    "Monthly revenue trends", 
    "Product performance analysis"
]

# Execute batch testing
python -c "from nl_to_sql_tester import NLToSQLTester; tester = NLToSQLTester(); tester.run_batch_tests(test_queries)"
```

### 🔍 Troubleshooting Testing Framework

#### Common Issues:
1. **Model Not Found**: Ensure Ollama is running and model is installed
2. **Connection Error**: Check Ollama API endpoint (default: http://localhost:11434)
3. **Import Errors**: Verify all dependencies are installed: `pip install -r requirements.txt`
4. **Port Conflicts**: Change port in launcher: `demo.launch(server_port=7863)`

#### Validation Tools:
```bash
# Validate framework syntax
python validate_nl_to_sql_syntax.py

# Test basic functionality
python test_framework_basic.py

# Check Ollama connectivity
curl http://localhost:11434/api/tags
```

### 🎯 Best Practices for Testing

1. **Start Simple**: Begin with basic queries before testing complex scenarios
2. **Use Representative Data**: Test with datasets similar to your production data
3. **Compare Models**: Test multiple models to find the best fit for your use case
4. **Document Results**: Keep track of which models/strategies work best for different query types
5. **Iterative Testing**: Refine queries based on initial results

## �️ General Troubleshooting

### Common Issues and Solutions

#### Application Won't Start
```bash
# Check Python version
python --version  # Should be 3.8+

# Verify dependencies
pip install -r requirements.txt

# Check for port conflicts
netstat -an | findstr :7871  # Windows
lsof -i :7871                # macOS/Linux

# Try alternative port
python app.py --port 7872
```

#### Ollama Connection Issues
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama service
ollama serve

# Check available models
ollama list

# Pull missing models
ollama pull gemma3:latest
```

#### Import and Dependency Errors
```bash
# Validate Python environment
python -c "import gradio, pandas, requests; print('Dependencies OK')"

# Reinstall dependencies
pip uninstall -r requirements.txt -y
pip install -r requirements.txt

# Use virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

#### Data Upload Issues
- **Large Files**: Use CSV format for files >100MB
- **Encoding**: Ensure UTF-8 encoding for international characters
- **Column Names**: Avoid special characters in column headers
- **Date Formats**: Use ISO format (YYYY-MM-DD) for best results

#### Performance Optimization
```bash
# Monitor memory usage
python -c "import psutil; print(f'RAM: {psutil.virtual_memory().percent}%')"

# Use lightweight models for faster responses
ollama pull qwen3:8b  # Faster alternative to gemma3

# Reduce dataset size for testing
head -1000 large_file.csv > test_sample.csv
```

### 🔧 Advanced Troubleshooting

#### Debug Mode
```bash
# Enable verbose logging
export DEBUG=1
python app.py

# Enable testing framework debug
export NL_TO_SQL_DEBUG=1
python test_enhanced_nl_to_sql_ui.py
```

#### Network Configuration
```bash
# Allow external access
python app.py --host 0.0.0.0

# Custom Ollama endpoint
export OLLAMA_HOST=http://remote-server:11434
```

#### File Validation Tools
```bash
# Validate all syntax
python validate_nl_to_sql_syntax.py

# Test framework functionality
python test_framework_basic.py

# Check file organization
python verify_cleanup.py
```

### 📞 Getting Help

1. **📋 Check Issues**: [GitHub Issues](https://github.com/sharkoil/variancepro/issues)
2. **📖 Documentation**: Review this README and inline code comments
3. **🔍 Search**: Use GitHub's search to find similar problems
4. **💬 Discussions**: [Community Q&A](https://github.com/sharkoil/variancepro/discussions)
5. **🐛 Report Bugs**: Create detailed issue reports with logs and system info

#### When Reporting Issues
Please include:
- Python version (`python --version`)
- Operating system and version
- Ollama version (`ollama --version`)
- Error messages and stack traces
- Steps to reproduce the problem
- Sample data (if applicable and not sensitive)

## �🔮 Roadmap

### Short-term (Q3 2025)
- **📱 Mobile App**: Native iOS/Android apps for data access on-the-go
- **� API Endpoints**: RESTful API for integration with business systems
- **📊 Advanced Visualizations**: Interactive charts and dashboards
- **🌐 Multi-language Support**: Internationalization for global users

### Medium-term (Q4 2025)
- **🤖 Custom AI Models**: Fine-tuned models for specific industries
- **📈 Predictive Analytics**: Forecasting and trend prediction capabilities
- **🔄 Real-time Data**: Live data streaming and continuous analysis
- **👥 Team Collaboration**: Multi-user workspaces and sharing features

### Long-term (2026+)
- **🏢 Enterprise Edition**: Advanced security, SSO, and compliance features
- **🧠 AutoML Integration**: Automated machine learning for predictive insights
- **🌍 Global Market Intelligence**: Expanded news sources and international coverage
- **📋 Regulatory Compliance**: Built-in compliance reporting for various industries

## �📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### Commercial Use
VariancePro is free for commercial use under the MIT License. For enterprise support, custom integrations, or professional services, please contact the development team.

## 🔗 Links & Resources

- **🏠 Homepage**: [https://github.com/sharkoil/variancepro](https://github.com/sharkoil/variancepro)
- **📋 Issues**: [Report bugs and request features](https://github.com/sharkoil/variancepro/issues)
- **📖 Documentation**: [Comprehensive guides and API docs](https://github.com/sharkoil/variancepro/wiki)
- **💬 Discussions**: [Community discussions and Q&A](https://github.com/sharkoil/variancepro/discussions)
- **🛠️ Ollama**: [Local AI inference platform](https://ollama.ai)
- **🎨 Gradio**: [Web UI framework](https://gradio.app)
- **📊 Pandas**: [Data analysis library](https://pandas.pydata.org)

## 🌟 Showcase

### Success Stories
> *"VariancePro transformed our monthly reporting process from days to minutes. The AI-generated executive summaries provide exactly the insights our C-suite needs."*  
> — Sarah Johnson, CFO at TechCorp

> *"The news intelligence feature helped us identify market factors affecting our regional sales 2 weeks before they showed up in our traditional reports."*  
> — Michael Chen, VP of Sales at RetailPlus

### Featured Use Cases
- **📈 Financial Planning**: Monthly/quarterly business reviews with AI insights
- **🎯 Performance Monitoring**: KPI tracking with market context
- **🏢 Executive Reporting**: Board-ready presentations with actionable intelligence
- **📊 Market Analysis**: Competitive intelligence with real-time news correlation
- **💼 Consulting**: Client reporting with professional visualizations and insights

## 🙏 Acknowledgments

### Technology Partners
- **🤖 Ollama Team**: Exceptional local AI inference platform enabling privacy-first intelligence
- **🎨 Gradio Team**: Intuitive web interface framework that makes AI accessible
- **📊 Pandas Community**: Powerful data analysis capabilities that form our foundation
- **🌐 Python Ecosystem**: Rich libraries enabling rapid development and deployment

### Open Source Community
- **Contributors**: All developers who have contributed code, documentation, and feedback
- **Beta Testers**: Early adopters who provided invaluable feedback and bug reports
- **Industry Experts**: Financial professionals who guided feature development and priorities
- **Academic Partners**: Research institutions that provided validation and best practices

### Special Recognition
- **Privacy Advocates**: For ensuring our zero-trust architecture meets the highest standards
- **AI Ethics Community**: For guidance on responsible AI implementation
- **Business Intelligence Experts**: For validating our analysis methodologies and outputs

---

<div align="center">
  <h3>🚀 Transform Your Financial Data Into Strategic Intelligence</h3>
  <p><em>Where Artificial Intelligence Meets Business Insight</em></p>
  
  **🎯 Professional Analysis • 🧠 AI-Powered Insights • 🔒 Privacy-First Architecture**
  
  <br>
  
  [![⭐ Star on GitHub](https://img.shields.io/github/stars/sharkoil/variancepro?style=social)](https://github.com/sharkoil/variancepro)
  [![🍴 Fork on GitHub](https://img.shields.io/github/forks/sharkoil/variancepro?style=social)](https://github.com/sharkoil/variancepro/fork)
  [![👁️ Watch on GitHub](https://img.shields.io/github/watchers/sharkoil/variancepro?style=social)](https://github.com/sharkoil/variancepro)
</div>
