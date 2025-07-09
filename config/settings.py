"""
Settings management for Quant Commander application
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
    app_name: str = "Quant Commander"
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
    
    def __post_init__(self):
        """Initialize default values that need to be mutable"""
        if self.supported_formats is None:
            self.supported_formats = ['.csv']
    
    @classmethod
    def from_env(cls) -> 'Settings':
        """
        Create settings instance from environment variables
        
        Returns:
            Settings instance with values from environment
        """
        return cls(
            llm_model=os.getenv('QUANTCOMMANDER_LLM_MODEL', 'gemma3:latest'),
            ollama_host=os.getenv('OLLAMA_HOST', 'http://localhost:11434'),
            llm_timeout=int(os.getenv('QUANTCOMMANDER_LLM_TIMEOUT', '180')),
            gradio_port=int(os.getenv('GRADIO_SERVER_PORT', '7860')),
            gradio_share=os.getenv('GRADIO_SHARE', 'false').lower() == 'true',
            contribution_threshold=float(os.getenv('QUANTCOMMANDER_CONTRIBUTION_THRESHOLD', '0.8')),
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


# Global settings instance
_settings_instance = None


def get_settings() -> Settings:
    """
    Get the global settings instance.
    
    Returns:
        Settings instance
    """
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = Settings.from_env()
    return _settings_instance


def reset_settings():
    """
    Reset the global settings instance (useful for testing).
    """
    global _settings_instance
    _settings_instance = None
