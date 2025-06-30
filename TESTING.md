# VariancePro Testing Documentation

This document outlines the testing strategy and procedures for the VariancePro application, with a particular focus on the financial data analysis components and the TimescaleAnalyzer module.

## Testing Strategy

VariancePro's testing strategy focuses on ensuring the accuracy and reliability of financial calculations and time series analysis, which are critical to the application's purpose. The test suite includes:

1. **Unit Tests**: Testing individual components in isolation
2. **Integration Tests**: Testing how components work together
3. **Financial Accuracy Tests**: Validating mathematical correctness of financial calculations
4. **Edge Case Tests**: Ensuring robust handling of unusual or extreme data situations

## Test Files

The following test files are included in the VariancePro test suite:

- `test_timescale_analyzer_unit.py`: Unit tests for the TimescaleAnalyzer class
- `test_timescale_analyzer_integration.py`: Integration tests between TimescaleAnalyzer and other components
- `test_financial_accuracy.py`: Tests focused on the financial calculation accuracy
- `test_timescale_analyzer_edge_cases.py`: Tests for handling edge cases and unusual data patterns

## Running Tests

### Running All Tests

To run all tests, use one of the following methods:

#### Option 1: Run Test Script
```bash
python run_tests.py
```

#### Option 2: Run Batch File (Windows)
```bash
run_tests.bat
```

#### Option 3: Run with Pytest
```bash
pytest test_timescale_analyzer_unit.py test_timescale_analyzer_integration.py test_financial_accuracy.py test_timescale_analyzer_edge_cases.py -v
```

### Continuous Testing During Development

For test-driven development, you can use the continuous test runner which automatically runs tests when files change:

```bash
python continuous_test.py
```

## Test Reports

Test reports are generated in the `test_reports` directory when using the HTML test runner. These reports provide detailed information about test results, including:

- Test summary statistics
- Detailed test case results
- Execution time information
- Error and failure details

## Key Test Areas

### Time Granularity Detection

Tests verify that the system correctly identifies the appropriate time granularity (daily, weekly, monthly, quarterly, yearly) from the data.

### Period Aggregation

Tests confirm that data is correctly aggregated at different time scales, preserving financial integrity during summarization.

### Period-over-Period Calculations

Tests validate that period-over-period calculations (such as Month-over-Month, Quarter-over-Quarter, Year-over-Year) are mathematically correct and adhere to financial standards.

### Financial Metrics

Tests ensure the accuracy of key financial metrics:
- Growth rates
- Percentage changes
- Absolute changes
- Compound Annual Growth Rate (CAGR)
- Financial ratios (e.g., profit margins)

### Edge Cases

Tests verify graceful handling of challenging data scenarios:
- Irregular time intervals
- Missing data points
- Extreme outliers
- Negative values
- Very large datasets
- Very small datasets (single data point)

## Test Data

The test suite uses various data sources:

1. **Synthetic test data**: Carefully constructed datasets with predictable patterns to validate calculation accuracy
2. **Sample data files**: Real-world sample datasets included in the project
3. **Edge case data**: Specially created datasets to test boundary conditions and unusual patterns

## Adding New Tests

When adding new functionality to VariancePro, corresponding tests should be added:

1. For new components, add unit tests in a new file `test_component_name.py`
2. For enhancements to existing components, add test cases to the appropriate existing test file
3. For any financial calculations, add specific tests in `test_financial_accuracy.py`
4. For edge cases related to new functionality, add test cases in `test_timescale_analyzer_edge_cases.py`

## Testing Standards

- All tests should be well-documented with clear assertions
- Financial calculations should be tested against manually verified examples
- Edge cases should be explicitly tested rather than assumed to work
- Tests should be independent and not rely on the order of execution
- Tests should clean up after themselves and not leave side effects

## Dependencies

The test suite requires the following dependencies:

- unittest (Python standard library)
- pytest (optional for running tests)
- html-testRunner (optional for HTML reports)
- watchdog (optional for continuous testing)

To install dependencies:
```bash
pip install pytest pytest-html html-testRunner watchdog
```
