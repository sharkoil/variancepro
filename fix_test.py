import re

# Read the file with proper encoding
with open('test_date_column_detection.py', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# Replace the method name
fixed_content = content.replace('.find_date_column(', '.detect_date_column(')

# Write back
with open('test_date_column_detection.py', 'w', encoding='utf-8') as f:
    f.write(fixed_content)

print("Fixed test_date_column_detection.py")
