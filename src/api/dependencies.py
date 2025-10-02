"""FastAPI dependency injection"""
import logging
from functools import lru_cache
from src.core.builders.mindmap_builder import MindmapBuilder
from src.infrastructure.llm.groq_client import GroqClient
from src.infrastructure.embedding.embedder import get_embedding_service
from src.loader.json_loader import JSONPreprocessor
from config.settings import settings

logger = logging.getLogger(__name__)


@lru_cache()
def get_mindmap_builder() -> MindmapBuilder:
    """
    Get mindmap builder instance (cached).

    Returns:
        MindmapBuilder instance
    """
    logger.info("Creating MindmapBuilder instance")
    return MindmapBuilder()


@lru_cache()
def get_llm_client() -> GroqClient:
    """
    Get LLM client instance (cached).

    Returns:
        GroqClient instance
    """
    logger.info("Creating GroqClient instance")
    return GroqClient()


def get_json_preprocessor() -> JSONPreprocessor:
    """
    Get JSON preprocessor instance.

    Returns:
        JSONPreprocessor instance
    """
    return JSONPreprocessor()


@lru_cache()
def get_settings():
    """
    Get application settings (cached).

    Returns:
        Settings instance
    """
    return settings
