"""
AI layer for Quant Commander
Provides LLM integration and narrative generation
"""

from .llm_interpreter import LLMInterpreter
from .narrative_generator import NarrativeGenerator

__all__ = ['LLMInterpreter', 'NarrativeGenerator']
