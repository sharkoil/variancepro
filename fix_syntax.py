"""
A script to fix the syntax error in app.py
"""
import sys
import re

def fix_syntax(input_file, output_file):
    """Fix the syntax error in app.py"""
    print(f"Fixing {input_file}...")
    
    with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    
    # Variables to track parentheses
    open_count = 0
    line_tracking = []
    
    # Process each line
    for i, line in enumerate(lines):
        line_num = i + 1
        opens = line.count('(')
        closes = line.count(')')
        
        open_count += opens - closes
        
        if opens > 0 or closes > 0:
            line_tracking.append(f"Line {line_num}: {open_count} after '{line.strip()}'")
        
        if open_count < 0:
            print(f"Found extra closing parenthesis at line {line_num}: {line.strip()}")
            print(f"Fixing line {line_num}...")
            
            # Remove the extra closing parenthesis
            last_paren_index = line.rindex(')')
            lines[i] = line[:last_paren_index] + line[last_paren_index+1:]
            
            # Update the count
            open_count += 1
    
    # Write the fixed content
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print(f"Fixed file saved to {output_file}")
    print(f"Final parenthesis balance: {open_count}")
    
    if open_count != 0:
        print("Warning: Parentheses are still unbalanced!")
    else:
        print("Success: Parentheses are now balanced!")

if __name__ == "__main__":
    fix_syntax("app.py", "app_fixed.py")
