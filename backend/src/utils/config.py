# backend/src/utils/config.py

from typing import List
from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration using Pydantic Settings."""
    
    # Database configuration
    database_url: str = "mysql+mysqlconnector://user:password@localhost:3306/clash_deck_builder"
    
    # Clash Royale API configuration
    clash_royale_api_key: str = "your-api-key-here"
    clash_royale_api_base_url: str = "https://api.clashroyale.com/v1"
    
    # CORS configuration
    cors_origins: List[str] = ["http://localhost:3000"]
    
    # Application configuration
    debug: bool = True
    app_name: str = "Clash Royale Deck Builder"
    app_version: str = "1.0.0"
    
    # Server configuration
    host: str = "0.0.0.0"
    port: int = 8000
    
    @field_validator('database_url')
    @classmethod
    def validate_database_url(cls, v):
        # Allow default values for development/testing
        if not v:
            raise ValueError("DATABASE_URL cannot be empty")
        return v
    
    @field_validator('clash_royale_api_key')
    @classmethod
    def validate_api_key(cls, v):
        # Allow default values for development/testing
        if not v:
            raise ValueError("CLASH_ROYALE_API_KEY cannot be empty")
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()
