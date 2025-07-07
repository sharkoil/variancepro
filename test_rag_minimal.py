"""Minimal test to isolate RAG issues"""
import sys
print("Testing minimal imports...")

try:
    print("Testing basic imports...")
    import os, uuid, hashlib, datetime, json, re
    print("✅ Basic imports OK")
    
    import pandas as pd
    print("✅ Pandas OK")
    
    import requests
    print("✅ Requests OK")
    
    # Test PDF imports
    try:
        import PyPDF2
        print("✅ PyPDF2 available")
    except ImportError:
        print("⚠️ PyPDF2 not available")
    
    try:
        import fitz
        print("✅ PyMuPDF available")
    except ImportError:
        print("⚠️ PyMuPDF not available")
    
    print("Now testing RAG manager class...")
    
    # Import the class definition without initializing
    sys.path.append('.')
    from analyzers.rag_document_manager import RAGDocumentManager
    print("✅ RAGDocumentManager class imported")
    
    print("Testing initialization...")
    manager = RAGDocumentManager()
    print("✅ RAGDocumentManager initialized")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
