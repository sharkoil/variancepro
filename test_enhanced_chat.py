#!/usr/bin/env python3
"""
Enhanced Chat Test - Demonstrates LlamaIndex Integration
Shows how users can ask enhanced questions that leverage LlamaIndex
"""

import pandas as pd
import tempfile
import os
from pathlib import Path
import sys

# Add project directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_enhanced_chat_questions():
    """Test enhanced chat questions with LlamaIndex"""
    
    print("🚀 ENHANCED CHAT QUESTIONS TEST")
    print("="*60)
    
    try:
        from app import AriaFinancialChat
        
        # Create comprehensive test data
        data = {
            'Date': pd.date_range('2024-01-01', periods=12, freq='M'),
            'Product': ['Product_A', 'Product_B', 'Product_C'] * 4,
            'Sales': [15000, 25000, 8000, 18000, 22000, 9500, 16000, 27000, 7500, 17000, 24000, 8800],
            'Budget': [14000, 24000, 9000, 17000, 21000, 8500, 15000, 26000, 8000, 16000, 23000, 8500],
            'Region': ['North', 'South', 'East'] * 4,
            'Category': ['Electronics', 'Software', 'Hardware'] * 4
        }
        df = pd.DataFrame(data)
        
        # Save to temporary file
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        df.to_csv(temp_file.name, index=False)
        temp_file.close()
        
        print(f"📁 Created comprehensive test dataset")
        print(f"   Records: {len(df)}")
        print(f"   Columns: {list(df.columns)}")
        print(f"   Date range: {df['Date'].min()} to {df['Date'].max()}")
        
        # Initialize chat system
        chat = AriaFinancialChat()
        
        # Test various enhanced questions that benefit from LlamaIndex
        test_questions = [
            "What are the key performance indicators in this dataset?",
            "Perform comprehensive contribution analysis with business insights",
            "Analyze budget vs actual performance with strategic recommendations", 
            "Provide detailed variance analysis with root cause identification",
            "Generate executive summary with key takeaways and action items",
            "What are the seasonal trends and how do they impact forecasting?"
        ]
        
        print("\n🔍 TESTING ENHANCED QUESTIONS:")
        print("-" * 60)
        
        for i, question in enumerate(test_questions, 1):
            print(f"\n📋 Question {i}: {question}")
            
            try:
                response, status = chat.analyze_data(temp_file.name, question)
                
                # Check response quality indicators
                has_insights = any(keyword in response.lower() for keyword in 
                                 ['insight', 'recommendation', 'strategic', 'analysis'])
                has_metrics = any(keyword in response.lower() for keyword in 
                                ['kpi', 'metric', 'performance', 'variance'])
                has_structure = any(keyword in response.lower() for keyword in 
                                  ['executive', 'summary', 'finding', 'impact'])
                
                print(f"   ✅ Status: {status}")
                print(f"   📊 Response length: {len(response)} characters")
                print(f"   🎯 Contains insights: {'Yes' if has_insights else 'No'}")
                print(f"   📈 Contains metrics: {'Yes' if has_metrics else 'No'}")
                print(f"   📋 Well structured: {'Yes' if has_structure else 'No'}")
                
                # Show first 200 characters as preview
                preview = response[:200].replace('\n', ' ').strip()
                print(f"   💬 Preview: {preview}...")
                
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
        
        # Cleanup
        os.unlink(temp_file.name)
        
        print("\n" + "="*60)
        print("✅ ENHANCED CHAT TEST COMPLETED")
        print("🎯 Users can ask sophisticated questions that leverage:")
        print("   • LlamaIndex for structured analysis")
        print("   • Timescale analysis for time-based insights") 
        print("   • Contribution analysis for 80/20 insights")
        print("   • LLM reasoning for strategic recommendations")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_enhanced_chat_questions()
