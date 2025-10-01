# src/mindmap/builder.py
import numpy as np
from src.core.node import MindmapNode
from src.core.dynamic_clustering import recursive_cluster
from src.core.embedder import Embedder

embedder = Embedder()


def build_mindmap(doc, lang="en", max_depth=3, min_size=2):
    """
    Build a hierarchical mindmap from a document.
    
    Args:
        doc: Input document text
        lang: Language code (default: "en")
        max_depth: Maximum depth of clustering (default: 3)
        min_size: Minimum cluster size (default: 2)
    
    Returns:
        Dictionary representation of the mindmap tree
    """
    # Split document into sentences
    sentences = doc.split("\n")  # or use your simple_sentence_split function
    
    # Encode sentences
    embeddings = embedder.encode(sentences)
    
    # Build the tree recursively
    root_node = cluster_to_node(
        sentences, 
        embeddings, 
        depth=0, 
        cluster_id="root",
        max_depth=max_depth,
        min_size=min_size
    )
    
    return root_node.to_dict() if root_node else {}


def cluster_to_node(sentences, embeddings, depth, cluster_id, max_depth, min_size):
    """
    Recursively cluster sentences and build a MindmapNode tree.
    
    Args:
        sentences: List of sentence strings
        embeddings: Numpy array of sentence embeddings
        depth: Current depth in the tree
        cluster_id: Identifier for this cluster
        max_depth: Maximum allowed depth
        min_size: Minimum cluster size
    
    Returns:
        MindmapNode or None if cluster is too small or max depth reached
    """
    # Base case: stop if cluster too small or max depth reached
    if len(sentences) < min_size or depth >= max_depth:
        return None
    
    # Create node for this cluster
    node = MindmapNode(cluster_id, f"Cluster {cluster_id}")
    
    # Use dynamic clustering to split into subclusters
    clusters = recursive_cluster(
        sentences, 
        embeddings, 
        depth=depth, 
        max_depth_base=max_depth, 
        min_size_base=min_size, 
        cluster_id=cluster_id
    )
    
    # Process each subcluster
    if clusters:
        for sub_id, (sub_sentences, sub_embeddings) in enumerate(clusters):
            sub_node = cluster_to_node(
                sub_sentences, 
                sub_embeddings, 
                depth + 1, 
                f"{cluster_id}.{sub_id}",
                max_depth,
                min_size
            )
            if sub_node:
                node.children.append(sub_node)
    
    return node