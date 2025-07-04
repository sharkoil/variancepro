"""
Settings management for VariancePro application
Provides centralized configuration for all components
"""

import os
from typing import List, Optional
from dataclasses import dataclass


@dataclass
class Settings:
    """
    Application configuration settings
    """
    
    # Application Information
    app_name: str = "VariancePro"
    app_version: str = "1.0.0"
    
    # LLM Configuration
    llm_model: str = "gemma3:latest"
    ollama_host: str = "http://localhost:11434"
    llm_timeout: int = 180
    llm_temperature: float = 0.3
    llm_max_tokens: int = 2048
    llm_context_length: int = 8192
    
    # File Processing
    max_file_size: int = 50_000_000  # 50MB
    supported_formats: List[str] = None
    
    # UI Configuration
    gradio_port: int = 7860
    gradio_share: bool = False
    
    # Analysis Configuration
    contribution_threshold: float = 0.8  # For 80/20 analysis
    timescale_auto_detect: bool = True
    
    # Security & Privacy
    local_processing_only: bool = True
    no_code_suggestions: bool = True
    csv_only_analysis: bool = True
    
    # Function Calling Configuration
    enable_function_calling: bool = False  # Start disabled for safety
    function_calling_timeout: int = 30  # Timeout for function calling requests
    function_calling_confidence_threshold: float = 0.7  # Minimum confidence for function calls
    function_calling_query_types: List[str] = None  # Start empty, add progressively
    function_calling_fallback_always: bool = True  # Always fall back to existing methods
    function_calling_max_attempts: int = 3  # Max attempts for function calling
    
    def __post_init__(self):
        """Initialize default values that need to be mutable"""
        if self.supported_formats is None:
            self.supported_formats = ['.csv']
        if self.function_calling_query_types is None:
            self.function_calling_query_types = []  # Start with no enabled query types
    
    @classmethod
    def from_env(cls) -> 'Settings':
        """
        Create settings instance from environment variables
        
        Returns:
            Settings instance with values from environment
        """
        return cls(
            llm_model=os.getenv('VARIANCEPRO_LLM_MODEL', 'gemma3:latest'),
            ollama_host=os.getenv('OLLAMA_HOST', 'http://localhost:11434'),
            llm_timeout=int(os.getenv('VARIANCEPRO_LLM_TIMEOUT', '180')),
            gradio_port=int(os.getenv('GRADIO_SERVER_PORT', '7860')),
            gradio_share=os.getenv('GRADIO_SHARE', 'false').lower() == 'true',
            contribution_threshold=float(os.getenv('VARIANCEPRO_CONTRIBUTION_THRESHOLD', '0.8')),
            enable_function_calling=os.getenv('VARIANCEPRO_ENABLE_FUNCTION_CALLING', 'false').lower() == 'true',
            function_calling_confidence_threshold=float(os.getenv('VARIANCEPRO_FUNCTION_CALLING_THRESHOLD', '0.7')),
        )
    
    def validate(self) -> bool:
        """
        Validate configuration settings
        
        Returns:
            True if configuration is valid
            
        Raises:
            ValueError: If configuration is invalid
        """
        if self.llm_timeout <= 0:
            raise ValueError("LLM timeout must be positive")
        
        if not (0.0 <= self.llm_temperature <= 2.0):
            raise ValueError("LLM temperature must be between 0.0 and 2.0")
        
        if self.max_file_size <= 0:
            raise ValueError("Max file size must be positive")
        
        if not (0.1 <= self.contribution_threshold <= 1.0):
            raise ValueError("Contribution threshold must be between 0.1 and 1.0")
        
        if not (1024 <= self.gradio_port <= 65535):
            raise ValueError("Gradio port must be between 1024 and 65535")
        
        return True
    
    def get_ollama_config(self) -> dict:
        """
        Get configuration dictionary for Ollama client
        
        Returns:
            Dictionary with Ollama configuration
        """
        return {
            'host': self.ollama_host,
            'timeout': self.llm_timeout,
            'model': self.llm_model,
            'options': {
                'temperature': self.llm_temperature,
                'num_predict': self.llm_max_tokens,
                'num_ctx': self.llm_context_length,
                'top_k': 40,
                'top_p': 0.9,
            }
        }
    
    def get_gradio_config(self) -> dict:
        """
        Get configuration dictionary for Gradio interface
        
        Returns:
            Dictionary with Gradio configuration
        """
        return {
            'server_port': self.gradio_port,
            'share': self.gradio_share,
            'show_error': True,
            'show_tips': True,
        }
    
    def get_function_calling_config(self) -> dict:
        """
        Get configuration dictionary for function calling
        
        Returns:
            Dictionary with function calling configuration
        """
        return {
            'enabled': self.enable_function_calling,
            'timeout': self.function_calling_timeout,
            'confidence_threshold': self.function_calling_confidence_threshold,
            'query_types': self.function_calling_query_types,
            'fallback_always': self.function_calling_fallback_always,
            'max_attempts': self.function_calling_max_attempts
        }
    
    def enable_function_calling_for_query_type(self, query_type: str):
        """
        Enable function calling for a specific query type
        
        Args:
            query_type: Type of query to enable (e.g., 'time_variance', 'contribution')
        """
        if query_type not in self.function_calling_query_types:
            self.function_calling_query_types.append(query_type)
    
    def disable_function_calling_for_query_type(self, query_type: str):
        """
        Disable function calling for a specific query type
        
        Args:
            query_type: Type of query to disable
        """
        if query_type in self.function_calling_query_types:
            self.function_calling_query_types.remove(query_type)
