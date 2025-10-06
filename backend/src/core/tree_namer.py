import logging
import json
from backend.infrastructure.llm import GroqClient

logger = logging.getLogger("TreeNamer")


class TreeNamerService:
    def __init__(self):
        self.llm = GroqClient()

    def summarize_tree(self, node, depth=0):
        """
        Recursively collect labels and descriptions from the tree.
        """
        text = []
        if "label" in node:
            text.append(f"{'  ' * depth}- {node['label']}: {node.get('description', '')}")
        if "clusters" in node:
            for child in node["clusters"].values():
                text.append(self.summarize_tree(child, depth + 1))
        return "\n".join(t for t in text if t)

    def generate_tree_name(self, enriched_tree, lang="Arabic"):
        """
        Generate a global name and description for the full hierarchy.
        Ensures output is in the requested language.
        """
        hierarchy_summary = self.summarize_tree(enriched_tree)

        prompt = f"""
        You are naming a hierarchical mindmap based on the following summary
        of all nodes and their descriptions:

        {hierarchy_summary}

        Your task:
        1. Generate a concise title (maximum 6 words) that represents the overall topic.
        2. Write a 1–2 sentence summary describing the mindmap’s main theme.
        3. Both the title and summary must be written in **{lang}**.

        Respond strictly in JSON format with the following keys:
        {{
            "title": "<short title in {lang}>",
            "summary": "<summary in {lang}>"
        }}
        """

        try:
            response = self.llm.generate(prompt).strip()

            # --- Attempt to extract valid JSON safely ---
            try:
                data = json.loads(response)
            except json.JSONDecodeError:
                # Try to recover JSON from a larger response
                import re
                match = re.search(r"\{.*\}", response, re.DOTALL)
                if match:
                    data = json.loads(match.group())
                else:
                    raise ValueError(f"Invalid JSON response: {response}")

            title = data.get("title", "Untitled Mindmap")
            summary = data.get("summary", "No overview available.")
            logger.info(f"🧭 Tree named as: {title} ({lang})")
            return title, summary

        except Exception as e:
            logger.error(f"Tree naming failed: {e}")
            return f"Untitled Mindmap ({lang})", f"No overview available in {lang}."
