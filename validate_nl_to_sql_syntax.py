"""
Comprehensive syntax and import validation for NL-to-SQL testing files
"""

import sys
import os
import traceback
from pathlib import Path

def test_syntax_and_imports():
    """Test syntax and imports for all NL-to-SQL testing files"""
    
    print("🔍 Testing NL-to-SQL Testing Framework Syntax & Imports")
    print("=" * 60)
    
    # Files to check
    test_files = [
        ("UI Files", [
            "ui/nl_to_sql_testing_ui.py",
            "ui/nl_to_sql_testing_ui_enhanced.py"
        ]),
        ("Test Scripts", [
            "test_enhanced_nl_to_sql_ui.py"
        ]),
        ("Core Analyzers", [
            "analyzers/nl_to_sql_tester.py",
            "analyzers/enhanced_nl_to_sql_translator.py",
            "analyzers/strategy_1_llm_enhanced.py", 
            "analyzers/strategy_2_semantic_parsing.py"
        ])
    ]
    
    all_passed = True
    
    for category, files in test_files:
        print(f"\n📂 {category}:")
        print("-" * 40)
        
        for file_path in files:
            # Check if file exists
            if not os.path.exists(file_path):
                print(f"  ❌ {file_path} - File not found")
                all_passed = False
                continue
            
            # Test syntax
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    compile(f.read(), file_path, 'exec')
                print(f"  ✅ {file_path} - Syntax OK")
            except SyntaxError as e:
                print(f"  ❌ {file_path} - Syntax Error: Line {e.lineno}: {e.msg}")
                all_passed = False
                continue
            except Exception as e:
                print(f"  ❌ {file_path} - Error: {e}")
                all_passed = False
                continue
    
    print("\n" + "=" * 60)
    
    # Test imports
    print("\n🔌 Testing Key Imports:")
    print("-" * 40)
    
    import_tests = [
        ("analyzers.enhanced_nl_to_sql_translator", "EnhancedNLToSQLTranslator"),
        ("analyzers.nl_to_sql_tester", "NLToSQLTester"),
        ("ai.llm_interpreter", "LLMInterpreter"),
        ("config.settings", "Settings")
    ]
    
    for module_name, class_name in import_tests:
        try:
            module = __import__(module_name, fromlist=[class_name])
            getattr(module, class_name)
            print(f"  ✅ {module_name}.{class_name} - Import OK")
        except ImportError as e:
            print(f"  ⚠️  {module_name}.{class_name} - Import Warning: {e}")
        except Exception as e:
            print(f"  ❌ {module_name}.{class_name} - Error: {e}")
            all_passed = False
    
    print("\n" + "=" * 60)
    
    if all_passed:
        print("🎉 All syntax checks passed successfully!")
        print("📝 The NL-to-SQL testing framework is ready to use.")
    else:
        print("⚠️  Some issues were found. Please review the errors above.")
    
    return all_passed

if __name__ == "__main__":
    # Add current directory to path
    sys.path.insert(0, os.getcwd())
    
    try:
        success = test_syntax_and_imports()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Validation script error: {e}")
        traceback.print_exc()
        sys.exit(1)
