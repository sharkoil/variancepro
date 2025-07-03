@echo off
echo 💼 Quant Commander Financial Chat App - Fresh Start
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
    echo 🔍 Checking for gemma3:latest model...
    curl -s http://localhost:11434/api/tags | findstr "gemma3:latest" > nul
    if %errorlevel% neq 0 (
        echo ⚠️ gemma3:latest not found - will use other available models or built-in analysis
        echo 💡 To install: ollama pull gemma3:latest
    ) else (
        echo ✅ gemma3:latest model is available
    )
)

echo 🚀 Starting the app...
python app_new.py

echo 👋 App finished
pause
