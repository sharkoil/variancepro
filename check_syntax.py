"""
A script to check for syntax errors in a Python file
"""
import sys
import tokenize
from io import BytesIO

def check_syntax(filename):
    """Check a Python file for syntax errors"""
    print(f"Checking {filename}...")
    
    try:
        with open(filename, 'rb') as f:
            content = f.read()
            
        # Count parentheses
        paren_count = 0
        lines_with_parens = []
        
        # Tokenize the file
        tokens = list(tokenize.tokenize(BytesIO(content).readline))
        
        for token in tokens:
            if token.string == '(':
                paren_count += 1
                lines_with_parens.append((token.start[0], 'open'))
            elif token.string == ')':
                paren_count -= 1
                lines_with_parens.append((token.start[0], 'close'))
                
                # Check for unmatched closing parenthesis
                if paren_count < 0:
                    print(f"Error: Unmatched closing parenthesis at line {token.start[0]}")
                    break
        
        if paren_count > 0:
            print(f"Error: {paren_count} unclosed parentheses")
            # Print the last 5 unclosed parentheses
            open_parens = [line for line, type in lines_with_parens if type == 'open']
            print(f"Open parentheses at lines: {open_parens[-5:]}")
        elif paren_count < 0:
            print(f"Error: {abs(paren_count)} extra closing parentheses")
        else:
            print("No parentheses issues found")
            
    except Exception as e:
        print(f"Error checking file: {e}")

if __name__ == "__main__":
    check_syntax("app.py")
