# Test Organization Plan for Quant Commander v2.0

## Current Issues
- All test files are in root folder (violates quality standards)
- Mixed purposes: tests, demos, debugging scripts, validation
- No proper naming conventions
- No organization by test type

## Proposed Structure

```
tests/
├── __init__.py
├── unit/
│   ├── __init__.py
│   ├── test_app_core.py
│   ├── test_file_handler.py
│   ├── test_chat_handler.py
│   ├── test_quick_action_handler.py
│   ├── test_variance_analyzer.py
│   ├── test_rag_document_manager.py
│   └── test_rag_enhanced_analyzer.py
├── integration/
│   ├── __init__.py
│   ├── test_csv_upload_flow.py
│   ├── test_rag_integration.py
│   ├── test_full_analysis_pipeline.py
│   └── test_interface_integration.py
├── fixtures/
│   ├── __init__.py
│   ├── sample_data.csv
│   ├── sample_documents.pdf
│   └── test_config.json
└── conftest.py
```

## Files to Move/Refactor

### Unit Tests (move to tests/unit/)
- `minimal_variance_test.py` → `test_variance_analyzer.py`
- `debug_app_import.py` → `test_app_core.py`
- `debug_interface.py` → `test_interface_components.py`

### Integration Tests (move to tests/integration/)
- `comprehensive_validation.py` → `test_full_validation_suite.py`
- `final_validation_suite.py` → `test_complete_integration.py`
- `integration_example.py` → `test_rag_integration.py`
- `demo_rag_integration.py` → `test_rag_integration.py`

### Fixtures and Test Data (move to tests/fixtures/)
- `oob_test_data.csv` → `tests/fixtures/sample_variance_data.csv`
- `generate_sample_data.py` → `tests/fixtures/generate_test_data.py`

### Debugging/Development Tools (move to tools/ or scripts/)
- `debug_*.py` files
- `check_llm_status.py`
- `diagnose_*.py` files

### Demo Files (move to examples/)
- `demo_*.py` files

## Benefits of Proper Organization
1. **Follows quality standards** - Tests in proper test folder
2. **Clear separation** - Unit vs integration vs fixtures
3. **Easy discovery** - Consistent naming conventions
4. **Better maintainability** - Related tests grouped together
5. **Proper test coverage** - Clear understanding of what's tested

## Next Steps
1. Create proper test directory structure ✅
2. Move existing test files to appropriate locations
3. Rename files to follow conventions (test_*.py)
4. Create proper unit tests for each module
5. Create integration tests for major features
6. Set up test fixtures and sample data
7. Add conftest.py for shared test configuration
