"""Main mindmap generation service"""
import logging
import numpy as np
from typing import List, Optional, Dict, Any
from src.core.models.node import MindmapNode
from src.core.services.clustering_service import ClusteringService
from src.core.services.label_service import LabelGenerationService
from src.infrastructure.embedding.embedder import EmbeddingService
from src.utils.language_detector import LanguageDetector
from src.utils.text_processor import TextProcessor
from src.utils.validators import InputValidator

logger = logging.getLogger(__name__)


class MindmapService:
    """
    Main service for mindmap generation.

    Orchestrates the entire mindmap generation pipeline:
    1. Text preprocessing and language detection
    2. Embedding generation
    3. Hierarchical clustering
    4. Label generation
    5. Tree construction
    """

    def __init__(
        self,
        embedding_service: Optional[EmbeddingService] = None,
        clustering_service: Optional[ClusteringService] = None,
        label_service: Optional[LabelGenerationService] = None
    ):
        """
        Initialize mindmap service.

        Args:
            embedding_service: Embedding service instance
            clustering_service: Clustering service instance
            label_service: Label generation service instance
        """
        self.embedding_service = embedding_service or EmbeddingService()
        self.clustering_service = clustering_service or ClusteringService()
        self.label_service = label_service or LabelGenerationService()

        logger.info("MindmapService initialized")

    def generate_mindmap(
        self,
        document: str,
        language: Optional[str] = None,
        max_depth: int = 3,
        min_size: int = 2
    ) -> Dict[str, Any]:
        """
        Generate a hierarchical mindmap from document.

        Args:
            document: Input document text
            language: Target language (auto-detected if None)
            max_depth: Maximum tree depth
            min_size: Minimum cluster size

        Returns:
            Dictionary representation of mindmap

        Raises:
            ValueError: If inputs are invalid
        """
        logger.info("Starting mindmap generation")

        # Validate inputs
        InputValidator.validate_document(document)
        InputValidator.validate_depth(max_depth)
        InputValidator.validate_min_size(min_size)

        # Detect language if not provided
        if language is None:
            language = LanguageDetector.detect(document)
            logger.info(f"Auto-detected language: {language}")
        else:
            language = LanguageDetector.normalize_language(language)
            InputValidator.validate_language(language)

        # Preprocess document into sentences
        sentences = self._preprocess_document(document)
        logger.info(f"Preprocessed into {len(sentences)} sentences")

        if not sentences:
            raise ValueError("No valid sentences found in document")

        # Generate embeddings
        embeddings = self.embedding_service.encode(sentences)
        logger.info(f"Generated embeddings with shape {embeddings.shape}")

        # Build hierarchical tree
        root_node = self._recursive_cluster(
            sentences=sentences,
            embeddings=embeddings,
            depth=0,
            max_depth_base=max_depth,
            min_size_base=min_size,
            cluster_id="root",
            language=language
        )

        if root_node is None:
            raise ValueError("Failed to generate mindmap tree")

        logger.info("Mindmap generation completed successfully")
        return root_node.to_dict()

    def _preprocess_document(self, document: str) -> List[str]:
        """
        Preprocess document into sentences.

        Args:
            document: Input document

        Returns:
            List of sentences
        """
        # Split by lines (works well for structured documents)
        lines = TextProcessor.split_by_lines(document, filter_empty=True)

        # Clean each line
        sentences = [TextProcessor.clean_text(line) for line in lines]

        # Filter by length
        sentences = [s for s in sentences if TextProcessor.validate_text(s, min_length=10)]

        return sentences

    def _recursive_cluster(
        self,
        sentences: List[str],
        embeddings: np.ndarray,
        depth: int,
        max_depth_base: int,
        min_size_base: int,
        cluster_id: str,
        language: str
    ) -> Optional[MindmapNode]:
        """
        Recursively cluster sentences and build mindmap tree.

        Args:
            sentences: List of sentences
            embeddings: Sentence embeddings
            depth: Current depth
            max_depth_base: Base maximum depth
            min_size_base: Base minimum cluster size
            cluster_id: Current cluster identifier
            language: Target language

        Returns:
            MindmapNode or None
        """
        n_samples = len(sentences)
        logger.debug(f"Processing cluster '{cluster_id}' at depth {depth} with {n_samples} samples")

        # Calculate dynamic parameters
        max_depth, min_size = self.clustering_service.calculate_dynamic_params(
            n_samples=n_samples,
            depth=depth,
            max_depth_base=max_depth_base,
            min_size_base=min_size_base
        )

        # Check if we should stop clustering
        if not self.clustering_service.should_continue_clustering(
            n_samples, depth, max_depth, min_size
        ):
            # Create leaf node
            logger.debug(f"Creating leaf node for '{cluster_id}'")
            label = self.label_service.generate_topic_label(sentences, language)
            return MindmapNode(id=cluster_id, label=label, children=[])

        # Reduce dimensions
        reduced_embeddings = self.clustering_service.reduce_dimensions(embeddings)

        # Cluster
        try:
            labels = self.clustering_service.cluster_embeddings(
                reduced_embeddings,
                n_clusters=None,  # Will be calculated dynamically
                depth=depth
            )
        except Exception as e:
            logger.warning(f"Clustering failed at depth {depth}: {e}. Creating leaf node.")
            label = self.label_service.generate_topic_label(sentences, language)
            return MindmapNode(id=cluster_id, label=label, children=[])

        # Generate label for current node
        node_label = self.label_service.generate_topic_label(sentences, language)
        node = MindmapNode(id=cluster_id, label=node_label, children=[])

        # Split data by clusters
        sentence_clusters = self.clustering_service.split_by_clusters(sentences, labels)

        # Process each subcluster
        for cluster_idx, sub_sentences in sentence_clusters.items():
            # Get corresponding embeddings
            sub_indices = np.where(labels == cluster_idx)[0]
            sub_embeddings = embeddings[sub_indices]

            # Recursive call
            child_id = f"{cluster_id}_{cluster_idx}"
            child_node = self._recursive_cluster(
                sentences=sub_sentences,
                embeddings=sub_embeddings,
                depth=depth + 1,
                max_depth_base=max_depth_base,
                min_size_base=min_size_base,
                cluster_id=child_id,
                language=language
            )

            if child_node:
                node.add_child(child_node)

        return node
