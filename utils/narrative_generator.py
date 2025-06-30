import pandas as pd
import numpy as np
import requests
import json
from typing import Optional, Dict, Any

def generate_narrative_response(analysis_data: str) -> str:
    """
    Generate a narrative response from the financial analysis data using an LLM.
    
    Args:
        analysis_data: String containing the automatic analysis from TimescaleAnalyzer
        
    Returns:
        str: Narrative response from the LLM
    """
    # System prompt for Aria Sterling financial analyst persona
    system_prompt = """You are **Aria Sterling**, a world-class financial analyst and strategist. You possess exceptional quantitative reasoning, market intuition, and business acumen. You analyze financial data with precision, distill market signals into actionable insights, and communicate with clarity, confidence, and charisma.

### 🎯 Core Attributes
- **Brilliant and Analytical**: Expert in time series analysis, financial forecasting, valuation, corporate finance, and macroeconomic interpretation.
- **Data-Driven**: Extracts insights from raw data using rigorous statistical and financial techniques. You speak in ratios, deltas, time horizons, and benchmarks.
- **Fluent in Market Language**: Speaks in sharp, well-structured financial commentary—think investor calls, analyst briefings, earnings breakdowns, pitch decks.
- **Human-Centric Communicator**: Makes complex concepts accessible to both CFOs and startup founders. Adjusts tone and vocabulary based on audience's financial fluency.
- **Forward-Looking**: Scans for inflection points, tailwinds/headwinds, and market signals that influence KPIs and company valuations.

### 🧠 Knowledge Domains
- Financial statements, KPIs, profitability analysis
- Forecasting, TTM, YoY, QoQ analysis
- Time series analysis and growth metrics (CAGR, MoM, rolling averages)
- Corporate strategy, M&A basics, capital structure
- Industry benchmarking and competitive analysis
- Equities, credit markets, macroeconomic indicators

### 💬 Communication Style
- Sharp, credible, and confident—yet approachable.
- Speaks in terms like "overdelivered by 14.2%," "driven by margin expansion," or "growth decelerating at a 3-month rolling rate."
- Capable of switching tones: quick elevator pitch, deep-dive analysis, or executive summary."""

    # Check if Ollama is running locally
    try:
        ollama_url = "http://localhost:11434"
        response = requests.get(f"{ollama_url}/api/tags", timeout=5)
        if response.status_code == 200:
            return generate_response_ollama(system_prompt, analysis_data)
    except:
        pass
    
    # Fallback to a pre-generated response if no LLM is available
    return generate_fallback_narrative(analysis_data)

def generate_response_ollama(system_prompt: str, analysis_data: str) -> str:
    """Generate response using Ollama"""
    try:
        # Create a prompt that includes the system instructions and the analysis data
        prompt = f"{system_prompt}\n\n### Financial Analysis Data\n{analysis_data}\n\nBased on this financial data, provide a brief, engaging introduction as Aria Sterling to start a conversation with the user. Focus on the most interesting insights from the data, express it in your characteristic analytical style, and invite the user to ask questions about their financial data."
        
        # Query an available model (will use deepseek-coder or another available model)
        payload = {
            "model": "deepseek-coder:6.7b",  # Can be replaced with any available model
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "num_predict": 1024
            }
        }
        
        response = requests.post(
            "http://localhost:11434/api/generate",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json().get("response", "").strip()
        else:
            # Fallback if the request fails
            return generate_fallback_narrative(analysis_data)
            
    except Exception as e:
        # Fallback if any error occurs
        return generate_fallback_narrative(analysis_data)

def generate_fallback_narrative(analysis_data: str) -> str:
    """Generate a fallback narrative response without an LLM"""
    
    # Extract some key points from the analysis_data
    has_yearly = "Year-over-Year" in analysis_data
    has_quarterly = "Quarter-over-Quarter" in analysis_data
    has_monthly = "Month-over-Month" in analysis_data
    
    # Check for growth or decline patterns
    growth_indicated = "growth" in analysis_data.lower() or "increased" in analysis_data.lower() or "increase" in analysis_data.lower()
    decline_indicated = "decline" in analysis_data.lower() or "decreased" in analysis_data.lower() or "decrease" in analysis_data.lower()
    
    # Generate appropriate narrative
    greeting = "👋 **Hello, I'm Aria Sterling, your financial analyst.**"
    
    if "Automatic Timescale Analysis" in analysis_data:
        intro = "\n\nI've conducted an initial review of your financial data, and there are some fascinating patterns emerging."
    else:
        intro = "\n\nI'd be delighted to analyze your financial data. Once you upload your CSV file, I'll provide detailed insights tailored to your specific metrics."
    
    if has_yearly or has_quarterly or has_monthly:
        time_analysis = "\n\nYour dataset contains valuable time series information that reveals"
        
        if growth_indicated and decline_indicated:
            time_analysis += " mixed performance signals across different periods and metrics."
        elif growth_indicated:
            time_analysis += " generally positive momentum in key performance indicators."
        elif decline_indicated:
            time_analysis += " some concerning downward trends that warrant further investigation."
        else:
            time_analysis += " interesting temporal patterns worth exploring in detail."
    else:
        time_analysis = "\n\nTime-based analysis will be available once you upload data with clear date or period columns."
    
    call_to_action = "\n\n**What specific aspects of your financial data would you like me to analyze?** I can examine period-over-period changes, identify growth drivers, highlight anomalies, or generate forecasts based on historical patterns."
    
    signature = "\n\n*— Aria Sterling, Financial Analyst*"
    
    return greeting + intro + time_analysis + call_to_action + signature

# Function to integrate with the main application
def add_narrative_to_app(app_instance):
    """
    Add the narrative generation capability to the VariancePro app.
    
    Args:
        app_instance: The main app instance
    """
    # Store the original method
    original_timescale_analysis = app_instance.timescale_analyzer.generate_timescale_analysis
    
    # Create a wrapper function that adds narrative
    def enhanced_timescale_analysis(df):
        # Get the original analysis
        analysis_text = original_timescale_analysis(df)
        
        # Generate narrative
        narrative = generate_narrative_response(analysis_text)
        
        # Combine with original analysis
        return narrative + "\n\n---\n\n" + analysis_text
    
    # Replace the original method with the enhanced one
    app_instance.timescale_analyzer.generate_timescale_analysis = enhanced_timescale_analysis
