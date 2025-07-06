# VariancePro - AI-Powered Financial Intelligence Platform

<div align="center">
  <img src="logo.png" alt="VariancePro Logo" width="200"/>
  
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
  [![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
  [![Gradio](https://img.shields.io/badge/Gradio-4.0+-orange.svg)](https://gradio.app/)
  [![AI-Powered](https://img.shields.io/badge/AI-Powered-green.svg)](https://github.com/sharkoil/variancepro)
</div>

## 🚀 Introduction

VariancePro is an AI-powered financial intelligence platform that transforms your CSV data into comprehensive business insights. Chat with Aria Sterling, your AI financial analyst, to get instant analysis including contribution analysis, variance reporting, trend analysis, and intelligent business recommendations.

**Key Features:**
- 🤖 **AI Chat Interface**: Natural language queries with intelligent responses
- 📊 **Advanced Analytics**: Contribution, variance, and trend analysis
- 🔒 **Privacy-First**: 100% local processing - your data never leaves your machine
- 📈 **Professional Reports**: Publication-ready tables and insights
- 🧠 **Smart Detection**: Auto-identifies data patterns and business context
- 🆔 **Session Management**: Timestamped responses with unique session IDs

## 🛠️ Technology Stack

- **Frontend**: Gradio web interface with responsive design
- **Backend**: Python with pandas for data processing
- **AI Engine**: Ollama with local model inference
- **Analysis**: Modular analyzer architecture
- **Security**: Zero-trust local processing

## 📋 Requirements

- **Python**: 3.8 or higher
- **Memory**: 8GB+ RAM (recommended for AI model performance)
- **Ollama**: Local AI inference engine with models
- **Browser**: Modern web browser (Chrome, Firefox, Safari, Edge)
- **Internet**: Optional (for news intelligence features only)

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/sharkoil/variancepro.git
cd variancepro
```

### 2. Install Dependencies
```bash
# Install core dependencies
pip install -r requirements.txt
```

### 3. Install and Setup Ollama
```bash
# Visit https://ollama.ai for platform-specific installation

# Pull recommended models
ollama pull gemma3:latest      # Primary model
ollama pull deepseek-r1:14b    # Advanced reasoning
ollama pull qwen3:8b           # Fast responses

# Verify installation
ollama list
```

## 🎯 How to Run

### Main Application
```bash
# Start VariancePro
python app_new.py
```
Access at: `http://localhost:7871`

### Testing Framework
```bash
# Start NL-to-SQL Testing Framework
python test_enhanced_nl_to_sql_ui.py
```
Access at: `http://localhost:7862`

## 🧪 Testing Tools

### Enhanced NL-to-SQL Testing Framework
The testing framework allows you to evaluate Natural Language to SQL translation across multiple AI models:

**Features:**
- 🤖 Multi-model support (any Ollama-deployed model)
- 🔄 Strategy comparison (LLM-enhanced vs semantic parsing)
- 📊 Quality scoring with automated assessment
- � Performance metrics and response time tracking
- 🎨 Interactive web-based interface

**Usage:**
1. Launch the testing framework
2. Upload your dataset (CSV/Excel)
3. Select AI model from dropdown
4. Enter natural language queries
5. Compare translation strategies
6. Review quality scores and performance

**Example Test Queries:**
- "Show me the top 5 products by revenue"
- "Find customers with orders above $10,000"
- "Compare revenue between regions"
- "What are the sales figures for Q1?"

## 🏗️ System Architecture

### Main Application Flow

```mermaid
sequenceDiagram
    participant User
    participant Gradio as Gradio UI
    participant App as QuantCommanderApp
    participant CSV as CSVLoader
    participant AI as LLMInterpreter
    participant Router as QueryRouter
    participant Analyzer as Analysis Engines

    User->>Gradio: Upload CSV File
    Gradio->>App: handle_file_upload()
    App->>CSV: load_and_validate()
    CSV->>CSV: Auto-detect columns & types
    CSV-->>App: Data + Column suggestions
    
    App->>Gradio: Display data preview & session info
    Note over Gradio: Show Session ID & timestamp
    
    User->>Gradio: Ask analytical question
    Gradio->>App: chat_response() with timestamp
    
    App->>Router: route_user_query()
    Router->>AI: classify_intent()
    AI-->>Router: Analysis type + parameters
    Router-->>App: Routing decision
    
    alt Contribution Analysis
        App->>Analyzer: ContributorAnalyzer.analyze()
        Analyzer-->>App: Pareto analysis results
    else Variance Analysis
        App->>Analyzer: FinancialAnalyzer.analyze()
        Analyzer-->>App: Budget vs actual comparison
    else Trend Analysis
        App->>Analyzer: TimescaleAnalyzer.analyze()
        Analyzer-->>App: Time series insights
    else SQL Query
        App->>Analyzer: SQLQueryEngine.execute()
        Analyzer-->>App: Query results
    end
    
    opt AI Insights Available
        App->>AI: query_llm(analysis_context)
        AI-->>App: Strategic recommendations
    end
    
    App->>App: Add timestamp to response
    App->>Gradio: Return timestamped analysis
    Gradio->>User: Display results with session context
```

### Testing Framework Flow

```mermaid
sequenceDiagram
    participant User
    participant TestUI as Testing Interface
    participant Ollama as Ollama API
    participant Translator as NL-to-SQL Engine
    participant Strategies as Translation Strategies
    participant Scorer as Quality Assessment

    User->>TestUI: Upload dataset & enter NL query
    TestUI->>TestUI: Validate inputs
    TestUI->>Ollama: Get available models
    Ollama-->>TestUI: Return model list
    
    User->>TestUI: Select model & strategy
    TestUI->>Translator: Initialize with selected model
    
    loop For each strategy
        TestUI->>Strategies: Execute translation strategy
        Strategies->>Ollama: Send NL query with context
        Ollama-->>Strategies: Return SQL translation
        
        Strategies->>Strategies: Validate SQL syntax
        Strategies->>Strategies: Execute SQL query
        Strategies->>Scorer: Calculate quality metrics
        
        Scorer->>Scorer: Assess syntax correctness
        Scorer->>Scorer: Evaluate execution success
        Scorer->>Scorer: Analyze logic accuracy
        Scorer->>Scorer: Measure performance
        
        Scorer-->>Strategies: Quality score (0-100)
        Strategies-->>TestUI: Strategy results
    end
    
    TestUI->>TestUI: Compare strategy performance
    TestUI->>TestUI: Generate comprehensive report
    TestUI-->>User: Display results & recommendations
```

## 🔮 Roadmap

### Immediate (Q3 2025)
- **Enhanced Session Management**: Persistent session storage and recovery
- **Advanced Timestamp Analytics**: Query performance tracking and optimization
- **Custom AI Models**: Fine-tuned models for financial terminology
- **Export Capabilities**: PDF and Excel report generation

### Short-term (Q4 2025)
- **📱 Mobile App**: Native iOS/Android apps for data access
- **🔄 Real-time Data**: Live data streaming and continuous analysis
- **👥 Team Collaboration**: Multi-user workspaces and sharing
- **📊 Advanced Visualizations**: Interactive charts and dashboards

### Medium-term (2026)
- **🤖 AutoML Integration**: Automated machine learning for predictions
- **🌍 Global Intelligence**: Expanded news sources and international coverage
- **🏢 Enterprise Edition**: SSO, advanced security, and compliance features
- **📋 Regulatory Compliance**: Built-in compliance reporting

### Long-term (2027+)
- **🧠 Predictive Analytics**: Advanced forecasting and trend prediction
- **🌐 API Ecosystem**: RESTful APIs for integration with business systems
- **🔒 Advanced Security**: Enterprise-grade encryption and audit trails
- **🎯 Industry Templates**: Pre-built analysis templates for specific sectors

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links & Resources

- **🏠 Repository**: [https://github.com/sharkoil/variancepro](https://github.com/sharkoil/variancepro)
- **📋 Issues**: [Report bugs and request features](https://github.com/sharkoil/variancepro/issues)
- **💬 Discussions**: [Community Q&A](https://github.com/sharkoil/variancepro/discussions)
- **🛠️ Ollama**: [Local AI inference platform](https://ollama.ai)
- **🎨 Gradio**: [Web UI framework](https://gradio.app)

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
