#!/usr/bin/env python3
"""
Simple test to verify cache integration works in QuickActionHandler
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
from unittest.mock import Mock

# Test imports
try:
    from handlers.quick_action_handler import QuickActionHandler
    from utils.cache_manager import get_cache_manager, clear_global_cache
    from utils.performance_monitor import get_performance_monitor, clear_performance_metrics
    print("✅ All imports successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def test_basic_cache_integration():
    """Test basic cache integration functionality"""
    print("\n🧪 Testing basic cache integration...")
    
    # Clear cache before test
    clear_global_cache()
    clear_performance_metrics()
    
    # Create mock app core
    mock_app_core = Mock()
    mock_app_core.has_data.return_value = True
    
    # Create sample test data
    test_data = pd.DataFrame({
        'Date': pd.date_range('2024-01-01', periods=5, freq='D'),
        'Revenue': [100, 150, 200, 180, 220],
        'Cost': [50, 75, 100, 90, 110],
        'Profit': [50, 75, 100, 90, 110]
    })
    
    # Mock data summary
    mock_data_summary = {
        'row_count': 5,
        'column_count': 4,
        'columns': ['Date', 'Revenue', 'Cost', 'Profit'],
        'basic_stats': {
            'Revenue': {'mean': 170, 'min': 100, 'max': 220},
            'Cost': {'mean': 85, 'min': 50, 'max': 110}
        }
    }
    
    mock_app_core.get_current_data.return_value = (test_data, mock_data_summary)
    
    # Create handler
    handler = QuickActionHandler(
        app_core=mock_app_core,
        rag_manager=None,
        rag_analyzer=None
    )
    
    # Test 1: Cache manager initialization
    print("📊 Testing cache manager initialization...")
    assert handler.cache_manager is not None, "Cache manager should be initialized"
    assert handler.performance_monitor is not None, "Performance monitor should be initialized"
    print("✅ Cache manager and performance monitor initialized")
    
    # Test 2: Cache stats access
    print("📊 Testing cache stats access...")
    stats = handler.get_cache_stats()
    assert isinstance(stats, dict), "Cache stats should be a dict"
    assert 'hits' in stats, "Stats should contain 'hits'"
    assert 'misses' in stats, "Stats should contain 'misses'"
    assert 'size' in stats, "Stats should contain 'size'"
    print("✅ Cache stats accessible")
    
    # Test 3: Performance stats access
    print("📊 Testing performance stats access...")
    perf_stats = handler.get_performance_stats()
    assert isinstance(perf_stats, dict), "Performance stats should be a dict"
    print("✅ Performance stats accessible")
    
    # Test 4: Basic summary action with caching
    print("📊 Testing summary action with caching...")
    
    # First call - should be cache miss
    result1 = handler._handle_summary_action()
    assert isinstance(result1, str), "Summary result should be a string"
    assert "Summary" in result1, "Result should contain 'Summary'"
    
    stats_after_first = handler.get_cache_stats()
    assert stats_after_first['misses'] >= 1, "Should have at least one cache miss"
    print(f"✅ First call completed - Cache misses: {stats_after_first['misses']}")
    
    # Second call - should be cache hit
    result2 = handler._handle_summary_action()
    assert result1 == result2, "Cached results should be identical"
    
    stats_after_second = handler.get_cache_stats()
    assert stats_after_second['hits'] >= 1, "Should have at least one cache hit"
    print(f"✅ Second call completed - Cache hits: {stats_after_second['hits']}")
    
    # Test 5: Cache invalidation
    print("📊 Testing cache invalidation...")
    handler.invalidate_cache_for_data_change()
    
    stats_after_invalidation = handler.get_cache_stats()
    assert stats_after_invalidation['size'] == 0, "Cache should be empty after invalidation"
    print("✅ Cache invalidation successful")
    
    print("\n🎉 All cache integration tests passed!")
    return True

if __name__ == "__main__":
    try:
        test_basic_cache_integration()
        print("\n✅ Cache integration is working correctly!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
