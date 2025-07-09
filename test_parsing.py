#!/usr/bin/env python3
"""
Simple test for top N parsing
"""

import re

def test_top_n_parsing():
    """Test the new parsing logic"""
    
    test_queries = [
        "top 5 by State",
        "top 2 by Budget", 
        "bottom 2 analysis",
        "top provide bottom 2 analysis",
        "top 5",
        "bottom 3",
        "show me top 10"
    ]
    
    def is_top_bottom_query(message):
        """Simplified version of the detection logic"""
        message_lower = message.lower().strip()
        
        # Pattern 1: "top N" or "bottom N" where N is a number
        pattern1 = r'\b(top|bottom)\s+(\d+)\b'
        if re.search(pattern1, message_lower):
            return True
            
        # Pattern 2: "top N by column" or "bottom N by column"
        pattern2 = r'\b(top|bottom)\s+(\d+)\s+by\s+\w+'
        if re.search(pattern2, message_lower):
            return True
            
        # Pattern 3: Common phrases
        top_bottom_phrases = [
            'show me top', 'show me bottom', 'give me top', 'give me bottom',
            'what are the top', 'what are the bottom', 'find top', 'find bottom',
            'highest values', 'lowest values'
        ]
        
        for phrase in top_bottom_phrases:
            if phrase in message_lower:
                return True
                
        return False
    
    def parse_top_bottom_query(message):
        """Parse the query to extract action"""
        message_lower = message.lower().strip()
        
        # Pattern for "top N by column" or "bottom N by column"
        pattern_with_column = r'\b(top|bottom)\s+(\d+)\s+by\s+(\w+)'
        match_with_column = re.search(pattern_with_column, message_lower)
        
        if match_with_column:
            direction = match_with_column.group(1)
            n = int(match_with_column.group(2))
            column = match_with_column.group(3)
            return f"{direction} {n} by {column}"
        else:
            # Pattern for "top N" or "bottom N" without column
            pattern_simple = r'\b(top|bottom)\s+(\d+)'
            match_simple = re.search(pattern_simple, message_lower)
            
            if match_simple:
                direction = match_simple.group(1)
                n = int(match_simple.group(2))
                return f"{direction} {n}"
            else:
                # Fallback
                numbers = re.findall(r'\d+', message)
                n = int(numbers[0]) if numbers else 5
                
                if any(word in message_lower for word in ['top', 'highest', 'best', 'largest']):
                    return f"top {n}"
                else:
                    return f"bottom {n}"
    
    print("🔍 Testing Top N Query Parsing")
    print("=" * 50)
    
    for query in test_queries:
        is_detected = is_top_bottom_query(query)
        if is_detected:
            parsed_action = parse_top_bottom_query(query)
            print(f"✅ '{query}' → detected → '{parsed_action}'")
        else:
            print(f"❌ '{query}' → NOT detected")
    
    print("\n🎯 Parsing test complete!")

if __name__ == "__main__":
    test_top_n_parsing()
