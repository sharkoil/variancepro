"""Test just the quick action handler"""
try:
    from handlers.quick_action_handler import QuickActionHandler
    print("✅ QuickActionHandler imported successfully")
    
    # Test with mock app_core
    class MockAppCore:
        def has_data(self):
            return True
        def get_current_data(self):
            import pandas as pd
            data = pd.DataFrame({'Budget': [100, 200], 'Actuals': [110, 180]})
            summary = {'row_count': 2, 'column_count': 2, 'columns': ['Budget', 'Actuals']}
            return data, summary
    
    handler = QuickActionHandler(MockAppCore())
    print("✅ QuickActionHandler initialized successfully")
    
    # Test summary action
    result = handler._handle_summary_action()
    print("✅ Summary action works")
    print("Summary result preview:", result[:100], "...")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
