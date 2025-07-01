"""
Test suite for CSV loader
Tests the CSVLoader class functionality
"""

import pytest
import pandas as pd
import io
import tempfile
import os
from pathlib import Path

from config.settings import Settings
from data.csv_loader import CSVLoader, CSVLoadError


class TestCSVLoader:
    """Test cases for CSVLoader class"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.settings = Settings()
        self.loader = CSVLoader(self.settings)
        
        # Create sample CSV data
        self.sample_data = pd.DataFrame({
            'Date': ['2024-01-01', '2024-01-02', '2024-01-03'],
            'Product': ['Product_A', 'Product_B', 'Product_A'],
            'Region': ['North', 'South', 'North'],
            'Sales': [1000, 1500, 1200],
            'Budget': [900, 1400, 1100],
            'Actual': [1000, 1500, 1200]
        })
    
    def test_load_csv_from_dataframe_string(self):
        """Test loading CSV from string representation"""
        csv_string = self.sample_data.to_csv(index=False)
        csv_io = io.StringIO(csv_string)
        
        result = self.loader.load_csv(csv_io)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3
        assert len(result.columns) == 6
        assert self.loader.status == "loaded"
        
        # Check column detection
        assert 'Sales' in self.loader.column_info['numeric_columns']
        assert 'Product' in self.loader.column_info['text_columns']
        assert 'Date' in self.loader.column_info['potential_date_columns']
    
    def test_load_csv_from_bytes(self):
        """Test loading CSV from bytes"""
        csv_string = self.sample_data.to_csv(index=False)
        csv_bytes = csv_string.encode('utf-8')
        
        result = self.loader.load_csv(csv_bytes)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3
        assert self.loader.status == "loaded"
    
    def test_load_csv_from_file_path(self):
        """Test loading CSV from file path"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            self.sample_data.to_csv(f, index=False)
            temp_path = f.name
        
        try:
            result = self.loader.load_csv(temp_path)
            
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 3
            assert self.loader.file_path == temp_path
            assert self.loader.status == "loaded"
        finally:
            os.unlink(temp_path)
    
    def test_load_csv_file_not_found(self):
        """Test error handling for non-existent file"""
        with pytest.raises(CSVLoadError, match="File not found"):
            self.loader.load_csv("nonexistent_file.csv")
    
    def test_load_csv_empty_file(self):
        """Test error handling for empty CSV"""
        empty_csv = io.StringIO("")
        
        with pytest.raises(CSVLoadError, match="CSV file is empty"):
            self.loader.load_csv(empty_csv)
    
    def test_load_csv_invalid_format(self):
        """Test error handling for invalid CSV format"""
        invalid_csv = io.StringIO("This is not a CSV file\nIt has no proper structure")
        
        # Should still load but might have issues with structure
        result = self.loader.load_csv(invalid_csv)
        
        # The pandas parser is quite forgiving, so this might actually work
        assert isinstance(result, pd.DataFrame)
    
    def test_file_size_limit(self):
        """Test file size limit enforcement"""
        # Create a loader with small file size limit
        small_settings = Settings(max_file_size=100)  # 100 bytes
        small_loader = CSVLoader(small_settings)
        
        # Create large CSV data
        large_data = pd.DataFrame({
            'col1': range(1000),
            'col2': [f'text_{i}' for i in range(1000)]
        })
        csv_string = large_data.to_csv(index=False)
        csv_bytes = csv_string.encode('utf-8')
        
        with pytest.raises(CSVLoadError, match="File too large"):
            small_loader.load_csv(csv_bytes)
    
    def test_column_detection_numeric(self):
        """Test detection of numeric columns"""
        csv_data = pd.DataFrame({
            'sales': [100, 200, 300],
            'revenue': [1000.5, 2000.7, 3000.9],
            'count': [1, 2, 3]
        })
        csv_io = io.StringIO(csv_data.to_csv(index=False))
        
        self.loader.load_csv(csv_io)
        
        assert 'sales' in self.loader.column_info['numeric_columns']
        assert 'revenue' in self.loader.column_info['numeric_columns']
        assert 'count' in self.loader.column_info['numeric_columns']
        assert len(self.loader.column_info['text_columns']) == 0
    
    def test_column_detection_financial(self):
        """Test detection of financial column patterns"""
        csv_data = pd.DataFrame({
            'sales_actual': [100, 200, 300],
            'sales_budget': [90, 210, 290],
            'revenue_amount': [1000, 2000, 3000],
            'product_category': ['A', 'B', 'C'],
            'customer_region': ['North', 'South', 'East']
        })
        csv_io = io.StringIO(csv_data.to_csv(index=False))
        
        self.loader.load_csv(csv_io)
        
        financial_cols = self.loader.column_info['financial_columns']
        
        # Check value columns
        assert 'sales_actual' in financial_cols.get('value_columns', [])
        assert 'revenue_amount' in financial_cols.get('value_columns', [])
        
        # Check budget/actual columns
        assert 'sales_budget' in financial_cols.get('budget_columns', [])
        assert 'sales_actual' in financial_cols.get('actual_columns', [])
        
        # Check category columns
        assert 'product_category' in financial_cols.get('category_columns', [])
        assert 'customer_region' in financial_cols.get('category_columns', [])
    
    def test_column_detection_dates(self):
        """Test detection of date columns"""
        csv_data = pd.DataFrame({
            'date_column': ['2024-01-01', '2024-01-02', '2024-01-03'],
            'period_end': ['2024-01-31', '2024-02-29', '2024-03-31'],
            'not_a_date': ['text1', 'text2', 'text3'],
            'value': [100, 200, 300]
        })
        csv_io = io.StringIO(csv_data.to_csv(index=False))
        
        self.loader.load_csv(csv_io)
        
        # Check potential date columns
        assert 'date_column' in self.loader.column_info['potential_date_columns']
        assert 'period_end' in self.loader.column_info['potential_date_columns']
        
        # Check that actual date parsing worked
        assert 'date_column' in self.loader.column_info['date_columns']
        assert 'period_end' in self.loader.column_info['date_columns']
        
        # Check that non-date text column is in text columns
        assert 'not_a_date' in self.loader.column_info['text_columns']
    
    def test_data_quality_analysis(self):
        """Test data quality analysis"""
        csv_data = pd.DataFrame({
            'complete_col': [1, 2, 3, 4, 5],
            'missing_col': [1, None, 3, None, 5],
            'duplicate_row': ['A', 'B', 'A', 'C', 'A']  # Will create duplicates
        })
        # Add a duplicate row
        csv_data = pd.concat([csv_data, csv_data.iloc[[0]]], ignore_index=True)
        
        csv_io = io.StringIO(csv_data.to_csv(index=False))
        
        self.loader.load_csv(csv_io)
        
        quality = self.loader.data_quality
        
        # Check missing data detection
        assert 'missing_col' in quality['missing_data']
        assert quality['missing_data']['missing_col']['count'] == 2
        assert quality['missing_data']['missing_col']['percentage'] == pytest.approx(33.33, rel=1e-2)
        
        # Check duplicate detection
        assert quality['duplicate_rows'] == 1  # One duplicate row
        
        # Check basic stats
        assert quality['total_rows'] == 6
        assert quality['total_columns'] == 3
    
    def test_get_column_suggestions(self):
        """Test column suggestions for analysis"""
        csv_data = pd.DataFrame({
            'sales_budget': [900, 1400, 1100],
            'sales_actual': [1000, 1500, 1200],
            'product_name': ['A', 'B', 'C'],
            'customer_region': ['North', 'South', 'East'],
            'date': ['2024-01-01', '2024-01-02', '2024-01-03']
        })
        csv_io = io.StringIO(csv_data.to_csv(index=False))
        
        self.loader.load_csv(csv_io)
        suggestions = self.loader.get_column_suggestions()
        
        # Check value column suggestions
        assert 'sales_budget' in suggestions['value_columns']
        assert 'sales_actual' in suggestions['value_columns']
        
        # Check category column suggestions
        assert 'product_name' in suggestions['category_columns']
        assert 'customer_region' in suggestions['category_columns']
        
        # Check budget vs actual pairing
        assert 'sales_budget' in suggestions['budget_vs_actual']
        assert suggestions['budget_vs_actual']['sales_budget'] == 'sales_actual'
    
    def test_get_data_summary(self):
        """Test data summary generation"""
        csv_io = io.StringIO(self.sample_data.to_csv(index=False))
        
        self.loader.load_csv(csv_io)
        summary = self.loader.get_data_summary()
        
        assert "Dataset Overview" in summary
        assert "Rows: 3" in summary
        assert "Columns: 6" in summary
        assert "Numeric Columns: 3" in summary
        assert "Text Columns: 2" in summary
    
    def test_unsupported_input_type(self):
        """Test error handling for unsupported input types"""
        with pytest.raises(CSVLoadError, match="Unsupported input type"):
            self.loader.load_csv(123)  # Integer input
    
    def test_unicode_decode_error(self):
        """Test handling of invalid unicode in file bytes"""
        # Create bytes with invalid unicode
        invalid_bytes = b'\xff\xfe' + "col1,col2\n1,2\n3,4".encode('utf-8')
        
        # Should fall back to latin-1 encoding
        result = self.loader.load_csv(invalid_bytes)
        assert isinstance(result, pd.DataFrame)
        
    def test_too_many_rows(self):
        """Test handling of datasets that are too large"""
        # Create a dataset with too many rows
        large_data = pd.DataFrame({
            'col1': range(1_000_001),  # Over 1M rows
            'col2': range(1_000_001)
        })
        csv_io = io.StringIO(large_data.to_csv(index=False))
        
        with pytest.raises(CSVLoadError, match="Dataset too large"):
            self.loader.load_csv(csv_io)
    
    def test_too_many_columns(self):
        """Test handling of datasets with too many columns"""
        # Create a dataset with too many columns
        large_data = pd.DataFrame({f'col_{i}': [1, 2, 3] for i in range(1001)})
        csv_io = io.StringIO(large_data.to_csv(index=False))
        
        with pytest.raises(CSVLoadError, match="Too many columns"):
            self.loader.load_csv(csv_io)


if __name__ == "__main__":
    # Run tests if executed directly
    import sys
    
    test_class = TestCSVLoader()
    
    # Get all test methods
    test_methods = [method for method in dir(test_class) if method.startswith('test_')]
    
    print(f"🧪 Running {len(test_methods)} CSV loader tests...")
    
    passed = 0
    failed = 0
    
    for test_method in test_methods:
        try:
            print(f"  ▶️ {test_method}... ", end="")
            test_instance = TestCSVLoader()
            test_instance.setup_method()
            getattr(test_instance, test_method)()
            print("✅ PASSED")
            passed += 1
        except Exception as e:
            print(f"❌ FAILED: {str(e)}")
            failed += 1
    
    print(f"\n📊 Results: {passed} passed, {failed} failed")
    
    if failed > 0:
        sys.exit(1)
    else:
        print("🎉 All CSV loader tests passed!")
        sys.exit(0)
