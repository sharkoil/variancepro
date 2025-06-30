# Setup script for Aria Sterling narrative generation

import os
import sys
from pathlib import Path

def setup_narrative_generator():
    """Set up the Aria Sterling narrative generation module"""
    # Check for utils directory
    utils_dir = Path("utils")
    if not utils_dir.exists():
        print("Creating utils directory...")
        utils_dir.mkdir(exist_ok=True)
    
    # Check for __init__.py in utils
    init_file = utils_dir / "__init__.py"
    if not init_file.exists():
        print("Creating utils/__init__.py...")
        with open(init_file, "w") as f:
            f.write("# Utils package initialization\n")
    
    print("\n✅ Narrative generation setup complete!")
    print("✅ Aria Sterling financial analyst persona is ready to provide insights")
    print("\nTo use:")
    print("1. Upload your financial CSV data")
    print("2. Aria will automatically analyze time series patterns")
    print("3. Ask follow-up questions to explore your data further")
    print("\nEnjoy enhanced financial analysis with your AI analyst!")

if __name__ == "__main__":
    setup_narrative_generator()
