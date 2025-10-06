# backend/src/services/node_labeler.py
import logging
from backend.infrastructure.llm import GroqClient

logger = logging.getLogger("NodeLabeler")

class NodeLabelerService:
    def __init__(self):
        self.llm = GroqClient()

    def generate_label(self, texts, depth=0, parent_label=None):
        """
        Generate a concise label for a cluster node.
        """
        sample_text = " ".join(texts[:5])  # Use only first few texts to summarize
        prompt = f"""
        You are labeling nodes in a hierarchical mindmap.
        The following text samples belong to one cluster:

        {sample_text}

        Parent node: {parent_label or "ROOT"}
        Depth: {depth}

        Provide a short, descriptive label (3–5 words max)
        that best represents the common topic.
        """
        try:
            label = self.llm.generate(prompt).strip()
            logger.info(f"Generated label: {label}")
            return label
        except Exception as e:
            logger.error(f"Label generation failed: {e}")
            return "Unnamed Cluster"
