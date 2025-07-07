"""
Comprehensive validation script for VariancePro v2.0 RAG integration
Tests all major components including:
- Variance analysis (fixed signature)
- RAG document management 
- Summary analysis formatting
- Quick action handlers
"""

import os
import sys
import pandas as pd
import tempfile
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath('.'))

def test_variance_analysis():
    """Test variance analysis functionality"""
    print("🔧 Testing Variance Analysis...")
    
    try:
        from analyzers.variance_analyzer import VarianceAnalyzer
        
        # Sample data
        data = pd.DataFrame({
            'Product': ['A', 'B', 'C'],
            'Actual_Sales': [1000, 1500, 800],
            'Planned_Sales': [900, 1400, 900],
            'Date': pd.to_datetime(['2024-01-01', '2024-01-02', '2024-01-03'])
        })
        
        analyzer = VarianceAnalyzer()
        
        # Test comprehensive analysis
        result = analyzer.comprehensive_variance_analysis(
            data=data,
            actual_col='Actual_Sales',
            planned_col='Planned_Sales',
            date_col='Date'
        )
        
        # Test formatting (this was the broken part)
        formatted = analyzer.format_comprehensive_analysis(result)
        
        print("✅ Variance analysis passed")
        print(f"   - Result type: {type(result)}")
        print(f"   - Formatted length: {len(formatted)} chars")
        return True
        
    except Exception as e:
        print(f"❌ Variance analysis failed: {e}")
        return False

def test_rag_components():
    """Test RAG document management"""
    print("🔧 Testing RAG Components...")
    
    try:
        from analyzers.rag_document_manager import RAGDocumentManager
        from analyzers.rag_enhanced_analyzer import RAGEnhancedAnalyzer
        
        rag_manager = RAGDocumentManager()
        print("✅ RAGDocumentManager created")
        
        rag_analyzer = RAGEnhancedAnalyzer()
        print("✅ RAGEnhancedAnalyzer created")
        
        # Test basic functionality without actual documents
        has_docs = rag_manager.has_documents()
        print(f"✅ Has documents check: {has_docs}")
        
        return True
        
    except Exception as e:
        print(f"❌ RAG components failed: {e}")
        return False

def test_quick_action_handlers():
    """Test quick action handlers"""
    print("🔧 Testing Quick Action Handlers...")
    
    try:
        from handlers.quick_action_handler import QuickActionHandler
        from core.app_core import AppCore
        
        # Create app core with sample data
        app_core = AppCore()
        app_core.current_data = pd.DataFrame({
            'Product': ['Widget A', 'Widget B'],
            'Actual_Sales': [1200, 1800],
            'Planned_Sales': [1000, 1600],
            'Budget': [950, 1550],
            'Date': pd.to_datetime(['2024-01-01', '2024-01-02'])
        })
        
        handler = QuickActionHandler(app_core=app_core)
        print("✅ QuickActionHandler created")
        
        # Test variance analysis (the one that was broken)
        variance_result = handler.handle_variance_analysis()
        print(f"✅ Variance analysis handler: {len(variance_result)} chars")
        
        # Test summary analysis
        summary_result = handler.handle_summary_analysis()
        print(f"✅ Summary analysis handler: {len(summary_result)} chars")
        
        return True
        
    except Exception as e:
        print(f"❌ Quick action handlers failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_app_core():
    """Test app core functionality"""
    print("🔧 Testing App Core...")
    
    try:
        from core.app_core import AppCore
        
        app_core = AppCore()
        
        # Test data loading
        sample_data = pd.DataFrame({
            'A': [1, 2, 3],
            'B': [4, 5, 6]
        })
        
        app_core.current_data = sample_data
        print(f"✅ App core data set: {app_core.current_data.shape}")
        
        # Test summary generation
        summary = app_core.generate_summary()
        print(f"✅ Summary generated: {len(summary)} chars")
        
        return True
        
    except Exception as e:
        print(f"❌ App core failed: {e}")
        return False

def main():
    """Run all validation tests"""
    print("🚀 VariancePro v2.0 - Comprehensive Validation")
    print("=" * 60)
    
    tests = [
        ("Variance Analysis", test_variance_analysis),
        ("RAG Components", test_rag_components), 
        ("Quick Action Handlers", test_quick_action_handlers),
        ("App Core", test_app_core)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("📊 VALIDATION SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:8} {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! VariancePro v2.0 is ready for use.")
    else:
        print("⚠️ Some tests failed. Please review the errors above.")

if __name__ == "__main__":
    main()
