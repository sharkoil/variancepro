# 🎉 Fresh Financial Chat App - Complete Setup

## ⚡ UPDATED: 2-Minute Timeout

The app now uses a **2-minute timeout** for AI requests instead of 30 seconds, allowing for more complex analyses and longer code generation.

## ✅ What's Been Created

Your fresh Gradio-based financial chat app is ready! Here's what's been set up:

### 📁 Core Files
- **`app_new.py`** - Clean Gradio app with StarCoder2 integration
- **`requirements_new.txt`** - All Python dependencies  
- **`setup_new.py`** - Setup script for Ollama + StarCoder2
- **`launch.py`** - Smart launcher with prerequisite checks
- **`test_app.py`** - Component testing script
- **`start_app.bat`** - Windows batch file for easy launching

### 📊 Sample Data
- **`sample_financial_data.csv`** - 365 rows of realistic financial data
  - Daily revenue, costs, profit data for 2023
  - Department, region, product breakdowns
  - Customer satisfaction scores

### 📚 Documentation
- **`README_NEW.md`** - Complete setup and usage guide

## 🚀 Quick Start

### Option 1: Automatic Test & Launch
```bash
python test_app.py    # Check if everything works
python launch.py      # Smart launcher with checks
```

### Option 2: Direct Launch
```bash
python app_new.py     # Start the app directly
```

### Option 3: Windows Users
```
Double-click: start_app.bat
```

## 🔧 If Ollama/StarCoder2 Isn't Set Up

1. **Install Ollama**: Download from https://ollama.com/download
2. **Run setup**: `python setup_new.py`
3. **Test setup**: `python test_app.py`

## 💡 App Features

- **📊 CSV Upload**: Drag and drop financial data
- **💬 AI Chat**: Multi-turn conversations with StarCoder2
- **📈 Data Analysis**: AI-powered insights and recommendations  
- **🔍 Code Generation**: Get Python code for analysis
- **⚡ Real-time**: Instant responses via local AI
- **⏱️ Extended Timeout**: 2-minute timeout for complex analysis

## ⚙️ Performance Notes

- **Response timeout**: 2 minutes for complex financial analysis
- **Local processing**: All AI computation happens on your machine
- **Memory usage**: 8GB+ RAM recommended for optimal performance

## 🎯 Example Usage

1. **Start the app**: `python launch.py`
2. **Upload data**: Use the sample CSV or your own
3. **Chat**: Try these questions:
   - "What's the total revenue for 2023?"
   - "Show me profit trends by department"
   - "Generate code to analyze monthly growth"
   - "What insights can you find in this data?"

## 🌐 Access

Once running, open: **http://localhost:7860**

The app will show:
- ✅ System status (Ollama + StarCoder2)
- 📊 Data upload and preview
- 💬 Chat interface
- 🔄 Real-time AI responses

## 🎨 Interface Overview

**Left Panel:**
- System status indicators
- CSV file upload
- Data preview (first 10 rows)

**Right Panel:**  
- Chat interface with StarCoder2
- Message input and send
- Quick action buttons

## 🔍 Troubleshooting

**App won't start?**
- Run: `python test_app.py`
- Check Python version: `python --version`
- Install requirements: `pip install -r requirements_new.txt`

**Ollama issues?**
- Download: https://ollama.com/download
- Check service: Open http://localhost:11434
- Run setup: `python setup_new.py`

**StarCoder2 missing?**
- Pull model: `ollama pull starcoder2:latest`
- Verify: `ollama list`

## 🎊 You're All Set!

Your fresh financial chat app is ready to analyze data with AI! 

**Start exploring**: `python launch.py` 🚀
