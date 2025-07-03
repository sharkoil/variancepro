# 📊 Quant Commander - AI-Powered Financial Data Analysis

**Quant Commander** (formerly VariancePro) is an intelligent financial analysis chat application that combines the power of **Gemma3 LLM**, **LlamaIndex**, and advanced **contribution analysis** to provide comprehensive insights from your CSV data. Built with **Gradio** for an intuitive web interface.

![Quant Commander](https://img.shields.io/badge/Quant%20Commander-Financial%20Analysis-blue?style=for-the-badge&logo=chart-dot-js)

## 🎯 **Key Features**

### 🤖 **AI-Powered Analysis**
- **Gemma3 Integration**: Advanced language model for sophisticated financial insights
- **LlamaIndex Enhanced**: Structured analysis with enhanced document processing
- **Aria Sterling Persona**: Professional financial analyst assistant
- **Natural Language Queries**: Ask questions in plain English

### 📈 **Advanced Analytics**
- **80/20 Contribution Analysis**: Automated Pareto principle analysis from Medium methodology
- **Timescale Analysis**: TTM (Trailing Twelve Months) calculations and trends
- **Budget vs Actual Variance**: Comprehensive variance analysis
- **Smart Column Detection**: Automatic identification of categories, values, and time columns

### 💬 **Chat Interface**
- **Pure Chat Experience**: All analysis appears inline in conversation
- **CSV-Only Analysis**: Guaranteed to use only your uploaded data
- **No Code Suggestions**: Focused on insights, not programming
- **Clean Responses**: No redundant analysis repetition

### 🔧 **Technical Excellence**
- **Modern Architecture**: Python, Gradio, Ollama integration
- **Local Processing**: Your data stays private and secure
- **Extensible Design**: Easy to add new analysis types
- **Production Ready**: Comprehensive error handling and logging

## 🚀 **Quick Start**

### **Prerequisites**
- Python 3.8+
- Ollama (for local LLM hosting)
- 8GB+ RAM recommended

### **Installation**

1. **Clone the Repository**
```bash
git clone https://github.com/yourusername/variancepro.git
cd variancepro
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

Run the Gradio app:
```bash
python app_new.py
```

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

## � **Example Conversations**

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
📈 Shows detailed breakdown with visual charts
� Provides strategic recommendations
```

## 🏗️ **Project Structure**
```
📁 Quant Commander/ (Clean Architecture)
├── 🎯 app_new.py                # Main Quant Commander application
├── 📁 ai/                       # AI Integration Components
│   ├── llm_interpreter.py       # Ollama/Gemma3 interface
│   └── narrative_generator.py   # Aria Sterling persona
├── � analyzers/                # Analysis Modules
│   ├── contributor_analyzer.py  # 80/20 Pareto analysis
│   ├── financial_analyzer.py    # Variance & trend analysis
│   ├── news_analyzer_v2.py      # Business context news
│   └── timescale_analyzer.py    # Multi-period analysis
├── 📁 config/                   # Configuration
│   └── settings.py              # Application settings
├── 📁 data/                     # CSV Processing
│   └── csv_loader.py            # Enhanced CSV loading
├── 📁 tests/                    # Test Suite
│   └── data/                    # Test datasets
├── 📁 sample_data/              # Example datasets
├── 🔧 requirements.txt          # Python dependencies
├── 📚 README.md                 # This documentation
├── 🤝 CONTRIBUTING.md           # Contribution guidelines
├── 📄 LICENSE                   # MIT license
├── 🖼️ logo.png                 # Quant Commander logo
└── 🚀 start_app.bat             # Windows launcher
```

## 🔧 **Configuration**

### **Model Selection**
```python
# Default configuration (in config/settings.py)
llm_model = "gemma3:latest"  # Primary LLM
ollama_host = "http://localhost:11434"
```

### **Environment Variables** (Optional)
```bash
export VARIANCEPRO_LLM_MODEL=gemma3:latest
export OLLAMA_HOST=http://localhost:11434
export GRADIO_SERVER_PORT=7862
```

## 🧪 **Testing**

### **Sample Data**
```bash
# Sample datasets available in sample_data/
sample_data/sample_variance_data.csv     # Financial variance analysis
sample_data/sample_variance_data.xlsx    # Excel format sample
sample_data/comprehensive_sales_data.csv # Sales analysis example
sample_data/sales_budget_actuals.csv     # Budget vs actual example

# Test datasets in tests/data/
# Various test scenarios for validation
```

### **Manual Testing**
```bash
# Start the application
python app_new.py

# Upload sample_data/sample_variance_data.csv
# Test various analysis commands
```

### **File Organization**
```bash
# If sample files are in the root directory, organize them:
python organize_files.py

# This will move sample data files to sample_data/ folder
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

## 📚 **Documentation**

- **[Contributing Guidelines](CONTRIBUTING.md)**: Development and contribution guide
- **[License](LICENSE)**: MIT open source license
- **Architecture Documentation**: Coming soon with modular refactor

## 🔐 **Security & Privacy**

- **Local Processing**: All data analysis happens locally
- **No External APIs**: Your data never leaves your environment
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

## 📞 **Repository Information**

**🔗 GitHub Repository**: [https://github.com/yourusername/variancepro](https://github.com/yourusername/variancepro)

### **Clean Project Structure**
This repository maintains a clean, production-ready structure:
- **Core Application**: `app_new.py` (main entry point)
- **Modular Components**: Organized in `ai/`, `analyzers/`, `config/`, `data/` folders
- **Documentation**: README.md, CONTRIBUTING.md, LICENSE
- **Sample Data**: Available in `sample_data/` for testing
- **Tests**: Organized test suite in `tests/` folder

For the latest updates, documentation, and community contributions, visit our public repository.

## 🙏 **Acknowledgments**

- **Ollama Team**: For local LLM hosting infrastructure
- **Gradio Team**: For the excellent web UI framework
- **Google**: For the powerful Gemma3 language model
- **Community**: For feedback and contributions to make Quant Commander better
