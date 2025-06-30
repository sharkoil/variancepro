@echo off
REM VariancePro Test Runner Batch File
REM This script runs all VariancePro tests and generates a report

echo ======================================================
echo VariancePro Test Runner
echo ======================================================
echo.

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Python is not installed or not in the PATH. Please install Python.
    exit /b 1
)

REM Optional: Install test dependencies if needed
echo Installing test dependencies...
python -m pip install html-testRunner pytest pytest-html --quiet

REM Run tests with either the Python script or pytest
echo.
echo Running tests...
echo.

REM Option 1: Run with our custom test runner
python run_tests.py

REM Option 2: Run with pytest (commented out but available)
REM pytest test_timescale_analyzer_unit.py test_timescale_analyzer_integration.py test_financial_accuracy.py test_timescale_analyzer_edge_cases.py -v --html=test_reports/pytest_report.html

echo.
echo ======================================================
echo Test run complete
echo ======================================================
