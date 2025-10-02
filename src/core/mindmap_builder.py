# src/mindmap/builder.py
import re
import numpy as np
from src.core.node import MindmapNode
from src.core.dynamic_clustering import recursive_cluster
from src.core.embedder import Embedder
from utils.language_detector import returnlang

embedder = Embedder()


# --- Main builder ---
def build_mindmap(doc, lang=None, max_depth=3, min_size=2):
    """
    Build a hierarchical mindmap from a document.
    """
    # Normalize input into a list of sentences
    if isinstance(doc, list):
        sentences = [s.strip() for s in doc if s.strip()]
    elif isinstance(doc, str):
        sentences = [s.strip() for s in doc.split("\n") if s.strip()]
    else:
        raise ValueError("doc must be a string or a list of sentences.")

    # Detect language if not provided
    if lang is None:
        lang = returnlang(doc)  
    
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
        lang=lang  
    )
    
    mindmap_dict = root_node.to_dict() if root_node else {}

    # Clean labels from hidden tags
    clean_mindmap_labels(mindmap_dict)

    return mindmap_dict


def cluster_to_node(sentences, embeddings, depth, cluster_id, max_depth, min_size):
    """
    Recursively cluster sentences and build a MindmapNode tree.
    """
    if len(sentences) < min_size or depth >= max_depth:
        return None
    
    node = MindmapNode(cluster_id, f"Cluster {cluster_id}")
    
    clusters = recursive_cluster(
        sentences, 
        embeddings, 
        depth=depth, 
        max_depth_base=max_depth, 
        min_size_base=min_size, 
        cluster_id=cluster_id
    )
    
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
# --- Text cleaning helpers ---
def strip_hidden_tags(text: str) -> str:
    if not text:
        return text

    # Remove reasoning/debug tags completely
    text = re.sub(r'<(think|reflection|debug)[^>]*>[\s\S]*?</\1>', '', text, flags=re.IGNORECASE)

    # Remove any leftover inline tags like <tag>
    text = re.sub(r'<[^>]+>', '', text)

    # Normalize whitespace
    return re.sub(r'\s+', ' ', text).strip()


def clean_mindmap_labels(node: dict):
    """Recursively clean all labels in a mindmap dict structure."""
    if "label" in node and isinstance(node["label"], str):
        node["label"] = strip_hidden_tags(node["label"])

    if "children" in node:
        for child in node["children"]:
            clean_mindmap_labels(child)

