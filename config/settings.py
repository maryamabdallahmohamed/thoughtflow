"""Application configuration settings"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # API Settings
    API_TITLE: str = "ThoughtFlow Mindmap API"
    API_VERSION: str = "2.0.0"
    API_DESCRIPTION: str = "API for generating hierarchical mindmaps from documents with language-aware processing"

    # GROQ LLM Settings
    GROQ_API_KEY: str = os.getenv("Groq_API", "")
    GROQ_MODEL: str = "qwen/qwen3-32b"
    GROQ_TEMPERATURE: float = 0.0
    GROQ_MAX_TOKENS: int = 1024
    GROQ_TOP_P: float = 0.95

    # Embedding Settings
    EMBEDDING_MODEL: str = "sentence-transformers/LaBSE"
    EMBEDDING_DEVICE: str = os.getenv("DEVICE", "mps")
    EMBEDDING_CACHE_DIR: Optional[str] = os.getenv("CACHE_DIR", None)
    EMBEDDING_BATCH_SIZE: int = 16

    # Mindmap Generation Settings
    DEFAULT_MAX_DEPTH: int = 3
    DEFAULT_MIN_SIZE: int = 2
    DEFAULT_LANGUAGE: str = "en"
    MAX_DEPTH_LIMIT: int = 10
    MIN_SIZE_LIMIT: int = 100

    # Clustering Settings
    SVD_COMPONENTS: int = 50
    MIN_CLUSTER_SIZE_RATIO: float = 0.15

    # File Upload Settings
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10 MB
    ALLOWED_EXTENSIONS: set = {".json", ".pdf"}

    # CORS Settings
    CORS_ORIGINS: list = ["*"]  # Configure appropriately for production
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: list = ["*"]
    CORS_HEADERS: list = ["*"]

    # Logging Settings
    LOG_LEVEL: str = "INFO"

    # Prompt Settings
    PROMPTS_DIR: str = "prompts"
    TOPIC_LABEL_PROMPT: str = "topic_system_prompt.yaml"
    DESCRIPTIVE_PROMPT: str = "descriptive_system_prompt.yaml"
    # Pydantic v2 uses `model_config` instead of `Config`.
    # Configure all model settings here to avoid the "Config and model_config"
    # conflict. We allow extra env vars and set the env file and case sensitivity.
    model_config = {
        "extra": "allow",
        "env_file": ".env",
        "case_sensitive": True,
    }


# Global settings instance
settings = Settings()
