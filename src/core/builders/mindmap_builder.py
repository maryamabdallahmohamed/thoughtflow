"""Mindmap builder orchestration - facade pattern"""
import logging
from typing import Optional, Dict, Any
from src.core.services.mindmap_service import MindmapService
from src.core.services.clustering_service import ClusteringService
from src.core.services.label_service import LabelGenerationService
from src.infrastructure.embedding.embedder import get_embedding_service
from src.infrastructure.llm.groq_client import GroqClient

logger = logging.getLogger(__name__)


class MindmapBuilder:
    """
    Facade for mindmap generation.

    Provides a simplified interface to the mindmap generation system
    with dependency injection and configuration management.
    """

    def __init__(
        self,
        llm_client: Optional[GroqClient] = None,
        use_cache: bool = True
    ):
        """
        Initialize mindmap builder.

        Args:
            llm_client: Custom LLM client (creates default if None)
            use_cache: Whether to use cached services
        """
        logger.info("Initializing MindmapBuilder")

        # Initialize infrastructure
        embedding_service = get_embedding_service() if use_cache else None
        llm_client = llm_client or GroqClient()

        # Initialize services
        label_service = LabelGenerationService(llm_client=llm_client)
        clustering_service = ClusteringService()

        # Initialize main service
        self.mindmap_service = MindmapService(
            embedding_service=embedding_service,
            clustering_service=clustering_service,
            label_service=label_service
        )

        logger.info("MindmapBuilder initialized successfully")

    def build(
        self,
        document: str,
        language: Optional[str] = None,
        max_depth: int = 3,
        min_size: int = 2
    ) -> Dict[str, Any]:
        """
        Build a mindmap from document.

        Args:
            document: Input document text
            language: Target language (auto-detected if None)
            max_depth: Maximum tree depth
            min_size: Minimum cluster size

        Returns:
            Mindmap dictionary

        Raises:
            ValueError: If generation fails
        """
        logger.info("Building mindmap")

        try:
            mindmap = self.mindmap_service.generate_mindmap(
                document=document,
                language=language,
                max_depth=max_depth,
                min_size=min_size
            )

            logger.info("Mindmap built successfully")
            return mindmap

        except Exception as e:
            logger.error(f"Failed to build mindmap: {e}")
            raise


# Convenience function for backward compatibility
def build_mindmap(
    doc: str,
    lang: Optional[str] = None,
    max_depth: int = 3,
    min_size: int = 2
) -> Dict[str, Any]:
    """
    Build a hierarchical mindmap from a document (backward compatible).

    Args:
        doc: Document text
        lang: Language (auto-detected if None)
        max_depth: Maximum tree depth
        min_size: Minimum cluster size

    Returns:
        Mindmap dictionary
    """
    builder = MindmapBuilder()
    return builder.build(
        document=doc,
        language=lang,
        max_depth=max_depth,
        min_size=min_size
    )
