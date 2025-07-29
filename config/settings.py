from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # API Configuration
    inoreader_app_id: Optional[str] = None
    inoreader_api_key: Optional[str] = None
    
    # Inoreader Login Credentials
    inoreader_email: Optional[str] = None
    inoreader_password: Optional[str] = None
    
    # Database Configuration
    database_url: str = "sqlite:///./rss_processor.db"
    
    # ML Configuration
    model_cache_dir: str = "./models"
    spacy_model: str = "en_core_web_sm"
    
    # Processing Configuration
    max_articles_per_day: int = 100
    summary_max_length: int = 150
    surprise_articles_count: int = 5
    
    # Obsidian Configuration
    obsidian_vault_path: Optional[str] = None
    newsletter_template_path: str = "./templates/newsletter.md"
    
    # Rate Limiting
    inoreader_daily_limit: int = 1000
    rate_limit_buffer: float = 0.1  # 10% buffer
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "./logs/rss_processor.log"
    
    model_config = {
        "env_file": [".env", "~/.env"],  # Check project directory first, then home
        "case_sensitive": False,
        "extra": "ignore",
        "protected_namespaces": ('settings_',)
    }

settings = Settings()