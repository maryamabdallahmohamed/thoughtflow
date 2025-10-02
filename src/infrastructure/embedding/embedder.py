"""Sentence embedding service"""
import logging
import numpy as np
from typing import List, Union
from sentence_transformers import SentenceTransformer
from config.settings import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Service for generating sentence embeddings.

    Uses SentenceTransformer with LaBSE model for multilingual support.
    """

    def __init__(
        self,
        model_name: str = None,
        device: str = None,
        cache_dir: str = None
    ):
        """
        Initialize embedding service.

        Args:
            model_name: Name of the sentence transformer model
            device: Device to run model on (cpu/cuda)
            cache_dir: Directory to cache models
        """
        self.model_name = model_name or settings.EMBEDDING_MODEL
        self.device = device or settings.EMBEDDING_DEVICE
        self.cache_dir = cache_dir or settings.EMBEDDING_CACHE_DIR

        logger.info(f"Initializing EmbeddingService with model: {self.model_name}")
        logger.info(f"Device: {self.device}, Cache dir: {self.cache_dir}")

        try:
            self.model = SentenceTransformer(
                self.model_name,
                device=self.device,
                cache_folder=self.cache_dir
            )
            logger.info("EmbeddingService initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize embedding model: {e}")
            raise RuntimeError(f"Failed to initialize embedding model: {e}")

    def encode(
        self,
        texts: Union[str, List[str]],
        batch_size: int = None,
        normalize: bool = True,
        show_progress: bool = False
    ) -> np.ndarray:
        """
        Generate embeddings for input texts.

        Args:
            texts: Single text or list of texts to encode
            batch_size: Batch size for encoding (defaults to settings)
            normalize: Whether to normalize embeddings
            show_progress: Whether to show progress bar

        Returns:
            Numpy array of embeddings (shape: [n_texts, embedding_dim])

        Raises:
            ValueError: If texts is empty
        """
        if not texts:
            raise ValueError("Cannot encode empty text list")

        # Convert single string to list
        if isinstance(texts, str):
            texts = [texts]

        batch_size = batch_size or settings.EMBEDDING_BATCH_SIZE

        try:
            logger.debug(f"Encoding {len(texts)} texts with batch_size={batch_size}")

            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                normalize_embeddings=normalize,
                device=self.device,
                convert_to_numpy=True,
                show_progress_bar=show_progress
            )

            logger.debug(f"Generated embeddings with shape: {embeddings.shape}")
            return embeddings

        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            raise RuntimeError(f"Embedding generation failed: {e}")

    def encode_batch(
        self,
        batch_texts: List[List[str]],
        **kwargs
    ) -> List[np.ndarray]:
        """
        Encode multiple batches of texts.

        Args:
            batch_texts: List of text batches
            **kwargs: Additional arguments for encode()

        Returns:
            List of embedding arrays
        """
        return [self.encode(texts, **kwargs) for texts in batch_texts]

    def get_embedding_dimension(self) -> int:
        """
        Get the dimensionality of the embeddings.

        Returns:
            Embedding dimension
        """
        return self.model.get_sentence_embedding_dimension()


# Global embedding service instance
_embedding_service = None


def get_embedding_service() -> EmbeddingService:
    """
    Get the global EmbeddingService instance (singleton pattern).

    Returns:
        EmbeddingService instance
    """
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
