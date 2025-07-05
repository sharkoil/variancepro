"""
Demo script for NL-to-SQL Testing Framework
Shows how to use the testing framework independently or with your main app
"""

import sys
import os
import pandas as pd

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.nl_to_sql_testing_ui import NLToSQLTestingUI
from ai.llm_interpreter import LLMInterpreter
import gradio as gr


def create_standalone_testing_app():
    """
    Create a standalone testing application
    Run this to test NL-to-SQL strategies independently
    """
    
    print("🧪 Initializing NL-to-SQL Testing Framework...")
    
    # Initialize LLM interpreter (optional - will work without it)
    llm_interpreter = None
    try:
        from config.settings import OLLAMA_BASE_URL, OLLAMA_MODEL
        llm_interpreter = LLMInterpreter(
            base_url=OLLAMA_BASE_URL,
            model_name=OLLAMA_MODEL
        )
        print("✅ LLM Interpreter initialized")
    except Exception as e:
        print(f"⚠️ LLM Interpreter not available: {e}")
        print("   (Testing will work with reduced Strategy 1 functionality)")
    
    # Find data file
    data_file_paths = [
        "sample_variance_data.csv",
        "sample_data/sample_variance_data.csv", 
        "sample_data/comprehensive_sales_data.csv"
    ]
    
    data_file_path = None
    for path in data_file_paths:
        if os.path.exists(path):
            data_file_path = path
            print(f"📊 Using data file: {path}")
            break
    
    if not data_file_path:
        print("📊 No data file found, using sample data")
    
    # Initialize testing UI
    testing_ui = NLToSQLTestingUI(data_file_path, llm_interpreter)
    
    # Create the interface
    interface = testing_ui.create_testing_interface()
    
    print("🚀 Testing framework ready!")
    print("\n" + "="*60)
    print("🧪 NL-TO-SQL TESTING FRAMEWORK")
    print("="*60)
    print("Test and compare different strategies for converting")
    print("natural language to SQL queries.")
    print("")
    print("🎯 Features:")
    print("  • Single query testing")
    print("  • Side-by-side strategy comparison") 
    print("  • Comprehensive evaluation suite")
    print("  • Data schema exploration")
    print("")
    print("🔗 The interface will open in your browser...")
    print("="*60)
    
    return interface


def demonstrate_programmatic_usage():
    """
    Demonstrate how to use the testing framework programmatically
    """
    
    print("\n🔬 Demonstrating Programmatic Usage...")
    
    # Initialize with sample data
    testing_ui = NLToSQLTestingUI()
    
    # Test a single query
    test_query = "Show me sales where region is North"
    print(f"\n📝 Testing query: '{test_query}'")
    
    try:
        result = testing_ui.test_single_query(test_query)
        print("✅ Test completed successfully!")
        
        # You can access individual results
        if hasattr(testing_ui.tester, 'test_single_query'):
            detailed_result = testing_ui.tester.test_single_query(test_query)
            
            print(f"\n📊 Quality Scores:")
            print(f"  Current: {detailed_result.quality_scores['current']:.1f}/100")
            print(f"  Strategy 1: {detailed_result.quality_scores['strategy_1']:.1f}/100") 
            print(f"  Strategy 2: {detailed_result.quality_scores['strategy_2']:.1f}/100")
            
            print(f"\n🎯 Recommendations:")
            for rec in detailed_result.recommendations[:3]:
                print(f"  • {rec}")
                
    except Exception as e:
        print(f"❌ Test failed: {e}")


def integrate_with_existing_app_example():
    """
    Example of how to integrate with your existing app
    """
    
    print("\n🔗 Integration Example...")
    print("""
To add testing to your existing app, add this to your app.py:

```python
from ui.nl_to_sql_testing_integration import add_testing_to_main_app

# After creating your main Gradio interface
demo = add_testing_to_main_app(demo, llm_interpreter)
```

This will add a new '🧪 NL-to-SQL Testing' tab to your existing interface.
""")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="NL-to-SQL Testing Framework Demo")
    parser.add_argument(
        "--mode", 
        choices=["standalone", "demo", "integration"], 
        default="standalone",
        help="Run mode: standalone UI, programmatic demo, or show integration example"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=7860,
        help="Port for Gradio interface (default: 7860)"
    )
    parser.add_argument(
        "--share", 
        action="store_true",
        help="Create public Gradio link"
    )
    
    args = parser.parse_args()
    
    if args.mode == "standalone":
        # Create and launch standalone testing app
        interface = create_standalone_testing_app()
        interface.launch(
            server_port=args.port,
            share=args.share,
            inbrowser=True
        )
        
    elif args.mode == "demo":
        # Run programmatic demonstration
        demonstrate_programmatic_usage()
        
    elif args.mode == "integration":
        # Show integration example
        integrate_with_existing_app_example()
    
    print("\n✅ Demo completed!")
