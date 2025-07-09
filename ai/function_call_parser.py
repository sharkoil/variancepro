"""
Function Call Parser for Quant Commander Gemma 3 Function Calling
Parses function calls from LLM responses based on specified formats.
"""

import json
import re
from typing import List, Dict, Any

class FunctionCallParser:
    """Parses function calls from Gemma 3 LLM responses."""

    def parse(self, response_text: str) -> List[Dict[str, Any]]:
        """Parses function calls from the LLM response text."""
        # Gemma prefers JSON format, so we prioritize that.
        return self._parse_json_format(response_text)

    def _parse_json_format(self, text: str) -> List[Dict[str, Any]]:
        """Parses JSON-formatted function calls from the text."""
        function_calls = []
        # Regex to find JSON objects that look like function calls
        json_pattern = r'\{\s*"name"\s*:\s*"[^"]+"\s*,\s*"parameters"\s*:\s*\{[^}]*\}\s*\}'
        matches = re.findall(json_pattern, text, re.DOTALL)

        for match in matches:
            try:
                call_obj = json.loads(match)
                if "name" in call_obj and "parameters" in call_obj:
                    function_calls.append(call_obj)
            except json.JSONDecodeError:
                # Ignore parts of the text that look like JSON but aren't valid
                continue
        
        return function_calls

# Create a global instance for easy access
function_call_parser = FunctionCallParser()
