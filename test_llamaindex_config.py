"""
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
