#!/usr/bin/env python3
"""
GenAI Legacy Code Understanding & Risk Analyzer
Main entry point for the application
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.app import app
import uvicorn

if __name__ == "__main__":
    print("=" * 60)
    print("GenAI Legacy Code Understanding & Risk Analyzer")
    print("=" * 60)
    print(f"Version: 1.0.0")
    print(f"API: http://127.0.0.1:8000")
    print(f"Docs: http://127.0.0.1:8000/docs")
    print("=" * 60)
    
    uvicorn.run(
        "ui.app:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )