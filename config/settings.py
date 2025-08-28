"""
Configuration settings for the LLM-Driven Autonomous Software Engineer
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Gemini API Configuration
    GEMINI_API_KEY: str
    GEMINI_MODEL: str = "gemini-1.5-flash"
    GEMINI_TEMPERATURE: float = 0.7
    GEMINI_MAX_TOKENS: int = 8192
    
    # Application Settings
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    # Project Settings
    DEFAULT_PROJECT_DIR: str = "./generated_projects"
    MAX_ITERATIONS: int = 5
    TIMEOUT_SECONDS: int = 300
    
    # Testing Settings
    AUTO_RUN_TESTS: bool = True
    TEST_TIMEOUT: int = 60
    
    # Deployment Settings
    AUTO_DEPLOY: bool = False
    DOCKER_ENABLED: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Global settings instance
settings = Settings()

# Ensure required directories exist
os.makedirs(settings.DEFAULT_PROJECT_DIR, exist_ok=True)
