# Troubleshooting Guide

Common issues, solutions, and debugging strategies for VariancePro.

## 🚨 Quick Diagnostics

### System Health Check

Run this quick diagnostic to identify common issues:

```bash
# Check Python environment
python --version  # Should be 3.8+

# Verify Ollama service
curl http://localhost:11434/api/tags

# Check required packages
pip list | grep -E "(gradio|pandas|requests|ollama)"

# Memory check
python -c "import psutil; print(f'Available RAM: {psutil.virtual_memory().available // (1024**3)} GB')"

# File permissions
python -c "import tempfile; tempfile.NamedTemporaryFile()"
```

### Application Status

```python
# Run this in Python to check VariancePro status
import requests
import sys
import os

def health_check():
    """Comprehensive health check for VariancePro."""
    
    checks = {}
    
    # 1. Ollama connectivity
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        checks['ollama'] = response.status_code == 200
    except:
        checks['ollama'] = False
    
    # 2. Required modules
    required_modules = ['gradio', 'pandas', 'requests', 'ollama']
    checks['modules'] = all(
        __import__(mod) for mod in required_modules
    )
    
    # 3. Memory availability
    import psutil
    available_gb = psutil.virtual_memory().available // (1024**3)
    checks['memory'] = available_gb >= 2  # At least 2GB
    
    # 4. File system access
    try:
        import tempfile
        with tempfile.NamedTemporaryFile():
            pass
        checks['filesystem'] = True
    except:
        checks['filesystem'] = False
    
    # Report results
    print("VariancePro Health Check Results:")
    print("=" * 40)
    for check, status in checks.items():
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {check.title()}: {'OK' if status else 'FAILED'}")
    
    return all(checks.values())

if __name__ == "__main__":
    health_check()
```

## 🔧 Installation Issues

### Issue: Python Version Incompatibility

**Symptoms:**
- Syntax errors on startup
- Module import failures
- Gradio compatibility issues

**Solution:**
```bash
# Check Python version
python --version

# If < 3.8, install compatible version
# On Windows with Chocolatey:
choco install python --version=3.11.0

# On macOS with Homebrew:
brew install python@3.11

# On Linux:
sudo apt update && sudo apt install python3.11
```

### Issue: Ollama Not Installed

**Symptoms:**
```
ConnectionError: Cannot connect to Ollama service at http://localhost:11434
```

**Solution:**
```bash
# Install Ollama
# Windows/macOS: Download from https://ollama.ai
# Linux:
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
ollama serve

# Install required model
ollama pull llama3.1:8b

# Verify installation
ollama list
```

### Issue: Package Installation Failures

**Symptoms:**
- `ModuleNotFoundError` for gradio, pandas, etc.
- Permission denied errors during pip install

**Solution:**
```bash
# Create virtual environment (recommended)
python -m venv variancepro_env

# Activate virtual environment
# Windows:
variancepro_env\Scripts\activate
# Linux/macOS:
source variancepro_env/bin/activate

# Upgrade pip
python -m pip install --upgrade pip

# Install with specific versions if needed
pip install gradio==4.7.1 pandas==2.1.4 requests==2.31.0

# If permission issues persist:
pip install --user -r requirements.txt
```

### Issue: Port Already in Use

**Symptoms:**
```
OSError: [Errno 98] Address already in use: ('127.0.0.1', 7860)
```

**Solution:**
```bash
# Find process using port 7860
# Windows:
netstat -ano | findstr :7860
taskkill /PID <process_id> /F

# Linux/macOS:
lsof -ti:7860 | xargs kill -9

# Or use different port
export GRADIO_SERVER_PORT=7861
python app.py
```

## 🤖 AI and Model Issues

### Issue: Model Not Found

**Symptoms:**
```
Error: Model 'llama3.1:8b' not found
```

**Solution:**
```bash
# List available models
ollama list

# Pull required model
ollama pull llama3.1:8b

# If model pull fails, try smaller model
ollama pull llama3.1:7b

# Update configuration
export MODEL_NAME="llama3.1:7b"
```

### Issue: Slow AI Responses

**Symptoms:**
- Long delays in chat responses
- Timeout errors
- High CPU usage

**Solution:**

1. **Use smaller model:**
```bash
ollama pull llama3.1:7b
export MODEL_NAME="llama3.1:7b"
```

2. **Optimize model parameters:**
```bash
export MODEL_TIMEOUT="60"
export TEMPERATURE="0.3"
export MAX_CONTEXT_LENGTH="2048"
```

3. **Check system resources:**
```python
import psutil
print(f"CPU Usage: {psutil.cpu_percent()}%")
print(f"Memory Usage: {psutil.virtual_memory().percent}%")
```

### Issue: AI Responses Too Generic

**Symptoms:**
- Vague or unhelpful analysis
- Missing business context
- No specific insights

**Solution:**

1. **Improve query specificity:**
```
❌ "Analyze my data"
✅ "Show variance analysis for Q3 sales by region with explanations for negative variances"
```

2. **Provide more context:**
```
"I'm analyzing retail sales data. Show top 5 underperforming products and suggest reasons for the decline."
```

3. **Adjust model parameters:**
```bash
export TEMPERATURE="0.5"  # More creative responses
export TOP_P="0.9"        # More diverse vocabulary
```

## 📊 Data Processing Issues

### Issue: CSV Upload Failures

**Symptoms:**
- File upload errors
- "Invalid file format" messages
- Data not displaying correctly

**Solution:**

1. **Check file format:**
```python
import pandas as pd

# Test file loading
try:
    df = pd.read_csv('your_file.csv')
    print(f"Loaded {len(df)} rows, {len(df.columns)} columns")
    print(f"Columns: {list(df.columns)}")
except Exception as e:
    print(f"Error: {e}")
```

2. **Common file issues:**
```bash
# Check file encoding
file -i your_file.csv

# Convert encoding if needed
iconv -f ISO-8859-1 -t UTF-8 your_file.csv > your_file_utf8.csv

# Check for special characters
head -n 5 your_file.csv
```

3. **File size limits:**
```bash
# Check file size
ls -lh your_file.csv

# If too large, split file
split -l 50000 your_file.csv your_file_part_
```

### Issue: Memory Errors with Large Files

**Symptoms:**
```
MemoryError: Unable to allocate array
OutOfMemoryError: Cannot load file
```

**Solution:**

1. **Increase memory limits:**
```bash
export MEMORY_LIMIT_GB="8"
export MAX_ROWS="2000000"
```

2. **Optimize data processing:**
```python
# Use chunked reading for large files
def load_large_csv(filepath):
    chunks = []
    for chunk in pd.read_csv(filepath, chunksize=10000):
        # Process chunk
        chunks.append(chunk)
    return pd.concat(chunks, ignore_index=True)
```

3. **Pre-process large files:**
```bash
# Sample large files
head -n 100000 large_file.csv > sample_file.csv

# Remove unnecessary columns
cut -d',' -f1,2,3,5,7 large_file.csv > reduced_file.csv
```

### Issue: Date Column Recognition

**Symptoms:**
- Dates treated as text
- Timescale analysis not working
- "No date columns found" errors

**Solution:**

1. **Check date formats:**
```python
import pandas as pd

# Load and inspect dates
df = pd.read_csv('your_file.csv')
date_columns = df.select_dtypes(include=['object']).columns

for col in date_columns:
    print(f"Column {col} sample values:")
    print(df[col].head())
    
    # Try to parse dates
    try:
        pd.to_datetime(df[col])
        print(f"✅ {col} can be parsed as dates")
    except:
        print(f"❌ {col} cannot be parsed as dates")
```

2. **Standard date formats:**
```
✅ Supported formats:
- 2024-01-15
- 01/15/2024
- 15-Jan-2024
- 2024-01-15 10:30:00
- January 15, 2024

❌ Problematic formats:
- 15/13/2024 (invalid month)
- 2024-1-1 (inconsistent padding)
- "Quarter 1 2024" (text)
```

3. **Manual date conversion:**
```python
# Convert custom date formats
df['date_column'] = pd.to_datetime(df['date_column'], format='%d/%m/%Y')
```

## 🔍 Query and Analysis Issues

### Issue: SQL Translation Errors

**Symptoms:**
- "Could not translate query to SQL"
- Incorrect SQL generation
- Empty results from valid questions

**Solution:**

1. **Improve query phrasing:**
```
❌ "Show me stuff about sales"
✅ "Show total sales by region"

❌ "What happened?"
✅ "Compare actual vs budget sales for Q3"
```

2. **Use explicit column names:**
```
❌ "Show performance"
✅ "Show sales performance by product_name"
```

3. **Debug SQL translation:**
```python
from analyzers.nl_to_sql_translator import NLToSQLTranslator

translator = NLToSQLTranslator()
result = translator.translate_to_sql("your query here", dataframe)
print(f"Generated SQL: {result.sql}")
print(f"Confidence: {result.confidence}")
print(f"Explanation: {result.explanation}")
```

### Issue: Analysis Results Don't Make Sense

**Symptoms:**
- Unexpected variance calculations
- Incorrect trend analysis
- Misleading insights

**Solution:**

1. **Verify data quality:**
```python
# Check for data issues
print("Data shape:", df.shape)
print("Null values:", df.isnull().sum())
print("Data types:", df.dtypes)
print("Numeric columns stats:", df.describe())

# Check for duplicates
print("Duplicates:", df.duplicated().sum())

# Check for outliers
numeric_cols = df.select_dtypes(include=['number']).columns
for col in numeric_cols:
    q1, q3 = df[col].quantile([0.25, 0.75])
    iqr = q3 - q1
    outliers = ((df[col] < q1 - 1.5*iqr) | (df[col] > q3 + 1.5*iqr)).sum()
    print(f"Outliers in {col}: {outliers}")
```

2. **Validate business logic:**
```python
# Check variance calculation
df['manual_variance'] = df['actual'] - df['budget']
df['manual_variance_pct'] = (df['actual'] - df['budget']) / df['budget'] * 100

# Compare with system calculation
print("Manual variance sample:", df['manual_variance'].head())
```

3. **Review analysis parameters:**
```bash
# Adjust analysis sensitivity
export VARIANCE_TOLERANCE="0.05"  # 5% tolerance
export MATERIALITY_THRESHOLD="500"  # Lower threshold
export SIGNIFICANCE_THRESHOLD="0.01"  # More sensitive
```

## 🔧 Performance Issues

### Issue: Slow Application Startup

**Symptoms:**
- Long delay before UI appears
- "Loading..." screens persist
- Timeout errors

**Solution:**

1. **Check model loading:**
```bash
# Pre-load model
ollama run llama3.1:8b "Hello"

# Monitor model loading time
time ollama run llama3.1:8b "test"
```

2. **Optimize startup configuration:**
```bash
export DEBUG_MODE="False"
export ENABLE_PROFILING="False"
export LOG_LEVEL="WARNING"
```

3. **Monitor startup process:**
```python
import time
import logging

# Add timing logs to identify bottlenecks
start_time = time.time()
# ... initialization code ...
print(f"Component loaded in {time.time() - start_time:.2f}s")
```

### Issue: High Memory Usage

**Symptoms:**
- System becoming unresponsive
- Out of memory errors
- Slow query performance

**Solution:**

1. **Monitor memory usage:**
```python
import psutil
import gc

def memory_usage():
    process = psutil.Process()
    return process.memory_info().rss / (1024**3)  # GB

print(f"Current memory usage: {memory_usage():.2f} GB")

# Force garbage collection
gc.collect()
print(f"After cleanup: {memory_usage():.2f} GB")
```

2. **Optimize settings:**
```bash
export MAX_ROWS="500000"
export MEMORY_LIMIT_GB="4"
export ENABLE_QUERY_CACHE="True"
export CACHE_TTL_SECONDS="1800"  # 30 minutes
```

3. **Clear session data:**
```python
# In the application, periodically clear data
if len(session_data) > 100:
    session_data = session_data[-50:]  # Keep only recent entries
```

## 🔒 Security and Privacy Issues

### Issue: Unauthorized Access

**Symptoms:**
- Unexpected users accessing the interface
- Security warnings
- Suspicious activity logs

**Solution:**

1. **Enable authentication:**
```bash
export GRADIO_USERNAME="admin"
export GRADIO_PASSWORD="secure_password_123!"
export GRADIO_SHARE="False"
```

2. **Restrict network access:**
```bash
export GRADIO_SERVER_NAME="127.0.0.1"  # Localhost only
# or
export GRADIO_SERVER_NAME="0.0.0.0"    # Specific interface
```

3. **Monitor access logs:**
```python
import logging

# Configure access logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('access.log'),
        logging.StreamHandler()
    ]
)
```

### Issue: Data Privacy Concerns

**Symptoms:**
- Uncertainty about data handling
- Compliance requirements
- External data transmission fears

**Solution:**

1. **Verify zero-trust mode:**
```bash
export ZERO_TRUST_MODE="True"
export LOG_USER_QUERIES="False"
export PERSIST_SESSION_DATA="False"
```

2. **Network isolation verification:**
```bash
# Verify no external connections
netstat -an | grep ESTABLISHED
# Should only show localhost connections

# Check firewall rules
# Windows:
netsh advfirewall firewall show rule name=all | findstr VariancePro
# Linux:
iptables -L | grep variancepro
```

3. **Data cleanup verification:**
```python
# Verify data cleanup
import os
import tempfile

temp_dir = tempfile.gettempdir()
temp_files = [f for f in os.listdir(temp_dir) if 'variancepro' in f.lower()]
print(f"Temporary files: {temp_files}")
```

## 📞 Getting Help

### Enable Debug Mode

For detailed troubleshooting, enable debug mode:

```bash
export DEBUG_MODE="True"
export LOG_LEVEL="DEBUG"
export GRADIO_DEBUG="True"
export ENABLE_PROFILING="True"
```

### Collect Diagnostic Information

```python
def collect_diagnostics():
    """Collect system information for troubleshooting."""
    
    import platform
    import sys
    import psutil
    import pkg_resources
    
    info = {
        'system': {
            'platform': platform.platform(),
            'python_version': sys.version,
            'cpu_count': psutil.cpu_count(),
            'memory_gb': psutil.virtual_memory().total // (1024**3)
        },
        'packages': {
            pkg.project_name: pkg.version 
            for pkg in pkg_resources.working_set
        },
        'environment': {
            key: value for key, value in os.environ.items()
            if 'VARIANCEPRO' in key or 'OLLAMA' in key or 'GRADIO' in key
        }
    }
    
    return info

# Save diagnostic information
import json
with open('diagnostics.json', 'w') as f:
    json.dump(collect_diagnostics(), f, indent=2)
```

### Contact Information

- **GitHub Issues**: [Report bugs and request features](https://github.com/yourusername/variancepro/issues)
- **Documentation**: Check the wiki for additional guides
- **Community**: Join discussions in GitHub Discussions

### Before Reporting Issues

1. **Check this troubleshooting guide**
2. **Run the health check script**
3. **Collect diagnostic information**
4. **Try minimal reproduction steps**
5. **Include error logs and configuration**

---

This troubleshooting guide covers the most common issues. For complex problems, the diagnostic tools and debug modes will provide additional insights for resolution.
