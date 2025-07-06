# Installation Guide

This guide walks you through installing VariancePro and its dependencies.

## 📋 Requirements

- **Python 3.8 or higher**
- **8GB+ RAM** (recommended for AI model performance)
- **Ollama** installed locally with Gemma3 model
- **Modern web browser** (Chrome, Firefox, Safari, Edge)
- **Internet connection** (for news intelligence features only)

## 🚀 Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/sharkoil/variancepro.git
cd variancepro
```

### 2. Install Python Dependencies

You have three options for installing dependencies:

#### Core Dependencies (Recommended)
```bash
pip install -r requirements.txt
```

#### Minimal Dependencies
```bash
pip install -r requirements-minimal.txt
```

#### Full Feature Set
```bash
pip install -r requirements-full.txt
```

### 3. Install and Setup Ollama

#### Install Ollama
Visit [https://ollama.ai](https://ollama.ai) for platform-specific installation instructions.

#### Pull Recommended Models
```bash
# Primary model for analysis
ollama pull gemma3:latest

# Advanced reasoning model
ollama pull deepseek-r1:14b

# Fast response model
ollama pull qwen3:8b

# Multi-modal capabilities
ollama pull llava:latest
```

#### Verify Installation
```bash
ollama list
```

### 4. Verify Installation

```bash
# Check Python version
python --version  # Should be 3.8+

# Validate Python environment
python -c "import gradio, pandas, requests; print('Dependencies OK')"

# Check Ollama connectivity
curl http://localhost:11434/api/tags
```

## ⚙️ Environment Setup

### Environment Variables

```bash
# Set custom ports
export VARIANCEPRO_PORT=7871
export TESTING_FRAMEWORK_PORT=7862
export OLLAMA_HOST=localhost:11434

# Set default model
export DEFAULT_MODEL=gemma3:latest
```

### Windows Environment Variables
```cmd
set VARIANCEPRO_PORT=7871
set TESTING_FRAMEWORK_PORT=7862
set OLLAMA_HOST=localhost:11434
set DEFAULT_MODEL=gemma3:latest
```

## 🐍 Virtual Environment (Recommended)

### Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Linux/macOS:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

### Install Dependencies in Virtual Environment
```bash
pip install -r requirements.txt
```

## 🔧 Alternative Installation Methods

### Using Conda
```bash
# Create conda environment
conda create -n variancepro python=3.9

# Activate environment
conda activate variancepro

# Install dependencies
pip install -r requirements.txt
```

### Using Docker (Coming Soon)
Docker support is planned for future releases.

## ✅ Post-Installation Verification

### Test Main Application
```bash
python app_new.py
# Should start on http://localhost:7871
```

### Test Enhanced Testing Framework
```bash
python test_enhanced_nl_to_sql_ui.py
# Should start on http://localhost:7862
```

### Validate Framework Components
```bash
# Validate syntax
python validate_nl_to_sql_syntax.py

# Test basic functionality
python test_framework_basic.py
```

## 🛠️ Troubleshooting Installation

### Common Issues

#### Python Version Issues
```bash
# Check Python version
python --version

# If using multiple Python versions
python3 --version
python3 -m pip install -r requirements.txt
```

#### Dependency Conflicts
```bash
# Clean install
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

#### Ollama Connection Issues
```bash
# Start Ollama service
ollama serve

# Check if running
curl http://localhost:11434/api/tags
```

#### Port Conflicts
```bash
# Check port usage (Windows)
netstat -an | findstr :7871

# Check port usage (Linux/macOS)
lsof -i :7871

# Use alternative port
python app_new.py --port 7872
```

### Performance Optimization

#### Memory Usage
```bash
# Monitor memory usage
python -c "import psutil; print(f'RAM: {psutil.virtual_memory().percent}%')"

# Use lightweight models for faster responses
ollama pull qwen3:8b  # Faster alternative to gemma3
```

#### Disk Space
Ensure you have sufficient disk space for:
- Python dependencies: ~500MB
- Ollama models: 2-8GB per model
- Sample data: ~100MB

## 🎯 Next Steps

After successful installation:

1. **Read the [Quick Start Guide](Quick-Start.md)** to begin using VariancePro
2. **Review [Configuration](Configuration.md)** for customization options
3. **Explore [Usage Guide](Usage-Guide.md)** for detailed features
4. **Check [Analysis Types](Analysis-Types.md)** to understand capabilities

## 📞 Installation Support

If you encounter issues during installation:

1. Check the [Troubleshooting Guide](Troubleshooting.md)
2. Search [GitHub Issues](https://github.com/sharkoil/variancepro/issues)
3. Create a new issue with:
   - Your operating system and version
   - Python version
   - Complete error messages
   - Steps you followed
