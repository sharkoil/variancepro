#!/usr/bin/env python3
"""
Rebranding script to change Quant Commander to Quant Commander
This script will update all references across the codebase
"""

import os
import re
import json
from pathlib import Path

def update_file_content(file_path: str, replacements: dict) -> bool:
    """
    Update file content with the specified replacements
    
    Args:
        file_path: Path to the file to update
        replacements: Dictionary of old_text -> new_text replacements
        
    Returns:
        bool: True if file was modified, False otherwise
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        original_content = content
        
        # Apply all replacements
        for old_text, new_text in replacements.items():
            content = content.replace(old_text, new_text)
        
        # Only write if content changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
        
    except Exception as e:
        print(f"Error updating {file_path}: {e}")
        return False

def get_rebranding_replacements() -> dict:
    """Get all text replacements for rebranding"""
    return {
        # Application names
        'Quant Commander': 'Quant Commander',
        'quantcommander': 'quantcommander',
        'QUANTCOMMANDER': 'QUANTCOMMANDER',
        'quant_commander': 'quant_commander',
        'Quant Commander v2.0': 'Quant Commander v2.0',
        
        # Descriptions and titles
        'Advanced quantitative analysis and trading command center': 'Advanced quantitative analysis and trading command center',
        'AI-Powered Quantitative Trading Analysis & Command Center': 'AI-Powered Quantitative Trading Analysis & Command Center',
        'quantitative analysis': 'quantitative analysis',
        'Quantitative analysis': 'Quantitative analysis',
        'QUANTITATIVE ANALYSIS': 'QUANTITATIVE ANALYSIS',
        
        # File and project references
        'f:\\Projects\\QUANTCOMMANDER': 'f:\\Projects\\QUANTCOMMANDER',
        'Projects/QUANTCOMMANDER': 'Projects/QUANTCOMMANDER',
        '/QUANTCOMMANDER/': '/QUANTCOMMANDER/',
        
        # URLs and repositories
        'https://github.com/sharkoil/quantcommander.git': 'https://github.com/sharkoil/quantcommander.git',
        'sharkoil/quantcommander': 'sharkoil/quantcommander',
        
        # Class and function references
        'QuantCommanderApp': 'QuantCommanderApp',
        'QuantAnalyzer': 'QuantAnalyzer',
        'quant_analyzer': 'quant_analyzer',
        
        # Documentation and branding
        'Quantitative Trading Analysis': 'Quantitative Trading Analysis',
        'quantitative trading and forecasting': 'quantitative trading and forecasting',
        'Quantitative trading analysis': 'Quantitative trading analysis',
        'trading data': 'trading data',
        'Quant Commander': 'Quant Commander'
    }

def rebrand_application():
    """Main rebranding function"""
    print("🔄 Rebranding Quant Commander to Quant Commander...")
    print("=" * 60)
    
    # Get all replacements
    replacements = get_rebranding_replacements()
    
    # File extensions to process
    target_extensions = ['.py', '.md', '.txt', '.json', '.csv', '.yml', '.yaml', '.html', '.css', '.js']
    
    # Files to skip (binary or problematic files)
    skip_patterns = [
        '__pycache__',
        '.git',
        '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico',
        '.woff', '.woff2', '.ttf', '.eot',
        'node_modules',
        '.pyc'
    ]
    
    updated_files = []
    
    # Process all files in the project
    for root, dirs, files in os.walk('.'):
        # Skip certain directories
        dirs[:] = [d for d in dirs if not any(pattern in d for pattern in skip_patterns)]
        
        for file in files:
            file_path = os.path.join(root, file)
            
            # Skip files with certain patterns
            if any(pattern in file_path for pattern in skip_patterns):
                continue
                
            # Only process text files
            if any(file.endswith(ext) for ext in target_extensions):
                if update_file_content(file_path, replacements):
                    updated_files.append(file_path)
                    print(f"✅ Updated: {file_path}")
    
    print(f"\n📊 Rebranding Summary:")
    print(f"   Files updated: {len(updated_files)}")
    print(f"   Total replacements: {len(replacements)}")
    
    # Update specific configuration files
    update_specific_configs()
    
    print("\n🎯 Rebranding complete!")
    print("📋 Next steps:")
    print("   1. Update repository name on GitHub")
    print("   2. Update any external references")
    print("   3. Test the application")
    print("   4. Update documentation")

def update_specific_configs():
    """Update specific configuration files that need special handling"""
    print("\n🔧 Updating specific configuration files...")
    
    # Update manifest.json files
    manifest_files = ['manifest.json', 'static/manifest.json']
    for manifest_file in manifest_files:
        if os.path.exists(manifest_file):
            try:
                with open(manifest_file, 'r') as f:
                    data = json.load(f)
                
                # Update manifest content
                data['name'] = 'Quant Commander'
                data['short_name'] = 'QuantCmd'
                data['description'] = 'Advanced quantitative analysis and trading command center'
                
                with open(manifest_file, 'w') as f:
                    json.dump(data, f, indent=2)
                
                print(f"✅ Updated manifest: {manifest_file}")
                
            except Exception as e:
                print(f"❌ Error updating {manifest_file}: {e}")
    
    # Update package.json if it exists
    if os.path.exists('package.json'):
        try:
            with open('package.json', 'r') as f:
                data = json.load(f)
            
            data['name'] = 'quant-commander'
            data['description'] = 'Advanced quantitative analysis and trading command center'
            
            with open('package.json', 'w') as f:
                json.dump(data, f, indent=2)
            
            print("✅ Updated package.json")
            
        except Exception as e:
            print(f"❌ Error updating package.json: {e}")

if __name__ == "__main__":
    rebrand_application()
