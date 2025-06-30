@echo off
REM VariancePro Test Suite Runner
REM This script runs the complete test suite and generates timestamped reports

echo ======================================================
echo VariancePro Test Suite - Timescale Analysis Tests
echo ======================================================
echo.

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Python is not installed or not in the PATH. Please install Python.
    exit /b 1
)

REM Create directories if needed
if not exist "test_logs" mkdir test_logs

echo Running test suite with timestamped reports...
echo.

REM Run the test suite
python run_test_suite.py

echo.
echo ======================================================
echo Test reports available in the test_logs directory
echo ======================================================

REM Open the test_logs directory
explorer test_logs
