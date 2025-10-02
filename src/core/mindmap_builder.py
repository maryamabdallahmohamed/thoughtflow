# src/mindmap/builder.py
import numpy as np
from src.core.node import MindmapNode
from src.core.dynamic_clustering import recursive_cluster
from src.core.embedder import Embedder
from utils.language_detector import returnlang
embedder = Embedder()

# In mindmap_builder.py
def build_mindmap(doc, lang=None, max_depth=3, min_size=2):
    """
    Build a hierarchical mindmap from a document.
    """
    # Split document into sentences
    sentences = doc.split("\n")
    
    # Detect language if not provided
    if lang is None:
        from utils.language_detector import returnlang
        lang = returnlang(doc)  # Pass the full document string
    
    # Encode sentences
    embeddings = embedder.encode(sentences)
    
    # Build the tree using recursive_cluster
    root_node = recursive_cluster(
        sentences, 
        embeddings, 
        depth=0, 
        max_depth_base=max_depth,
        min_size_base=min_size,
        cluster_id="root",
        lang=lang  # Pass detected language
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