import re

def fix_app_py():
    with open('app.py', 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Use regex to find and fix the problematic line
    pattern = r"'backgroundColor': color\.replace\('rgb', 'rgba'\)\.replace\('\)', ', 0\.5\)'\)"
    replacement = "'backgroundColor': color.replace('rgb', 'rgba').replace(')', ', 0.5)')"
    
    # Fix the content
    fixed_content = re.sub(pattern, replacement, content)
    
    # Save the fixed content
    with open('app_fixed.py', 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print("Fixed file saved as app_fixed.py")

if __name__ == "__main__":
    fix_app_py()
