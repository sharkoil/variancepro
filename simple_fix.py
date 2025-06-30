"""
Simple script to fix app.py
"""
import re

# Read the file
with open('app.py', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# Fix the specific issue with the rgba string replacement
content = content.replace("color.replace('rgb', 'rgba').replace(')', ', 0.5)'),", 
                          "color.replace('rgb', 'rgba').replace(')', ', 0.5)'),")

# Save the fixed content
with open('app_fixed.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed file saved as app_fixed.py")
