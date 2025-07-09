"""
Ollama API Connector for Quant Commander v2.0

This module handles all Ollama API interactions including:
- Connection status checking
- Model availability verification  
- API call management
- Error handling for Ollama requests

Extracted from app_v2.py to follow modular design principles.
"""

import requests
from typing import Dict, Any, Optional


class OllamaConnector:
    """
    Manages connections and interactions with the Ollama API server.
    
    This class encapsulates all Ollama-related functionality to keep
    the main application code clean and focused.
    """
    
    def __init__(self, base_url: str = "http://localhost:11434", model_name: str = "gemma3:latest"):
        """
        Initialize the Ollama connector.
        
        Args:
            base_url (str): The base URL for the Ollama API server
            model_name (str): The name of the model to use for generation
        """
        self.ollama_url = base_url  # Keep this name for backward compatibility
        self.base_url = base_url
        self.model_name = model_name
        
    def check_connection(self) -> str:
        """
        Check if Ollama is running and the specified model is available.
        
        Returns:
            str: Status message indicating connection state
                - "✅ Connected (model_name)" if everything is working
                - "⚠️ Model {model_name} not found" if model is missing
                - "❌ Ollama not responding" if server is unreachable
                - "❌ Ollama not running" if connection fails
        """
        try:
            # Check if Ollama server is running by getting available models
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [model['name'] for model in models]
                
                if self.model_name in model_names:
                    return f"✅ Connected ({self.model_name})"
                else:
                    return f"⚠️ Model {self.model_name} not found"
            else:
                return "❌ Ollama not responding"
                
        except requests.exceptions.RequestException:
            return "❌ Ollama not running"
    
    def generate_response(self, prompt: str, **kwargs) -> str:
        """
        Generate a response from the Ollama model.
        
        Args:
            prompt (str): The input prompt to send to the model
            **kwargs: Additional parameters for the generation request
            
        Returns:
            str: The generated response text, or an error message if the request fails
        """
        try:
            # Prepare the request payload
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                **kwargs  # Allow override of default parameters
            }
            
            # Make the API call to generate response
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=30  # 30 second timeout for generation
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', 'No response from model')
            else:
                return f"Error: Ollama API returned status {response.status_code}"
                
        except requests.exceptions.RequestException as e:
            return f"Error calling Ollama: {str(e)}"
    
    def is_available(self) -> bool:
        """
        Check if Ollama is available and ready to use.
        
        Returns:
            bool: True if Ollama is connected and model is available, False otherwise
        """
        status = self.check_connection()
        return status.startswith("✅")
    
    def get_model_info(self) -> Optional[Dict[str, Any]]:
        """
        Get information about the current model.
        
        Returns:
            Dict[str, Any]: Model information if available, None if not accessible
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            
            if response.status_code == 200:
                models = response.json().get('models', [])
                for model in models:
                    if model['name'] == self.model_name:
                        return model
                        
        except requests.exceptions.RequestException:
            pass
            
        return None
    
    def get_status(self) -> str:
        """
        Get the current connection status (alias for check_connection).
        
        Returns:
            str: Status message indicating connection state
        """
        return self.check_connection()
    
    def call_ollama(self, prompt: str) -> str:
        """
        Call Ollama API with the given prompt (alias for generate_response).
        
        Args:
            prompt (str): The input prompt to send to the model
            
        Returns:
            str: The generated response text, or an error message if the request fails
        """
        return self.generate_response(prompt)
