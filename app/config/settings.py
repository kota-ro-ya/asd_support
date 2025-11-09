"""
Application settings management.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings:
    """Application settings and configuration."""
    
    # Base paths
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    DATA_DIR = BASE_DIR / os.getenv("DATA_DIR", "data")
    USER_PROGRESS_DIR = BASE_DIR / os.getenv("USER_PROGRESS_DIR", "data/user_progress")
    EVENTS_DIR = DATA_DIR / "events"
    ASSETS_DIR = BASE_DIR / "assets"
    
    # OpenAI settings
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    # App settings
    APP_TITLE = os.getenv("APP_TITLE", "ASD支援アプリ")
    APP_VERSION = os.getenv("APP_VERSION", "0.5")
    DEBUG_MODE = os.getenv("DEBUG_MODE", "True").lower() == "true"  # デフォルトで有効化
    DEBUG_LOG_ALWAYS = os.getenv("DEBUG_LOG_ALWAYS", "True").lower() == "true"  # ログは常に記録（UI表示はDEBUG_MODEで制御）
    
    # AI response settings
    MAX_TOKENS = 500
    TEMPERATURE = 0.7
    STREAM = True
    
    # AI Generation settings
    USE_AI_GENERATION = os.getenv("USE_AI_GENERATION", "True").lower() == "true"
    AI_GENERATION_MAX_ATTEMPTS = int(os.getenv("AI_GENERATION_MAX_ATTEMPTS", "3"))
    AI_QUALITY_THRESHOLD = int(os.getenv("AI_QUALITY_THRESHOLD", "80"))
    
    # Cache settings
    ENABLE_SCENARIO_CACHE = os.getenv("ENABLE_SCENARIO_CACHE", "True").lower() == "true"
    CACHE_EXPIRY_HOURS = int(os.getenv("CACHE_EXPIRY_HOURS", "24"))
    MAX_CACHE_SIZE = int(os.getenv("MAX_CACHE_SIZE", "100"))
    
    # Loading animation settings
    LOADING_ANIMATION_TYPE = os.getenv("LOADING_ANIMATION_TYPE", "auto")  # auto, progress, animal, emoji, facts
    ENABLE_FUN_LOADING = os.getenv("ENABLE_FUN_LOADING", "True").lower() == "true"
    
    @classmethod
    def validate(cls):
        """Validate critical settings."""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set in environment variables")
        
        # Create directories if they don't exist
        cls.DATA_DIR.mkdir(parents=True, exist_ok=True)
        cls.USER_PROGRESS_DIR.mkdir(parents=True, exist_ok=True)
        cls.EVENTS_DIR.mkdir(parents=True, exist_ok=True)
        
        return True

