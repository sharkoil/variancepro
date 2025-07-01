#!/usr/bin/env python3
"""
Model Configuration Test
Verifies that all components are using gemma3:latest and NOT deepseek
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

def test_model_configuration():
    """Test that all components use gemma3:latest"""
    
    print("🔍 MODEL CONFIGURATION TEST")
    print("="*50)
    
    errors = []
    success_count = 0
    total_tests = 0
    
    # Test 1: Main App Model
    try:
        from app import AriaFinancialChat
        chat = AriaFinancialChat()
        total_tests += 1
        
        if chat.model_name == "gemma3:latest":
            print("✅ Main App: gemma3:latest")
            success_count += 1
        else:
            print(f"❌ Main App: {chat.model_name} (should be gemma3:latest)")
            errors.append(f"Main App using {chat.model_name}")
    except Exception as e:
        print(f"❌ Main App: Error - {e}")
        errors.append(f"Main App error: {e}")
    
    # Test 2: LLM Handler Default
    try:
        from utils.llm_handler import LLMHandler
        llm = LLMHandler()
        total_tests += 1
        
        if llm.model_name == "gemma3:latest":
            print("✅ LLM Handler: gemma3:latest")
            success_count += 1
        else:
            print(f"❌ LLM Handler: {llm.model_name} (should be gemma3:latest)")
            errors.append(f"LLM Handler using {llm.model_name}")
    except Exception as e:
        print(f"❌ LLM Handler: Error - {e}")
        errors.append(f"LLM Handler error: {e}")
    
    # Test 3: Chat Handler Integration
    try:
        if hasattr(chat, 'chat_handler') and chat.chat_handler.llm_handler:
            total_tests += 1
            handler_model = chat.chat_handler.llm_handler.model_name
            
            if handler_model == "gemma3:latest":
                print("✅ Chat Handler: gemma3:latest")
                success_count += 1
            else:
                print(f"❌ Chat Handler: {handler_model} (should be gemma3:latest)")
                errors.append(f"Chat Handler using {handler_model}")
    except Exception as e:
        print(f"❌ Chat Handler: Error - {e}")
        errors.append(f"Chat Handler error: {e}")
    
    # Test 4: LlamaIndex Integration
    try:
        from llamaindex_integration import LlamaIndexFinancialProcessor
        if hasattr(chat, 'llamaindex_processor') and chat.llamaindex_processor:
            total_tests += 1
            llamaindex_model = chat.llamaindex_processor.model_name
            
            if llamaindex_model == "gemma3:latest":
                print("✅ LlamaIndex: gemma3:latest")
                success_count += 1
            else:
                print(f"❌ LlamaIndex: {llamaindex_model} (should be gemma3:latest)")
                errors.append(f"LlamaIndex using {llamaindex_model}")
        else:
            print("ℹ️ LlamaIndex: Not initialized")
    except Exception as e:
        print(f"❌ LlamaIndex: Error - {e}")
        errors.append(f"LlamaIndex error: {e}")
    
    # Test 5: Check for deepseek references
    print(f"\n🔍 CHECKING FOR DEEPSEEK REFERENCES")
    print("-" * 30)
    
    # Check if any component mentions deepseek
    deepseek_found = False
    
    try:
        # Quick test - make a sample query to see what model is actually used
        test_response, test_status = chat.analyze_data("sample_financial_data.csv", "what model are you using?")
        
        if "deepseek" in test_response.lower() or "deepseek" in test_status.lower():
            print("❌ DeepSeek reference found in response")
            deepseek_found = True
            errors.append("DeepSeek reference in response")
        else:
            print("✅ No DeepSeek references in response")
    except Exception as e:
        print(f"⚠️ Could not test response: {e}")
    
    # Summary
    print(f"\n📊 TEST SUMMARY")
    print("="*50)
    print(f"✅ Passed: {success_count}/{total_tests}")
    print(f"❌ Failed: {len(errors)}")
    
    if errors:
        print(f"\n🔧 ISSUES TO FIX:")
        for error in errors:
            print(f"   • {error}")
        return False
    else:
        print(f"\n🎉 ALL TESTS PASSED!")
        print("✅ All components correctly use gemma3:latest")
        print("✅ No deepseek references found")
        return True

if __name__ == "__main__":
    test_model_configuration()
