"""Test the summary formatting specifically"""
try:
    from handlers.quick_action_handler import QuickActionHandler
    
    # Create test data that simulates the actual data summary structure
    class MockAppCore:
        def has_data(self):
            return True
        def get_current_data(self):
            import pandas as pd
            data = pd.DataFrame({
                'Date': ['2024-01-01', '2024-01-02'],
                'Product': ['Coffee Machine', 'Laptop'],
                'Budget': [32934, 169029],
                'Actuals': [38861, 209534]
            })
            # This is the exact structure that was causing the raw dict issue
            summary = {
                'row_count': 2,
                'column_count': 4,
                'columns': ['Date', 'Product', 'Budget', 'Actuals'],
                'column_types': {'Date': 'object', 'Product': 'object', 'Budget': 'int64', 'Actuals': 'int64'},
                'basic_stats': {
                    'Budget': {'min': 32934.0, 'max': 169029.0, 'mean': 100981.5},
                    'Actuals': {'min': 38861.0, 'max': 209534.0, 'mean': 124197.5}
                },
                'data_quality': {
                    'Date': {'null_count': 0, 'null_percentage': 0.0},
                    'Product': {'null_count': 0, 'null_percentage': 0.0},
                    'Budget': {'null_count': 0, 'null_percentage': 0.0},
                    'Actuals': {'null_count': 0, 'null_percentage': 0.0}
                }
            }
            return data, summary
    
    handler = QuickActionHandler(MockAppCore())
    
    # Test the summary action
    result = handler._handle_summary_action()
    
    print("📊 FORMATTED SUMMARY OUTPUT:")
    print("=" * 50)
    print(result)
    print("=" * 50)
    
    # Check if it's human-readable (not a raw dict)
    if result.startswith('📊 **Data Summary**'):
        print("✅ Summary is properly formatted (human-readable)")
    else:
        print("❌ Summary may still be raw data")
    
    # Check if it contains expected elements
    if 'Dataset Overview' in result and 'Columns' in result:
        print("✅ Summary contains expected sections")
    else:
        print("❌ Summary missing expected sections")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
