"""
ATS Resume Builder - Configuration
"""

from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # App
    app_name: str = "ATS Resume Builder"
    debug: bool = True
    
    # Database
    database_url: str = "sqlite:///./ats_builder.db"
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # OpenAI
    openai_api_key: str = ""
    
    # Google Gemini
    gemini_api_key: str = ""
    
    # Upload
    upload_dir: str = "./uploads"
    max_file_size_mb: int = 10
    
    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
