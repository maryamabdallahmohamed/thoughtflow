import logging
import numpy as np
from typing import List, Union
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class EmbeddingService:
    def __init__( self, model_name: str = None, device: str = None, cache_dir: str = None ):
        self.model_name ="sentence-transformers/LaBSE"
        self.device = "mps"
        self.cache_dir = "cache/"

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

    def encode( self, texts: Union[str, List[str]], batch_size=16, normalize: bool = True,
        show_progress: bool = False
    ) -> np.ndarray:

        # Convert single string to list
        if isinstance(texts, str):
            texts = [texts]

        batch_size = batch_size 

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
        return [self.encode(texts, **kwargs) for texts in batch_texts]


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