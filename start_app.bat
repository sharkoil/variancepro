@echo off
echo 💼 VariancePro Financial Chat App - Fresh Start
echo ================================================

cd /d "%~dp0"

echo 🔍 Checking Python...
python --version
if %errorlevel% neq 0 (
    echo ❌ Python not found
    pause
    exit /b 1
)

echo 🔍 Checking Ollama...
curl -s http://localhost:11434/api/tags > nul
if %errorlevel% neq 0 (
    echo ⚠️ Ollama not running - will use built-in analysis only
) else (
    echo ✅ Ollama is running
    echo 🔍 Checking for deepseek-coder:6.7b model...
    curl -s http://localhost:11434/api/tags | findstr "deepseek-coder:6.7b" > nul
    if %errorlevel% neq 0 (
        echo ⚠️ deepseek-coder:6.7b not found - will use other available models or built-in analysis
        echo 💡 To install: ollama pull deepseek-coder:6.7b
    ) else (
        echo ✅ deepseek-coder:6.7b model is available
    )
)

echo 🚀 Starting the app...
python app.py

echo 👋 App finished
pause
