#!/usr/bin/env python3
"""
File Organization Script for Quant Commander
Moves sample data files to the correct folders
"""

import os
import shutil
from pathlib import Path

def organize_files():
    """Move sample files to appropriate directories"""
    root_dir = Path(__file__).parent
    sample_data_dir = root_dir / "sample_data"
    
    # Ensure sample_data directory exists
    sample_data_dir.mkdir(exist_ok=True)
    
    # Files to move to sample_data
    sample_files = [
        "sample_variance_data.csv",
        "sample_variance_data.xlsx",
        "comprehensive_sales_data.csv",
        "sales_budget_actuals.csv",
        "sample_stock_data.csv"
    ]
    
    moved_files = []
    
    for filename in sample_files:
        source = root_dir / filename
        destination = sample_data_dir / filename
        
        if source.exists() and not destination.exists():
            try:
                shutil.move(str(source), str(destination))
                moved_files.append(filename)
                print(f"✅ Moved {filename} to sample_data/")
            except (PermissionError, OSError) as e:
                print(f"⚠️ Could not move {filename}: {e}")
                print(f"   (File may be open in another application)")
    
    if moved_files:
        print(f"\n🎉 Successfully organized {len(moved_files)} files!")
    else:
        print("ℹ️ All files are already in the correct locations.")

if __name__ == "__main__":
    organize_files()
