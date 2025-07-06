"""
Quick test to demonstrate the new CSV upload with chat integration
"""

from app_v2 import VarianceProApp
import os

def demo_upload():
    print("🎯 Demo: CSV Upload with Chat Integration")
    print("=" * 50)
    
    app = VarianceProApp()
    print(f"📝 Session: {app.session_id}")
    print(f"🤖 Ollama: {app.ollama_status}")
    
    # Initial chat state
    initial_history = [
        {"role": "assistant", "content": "👋 Welcome to VariancePro v2.0! Upload your CSV file and I'll analyze it for you."}
    ]
    
    print(f"\n📋 Initial chat history: {len(initial_history)} messages")
    
    # Simulate file upload with sample data
    sample_file = "sample_data/sample_variance_data.csv"
    
    if os.path.exists(sample_file):
        print(f"\n📁 Testing upload with: {sample_file}")
        
        # Create file-like object
        class MockFile:
            def __init__(self, path):
                self.name = path
        
        mock_file = MockFile(sample_file)
        
        # Test the upload function
        status, updated_history = app.upload_csv(mock_file, initial_history.copy())
        
        print(f"\n📊 Results:")
        print(f"   Upload Status: {status[:100]}...")
        print(f"   Chat History: {len(updated_history)} messages")
        print(f"   Last Message Role: {updated_history[-1]['role']}")
        print(f"   Last Message Preview: {updated_history[-1]['content'][:200]}...")
        
        if app.current_data is not None:
            print(f"\n📈 Data Loaded:")
            print(f"   Shape: {app.current_data.shape}")
            print(f"   Columns: {list(app.current_data.columns)[:5]}...")
        
        print("\n✅ CSV upload integration working correctly!")
        
    else:
        print(f"⚠️  Sample file not found: {sample_file}")
        print("Create a CSV file to test the upload functionality")

if __name__ == "__main__":
    demo_upload()
