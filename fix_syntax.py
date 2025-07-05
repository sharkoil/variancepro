#!/usr/bin/env python3
"""
Script to fix the syntax error in llm_interpreter.py
"""

def fix_llm_interpreter():
    """Fix the missing closing braces in llm_interpreter.py"""
    
    # Read the current file
    with open('ai/llm_interpreter.py', 'r') as f:
        lines = f.readlines()
    
    # Find the line with the problematic 'max_tokens' entry
    for i, line in enumerate(lines):
        if "'max_tokens': self.ollama_config['options']['num_predict']," in line:
            # Insert the missing lines after this line
            missing_lines = [
                "                'timeout': self.ollama_config['timeout']\n",
                "            }\n",
                "        }\n",
                "    \n",
                "    def clear_history(self):\n",
                '        """Clear conversation history"""\n',
                "        self.conversation_history = []\n",
                "    \n"
            ]
            
            # Insert the missing lines
            for j, missing_line in enumerate(missing_lines):
                lines.insert(i + 1 + j, missing_line)
            
            break
    
    # Write the fixed file
    with open('ai/llm_interpreter.py', 'w') as f:
        f.writelines(lines)
    
    print("✅ Fixed llm_interpreter.py syntax error")

if __name__ == "__main__":
    fix_llm_interpreter()
