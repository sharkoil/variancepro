# Configuration Guide

This guide covers all configuration options for VariancePro, from basic setup to advanced customization.

## 📋 Configuration Overview

VariancePro uses a hierarchical configuration system:
1. **Default Settings**: Built-in defaults for all options
2. **Environment Variables**: Override defaults via environment
3. **Config Files**: Local configuration files (future feature)
4. **Runtime Parameters**: Command-line arguments

## ⚙️ Core Configuration

### Settings File (`config/settings.py`)

```python
from typing import Optional, List, Tuple
import os

class Settings:
    """
    Main configuration class for VariancePro.
    All settings can be overridden via environment variables.
    """
    
    # ==================== AI CONFIGURATION ====================
    
    # Ollama Configuration
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    MODEL_NAME: str = os.getenv("MODEL_NAME", "llama3.1:8b")
    MODEL_TIMEOUT: int = int(os.getenv("MODEL_TIMEOUT", "30"))
    
    # AI Processing
    MAX_CONTEXT_LENGTH: int = int(os.getenv("MAX_CONTEXT_LENGTH", "4096"))
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.7"))
    TOP_P: float = float(os.getenv("TOP_P", "0.9"))
    
    # ==================== SECURITY SETTINGS ====================
    
    # File Upload Security
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "100000000"))  # 100MB
    ALLOWED_EXTENSIONS: List[str] = ['.csv', '.xlsx']
    UPLOAD_TIMEOUT: int = int(os.getenv("UPLOAD_TIMEOUT", "60"))
    
    # Data Processing Security
    MAX_ROWS: int = int(os.getenv("MAX_ROWS", "1000000"))  # 1M rows
    MAX_COLUMNS: int = int(os.getenv("MAX_COLUMNS", "100"))
    MEMORY_LIMIT_GB: int = int(os.getenv("MEMORY_LIMIT_GB", "4"))
    
    # Privacy Settings
    ZERO_TRUST_MODE: bool = os.getenv("ZERO_TRUST_MODE", "True").lower() == "true"
    LOG_USER_QUERIES: bool = os.getenv("LOG_USER_QUERIES", "False").lower() == "true"
    PERSIST_SESSION_DATA: bool = False  # Always False for security
    
    # ==================== PERFORMANCE SETTINGS ====================
    
    # Query Performance
    QUERY_TIMEOUT: int = int(os.getenv("QUERY_TIMEOUT", "30"))
    MAX_CONCURRENT_QUERIES: int = int(os.getenv("MAX_CONCURRENT_QUERIES", "5"))
    ENABLE_QUERY_CACHE: bool = os.getenv("ENABLE_QUERY_CACHE", "True").lower() == "true"
    CACHE_TTL_SECONDS: int = int(os.getenv("CACHE_TTL_SECONDS", "3600"))  # 1 hour
    
    # Memory Management
    GARBAGE_COLLECTION_INTERVAL: int = int(os.getenv("GC_INTERVAL", "300"))  # 5 minutes
    MAX_MEMORY_USAGE_PERCENT: int = int(os.getenv("MAX_MEMORY_PERCENT", "80"))
    
    # ==================== UI CONFIGURATION ====================
    
    # Gradio Settings
    GRADIO_SERVER_NAME: str = os.getenv("GRADIO_SERVER_NAME", "localhost")
    GRADIO_SERVER_PORT: int = int(os.getenv("GRADIO_SERVER_PORT", "7860"))
    GRADIO_SHARE: bool = os.getenv("GRADIO_SHARE", "False").lower() == "true"
    GRADIO_DEBUG: bool = os.getenv("GRADIO_DEBUG", "False").lower() == "true"
    
    # Authentication (Optional)
    GRADIO_AUTH: Optional[Tuple[str, str]] = None
    if os.getenv("GRADIO_USERNAME") and os.getenv("GRADIO_PASSWORD"):
        GRADIO_AUTH = (os.getenv("GRADIO_USERNAME"), os.getenv("GRADIO_PASSWORD"))
    
    # UI Behavior
    AUTO_REFRESH_INTERVAL: int = int(os.getenv("AUTO_REFRESH_INTERVAL", "30"))
    MAX_CHAT_HISTORY: int = int(os.getenv("MAX_CHAT_HISTORY", "50"))
    ENABLE_EXPORT: bool = os.getenv("ENABLE_EXPORT", "True").lower() == "true"
    
    # ==================== ANALYSIS SETTINGS ====================
    
    # Default Analysis Parameters
    DEFAULT_TOP_N: int = int(os.getenv("DEFAULT_TOP_N", "10"))
    PARETO_THRESHOLD: float = float(os.getenv("PARETO_THRESHOLD", "0.8"))  # 80%
    SIGNIFICANCE_THRESHOLD: float = float(os.getenv("SIGNIFICANCE_THRESHOLD", "0.05"))
    
    # Variance Analysis
    VARIANCE_TOLERANCE: float = float(os.getenv("VARIANCE_TOLERANCE", "0.1"))  # 10%
    MATERIALITY_THRESHOLD: float = float(os.getenv("MATERIALITY_THRESHOLD", "1000"))
    
    # Timescale Analysis
    MIN_PERIODS_FOR_TREND: int = int(os.getenv("MIN_PERIODS_FOR_TREND", "3"))
    SEASONALITY_DETECTION: bool = os.getenv("SEASONALITY_DETECTION", "True").lower() == "true"
    
    # ==================== LOGGING CONFIGURATION ====================
    
    # Log Levels
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    SQL_LOG_LEVEL: str = os.getenv("SQL_LOG_LEVEL", "WARNING")
    AI_LOG_LEVEL: str = os.getenv("AI_LOG_LEVEL", "INFO")
    
    # Log Destinations
    LOG_TO_CONSOLE: bool = os.getenv("LOG_TO_CONSOLE", "True").lower() == "true"
    LOG_TO_FILE: bool = os.getenv("LOG_TO_FILE", "False").lower() == "true"
    LOG_FILE_PATH: str = os.getenv("LOG_FILE_PATH", "logs/variancepro.log")
    LOG_ROTATION_SIZE: str = os.getenv("LOG_ROTATION_SIZE", "10MB")
    LOG_RETENTION_DAYS: int = int(os.getenv("LOG_RETENTION_DAYS", "7"))
    
    # ==================== DEVELOPMENT SETTINGS ====================
    
    # Debug Options
    DEBUG_MODE: bool = os.getenv("DEBUG_MODE", "False").lower() == "true"
    ENABLE_PROFILING: bool = os.getenv("ENABLE_PROFILING", "False").lower() == "true"
    MOCK_AI_RESPONSES: bool = os.getenv("MOCK_AI_RESPONSES", "False").lower() == "true"
    
    # Testing
    TESTING_MODE: bool = os.getenv("TESTING_MODE", "False").lower() == "true"
    TEST_DATA_PATH: str = os.getenv("TEST_DATA_PATH", "sample_data/")
    ENABLE_TEST_ENDPOINTS: bool = os.getenv("ENABLE_TEST_ENDPOINTS", "False").lower() == "true"

# Create global settings instance
settings = Settings()
```

## 🌍 Environment Variables

### Essential Variables

```bash
# AI Configuration
export OLLAMA_BASE_URL="http://localhost:11434"
export MODEL_NAME="llama3.1:8b"
export MODEL_TIMEOUT="30"

# Security
export MAX_FILE_SIZE="100000000"  # 100MB
export MEMORY_LIMIT_GB="4"
export ZERO_TRUST_MODE="True"

# UI Configuration
export GRADIO_SERVER_PORT="7860"
export GRADIO_SHARE="False"

# Performance
export QUERY_TIMEOUT="30"
export ENABLE_QUERY_CACHE="True"
```

### Authentication Setup

```bash
# Optional: Enable basic authentication
export GRADIO_USERNAME="admin"
export GRADIO_PASSWORD="secure_password_here"
```

### Production Environment

```bash
# Production optimizations
export LOG_LEVEL="WARNING"
export ENABLE_QUERY_CACHE="True"
export MAX_CONCURRENT_QUERIES="10"
export MEMORY_LIMIT_GB="8"
export GRADIO_DEBUG="False"
```

### Development Environment

```bash
# Development settings
export DEBUG_MODE="True"
export LOG_LEVEL="DEBUG"
export GRADIO_DEBUG="True"
export ENABLE_PROFILING="True"
export TESTING_MODE="True"
```

## 🔧 Configuration Examples

### High-Performance Setup

```bash
# .env file for high-performance environment
OLLAMA_BASE_URL=http://localhost:11434
MODEL_NAME=llama3.1:70b  # Larger model for better insights
MODEL_TIMEOUT=60
TEMPERATURE=0.3  # Lower temperature for more consistent results

# Performance optimizations
MAX_CONCURRENT_QUERIES=15
QUERY_TIMEOUT=60
MEMORY_LIMIT_GB=16
ENABLE_QUERY_CACHE=True
CACHE_TTL_SECONDS=7200

# File handling
MAX_FILE_SIZE=500000000  # 500MB
MAX_ROWS=5000000  # 5M rows

# UI settings
GRADIO_SERVER_PORT=7860
AUTO_REFRESH_INTERVAL=15
```

### Security-Focused Setup

```bash
# Maximum security configuration
ZERO_TRUST_MODE=True
LOG_USER_QUERIES=False
PERSIST_SESSION_DATA=False

# Strict file limits
MAX_FILE_SIZE=50000000  # 50MB
MAX_ROWS=500000  # 500K rows
MAX_COLUMNS=50
UPLOAD_TIMEOUT=30

# Authentication required
GRADIO_USERNAME=admin
GRADIO_PASSWORD=very_secure_password_123!
GRADIO_SHARE=False

# Minimal logging
LOG_LEVEL=ERROR
LOG_TO_FILE=False
SQL_LOG_LEVEL=ERROR
```

### Development Setup

```bash
# Developer-friendly configuration
DEBUG_MODE=True
LOG_LEVEL=DEBUG
GRADIO_DEBUG=True
ENABLE_PROFILING=True

# Relaxed limits for testing
MAX_FILE_SIZE=200000000
QUERY_TIMEOUT=120
MODEL_TIMEOUT=60

# Testing features
TESTING_MODE=True
ENABLE_TEST_ENDPOINTS=True
MOCK_AI_RESPONSES=False

# Development UI
GRADIO_SHARE=False
AUTO_REFRESH_INTERVAL=5
```

## 🎛️ Advanced Configuration

### Custom Model Configuration

```python
# Custom model settings in config/settings.py
class CustomModelSettings(Settings):
    # Alternative models for different use cases
    SUMMARY_MODEL = "llama3.1:8b"      # Fast model for summaries
    ANALYSIS_MODEL = "llama3.1:70b"     # Powerful model for deep analysis
    TRANSLATION_MODEL = "codellama:7b"  # Code-focused model for SQL
    
    # Model-specific parameters
    SUMMARY_TEMPERATURE = 0.5
    ANALYSIS_TEMPERATURE = 0.3
    TRANSLATION_TEMPERATURE = 0.1
    
    # Dynamic model selection
    AUTO_SELECT_MODEL = True
    MODEL_SELECTION_THRESHOLD = 1000  # rows
```

### Database Configuration (Future)

```python
# Future database connectivity options
class DatabaseSettings:
    # Connection settings
    DB_TYPE: str = "postgresql"  # postgresql, mysql, sqlite
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "variancepro"
    DB_USER: str = "variancepro_user"
    DB_PASSWORD: str = ""  # Set via environment
    
    # Connection pooling
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_TIMEOUT: int = 30
    
    # Security
    DB_SSL_MODE: str = "require"
    DB_CONNECTION_ENCRYPTION: bool = True
```

### API Configuration (Future)

```python
# Future API settings
class APISettings:
    # REST API
    API_ENABLED: bool = False
    API_PREFIX: str = "/api/v1"
    API_RATE_LIMIT: str = "100/hour"
    
    # Authentication
    API_KEY_REQUIRED: bool = True
    JWT_SECRET_KEY: str = ""  # Set via environment
    JWT_EXPIRATION_HOURS: int = 24
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    CORS_METHODS: List[str] = ["GET", "POST"]
```

## 🔍 Configuration Validation

### Startup Validation

```python
def validate_configuration():
    """Validate configuration at startup."""
    
    # Check Ollama connectivity
    try:
        response = requests.get(f"{settings.OLLAMA_BASE_URL}/api/tags")
        if response.status_code != 200:
            raise ConfigurationError("Cannot connect to Ollama")
    except requests.exceptions.ConnectionError:
        raise ConfigurationError("Ollama service not available")
    
    # Validate memory limits
    if settings.MEMORY_LIMIT_GB * 1024**3 > psutil.virtual_memory().total:
        logger.warning("Memory limit exceeds available RAM")
    
    # Check file system permissions
    import tempfile
    try:
        with tempfile.NamedTemporaryFile() as tf:
            pass
    except PermissionError:
        raise ConfigurationError("Insufficient file system permissions")
    
    # Validate model availability
    available_models = get_available_models()
    if settings.MODEL_NAME not in available_models:
        logger.warning(f"Model {settings.MODEL_NAME} not found. Available: {available_models}")

def get_available_models() -> List[str]:
    """Get list of available Ollama models."""
    try:
        response = requests.get(f"{settings.OLLAMA_BASE_URL}/api/tags")
        models = response.json().get("models", [])
        return [model["name"] for model in models]
    except:
        return []
```

### Runtime Configuration Monitoring

```python
# Monitor configuration changes during runtime
class ConfigurationMonitor:
    def __init__(self):
        self.last_check = time.time()
        self.check_interval = 300  # 5 minutes
    
    def check_for_updates(self):
        """Check for configuration changes."""
        if time.time() - self.last_check > self.check_interval:
            # Check environment variables for changes
            # Reload settings if necessary
            # Update component configurations
            self.last_check = time.time()
```

## 📝 Configuration Best Practices

### Environment Management

1. **Use Environment Files**: Create `.env` files for different environments
2. **Never Commit Secrets**: Use environment variables for sensitive data
3. **Document Settings**: Maintain clear documentation for all settings
4. **Validate on Startup**: Always validate configuration before starting
5. **Monitor Resources**: Track memory and CPU usage with current settings

### Security Guidelines

1. **Principle of Least Privilege**: Start with minimal permissions
2. **Regular Reviews**: Periodically review and update security settings
3. **Secure Defaults**: Default to the most secure options
4. **Audit Logging**: Log configuration changes and access attempts
5. **Encryption**: Use encrypted storage for sensitive configuration data

### Performance Tuning

1. **Monitor Metrics**: Track query performance and resource usage
2. **Gradual Changes**: Make incremental configuration adjustments
3. **Load Testing**: Test configuration changes under realistic loads
4. **Resource Limits**: Set appropriate limits based on available hardware
5. **Caching Strategy**: Optimize cache settings for your use patterns

---

This configuration guide ensures you can customize VariancePro to meet your specific security, performance, and operational requirements while maintaining the platform's core privacy and security principles.
