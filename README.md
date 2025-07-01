# 📊 VariancePro - AI-Powered Financial Data Analysis

**VariancePro** is an intelligent financial analysis chat application that combines the power of **Gemma3 LLM**, **LlamaIndex**, and advanced **contribution analysis** to provide comprehensive insights from your CSV data. Built with **Gradio** for an intuitive web interface.

![VariancePro Dashboard](https://img.shields.io/badge/VariancePro-Financial%20Analysis-blue?style=for-the-badge&logo=chart-dot-js)

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

4. **Launch VariancePro**
```bash
python app.py
```

5. **Access the Application**
- Open your browser to `http://localhost:7860`
- Upload a CSV file
- Start asking financial questions!

Run the Gradio app:
```bash
python app.py
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
🤖 VariancePro: Provides comprehensive overview with key metrics, trends, and insights

👤 User: "What are the top contributors to revenue?"
🤖 VariancePro: Performs 80/20 analysis showing key customers/products driving performance
```

### **Advanced Insights**
```
👤 User: "Perform contribution analysis"
🤖 VariancePro: 
📊 CONTRIBUTION ANALYSIS RESULTS (80/20 Pareto Principle)
🎯 Top 3 customers drive 78% of total revenue
📈 Shows detailed breakdown with visual charts
� Provides strategic recommendations
```

## 🏗️ **Project Structure**
```
📁 VariancePro/
├── 🎯 app.py                    # Main application & chat system
├── 🧠 utils/
│   ├── chat_handler.py          # LLM integration & chat logic  
│   ├── llm_handler.py           # Ollama/Gemma3 interface
│   └── narrative_generator.py   # Aria Sterling persona
├── 📊 llamaindex_integration.py # LlamaIndex enhanced analysis
├── 🔧 requirements.txt          # Python dependencies
└── 📚 docs/                     # Documentation & guides
```

## 🔧 **Configuration**

### **Model Selection**
```python
# Default configuration (in app.py)
self.model_name = "gemma3:latest"  # Primary LLM
```

### **LlamaIndex Setup** (Optional)
```bash
pip install llama-index llama-index-llms-ollama
```

## 🧪 **Testing**

### **Run Test Suite**
```bash
# Test core functionality
python test_contribution_analysis.py

# Test LlamaIndex integration
python test_llamaindex_integration.py

# Test model configuration
python test_model_configuration.py
```

## 🛠️ **Deployment**

### **Local Development**
```bash
python app.py
# Access: http://localhost:7860
```

### **Production Deployment**
```bash
# Set environment variables
export OLLAMA_HOST=your-ollama-server
export GRADIO_SERVER_PORT=7860

# Launch with production settings
python app.py
```

## 📚 **Documentation**

- **[LlamaIndex Integration Guide](LLAMAINDEX_INTEGRATION_GUIDE.md)**: Advanced analysis setup
- **[Deployment Guide](DEPLOYMENT_SUMMARY.md)**: Production deployment
- **[StarCoder Integration](STARCODER_INTEGRATION.md)**: Code generation features

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

## 📞 **Public Repository**

**🔗 GitHub Repository**: [https://github.com/yourusername/variancepro](https://github.com/yourusername/variancepro)

For the latest updates, documentation, and community contributions, visit our public repository.

## 🙏 **Acknowledgments**

- **Ollama Team**: For local LLM hosting infrastructure
- **Gradio Team**: For the excellent web UI framework
- **LlamaIndex**: For enhanced document processing capabilities
- **Google**: For the powerful Gemma3 language model
