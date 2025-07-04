"""
LLM Interpreter for VariancePro
Handles LLM communication and response processing
"""

import requests
import json
import time
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
from config.settings import Settings


@dataclass
class LLMResponse:
    """Structured LLM response"""
    content: str
    success: bool
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    processing_time: float = 0.0


class LLMError(Exception):
    """Custom exception for LLM errors"""
    pass


class LLMInterpreter:
    """
    Interface with LLM for data analysis queries
    Handles Ollama/Gemma3 communication and response processing
    """
    
    def __init__(self, settings: Settings):
        """
        Initialize LLM interpreter
        
        Args:
            settings: Application settings instance
        """
        self.settings = settings
        self.ollama_config = settings.get_ollama_config()
        self.model_name = settings.llm_model
        self.is_available = False
        self.last_error: Optional[str] = None
        self.conversation_history: List[Dict[str, str]] = []
        
        # Test connection on initialization
        self._test_connection()
    
    def _test_connection(self) -> bool:
        """
        Test connection to Ollama service
        
        Returns:
            True if connection successful
        """
        try:
            response = requests.get(
                f"{self.ollama_config['host']}/api/tags",
                timeout=5
            )
            
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [model['name'] for model in models]
                
                if any(self.model_name in name for name in model_names):
                    self.is_available = True
                    self.last_error = None
                    return True
                else:
                    self.last_error = f"Model '{self.model_name}' not found. Available models: {model_names}"
                    return False
            else:
                self.last_error = f"Ollama service returned status {response.status_code}"
                return False
                
        except requests.exceptions.ConnectionError:
            self.last_error = "Cannot connect to Ollama service. Please ensure Ollama is running."
            return False
        except requests.exceptions.Timeout:
            self.last_error = "Ollama service connection timeout"
            return False
        except Exception as e:
            self.last_error = f"Unexpected error testing Ollama connection: {str(e)}"
            return False
    
    def query_llm(self, question: str, context: Optional[Dict[str, Any]] = None) -> LLMResponse:
        """
        Send query to LLM and get response
        
        Args:
            question: User question or prompt
            context: Optional context data (dataset info, analysis results, etc.)
            
        Returns:
            LLMResponse with result
        """
        start_time = time.time()
        
        try:
            # Check if LLM is available
            if not self.is_available:
                return LLMResponse(
                    content="",
                    success=False,
                    error=f"LLM not available: {self.last_error}",
                    processing_time=time.time() - start_time
                )
            
            # Build prompt with context
            prompt = self._build_prompt(question, context)
            
            # Prepare request payload
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": self.ollama_config['options']
            }
            
            # Send request to Ollama
            response = requests.post(
                f"{self.ollama_config['host']}/api/generate",
                json=payload,
                timeout=self.ollama_config['timeout']
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result.get('response', '').strip()
                
                # Update conversation history
                self.conversation_history.append({
                    'user': question,
                    'assistant': content
                })
                
                # Keep history manageable
                if len(self.conversation_history) > 10:
                    self.conversation_history = self.conversation_history[-10:]
                
                return LLMResponse(
                    content=content,
                    success=True,
                    metadata={
                        'model': self.model_name,
                        'prompt_length': len(prompt),
                        'response_length': len(content),
                        'eval_count': result.get('eval_count', 0),
                        'eval_duration': result.get('eval_duration', 0)
                    },
                    processing_time=time.time() - start_time
                )
            else:
                error_msg = f"LLM request failed with status {response.status_code}"
                try:
                    error_details = response.json().get('error', 'Unknown error')
                    error_msg += f": {error_details}"
                except:
                    pass
                
                return LLMResponse(
                    content="",
                    success=False,
                    error=error_msg,
                    processing_time=time.time() - start_time
                )
                
        except requests.exceptions.Timeout:
            return LLMResponse(
                content="",
                success=False,
                error="LLM request timed out. The query may be too complex.",
                processing_time=time.time() - start_time
            )
        except requests.exceptions.ConnectionError:
            return LLMResponse(
                content="",
                success=False,
                error="Cannot connect to LLM service. Please check if Ollama is running.",
                processing_time=time.time() - start_time
            )
        except Exception as e:
            return LLMResponse(
                content="",
                success=False,
                error=f"Unexpected error in LLM communication: {str(e)}",
                processing_time=time.time() - start_time
            )
    
    def _build_prompt(self, question: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Build comprehensive prompt for LLM with strict formatting standards
        
        Args:
            question: User question
            context: Optional context data
            
        Returns:
            Formatted prompt string with formatting requirements
        """
        prompt_parts = []
        
        # System role and persona with strict formatting requirements
        prompt_parts.append(
            "You are Aria Sterling, a professional financial analyst and business intelligence expert. "
            "You provide clear, actionable insights from financial data analysis using standard business language. "
            "\nSTRICT FORMATTING REQUIREMENTS:\n"
            "• NEVER include code snippets, SQL queries, Python code, or any programming syntax\n"
            "• NEVER suggest technical solutions or programming approaches\n"
            "• ALWAYS state key assumptions clearly in your analysis\n"
            "• Use professional business language suitable for executives\n"
            "• Focus on business implications and actionable recommendations\n"
            "• Include specific numbers and percentages from analysis data\n"
            "• Structure responses with clear sections and bullet points\n"
            "• Avoid technical jargon and statistical terminology"
        )
        
        # Add context if provided
        if context:
            prompt_parts.append("\n=== DATASET CONTEXT ===")
            
            # Dataset overview
            if 'dataset_info' in context:
                info = context['dataset_info']
                prompt_parts.append(f"Dataset: {info.get('rows', 0):,} rows, {info.get('columns', 0)} columns")
                
                if 'column_types' in info:
                    prompt_parts.append(f"Available data types: {info['column_types']}")
                
                if 'date_range' in info:
                    prompt_parts.append(f"Time period: {info['date_range']}")
            
            # Analysis results
            if 'analysis_results' in context:
                prompt_parts.append("\n=== ANALYSIS RESULTS ===")
                results = context['analysis_results']
                
                # Format analysis results for LLM context
                if isinstance(results, dict):
                    for key, value in results.items():
                        if isinstance(value, (str, int, float)):
                            prompt_parts.append(f"{key}: {value}")
                        elif isinstance(value, dict) and 'summary' in value:
                            prompt_parts.append(f"{key}: {value['summary']}")
            
            # Previous conversation context
            if self.conversation_history:
                prompt_parts.append("\n=== CONVERSATION CONTEXT ===")
                # Include last 2 exchanges for context
                recent_history = self.conversation_history[-2:]
                for exchange in recent_history:
                    prompt_parts.append(f"Previous Q: {exchange['user']}")
                    prompt_parts.append(f"Previous A: {exchange['assistant'][:200]}...")
        
        # Current question
        prompt_parts.append(f"\n=== CURRENT QUESTION ===")
        prompt_parts.append(question)
        
        # Enhanced instructions with formatting standards
        prompt_parts.append(
            "\n=== RESPONSE REQUIREMENTS ===\n"
            "Provide a clear, professional financial analysis response that:\n\n"
            "CONTENT REQUIREMENTS:\n"
            "• Directly answers the user's question with specific business insights\n"
            "• Uses specific numbers, percentages, and metrics from the analysis data\n"
            "• Provides actionable business recommendations\n"
            "• Clearly states all assumptions made in the analysis\n"
            "• Focuses on business implications and strategic value\n\n"
            "FORMATTING REQUIREMENTS:\n"
            "• Use professional business language suitable for executives\n"
            "• Structure with clear sections and bullet points for readability\n"
            "• NO code snippets, SQL queries, Python syntax, or programming references\n"
            "• NO technical jargon or complex statistical terminology\n"
            "• Include assumption statements (e.g., 'Assuming standard business cycles...')\n"
            "• Format important findings with clear headers and bullet points\n\n"
            "PROHIBITED CONTENT:\n"
            "• Code examples or programming syntax of any kind\n"
            "• Technical implementation details\n"
            "• References to data manipulation techniques\n"
            "• Statistical formulas or mathematical notation\n\n"
            "Provide business-focused analysis suitable for strategic decision-making.\n\n"
            "Response:"
        )
        
        return "\n".join(prompt_parts)
    
    def process_response(self, raw_response: str) -> Dict[str, Any]:
        """
        Process and structure LLM response
        
        Args:
            raw_response: Raw LLM response text
            
        Returns:
            Structured response dictionary
        """
        processed = {
            'content': raw_response.strip(),
            'formatted_content': '',
            'key_insights': [],
            'recommendations': [],
            'data_points': []
        }
        
        # Clean up response
        content = raw_response.strip()
        
        # Extract key insights (look for bullet points or numbered lists)
        insights = []
        recommendations = []
        data_points = []
        
        lines = content.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detect sections
            line_lower = line.lower()
            if any(word in line_lower for word in ['insight', 'finding', 'key point']):
                current_section = 'insights'
            elif any(word in line_lower for word in ['recommend', 'suggest', 'action']):
                current_section = 'recommendations'
            elif any(word in line_lower for word in ['data', 'metric', 'number']):
                current_section = 'data_points'
            
            # Extract structured content
            if line.startswith(('•', '-', '*')) or line[0].isdigit():
                item = line.lstrip('•-*0123456789. ').strip()
                if current_section == 'insights':
                    insights.append(item)
                elif current_section == 'recommendations':
                    recommendations.append(item)
                elif current_section == 'data_points':
                    data_points.append(item)
                else:
                    insights.append(item)  # Default to insights
        
        # Format content with better structure
        formatted_lines = []
        for line in lines:
            line = line.strip()
            if line.startswith(('•', '-', '*')):
                formatted_lines.append(f"• {line.lstrip('•-* ').strip()}")
            elif line and line[0].isdigit() and '.' in line[:3]:
                formatted_lines.append(f"• {line.split('.', 1)[1].strip()}")
            elif line:
                formatted_lines.append(line)
        
        processed.update({
            'formatted_content': '\n'.join(formatted_lines),
            'key_insights': insights,
            'recommendations': recommendations,
            'data_points': data_points
        })
        
        return processed
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current LLM interpreter status
        
        Returns:
            Status dictionary
        """
        return {
            'available': self.is_available,
            'model': self.model_name,
            'host': self.ollama_config['host'],
            'last_error': self.last_error,
            'conversation_length': len(self.conversation_history),
            'settings': {
                'temperature': self.ollama_config['options']['temperature'],
                'max_tokens': self.ollama_config['options']['num_predict'],
                'timeout': self.ollama_config['timeout']
            }
        }
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
    
    def refresh_connection(self) -> bool:
        """
        Refresh connection to LLM service
        
        Returns:
            True if connection successful
        """
        return self._test_connection()
