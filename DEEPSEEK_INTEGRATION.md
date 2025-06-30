# DeepSeek LLM Integration

## Overview
This document describes how to integrate DeepSeek LLM models with VariancePro for enhanced financial analysis capabilities.

## Setup

1. Make sure Ollama is installed and running
2. Pull the DeepSeek model:
   ```
   ollama pull deepseek-coder
   ```

## Configuration

Add the following to your environment configuration:

```python
LLM_MODEL = "deepseek-coder"
LLM_CONTEXT_LENGTH = 16384  # DeepSeek supports longer context
LLM_TEMPERATURE = 0.1       # Lower temperature for more deterministic outputs
```

## Usage Examples

### Financial Data Analysis

```python
from utils.llm_handler import get_llm_response

prompt = """
Analyze the following financial data and identify key variance trends:
{financial_data}

Focus on:
1. Major variances between budget and actuals
2. YoY growth patterns
3. Seasonal trends
"""

response = get_llm_response(prompt, model="deepseek-coder")
```

### Code Generation for Custom Analysis

DeepSeek excels at generating Python code for data analysis tasks:

```python
prompt = """
Generate Python code using pandas to:
1. Load the financial data from 'sales_data.csv'
2. Calculate month-over-month growth rates
3. Identify outliers using IQR method
4. Create visualizations for the top 5 products by revenue
"""

code_response = get_llm_response(prompt, model="deepseek-coder", temperature=0.2)
```

## Benefits over StarCoder

- Improved financial domain knowledge
- Better code generation capabilities
- Longer context window
- Enhanced performance on complex analytical tasks

## Limitations

- Requires more system resources than StarCoder
- May not be optimized for some financial jargon or specialized accounting terms
