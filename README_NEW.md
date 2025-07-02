# � Quant Commander - AI-Powered Financial Data Analysis

<div align="center">
  <img src="https://i.imgur.com/HCqkkDM.png" alt="Quant Commander Logo" height="180">
</div>

**Quant Commander** is an intelligent financial analysis chat application that combines the power of **Gemma3 LLM**, **LlamaIndex**, and advanced **contribution analysis** to provide comprehensive insights from your CSV data. Built with **Gradio** for an intuitive web interface.

## 🎯 **Key Features**

### 🤖 **AI-Powered Analysis**
- **Gemma3 Integration**: Advanced language model for sophisticated financial insights
- **LlamaIndex Enhanced**: Structured analysis with enhanced document processing
- **Aria Sterling Persona**: Professional financial analyst assistant
- **Natural Language Queries**: Ask questions in plain English

### � **Advanced Analytics**
- **80/20 Contribution Analysis**: Automated Pareto principle analysis from Medium methodology
- **Timescale Analysis**: TTM (Trailing Twelve Months) calculations and trends
- **Budget vs Actual Variance**: Comprehensive variance analysis
- **Smart Column Detection**: Automatic identification of categories, values, and time columns
- **News Integration**: Automatic business context via location-based news analysis

### � **Chat Interface**
- **Pure Chat Experience**: All analysis appears inline in conversation
- **CSV-Only Analysis**: Guaranteed to use only your uploaded data
- **No Code Suggestions**: Focused on insights, not programming
- **Clean Responses**: No redundant analysis repetition

### 🔧 **Technical Excellence**
- **Modern Architecture**: Python, Gradio, Ollama integration
- **Local Processing**: Your data stays private and secure
- **Extensible Design**: Easy to add new analysis types
- **Production Ready**: Comprehensive error handling and logging

## � **Quick Start**

### **Prerequisites**
- Python 3.8+
- Ollama (for local LLM hosting)
- 8GB+ RAM recommended

### **Installation**

1. **Clone the Repository**
```bash
git clone https://github.com/yourusername/quant-commander.git
cd quant-commander
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Setup Ollama & Gemma3**
```bash
# Install Ollama from https://ollama.ai
ollama pull gemma3:latest
ollama serve
```

4. **Launch Quant Commander**
```bash
python app_new.py
```

5. **Access the Application**
- Open your browser to `http://localhost:7862`
- Upload a CSV file
- Start asking financial questions!

## 📊 **Use Cases**

### **Financial Analysis**
- Revenue trend analysis
- Budget variance investigation
- Customer/product contribution analysis
- Seasonal pattern identification
- Performance benchmarking

### **Business Intelligence**
- 80/20 Pareto analysis (which customers/products drive 80% of revenue)
- Regional performance comparison
- Time-series trend analysis
- Key performance indicator tracking
- Executive summary generation
- Location-based business context through news integration

## 💡 **Example Conversations**

### **Basic Analysis**
```
👤 User: "Analyze this sales data"
🤖 Quant Commander: Provides comprehensive overview with key metrics, trends, and insights

👤 User: "What are the top contributors to revenue?"
🤖 Quant Commander: Performs 80/20 analysis showing key customers/products driving performance
```

### **Advanced Insights**
```
👤 User: "Perform contribution analysis"
🤖 Quant Commander: 
📊 CONTRIBUTION ANALYSIS RESULTS (80/20 Pareto Principle)
🎯 Top 3 customers drive 78% of total revenue
� Shows detailed breakdown with visual charts
💡 Provides strategic recommendations
```

## 🏗️ **Project Structure**
```
📁 Quant Commander/ (Clean Architecture)
├── 🎯 app_new.py               # Main application
├── 🧠 ai/
│   ├── llm_interpreter.py       # Ollama/Gemma3 interface
│   └── narrative_generator.py   # Aria Sterling persona
├── 📊 analyzers/
│   ├── contributor_analyzer.py  # 80/20 Pareto analysis
│   ├── financial_analyzer.py    # Budget vs actual analysis
│   ├── timescale_analyzer.py    # Time series analysis
│   └── news_analyzer.py         # Business context from location data
├── 📁 data/
│   └── csv_loader.py            # CSV loading and preprocessing
├── 📁 config/
│   └── settings.py              # Application settings
├── 🧪 tests/
│   ├── test_news_analyzer.py    # News analyzer tests
│   ├── test_contribution_analysis.py # Contribution analyzer tests
│   └── test_financial_analyzer.py    # Financial analyzer tests
├── 🔧 requirements.txt          # Python dependencies
├── 📚 README.md                 # This documentation
├── 🤝 CONTRIBUTING.md           # Contribution guidelines
└── 📄 LICENSE                   # MIT license
```

## � **Configuration**

### **Model Selection**
```python
# Default configuration (in settings.py)
self.model_name = "gemma3:latest"  # Primary LLM
```

### **LlamaIndex Setup** (Optional)
```bash
pip install llama-index llama-index-llms-ollama
```

## 🛠️ **Deployment**

### **Local Development**
```bash
python app_new.py
# Access: http://localhost:7862
```

### **Production Deployment**
```bash
# Set environment variables
export OLLAMA_HOST=your-ollama-server
export GRADIO_SERVER_PORT=7862

# Launch with production settings
python app_new.py
```

## � **Documentation**

- **[Contributing Guidelines](CONTRIBUTING.md)**: Development and contribution guide
- **[License](LICENSE)**: MIT open source license
- **[News Analyzer Summary](NEWS_ANALYZER_SUMMARY.md)**: Documentation for the news analyzer module

## � **Security & Privacy**

- **Local Processing**: All data analysis happens locally
- **No External APIs**: Your data never leaves your environment (except for RSS news feeds)
- **CSV-Only Analysis**: No external data sources accessed
- **Secure by Design**: No data persistence unless explicitly configured

## 🐛 **Troubleshooting**

### **Common Issues**

**Ollama Connection Error**
```bash
# Check if Ollama is running
ollama list
# Start Ollama service
ollama serve
```

**Model Not Found**
```bash
# Pull required model
ollama pull gemma3:latest
```

**RSS Feed Issues**
```bash
# Install feedparser for news analysis
pip install feedparser
```

## � **Public Repository**

**🔗 GitHub Repository**: [https://github.com/yourusername/quant-commander](https://github.com/yourusername/quant-commander)

For the latest updates, documentation, and community contributions, visit our public repository.

## 🙏 **Acknowledgments**

- **Ollama Team**: For local LLM hosting infrastructure
- **Gradio Team**: For the excellent web UI framework
- **LlamaIndex**: For enhanced document processing capabilities
- **Google**: For the powerful Gemma3 language model
