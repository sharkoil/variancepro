#!/usr/bin/env python3
"""
Test manual top N prompts functionality
"""

import pandas as pd
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.app_core import AppCore
from handlers.chat_handler import ChatHandler

def test_manual_top_n():
    """Test manual top N prompts in chat handler"""
    print("🔍 Testing manual top N prompts...")
    
    # Create sample data
    sample_data = pd.DataFrame({
        'Name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
        'Revenue': [100000, 85000, 120000, 95000, 110000],
        'Expenses': [30000, 25000, 35000, 28000, 32000],
        'Profit': [70000, 60000, 85000, 67000, 78000]
    })
    
    print("📊 Sample data:")
    print(sample_data.to_string(index=False))
    print()
    
    # Initialize components
    app_core = AppCore()
    app_core.current_data = sample_data
    app_core.data_summary = "Sample data with revenue, expenses, and profit"
    
    chat_handler = ChatHandler(app_core)
    
    # Test different manual prompts
    test_prompts = [
        "top 5",
        "top 3",
        "bottom 5",
        "show me top 10",
        "what are the top 5",
        "give me bottom 3",
        "highest values",
        "lowest values"
    ]
    
    for prompt in test_prompts:
        print(f"🧪 Testing prompt: '{prompt}'")
        try:
            # Test if it's detected as a top/bottom query
            is_top_bottom = chat_handler._is_top_bottom_query(prompt)
            print(f"   Detected as top/bottom: {is_top_bottom}")
            
            if is_top_bottom:
                # Test the top/bottom handler
                result = chat_handler._handle_top_bottom_query(prompt)
                print(f"   Result: {result[:100]}...")
            else:
                # Test full response
                result = chat_handler._generate_response(prompt)
                print(f"   Response: {result[:100]}...")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        print("-" * 50)
    
    print("🎯 Manual top N prompt test complete!")

if __name__ == "__main__":
    test_manual_top_n()
