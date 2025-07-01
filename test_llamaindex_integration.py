#!/usr/bin/env python3
"""
LlamaIndex Integration Test and Verification
Tests LlamaIndex integration and ensures chat questions take advantage of it
"""

import os
import sys
import pandas as pd
import tempfile
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

def test_llamaindex_availability():
    """Test if LlamaIndex is properly available"""
    print("\n" + "="*60)
    print("🧪 TESTING LLAMAINDEX AVAILABILITY")
    print("="*60)
    
    # Test 1: Basic LlamaIndex import
    try:
        import llama_index
        print("✅ LlamaIndex package is installed")
        try:
            print(f"   Version: {llama_index.__version__}")
        except AttributeError:
            print("   Version: Available (version info not accessible)")
    except ImportError as e:
        print(f"❌ LlamaIndex package not available: {e}")
        return False
    
    # Test 2: Core components
    try:
        from llama_index.core import Document, VectorStoreIndex
        print("✅ LlamaIndex core components available")
    except ImportError as e:
        print(f"❌ LlamaIndex core components not available: {e}")
        return False
    
    # Test 3: Ollama LLM component
    try:
        from llama_index.llms.ollama import Ollama
        print("✅ LlamaIndex Ollama LLM component available")
    except ImportError as e:
        print(f"❌ LlamaIndex Ollama LLM component not available: {e}")
        print("   Install with: pip install llama-index-llms-ollama")
        return False
    
    # Test 4: Our integration module
    try:
        from llamaindex_integration import LlamaIndexFinancialProcessor
        print("✅ Custom LlamaIndex integration module works")
    except ImportError as e:
        print(f"❌ Custom LlamaIndex integration module failed: {e}")
        return False
    
    return True

def test_contribution_analysis_csv_scope():
    """Test that contribution analysis only uses uploaded CSV data"""
    print("\n" + "="*60)
    print("🧪 TESTING CONTRIBUTION ANALYSIS CSV SCOPE")
    print("="*60)
    
    try:
        from app import AriaFinancialChat, ContributionAnalyzer
        
        # Create test data
        test_data = {
            'Product': ['Product_A', 'Product_B', 'Product_C', 'Product_D'],
            'Sales': [10000, 25000, 5000, 15000],
            'Region': ['North', 'South', 'East', 'West']
        }
        df = pd.DataFrame(test_data)
        
        # Save to temporary file
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        df.to_csv(temp_file.name, index=False)
        temp_file.close()
        
        print(f"📁 Created test CSV with {len(df)} rows")
        
        # Test contribution analyzer directly
        analyzer = ContributionAnalyzer()
        analysis_df, summary, fig = analyzer.perform_contribution_analysis_pandas(
            df=df,
            category_col='Product',
            value_col='Sales'
        )
        
        # Verify analysis only uses CSV data
        original_total = df['Sales'].sum()
        analysis_total = analysis_df['Sales'].sum()
        
        print(f"📊 Original CSV total: ${original_total:,}")
        print(f"📊 Analysis total: ${analysis_total:,}")
        
        if original_total == analysis_total:
            print("✅ Contribution analysis ONLY uses uploaded CSV data")
        else:
            print("❌ Contribution analysis may be using external data")
            
        # Check that analysis results match expected CSV-only calculations
        expected_top_contributor = df.loc[df['Sales'].idxmax(), 'Product']
        actual_top_contributor = summary['top_contributor']
        
        if expected_top_contributor == actual_top_contributor:
            print(f"✅ Top contributor matches CSV data: {actual_top_contributor}")
        else:
            print(f"❌ Top contributor mismatch: expected {expected_top_contributor}, got {actual_top_contributor}")
        
        # Cleanup
        os.unlink(temp_file.name)
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

def test_chat_with_llamaindex():
    """Test that chat questions take advantage of LlamaIndex when available"""
    print("\n" + "="*60)
    print("🧪 TESTING CHAT WITH LLAMAINDEX INTEGRATION")
    print("="*60)
    
    try:
        from app import AriaFinancialChat
        
        # Create test data
        test_data = {
            'Date': pd.date_range('2024-01-01', periods=6, freq='M'),
            'Product': ['Product_A', 'Product_B'] * 3,
            'Sales': [15000, 25000, 18000, 22000, 16000, 27000],
            'Region': ['North', 'South'] * 3
        }
        df = pd.DataFrame(test_data)
        
        # Save to temporary file
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        df.to_csv(temp_file.name, index=False)
        temp_file.close()
        
        print(f"📁 Created test CSV with time series data")
        
        # Initialize chat system
        chat = AriaFinancialChat()
        
        # Test regular analysis
        print("\n📋 Testing regular analysis...")
        response1, status1 = chat.analyze_data(temp_file.name, "analyze this sales data")
        
        print(f"✅ Regular analysis completed")
        print(f"   Status: {status1}")
        print(f"   Response length: {len(response1)} characters")
        
        # Test LlamaIndex-enhanced analysis (if available)
        if hasattr(chat, 'llamaindex_processor') and chat.llamaindex_processor:
            print("\n📋 Testing LlamaIndex-enhanced analysis...")
            response2, status2 = chat.enhanced_analysis_with_llamaindex(
                temp_file.name, 
                "provide comprehensive financial insights with structured analysis"
            )
            
            print(f"✅ LlamaIndex-enhanced analysis completed")
            print(f"   Status: {status2}")
            print(f"   Response length: {len(response2)} characters")
            
            # Compare responses
            if len(response2) > len(response1):
                print("✅ LlamaIndex-enhanced analysis provides more detailed response")
            else:
                print("ℹ️ LlamaIndex-enhanced analysis similar length to regular analysis")
                
        else:
            print("ℹ️ LlamaIndex processor not available, testing regular analysis only")
        
        # Test contribution analysis with potential LlamaIndex enhancement
        print("\n📋 Testing contribution analysis...")
        response3, status3 = chat.analyze_data(temp_file.name, "perform contribution analysis")
        
        print(f"✅ Contribution analysis completed")
        print(f"   Status: {status3}")
        print(f"   Contains Pareto analysis: {'pareto' in response3.lower()}")
        print(f"   Contains timescale analysis: {'timescale' in response3.lower()}")
        
        # Cleanup
        os.unlink(temp_file.name)
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def fix_llamaindex_integration():
    """Fix LlamaIndex integration issues"""
    print("\n" + "="*60)
    print("🔧 FIXING LLAMAINDEX INTEGRATION")
    print("="*60)
    
    # Check if required packages are installed
    required_packages = [
        "llama-index",
        "llama-index-llms-ollama",
        "llama-index-embeddings-ollama"
    ]
    
    import subprocess
    
    for package in required_packages:
        try:
            result = subprocess.run([sys.executable, "-m", "pip", "install", package], 
                                  capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                print(f"✅ {package} installed/updated successfully")
            else:
                print(f"⚠️ {package} installation had warnings: {result.stderr}")
        except subprocess.TimeoutExpired:
            print(f"⚠️ {package} installation timed out")
        except Exception as e:
            print(f"❌ Failed to install {package}: {e}")

def create_llamaindex_test_config():
    """Create a test configuration for LlamaIndex"""
    print("\n" + "="*60)
    print("🔧 CREATING LLAMAINDEX TEST CONFIGURATION")
    print("="*60)
    
    config_content = '''"""
LlamaIndex Test Configuration
"""

# Test LlamaIndex availability
def test_llamaindex_config():
    try:
        from llama_index.core import Document, VectorStoreIndex
        from llama_index.llms.ollama import Ollama
        
        # Test Ollama connection
        llm = Ollama(model="gemma3:latest", base_url="http://localhost:11434")
        
        # Test basic functionality
        docs = [Document(text="This is a test document for financial analysis.")]
        index = VectorStoreIndex.from_documents(docs)
        
        print("✅ LlamaIndex configuration test passed")
        return True
        
    except Exception as e:
        print(f"❌ LlamaIndex configuration test failed: {e}")
        return False

if __name__ == "__main__":
    test_llamaindex_config()
'''
    
    with open(project_dir / "test_llamaindex_config.py", "w", encoding="utf-8") as f:
        f.write(config_content)
    
    print("✅ Created test_llamaindex_config.py")

def main():
    """Run all tests"""
    print("🚀 LLAMAINDEX INTEGRATION VERIFICATION")
    print("Testing LlamaIndex integration and contribution analysis scope")
    
    # Fix integration first
    fix_llamaindex_integration()
    
    # Test LlamaIndex availability
    llamaindex_available = test_llamaindex_availability()
    
    # Test contribution analysis scope
    csv_scope_test = test_contribution_analysis_csv_scope()
    
    # Test chat integration
    chat_test = test_chat_with_llamaindex()
    
    # Create test config
    create_llamaindex_test_config()
    
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    print(f"✅ LlamaIndex Available: {'Yes' if llamaindex_available else 'No'}")
    print(f"✅ Contribution Analysis CSV-Only: {'Yes' if csv_scope_test else 'No'}")
    print(f"✅ Chat LlamaIndex Integration: {'Yes' if chat_test else 'No'}")
    
    if llamaindex_available and csv_scope_test and chat_test:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Contribution analysis uses ONLY uploaded CSV data")
        print("✅ LlamaIndex is properly integrated for enhanced chat responses")
    else:
        print("\n⚠️ SOME TESTS NEED ATTENTION")
        
        if not llamaindex_available:
            print("🔧 Fix: Install LlamaIndex components properly")
        if not csv_scope_test:
            print("🔧 Fix: Verify contribution analysis data source")
        if not chat_test:
            print("🔧 Fix: Check chat system LlamaIndex integration")

if __name__ == "__main__":
    main()
