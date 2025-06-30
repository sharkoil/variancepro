# VariancePro - Financial Data Analysis Chat App

A multi-turn chat financial application built with Gradio that allows users to upload CSV files, analyze financial data, and interact through a conversational interface powered by Phi4 via Ollama.

## Features

- 📊 CSV file upload and data visualization
- 💬 Multi-turn chat interface for financial queries powered by AI
- 📈 Interactive data tables and charts
- 🔍 Financial data analysis capabilities
- 🤖 AI-powered data insights using Phi4

## Installation

1. Clone or download this project
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the Gradio app:
```bash
python app.py
```

## Project Structure

- `app.py` - Main Gradio application
- `utils/` - Utility functions for data processing and chat
- `requirements.txt` - Python dependencies
- `sample_data/` - Sample financial data files

## 🔄 Recent Updates - Phi4 Integration

**v2.0**: Migrated from Gemma3:12B to Microsoft Phi4 for improved performance:

- ⚡ **Faster responses** - Optimized 90s timeout vs 120s
- 💾 **Lower memory usage** - ~4GB RAM vs ~8GB 
- 🧠 **Enhanced reasoning** - Better financial analysis capabilities
- 🛠️ **Improved setup** - Streamlined installation process

See `PHI4_MIGRATION.md` for detailed migration information.

## 🚀 Quick Start with Phi4

### Prerequisites
1. **Install Ollama**: Download from [ollama.ai](https://ollama.ai/download)
2. **Install Phi4 model**:
   ```bash
   ollama pull phi4
   ```

### Running the App
1. **Start Ollama service**:
   ```bash
   ollama serve
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run VariancePro**:
   ```bash
   python app.py
   ```

4. **Access the application**: http://localhost:7860

### Alternative Setup
Use the automated setup script:
```bash
python setup_phi4.py
```
