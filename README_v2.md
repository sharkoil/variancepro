# VariancePro v2.0 - AI-Powered Financial Analysis

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![AI-Powered](https://img.shields.io/badge/AI-Powered-green.svg)](https://github.com/sharkoil/variancepro)

## 🚀 What is VariancePro?

AI-powered financial intelligence platform that transforms CSV data into comprehensive business insights. Features advanced variance analysis, RAG-enhanced insights, and natural language chat interface.

## ✨ Key Features

- 🤖 **AI Chat Interface** - Natural language queries with intelligent responses
- 📊 **Advanced Variance Analysis** - Actual vs Planned, Budget vs Sales comparisons
- 📚 **RAG Enhancement** - Upload PDFs/documents to enrich analysis with context
- 🔧 **Modular Architecture** - Clean, maintainable, extensible codebase
- 🎯 **Quick Actions** - One-click Summary, Trends, Variance, Top/Bottom analysis
- 🔒 **Privacy-First** - 100% local processing, data never leaves your machine

## 🔧 Recent Fixes (Latest)

- ✅ **Fixed Variance Analysis Error** - Resolved method signature mismatch
- ✅ **Improved RAG Integration** - Better error handling when components unavailable
- ✅ **Enhanced Summary Output** - Human-readable analysis results
- ✅ **Updated AI Models** - Changed from gemma2 to gemma3 for better performance

## 🏗️ Architecture

```
app_v2.py (Main Orchestrator)
├── core/app_core.py              # Application logic & state
├── handlers/                     # Request handlers (file, chat, actions)
├── analyzers/                    # Analysis engines (variance, RAG, etc.)
└── tests/                        # Unit & integration tests
```

## 🚀 Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start Ollama** (for AI features)
   ```bash
   ollama serve
   ollama pull gemma3:latest
   ```

3. **Run VariancePro**
   ```bash
   python app_v2.py
   ```

4. **Access Interface**
   - Open http://localhost:7873
   - Upload your CSV file
   - Start analyzing with AI chat or quick action buttons

## 📊 Sample Analysis Types

- **Summary Analysis** - Overview of your dataset
- **Variance Analysis** - Compare actual vs planned/budget
- **Trend Analysis** - Time-based patterns and trends
- **Top/Bottom N** - Best and worst performing items
- **RAG-Enhanced** - All analysis enhanced with uploaded documents

## 🔧 Configuration

### Ollama Models
- **Default**: `gemma3:latest`
- **Fallback**: `llama3.2:latest`

### Data Requirements
- CSV files with numeric columns for analysis
- Date columns for trend analysis (optional)
- Budget/Actual/Planned columns for variance analysis

## 🧪 Testing

Run comprehensive tests:
```bash
python -m pytest tests/ -v
python test_variance_with_data.py  # Specific variance test
```

## 📁 Project Structure

- `app_v2.py` - Main application (398 lines, down from 905)
- `core/` - Core business logic
- `handlers/` - Request processing
- `analyzers/` - Analysis engines
- `tests/` - Test suite (80%+ coverage)
- `sample_data/` - Test datasets

## 🤝 Contributing

1. Follow modular design principles
2. Add unit tests for new features
3. Use type hints and descriptive names
4. Keep files focused and small
5. Document changes in commit messages

## 📄 License

MIT License - see LICENSE file for details.

---

**VariancePro v2.0** - Built with ❤️ for financial intelligence
