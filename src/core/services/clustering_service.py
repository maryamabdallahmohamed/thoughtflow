"""Service for clustering operations"""
import logging
import numpy as np
from typing import List, Tuple, Dict
from sklearn.decomposition import TruncatedSVD
from sklearn.cluster import AgglomerativeClustering
from config.settings import settings
from src.utils.validators import InputValidator

logger = logging.getLogger(__name__)


class ClusteringService:
    """
    Service for hierarchical clustering of text embeddings.

    Handles dimensionality reduction and dynamic clustering.
    """

    def __init__(
        self,
        svd_components: int = None,
        min_cluster_size_ratio: float = None
    ):
        """
        Initialize clustering service.

        Args:
            svd_components: Number of SVD components for dimensionality reduction
            min_cluster_size_ratio: Minimum cluster size as ratio of total
        """
        self.svd_components = svd_components or settings.SVD_COMPONENTS
        self.min_cluster_size_ratio = min_cluster_size_ratio or settings.MIN_CLUSTER_SIZE_RATIO
        logger.info("ClusteringService initialized")

    def reduce_dimensions(
        self,
        embeddings: np.ndarray,
        n_components: int = None
    ) -> np.ndarray:
        """
        Reduce dimensionality of embeddings using SVD.

        Args:
            embeddings: Input embeddings (shape: [n_samples, n_features])
            n_components: Number of components (defaults to instance setting)

        Returns:
            Reduced embeddings

        Raises:
            ValueError: If embeddings are invalid
        """
        InputValidator.validate_embeddings(embeddings)

        n_components = n_components or self.svd_components
        n_components = min(n_components, embeddings.shape[1], embeddings.shape[0])

        logger.debug(f"Reducing dimensions from {embeddings.shape[1]} to {n_components}")

        svd = TruncatedSVD(n_components=n_components, random_state=42)
        reduced = svd.fit_transform(embeddings)

        logger.debug(f"Explained variance ratio: {svd.explained_variance_ratio_.sum():.3f}")
        return reduced

    def calculate_dynamic_params(
        self,
        n_samples: int,
        depth: int,
        max_depth_base: int,
        min_size_base: int
    ) -> Tuple[int, int]:
        """
        Calculate dynamic parameters for clustering.

        Args:
            n_samples: Number of samples to cluster
            depth: Current tree depth
            max_depth_base: Base maximum depth
            min_size_base: Base minimum size

        Returns:
            Tuple of (max_depth, min_size)
        """
        # Dynamic max depth: decreases with depth
        max_depth = max(1, max_depth_base - depth // 2)

        # Dynamic min size: based on sample count
        min_size = max(1, int(n_samples * self.min_cluster_size_ratio))
        min_size = max(min_size, min_size_base)

        logger.debug(
            f"Dynamic params at depth {depth}: "
            f"max_depth={max_depth}, min_size={min_size}"
        )

        return max_depth, min_size

    def cluster_embeddings(
        self,
        embeddings: np.ndarray,
        n_clusters: int = None,
        depth: int = 0
    ) -> np.ndarray:
        """
        Cluster embeddings using agglomerative clustering.

        Args:
            embeddings: Input embeddings
            n_clusters: Number of clusters (if None, calculated dynamically)
            depth: Current depth (used for dynamic calculation)

        Returns:
            Cluster labels array

        Raises:
            ValueError: If clustering fails
        """
        InputValidator.validate_embeddings(embeddings)

        n_samples = embeddings.shape[0]

        # Calculate number of clusters dynamically
        if n_clusters is None:
            n_clusters = min(2 + depth, n_samples)

        # Ensure valid number of clusters
        n_clusters = max(2, min(n_clusters, n_samples))

        logger.debug(f"Clustering {n_samples} samples into {n_clusters} clusters")

        try:
            clusterer = AgglomerativeClustering(
                n_clusters=n_clusters,
                linkage='ward'
            )
            labels = clusterer.fit_predict(embeddings)

            # Log cluster distribution
            unique, counts = np.unique(labels, return_counts=True)
            logger.debug(f"Cluster distribution: {dict(zip(unique, counts))}")

            return labels

        except Exception as e:
            logger.error(f"Clustering failed: {e}")
            raise ValueError(f"Clustering operation failed: {e}")

    def split_by_clusters(
        self,
        data: List,
        labels: np.ndarray
    ) -> Dict[int, List]:
        """
        Split data into clusters based on labels.

        Args:
            data: List of data items
            labels: Cluster labels for each item

        Returns:
            Dictionary mapping cluster ID to list of items
        """
        if len(data) != len(labels):
            raise ValueError(
                f"Data length ({len(data)}) doesn't match labels length ({len(labels)})"
            )

        clusters = {}
        for label in np.unique(labels):
            indices = np.where(labels == label)[0]
            clusters[int(label)] = [data[i] for i in indices]

        logger.debug(f"Split data into {len(clusters)} clusters")
        return clusters

    def should_continue_clustering(
        self,
        n_samples: int,
        depth: int,
        max_depth: int,
        min_size: int
    ) -> bool:
        """
        Determine if clustering should continue.

        Args:
            n_samples: Number of samples
            depth: Current depth
            max_depth: Maximum depth
            min_size: Minimum cluster size

        Returns:
            True if clustering should continue, False otherwise
        """
        if n_samples < min_size:
            logger.debug(f"Stopping: too few samples ({n_samples} < {min_size})")
            return False

        if depth >= max_depth:
            logger.debug(f"Stopping: max depth reached ({depth} >= {max_depth})")
            return False

        return True
