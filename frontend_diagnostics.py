#!/usr/bin/env python3
"""
Comprehensive frontend diagnostics for Quant Commander
"""

import os
import sys
import json
import subprocess
import importlib.util
from pathlib import Path

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        'gradio',
        'pandas',
        'numpy',
        'tabulate',
        'requests',
        'sqlite3',
        'datetime',
        'typing',
        'concurrent.futures'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'sqlite3':
                import sqlite3
            elif package == 'datetime':
                import datetime
            elif package == 'typing':
                import typing
            elif package == 'concurrent.futures':
                import concurrent.futures
            else:
                __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - MISSING")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️ Missing packages: {', '.join(missing_packages)}")
        return False
    else:
        print("\n✅ All dependencies are available")
        return True

def check_static_files():
    """Check static files and resources"""
    print("\n🔍 Checking static files...")
    
    static_dir = Path("static")
    if not static_dir.exists():
        print("❌ Static directory doesn't exist")
        return False
    
    expected_files = [
        "logo.png",
        "user_avatar.svg",
        "ai_avatar.svg"
    ]
    
    missing_files = []
    for file in expected_files:
        file_path = static_dir / file
        if file_path.exists():
            size = file_path.stat().st_size
            print(f"✅ {file} ({size} bytes)")
        else:
            print(f"❌ {file} - MISSING")
            missing_files.append(file)
    
    # Check for unexpected files
    actual_files = [f.name for f in static_dir.iterdir() if f.is_file()]
    unexpected_files = [f for f in actual_files if f not in expected_files and f != "avatar_preview.html"]
    
    if unexpected_files:
        print(f"ℹ️ Additional files found: {', '.join(unexpected_files)}")
    
    return len(missing_files) == 0

def check_gradio_version():
    """Check Gradio version for compatibility"""
    print("\n🔍 Checking Gradio version...")
    
    try:
        import gradio as gr
        version = gr.__version__
        print(f"✅ Gradio version: {version}")
        
        # Check if version is compatible (4.x is recommended)
        major_version = int(version.split('.')[0])
        if major_version >= 4:
            print("✅ Gradio version is compatible")
            return True
        else:
            print("⚠️ Gradio version might be outdated - recommend upgrading to 4.x")
            return False
    except Exception as e:
        print(f"❌ Error checking Gradio version: {e}")
        return False

def check_port_availability():
    """Check if the default port is available"""
    print("\n🔍 Checking port availability...")
    
    import socket
    
    ports_to_check = [7873, 7874, 7875]
    
    for port in ports_to_check:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        
        if result == 0:
            print(f"❌ Port {port} is already in use")
        else:
            print(f"✅ Port {port} is available")
    
    return True

def check_module_imports():
    """Check if all custom modules can be imported"""
    print("\n🔍 Checking module imports...")
    
    modules_to_check = [
        'core.app_core',
        'handlers.file_handler',
        'handlers.chat_handler',
        'handlers.quick_action_handler',
        'analyzers.quant_analyzer',
        'analyzers.rag_document_manager',
        'analyzers.rag_enhanced_analyzer',
        'utils.cache_manager',
        'utils.performance_monitor',
        'analyzers.forecast_analyzer'
    ]
    
    failed_imports = []
    
    for module in modules_to_check:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module} - {e}")
            failed_imports.append(module)
        except Exception as e:
            print(f"⚠️ {module} - {e}")
    
    if failed_imports:
        print(f"\n❌ Failed imports: {', '.join(failed_imports)}")
        return False
    else:
        print("\n✅ All modules can be imported")
        return True

def check_ollama_connection():
    """Check Ollama connection"""
    print("\n🔍 Checking Ollama connection...")
    
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            print(f"✅ Ollama connected - {len(models)} models available")
            
            # Check for gemma3 model
            model_names = [m.get('name', '') for m in models]
            if any('gemma3' in name for name in model_names):
                print("✅ gemma3 model found")
            else:
                print("⚠️ gemma3 model not found")
            
            return True
        else:
            print(f"❌ Ollama connection failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ollama connection error: {e}")
        return False

def generate_diagnostic_report():
    """Generate a comprehensive diagnostic report"""
    print("🔍 Quant Commander Frontend Diagnostics")
    print("=" * 50)
    
    checks = [
        ("Dependencies", check_dependencies),
        ("Static Files", check_static_files),
        ("Gradio Version", check_gradio_version),
        ("Port Availability", check_port_availability),
        ("Module Imports", check_module_imports),
        ("Ollama Connection", check_ollama_connection)
    ]
    
    results = {}
    
    for check_name, check_func in checks:
        try:
            results[check_name] = check_func()
        except Exception as e:
            print(f"❌ Error during {check_name} check: {e}")
            results[check_name] = False
    
    print("\n" + "=" * 50)
    print("📊 DIAGNOSTIC SUMMARY")
    print("=" * 50)
    
    for check_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{check_name}: {status}")
    
    overall_status = all(results.values())
    print(f"\n🎯 Overall Status: {'✅ ALL CHECKS PASSED' if overall_status else '❌ SOME CHECKS FAILED'}")
    
    if not overall_status:
        print("\n🔧 Recommendations:")
        print("1. Install missing dependencies: pip install -r requirements.txt")
        print("2. Check static files are present and accessible")
        print("3. Ensure Ollama is running: ollama serve")
        print("4. Update Gradio if needed: pip install --upgrade gradio")
        print("5. Check for port conflicts")
    
    return overall_status

if __name__ == "__main__":
    generate_diagnostic_report()
