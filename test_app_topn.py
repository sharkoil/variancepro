#!/usr/bin/env python3
"""
Test the actual application with improved top N functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_app_with_sample_data():
    """Test with sample data that mirrors the application"""
    print("🔍 Testing Quant Commander with sample data...")
    
    try:
        from app_v2 import QuantCommanderApp
        import pandas as pd
        
        # Initialize the app
        app = QuantCommanderApp()
        
        # Create sample data similar to the screenshot
        sample_data = pd.DataFrame({
            'Date': ['2023-12-30', '2023-12-28', '2023-12-27', '2023-12-26', '2023-12-25'],
            'Budget': [234000, 232000, 230000, 228000, 226000],
            'Actual': [230600, 228400, 226200, 224000, 221800],
            'Product': ['Product_D', 'Product_D', 'Product_C', 'Product_B', 'Product_A'],
            'Category': ['Electronics', 'Electronics', 'Electronics', 'Electronics', 'Electronics'],
            'State': ['Washington', 'Florida', 'California', 'Texas', 'New York'],
            'Type': ['Direct', 'Direct', 'Direct', 'Direct', 'Direct'],
            'Margin': [0.22, 0.21, 0.20, 0.19, 0.18],
            'variance': [-3400, -3600, -3800, -4000, -4200],
            'variance_pct': [-1.45299, -1.55172, -1.65789, -1.75439, -1.85263]
        })
        
        # Set the data in the app
        app.app_core.current_data = sample_data
        app.app_core.data_summary = "Budget vs Actual quantitative analysis"
        
        print("✅ App initialized with sample data")
        print(f"📊 Data shape: {sample_data.shape}")
        print(f"📋 Columns: {list(sample_data.columns)}")
        
        # Test the queries that were failing
        test_queries = [
            "top 5 by State",
            "top 2 by Budget",
            "bottom 2 analysis"
        ]
        
        print("\n🧪 Testing queries through chat handler:")
        for query in test_queries:
            print(f"\n📝 Query: '{query}'")
            try:
                # Test the chat handler process
                history = []
                updated_history, _ = app.chat_handler.process_message(query, history)
                
                if updated_history:
                    last_response = updated_history[-1]['content']
                    print(f"✅ Response: {last_response[:200]}...")
                else:
                    print("❌ No response generated")
                    
            except Exception as e:
                print(f"❌ Error: {e}")
        
        print("\n🎯 Application test complete!")
        
    except Exception as e:
        print(f"❌ Error initializing app: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_app_with_sample_data()
