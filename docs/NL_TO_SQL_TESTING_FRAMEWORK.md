# 🧪 NL-to-SQL Testing Framework

A comprehensive testing system for evaluating and comparing different natural language to SQL translation strategies.

## 🎯 **Problem Solved**

Your current NL-to-SQL implementation returns generic `SELECT * FROM table` queries without proper WHERE clauses, making it essentially "useless" for targeted data analysis. This framework provides:

1. **Safe testing environment** - Test improvements without breaking production
2. **Strategy comparison** - Compare current vs improved implementations
3. **Quality metrics** - Objective scoring based on SQL quality indicators
4. **Actionable insights** - Clear recommendations for improvement

## 🚀 **Quick Start**

### Option 1: Launch Full App with Testing (Recommended)
```bash
python launch_testing.py
# Choose option 1
```
Then look for the "🧪 NL-to-SQL Testing" tab in your interface.

### Option 2: Standalone Testing Interface
```bash
python test_nl_to_sql_strategies.py --mode standalone
```

### Option 3: Programmatic Demo
```bash
python test_nl_to_sql_strategies.py --mode demo
```

## 🔍 **Available Strategies**

### 🔵 **Current Implementation**
- Your existing `EnhancedNLToSQLTranslator`
- **Problem**: Falls back to `SELECT * FROM table` without WHERE clauses
- **Result**: Returns all rows instead of filtered data

### 🟢 **Strategy 1: LLM-Enhanced Pattern Matching**
- Uses LLM to understand intent and extract conditions
- Systematically builds SQL with proper WHERE clauses
- **Key Features**:
  - Intent analysis via LLM prompting
  - Enhanced column mapping with business terms
  - Pattern-based condition extraction
  - Confidence scoring based on extraction success

### 🟡 **Strategy 2: Advanced Semantic Parsing**
- Sophisticated pattern recognition with context learning
- Learns from data patterns for better mapping
- **Key Features**:
  - Advanced semantic pattern matching
  - Domain-specific vocabulary understanding
  - Context learning and adaptation
  - Conflict resolution for conditions

## 📊 **Testing Features**

### 🧪 **Single Query Test**
Test any query instantly against all three strategies:
```
Query: "Show me sales where region is North"

Results:
- Current: SELECT * FROM data LIMIT 100 (Score: 30/100)
- Strategy 1: SELECT * FROM data WHERE region = 'North' (Score: 85/100)
- Strategy 2: SELECT * FROM data WHERE region = 'North' (Score: 85/100)
```

### ⚖️ **Strategy Comparison**
Side-by-side detailed comparison showing:
- Generated SQL queries
- Confidence scores
- Quality metrics
- Performance timing
- Specific recommendations

### 📈 **Comprehensive Evaluation**
Runs 10+ test queries covering:
- Basic filtering conditions
- Numeric comparisons
- Date/time filtering
- Top N queries  
- Range queries
- Complex multi-condition filters

## 🎯 **Quality Scoring System**

Each strategy is scored on multiple factors:
- **WHERE clause presence** (25 points): Key indicator of filtering capability
- **Specific SELECT statements** (15 points): Avoiding generic `SELECT *`
- **Appropriate aggregations** (15 points): When sum/count/avg is needed
- **Correct LIMIT usage** (10 points): For top N queries
- **Confidence levels** (5 points): Strategy's own confidence assessment
- **Success rate** (30 points): Basic functionality

**Maximum Score: 100 points**

## 📝 **Example Test Results**

```
Query: "Find sales where region is North and actual > 15000"

🔵 Current Implementation:
SQL: SELECT * FROM data LIMIT 100
Score: 30/100
Issue: No WHERE clause, returns all data

🟢 Strategy 1 (LLM-Enhanced):  
SQL: SELECT * FROM data WHERE region = 'North' AND Sales_Actual > 15000
Score: 90/100
Improvement: Proper filtering conditions

🟡 Strategy 2 (Semantic Parsing):
SQL: SELECT * FROM data WHERE region = 'North' AND Sales_Actual > 15000  
Score: 88/100
Improvement: Context-aware column mapping

Recommendation: Switch to Strategy 1 for best WHERE clause generation
```

## 🔧 **Integration Guide**

### Add to Existing Gradio App
```python
from ui.nl_to_sql_testing_integration import add_testing_to_main_app

# After creating your main interface
demo = add_testing_to_main_app(demo, llm_interpreter)
```

### Programmatic Usage
```python
from ui.nl_to_sql_testing_ui import NLToSQLTestingUI

# Initialize testing framework
testing_ui = NLToSQLTestingUI(data_file_path, llm_interpreter)

# Test a single query
result = testing_ui.test_single_query("Show me sales > 15000")

# Access detailed results
scores = result.quality_scores
recommendations = result.recommendations
```

## 📁 **File Structure**

```
analyzers/
├── nl_to_sql_tester.py          # Core testing framework
├── strategy_1_llm_enhanced.py   # LLM-enhanced translator
└── strategy_2_semantic_parsing.py # Semantic parsing translator

ui/
├── nl_to_sql_testing_ui.py      # Gradio testing interface
└── nl_to_sql_testing_integration.py # App integration

test_nl_to_sql_strategies.py     # Standalone launcher
launch_testing.py               # Easy launcher script
```

## 🎪 **Key Improvements Over Current Implementation**

| Feature | Current | Strategy 1 | Strategy 2 |
|---------|---------|------------|------------|
| WHERE Clauses | ❌ Generic fallback | ✅ LLM-guided extraction | ✅ Pattern-based learning |
| Column Mapping | ❌ Basic matching | ✅ Business term mapping | ✅ Semantic similarity |
| Condition Extraction | ❌ Limited patterns | ✅ Intent analysis | ✅ Advanced patterns |
| Confidence Scoring | ⚠️ Basic | ✅ Multi-factor | ✅ Context-aware |
| Learning Capability | ❌ None | ⚠️ Session-based | ✅ Adaptive learning |

## 🚀 **Next Steps**

1. **Test Current State**: Run comprehensive evaluation to see baseline scores
2. **Compare Strategies**: Use side-by-side comparison for specific queries
3. **Choose Best Strategy**: Based on your data patterns and requirements
4. **Implement Gradually**: Test in production with A/B testing approach
5. **Monitor Improvements**: Track query success rates and user satisfaction

## 💡 **Pro Tips**

- **Start with Quick Test**: Use example queries to see immediate differences
- **Focus on WHERE Clauses**: The key problem is lack of filtering conditions
- **Test Your Own Queries**: Use queries from your actual use cases
- **Check Confidence Scores**: Higher confidence often means better results
- **Read Recommendations**: Framework provides specific guidance for improvement

## 🤝 **Support**

If you encounter issues:
1. Check that all dependencies are installed
2. Ensure your data file is accessible
3. Verify LLM interpreter is configured (optional but helpful)
4. Review console output for detailed error messages

The framework is designed to work even without LLM access - Strategy 2 works completely offline!
