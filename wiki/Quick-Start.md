# Quick Start Guide

Get VariancePro running in minutes with this streamlined guide.

## ⚡ Launch Applications

### Main Application
```bash
# Start the main VariancePro application
python app_new.py

# Alternative methods
python app.py
start_app.bat  # Windows batch launcher
```

**Access**: `http://localhost:7871`

### Testing Framework (Optional)
```bash
# Start the Enhanced NL-to-SQL Testing Framework
python test_enhanced_nl_to_sql_ui.py

# Alternative direct launch
python -c "from nl_to_sql_testing_ui_enhanced import EnhancedNLToSQLTestingUI; EnhancedNLToSQLTestingUI().launch()"
```

**Access**: `http://localhost:7862`

## 📊 Your First Analysis

### 1. Upload Data
1. Open VariancePro in your browser: `http://localhost:7871`
2. Click **"Upload CSV File"**
3. Select your financial data file
4. Wait for automatic column detection

### 2. Review Field Mapping
- The system automatically analyzes your data structure
- Review suggested column mappings in the **Field Picker** section
- Adjust mappings if needed

### 3. Start Analyzing
Once data is loaded, the chat interface becomes active. Try these example queries:

#### Basic Queries
```
"Show me the top 10 products by sales"
"What are our revenue trends this quarter?"
"Compare budget vs actual performance"
```

#### Advanced Queries
```
"Generate an executive summary of Q3 performance"
"Analyze variance and explain external factors"
"Which regions are underperforming and why?"
```

## 🎯 Key Features to Try

### AI-Powered Analysis
- Chat naturally with your data using the AI interface
- Get executive summaries with expandable details
- Receive actionable insights and recommendations

### Market Intelligence
- Automatic news correlation with your data patterns
- Geographic and industry-specific market context
- Real-time business intelligence integration

### Multiple Analysis Types
- **Contribution Analysis**: Find your 80/20 drivers
- **Variance Analysis**: Budget vs actual comparisons
- **Timescale Analysis**: Trend and pattern recognition
- **Ranking Analysis**: Top/bottom performers

## 📋 Sample Data

If you don't have data ready, VariancePro includes sample datasets:

```bash
# Use sample data files
sample_data/comprehensive_sales_data.csv
sample_data/sales_budget_actuals.csv
sample_data/sample_variance_data.csv
```

## 🧪 Test the NL-to-SQL Framework

The testing framework lets you experiment with natural language queries:

### 1. Launch Testing Interface
```bash
python test_enhanced_nl_to_sql_ui.py
```

### 2. Upload Test Data
- Use any CSV file or the provided sample data
- Framework automatically detects column structure

### 3. Try Natural Language Queries
```
"Show me sales where region is North"
"Find records where actual sales > 15000"
"Get data for Q1 2024"
"Show top 3 regions by sales"
```

### 4. Compare Translation Strategies
- Test multiple AI models (if available)
- Compare LLM Enhanced vs Semantic Parsing
- View quality scores and performance metrics

## ⚙️ Quick Configuration

### Change Default Ports
```bash
# Main application
python app_new.py --port 7872

# Testing framework
# Edit test_enhanced_nl_to_sql_ui.py line with server_port=7863
```

### Select Different AI Model
```bash
# Check available models
ollama list

# In the testing framework UI:
# Use the model dropdown to switch between available models
```

## 🔍 Verify Everything Works

### Health Checks
```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# Validate framework syntax
python validate_nl_to_sql_syntax.py

# Test basic functionality
python test_framework_basic.py
```

### Expected Results
- ✅ Main app loads at `http://localhost:7871`
- ✅ Testing framework loads at `http://localhost:7862`
- ✅ File upload works without errors
- ✅ AI chat responds to queries
- ✅ Analysis results display properly

## 🚨 Quick Troubleshooting

### App Won't Start
```bash
# Check Python version
python --version  # Should be 3.8+

# Verify dependencies
pip install -r requirements.txt

# Check ports
netstat -an | findstr :7871  # Windows
lsof -i :7871                # macOS/Linux
```

### Ollama Issues
```bash
# Start Ollama service
ollama serve

# Pull required model
ollama pull gemma3:latest
```

### Import Errors
```bash
# Reinstall dependencies
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

## 🎯 Next Steps

Once you have VariancePro running:

1. **Explore [Analysis Types](Analysis-Types.md)** - Understand different analysis capabilities
2. **Read [Usage Guide](Usage-Guide.md)** - Comprehensive feature documentation  
3. **Try [Analysis Examples](Analysis-Examples.md)** - Real-world scenarios
4. **Review [Best Practices](Best-Practices.md)** - Optimize your workflow

## 💡 Pro Tips

- **Start with simple queries** before trying complex analysis
- **Use sample data** to familiarize yourself with features
- **Check the AI chat history** to build on previous questions
- **Export results** for further analysis or reporting
- **Experiment with different models** in the testing framework

---

**🎉 Congratulations!** You're now ready to transform your financial data into strategic intelligence with VariancePro.
