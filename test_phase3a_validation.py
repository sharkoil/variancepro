#!/usr/bin/env python3
"""
Phase 3A Validation Test
Tests that all Phase 3A components are working correctly
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_phase3a_integration():
    """Test that Phase 3A components integrate correctly"""
    
    try:
        # Test imports
        from handlers.quick_action_handler import QuickActionHandler
        from core.app_core import AppCore
        from utils.cache_manager import get_cache_manager, clear_global_cache
        from utils.performance_monitor import get_performance_monitor, clear_performance_metrics
        print("✅ All imports successful")
        
        # Test cache manager
        cache_manager = get_cache_manager()
        assert cache_manager is not None, "Cache manager should not be None"
        print("✅ Cache manager available")
        
        # Test performance monitor
        perf_monitor = get_performance_monitor()
        assert perf_monitor is not None, "Performance monitor should not be None"
        print("✅ Performance monitor available")
        
        # Test clear functions
        clear_global_cache()
        clear_performance_metrics()
        print("✅ Cache and performance clearing works")
        
        # Test cache stats
        stats = cache_manager.get_stats()
        assert 'hits' in stats, "Cache stats should contain 'hits'"
        assert 'misses' in stats, "Cache stats should contain 'misses'"
        assert 'size' in stats, "Cache stats should contain 'size'"
        print("✅ Cache statistics available")
        
        # Test performance stats
        perf_stats = perf_monitor.get_performance_summary()
        assert 'system' in perf_stats, "Performance stats should contain 'system'"
        print("✅ Performance statistics available")
        
        print("\n🎉 Phase 3A validation complete - all components working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Phase 3A validation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_phase3a_integration()
    sys.exit(0 if success else 1)
