"""
Fix the syntax error in app.py by creating a new version
"""

def process_app_py():
    with open('app.py', 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    
    # Fix the specific line
    fixed_lines = []
    
    # Counter for parentheses balance
    paren_balance = 0
    
    for i, line in enumerate(lines):
        # Skip specific lines with known issues
        if i == 512:  # Line 513 (0-indexed)
            # Fix the backgroundColor line
            fixed_line = "                'backgroundColor': color.replace('rgb', 'rgba').replace(')', ', 0.5)'),\n"
            fixed_lines.append(fixed_line)
            continue
        
        # Count parentheses in this line
        opens = line.count('(')
        closes = line.count(')')
        
        paren_balance += opens - closes
        
        # Add the line
        fixed_lines.append(line)
    
    # Write the fixed content
    with open('app_fixed_manual.py', 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)
    
    print(f"Fixed file saved with final parenthesis balance: {paren_balance}")

if __name__ == "__main__":
    process_app_py()
