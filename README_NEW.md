# 💼 Financial Chat App - Fresh Start

A clean, modern financial data analysis chat application powered by **Gradio**, **Ollama**, and **StarCoder2**.

## ✨ Features

- 📊 **CSV Data Upload**: Upload and analyze financial datasets
- 💬 **AI Chat Interface**: Multi-turn conversations with StarCoder2
- 🔍 **Data Insights**: Get AI-powered analysis and recommendations
- 📈 **Code Suggestions**: Generate Python code for data analysis
- 🚀 **Local AI**: Runs entirely on your machine via Ollama

## 🛠️ Quick Setup

### 1. Install Requirements
```bash
pip install -r requirements_new.txt
```

### 2. Run Setup (First Time)
```bash
python setup_new.py
```

This will:
- Install Python dependencies
- Guide you through Ollama installation
- Download the StarCoder2 model
- Create sample data for testing

### 3. Launch the App
```bash
python launch.py
```

Or directly:
```bash
python app_new.py
```

## 🎯 Usage

1. **Start the app**: Run `python launch.py`
2. **Upload data**: Use the CSV upload panel
3. **Chat away**: Ask questions about your data
4. **Get insights**: Receive AI-powered analysis and code

## 💡 Example Queries

- "Analyze the revenue trends in this dataset"
- "Show me Python code to calculate month-over-month growth"
- "What are the key insights from this financial data?"
- "Generate a profit margin analysis"
- "Create a visualization of the sales performance"

## 🔧 System Requirements

- **Python**: 3.8 or higher
- **Ollama**: Local AI runtime
- **StarCoder2**: Code-focused language model
- **Memory**: 8GB+ RAM recommended
- **Storage**: 3GB+ for the StarCoder2 model

## 🏗️ Architecture

```
Financial Chat App
├── app_new.py           # Main Gradio application
├── launch.py            # App launcher with checks
├── setup_new.py         # One-time setup script
├── requirements_new.txt # Python dependencies
└── sample_financial_data.csv # Test dataset
```

## 🔍 Troubleshooting

### Ollama Issues
- Download from: https://ollama.com/download
- Ensure the service is running
- Check with: `ollama list`

### StarCoder2 Issues
- Pull model: `ollama pull starcoder2:latest`
- Verify: `ollama list` should show starcoder2

### App Issues
- Check Python version: `python --version`
- Install requirements: `pip install -r requirements_new.txt`
- Run launcher: `python launch.py`

## 📊 Sample Data

The setup creates `sample_financial_data.csv` with:
- Daily financial data for 2023
- Revenue, costs, profit columns
- Department and region breakdowns
- Perfect for testing the chat app

## 🚀 Getting Started

1. **Quick test**: 
   ```bash
   python launch.py
   ```

2. **Upload the sample data** in the Gradio interface

3. **Try these questions**:
   - "What's the total revenue for 2023?"
   - "Show me a profit analysis by department"
   - "Generate code to plot monthly trends"

## 🎨 Interface Preview

- **Left Panel**: Status, file upload, data preview
- **Right Panel**: Chat interface with StarCoder2
- **Quick Actions**: Preset analysis buttons
- **Real-time**: Instant AI responses

## 📈 Advanced Usage

- **Multi-turn conversations**: Build complex analyses step by step
- **Code generation**: Get pandas/matplotlib code for your data
- **Custom datasets**: Upload any CSV financial data
- **Export results**: Copy AI-generated code to run separately

---

**Ready to analyze your financial data with AI? Run `python launch.py` and get started!** 🚀
