"""
Test suite for configuration system
Tests the Settings class and environment variable handling
"""

import os
import pytest
from config.settings import Settings


class TestSettings:
    """Test cases for Settings configuration class"""
    
    def test_default_settings(self):
        """Test that default settings are created correctly"""
        settings = Settings()
        
        # Test default LLM configuration
        assert settings.llm_model == "gemma3:latest"
        assert settings.ollama_host == "http://localhost:11434"
        assert settings.llm_timeout == 180
        assert settings.llm_temperature == 0.3
        assert settings.llm_max_tokens == 2048
        assert settings.llm_context_length == 8192
        
        # Test default file processing
        assert settings.max_file_size == 50_000_000
        assert settings.supported_formats == ['.csv']
        
        # Test default UI configuration
        assert settings.gradio_port == 7860
        assert settings.gradio_share is False
        
        # Test default analysis configuration
        assert settings.contribution_threshold == 0.8
        assert settings.timescale_auto_detect is True
        
        # Test default security settings
        assert settings.local_processing_only is True
        assert settings.no_code_suggestions is True
        assert settings.csv_only_analysis is True
    
    def test_settings_validation_valid(self):
        """Test that valid settings pass validation"""
        settings = Settings()
        assert settings.validate() is True
    
    def test_settings_validation_invalid_timeout(self):
        """Test that invalid timeout fails validation"""
        settings = Settings(llm_timeout=0)
        with pytest.raises(ValueError, match="LLM timeout must be positive"):
            settings.validate()
    
    def test_settings_validation_invalid_temperature(self):
        """Test that invalid temperature fails validation"""
        settings = Settings(llm_temperature=3.0)
        with pytest.raises(ValueError, match="LLM temperature must be between 0.0 and 2.0"):
            settings.validate()
    
    def test_settings_validation_invalid_file_size(self):
        """Test that invalid file size fails validation"""
        settings = Settings(max_file_size=-1)
        with pytest.raises(ValueError, match="Max file size must be positive"):
            settings.validate()
    
    def test_settings_validation_invalid_threshold(self):
        """Test that invalid contribution threshold fails validation"""
        settings = Settings(contribution_threshold=1.5)
        with pytest.raises(ValueError, match="Contribution threshold must be between 0.1 and 1.0"):
            settings.validate()
    
    def test_settings_validation_invalid_port(self):
        """Test that invalid port fails validation"""
        settings = Settings(gradio_port=100)
        with pytest.raises(ValueError, match="Gradio port must be between 1024 and 65535"):
            settings.validate()
    
    def test_from_env_defaults(self):
        """Test creating settings from environment with defaults"""
        # Clear any existing environment variables
        env_vars = ['VARIANCEPRO_LLM_MODEL', 'OLLAMA_HOST', 'VARIANCEPRO_LLM_TIMEOUT', 
                   'GRADIO_SERVER_PORT', 'GRADIO_SHARE', 'VARIANCEPRO_CONTRIBUTION_THRESHOLD']
        
        original_values = {}
        for var in env_vars:
            original_values[var] = os.environ.get(var)
            if var in os.environ:
                del os.environ[var]
        
        try:
            settings = Settings.from_env()
            assert settings.llm_model == "gemma3:latest"
            assert settings.ollama_host == "http://localhost:11434"
            assert settings.llm_timeout == 180
            assert settings.gradio_port == 7860
            assert settings.gradio_share is False
            assert settings.contribution_threshold == 0.8
        finally:
            # Restore original environment
            for var, value in original_values.items():
                if value is not None:
                    os.environ[var] = value
    
    def test_from_env_custom_values(self):
        """Test creating settings from environment with custom values"""
        # Set custom environment variables
        test_env = {
            'VARIANCEPRO_LLM_MODEL': 'phi3:latest',
            'OLLAMA_HOST': 'http://custom-host:11434',
            'VARIANCEPRO_LLM_TIMEOUT': '300',
            'GRADIO_SERVER_PORT': '8080',
            'GRADIO_SHARE': 'true',
            'VARIANCEPRO_CONTRIBUTION_THRESHOLD': '0.9'
        }
        
        # Store original values
        original_values = {}
        for var in test_env:
            original_values[var] = os.environ.get(var)
            os.environ[var] = test_env[var]
        
        try:
            settings = Settings.from_env()
            assert settings.llm_model == 'phi3:latest'
            assert settings.ollama_host == 'http://custom-host:11434'
            assert settings.llm_timeout == 300
            assert settings.gradio_port == 8080
            assert settings.gradio_share is True
            assert settings.contribution_threshold == 0.9
        finally:
            # Restore original environment
            for var, value in original_values.items():
                if value is not None:
                    os.environ[var] = value
                elif var in os.environ:
                    del os.environ[var]
    
    def test_get_ollama_config(self):
        """Test Ollama configuration generation"""
        settings = Settings()
        config = settings.get_ollama_config()
        
        expected_config = {
            'host': 'http://localhost:11434',
            'timeout': 180,
            'model': 'gemma3:latest',
            'options': {
                'temperature': 0.3,
                'num_predict': 2048,
                'num_ctx': 8192,
                'top_k': 40,
                'top_p': 0.9,
            }
        }
        
        assert config == expected_config
    
    def test_get_gradio_config(self):
        """Test Gradio configuration generation"""
        settings = Settings()
        config = settings.get_gradio_config()
        
        expected_config = {
            'server_port': 7860,
            'share': False,
            'show_error': True,
            'show_tips': True,
        }
        
        assert config == expected_config
    
    def test_custom_settings(self):
        """Test creating settings with custom values"""
        settings = Settings(
            llm_model="phi3:latest",
            ollama_host="http://custom:11434",
            llm_timeout=300,
            llm_temperature=0.5,
            gradio_port=8080,
            contribution_threshold=0.9
        )
        
        assert settings.llm_model == "phi3:latest"
        assert settings.ollama_host == "http://custom:11434"
        assert settings.llm_timeout == 300
        assert settings.llm_temperature == 0.5
        assert settings.gradio_port == 8080
        assert settings.contribution_threshold == 0.9
        
        # Should still validate
        assert settings.validate() is True


if __name__ == "__main__":
    # Run tests if executed directly
    import sys
    
    test_class = TestSettings()
    
    # Get all test methods
    test_methods = [method for method in dir(test_class) if method.startswith('test_')]
    
    print(f"🧪 Running {len(test_methods)} configuration tests...")
    
    passed = 0
    failed = 0
    
    for test_method in test_methods:
        try:
            print(f"  ▶️ {test_method}... ", end="")
            getattr(test_class, test_method)()
            print("✅ PASSED")
            passed += 1
        except Exception as e:
            print(f"❌ FAILED: {str(e)}")
            failed += 1
    
    print(f"\n📊 Results: {passed} passed, {failed} failed")
    
    if failed > 0:
        sys.exit(1)
    else:
        print("🎉 All configuration tests passed!")
        sys.exit(0)
