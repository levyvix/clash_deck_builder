# backend/src/utils/config.py

from typing import List, Optional
from pydantic import field_validator, computed_field
from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    """Application configuration using Pydantic Settings."""
    
    # Database configuration - individual components for Docker environment
    db_host: str = "localhost"
    db_port: int = 3306
    db_name: str = "clash_deck_builder"
    db_user: str = "clash_user"
    db_password: str = "password"
    db_root_password: Optional[str] = None
    
    # Legacy database URL support (will be constructed from components if not provided)
    database_url: Optional[str] = None
    
    # Clash Royale API configuration
    clash_royale_api_key: str = "your-api-key-here"
    clash_royale_api_base_url: str = "https://api.clashroyale.com/v1"
    
    # CORS configuration
    cors_origins: str = "http://localhost:3000"
    
    # Application configuration
    debug: bool = False
    log_level: str = "info"
    environment: str = "development"
    app_name: str = "Clash Royale Deck Builder"
    app_version: str = "1.0.0"
    
    # Server configuration
    host: str = "0.0.0.0"
    port: int = 8000
    
    @computed_field
    @property
    def constructed_database_url(self) -> str:
        """Construct database URL from individual components."""
        if self.database_url:
            return self.database_url
        return f"mysql+mysqlconnector://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
    
    @field_validator('db_password')
    @classmethod
    def validate_db_password(cls, v):
        if not v or v == "password":
            # Only allow default password in development
            env = os.getenv("ENVIRONMENT", "development")
            if env == "production":
                raise ValueError("DB_PASSWORD must be set to a secure value in production")
        return v
    
    @field_validator('clash_royale_api_key')
    @classmethod
    def validate_api_key(cls, v):
        if not v or v == "your-api-key-here":
            # Allow default values for development/testing
            env = os.getenv("ENVIRONMENT", "development")
            if env == "production":
                raise ValueError("CLASH_ROYALE_API_KEY must be set in production")
        return v
    
    @computed_field
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from string to list."""
        if isinstance(self.cors_origins, str):
            return [origin.strip() for origin in self.cors_origins.split(',') if origin.strip()]
        return [self.cors_origins] if self.cors_origins else []
    
    def get_database_config(self) -> dict:
        """Get database configuration dictionary for mysql-connector-python."""
        return {
            "host": self.db_host,
            "port": self.db_port,
            "database": self.db_name,
            "user": self.db_user,
            "password": self.db_password,
            "charset": "utf8mb4",
            "collation": "utf8mb4_unicode_ci",
            "autocommit": False,
            "raise_on_warnings": True,
            "use_unicode": True
        }
    
    def validate_configuration(self) -> bool:
        """Validate that all required configuration is present."""
        errors = []
        
        # Check required database fields
        if not self.db_host:
            errors.append("DB_HOST is required")
        if not self.db_name:
            errors.append("DB_NAME is required")
        if not self.db_user:
            errors.append("DB_USER is required")
        if not self.db_password:
            errors.append("DB_PASSWORD is required")
        
        # Check API key in production
        if self.environment == "production" and (not self.clash_royale_api_key or self.clash_royale_api_key == "your-api-key-here"):
            errors.append("CLASH_ROYALE_API_KEY must be set in production")
        
        if errors:
            raise ValueError(f"Configuration validation failed: {', '.join(errors)}")
        
        return True
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        # Allow extra fields for flexibility
        extra = "ignore"


def get_settings() -> Settings:
    """Get application settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()
