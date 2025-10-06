import numpy as np
from typing import List, Dict, Any
from backend.src.core.clustering import ClusteringService


cluster_service = ClusteringService()


def recursive_cluster(
    embeddings: np.ndarray,
    texts: List[str],
    depth: int = 0,
    max_depth: int = 3,
    min_size: int = 2
) -> Dict[str, Any]:

    n_samples = len(texts)

    # Base condition: stop splitting if too shallow or small
    if depth >= max_depth or n_samples < min_size:
        return {
            "depth": depth,
            "size": n_samples,
            "texts": texts
        }

    # Reduce embedding dimensions for stability
    reduced_embeddings = cluster_service.reduce_dimensions(embeddings)

    # Perform clustering
    labels = cluster_service.cluster_embeddings(reduced_embeddings, depth=depth)

    # Split data and embeddings by cluster
    text_clusters = cluster_service.split_by_clusters(texts, labels)
    embedding_clusters = cluster_service.split_by_clusters(reduced_embeddings, labels)

    # Log cluster structure
    result_tree = {
        "depth": depth,
        "n_clusters": len(text_clusters),
        "clusters": {}
    }

    # Dynamically adjust parameters based on data size
    max_depth_dynamic, min_size_dynamic = cluster_service.calculate_dynamic_params(
        n_samples=n_samples,
        depth=depth,
        max_depth_base=max_depth,
        min_size_base=min_size
    )

    # Recursively process subclusters
    for label, sub_texts in text_clusters.items():
        sub_embeddings = np.array(embedding_clusters[label])

        result_tree["clusters"][int(label)] = recursive_cluster(
            embeddings=sub_embeddings,
            texts=sub_texts,
            depth=depth + 1,
            max_depth=max_depth_dynamic,
            min_size=min_size_dynamic
        )

    return result_tree
