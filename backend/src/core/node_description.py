# backend/src/services/node_description.py
import logging
from backend.infrastructure.llm import GroqClient

logger = logging.getLogger("NodeDescription")

class NodeDescriptionService:
    def __init__(self):
        self.llm = GroqClient()

    def generate_description(self, texts, label=None, depth=0):
        """
        Generate a descriptive summary for a cluster node.
        """
        joined_text = " ".join(texts[:10])  # small subset
        prompt = f"""
        You are describing a cluster node in a mindmap.
        Cluster label: {label or "Unknown"}
        Depth: {depth}
        
        Cluster text examples:
        {joined_text}

        Write a concise description (1–2 sentences)
        summarizing what this cluster discusses.
        """
        try:
            description = self.llm.generate(prompt).strip()
            logger.info(f"Generated description for {label}: {description}")
            return description
        except Exception as e:
            logger.error(f"Description generation failed: {e}")
            return "No description available."
