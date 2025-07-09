"""
Quant Commander Core Application Logic
Handles main application initialization, state management, and component coordination
"""

import uuid
from typing import Optional, Dict, Any
from datetime import datetime

from .ollama_connector import OllamaConnector
from analyzers.timescale_analyzer import TimescaleAnalyzer
from analyzers.base_analyzer import AnalysisError
from analyzers.nl2sql_function_caller import NL2SQLFunctionCaller
from config.settings import Settings


class AppCore:
    """Core application logic and state management"""
    
    def __init__(self):
        """Initialize the core application components"""
        # Generate unique session ID
        self.session_id = str(uuid.uuid4())[:8]
        
        # Application state
        self.current_data: Optional[Any] = None
        self.data_summary: Optional[Dict] = None
        self.gradio_status: str = "Initializing"
        
        # Initialize Ollama connector
        self.ollama_connector = OllamaConnector()
        
        # Initialize analyzers for out-of-box analysis
        self._initialize_analyzers()
        
        # Update status
        self.gradio_status = "Running"
        
        # Log initialization
        self._log_startup()
    
    def _initialize_analyzers(self) -> None:
        """
        Initialize analysis components with comprehensive error handling.
        
        This method safely initializes all analyzers with graceful degradation.
        If any analyzer fails to initialize, the system continues with reduced functionality.
        """
        try:
            # Initialize settings first
            self.settings = Settings()
            print(f"[DEBUG] Settings initialized successfully")
        except Exception as e:
            print(f"❌ Settings initialization failed: {e}")
            self.settings = None
        
        # Initialize timescale analyzer with dependency check
        try:
            if self.settings is not None:
                self.timescale_analyzer = TimescaleAnalyzer(self.settings)
                print(f"[DEBUG] TimescaleAnalyzer initialized successfully")
            else:
                raise Exception("Settings not available")
        except Exception as e:
            print(f"⚠️ TimescaleAnalyzer initialization failed: {e}")
            print(f"   → Trends analysis will be unavailable")
            self.timescale_analyzer = None
        
        # Initialize NL2SQL engine with Ollama connection check
        try:
            if self.ollama_connector.is_available():
                self.nl2sql_engine = NL2SQLFunctionCaller(
                    self.ollama_connector.ollama_url, 
                    self.ollama_connector.model_name
                )
                print(f"[DEBUG] NL2SQL engine initialized successfully")
            else:
                raise Exception("Ollama not available")
        except Exception as e:
            print(f"⚠️ NL2SQL engine initialization failed: {e}")
            print(f"   → Advanced query processing will be unavailable")
            self.nl2sql_engine = None
        
        # Summary of analyzer status
        analyzer_count = sum([
            self.timescale_analyzer is not None,
            self.nl2sql_engine is not None
        ])
        print(f"[DEBUG] Analyzers initialized: {analyzer_count}/2 successful")
    
    def _log_startup(self) -> None:
        """Log application startup information"""
        print(f"🚀 Quant Commander v2.0 Core initialized")
        print(f"📝 Session ID: {self.session_id}")
        print(f"🤖 Ollama Status: {self.ollama_connector.get_status()}")
        print(f"⚙️ Gradio Status: {self.gradio_status}")
    
    @property
    def ollama_status(self) -> str:
        """Get current Ollama connection status"""
        return self.ollama_connector.get_status()
    
    def set_current_data(self, data: Any, summary: Optional[Dict] = None) -> None:
        """Set current data and optional summary"""
        self.current_data = data
        self.data_summary = summary
        print(f"[DEBUG] Data updated in session {self.session_id}")
    
    def get_current_data(self) -> tuple[Any, Optional[Dict]]:
        """Get current data and summary"""
        return self.current_data, self.data_summary
    
    def has_data(self) -> bool:
        """Check if data is currently loaded"""
        return self.current_data is not None
    
    def clear_data(self) -> None:
        """Clear current data and summary"""
        self.current_data = None
        self.data_summary = None
        print(f"[DEBUG] Data cleared in session {self.session_id}")
    
    def get_session_info(self) -> Dict[str, str]:
        """Get session information for debugging/logging"""
        return {
            'session_id': self.session_id,
            'ollama_status': self.ollama_status,
            'gradio_status': self.gradio_status,
            'has_data': str(self.has_data()),
            'timestamp': datetime.now().isoformat()
        }
    
    def call_ollama(self, prompt: str) -> str:
        """Proxy method to call Ollama through the connector"""
        return self.ollama_connector.call_ollama(prompt)
    
    def is_ollama_available(self) -> bool:
        """Check if Ollama is available for use"""
        return self.ollama_connector.is_available()
