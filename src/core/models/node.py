"""MindmapNode model for representing hierarchical mindmap structure"""
from typing import List, Dict, Any, Optional
import re


class MindmapNode:
    """
    Represents a node in the hierarchical mindmap structure.

    Attributes:
        id: Unique identifier for the node (human-readable, snake_case)
        label: Display label for the node (concise, 5-10 words)
        children: List of child MindmapNode objects
        description: Optional detailed description
        metadata: Optional metadata dictionary
    """

    def __init__(
        self,
        id: str,
        label: str,
        children: Optional[List["MindmapNode"]] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.id = self._sanitize_id(id)
        self.label = self._sanitize_label(label)
        self.children = children or []
        self.description = description
        self.metadata = metadata or {}

    @staticmethod
    def _sanitize_id(id: str) -> str:
        """
        Convert ID to human-readable snake_case format.

        Examples:
            "root.0" -> "root_0"
            "Climate Change" -> "climate_change"
            "AI & ML" -> "ai_ml"
        """
        if not id:
            return "node"

        # Convert to lowercase
        sanitized = id.lower()

        # Replace dots, spaces, and special chars with underscores
        sanitized = re.sub(r'[^\w]+', '_', sanitized)

        # Remove leading/trailing underscores
        sanitized = sanitized.strip('_')

        # Collapse multiple underscores
        sanitized = re.sub(r'_+', '_', sanitized)

        return sanitized or "node"

    @staticmethod
    def _sanitize_label(label: str) -> str:
        """
        Clean up label by removing markdown formatting and limiting length.

        - Removes markdown artifacts (**, __, etc.)
        - Limits to 10 words max
        - Strips extra whitespace
        """
        if not label:
            return "Untitled"

        # Remove markdown formatting
        cleaned = re.sub(r'[*_`#\[\]]+', '', label)

        # Remove extra whitespace
        cleaned = ' '.join(cleaned.split())

        # Limit to 10 words
        words = cleaned.split()
        if len(words) > 10:
            cleaned = ' '.join(words[:10]) + '...'

        return cleaned.strip() or "Untitled"

    def add_child(self, child: "MindmapNode") -> None:
        """Add a child node"""
        if isinstance(child, MindmapNode):
            self.children.append(child)
        else:
            raise TypeError("Child must be a MindmapNode instance")

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert node and its children to dictionary representation.

        Returns:
            Dictionary with id, label, children, and optional fields
        """
        result = {
            "id": self.id,
            "label": self.label,
            "children": [child.to_dict() for child in self.children]
        }

        if self.description:
            result["description"] = self.description

        if self.metadata:
            result["metadata"] = self.metadata

        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MindmapNode":
        """
        Create a MindmapNode from dictionary representation.

        Args:
            data: Dictionary with node data

        Returns:
            MindmapNode instance
        """
        children_data = data.get("children", [])
        children = [cls.from_dict(child) for child in children_data]

        return cls(
            id=data["id"],
            label=data["label"],
            children=children,
            description=data.get("description"),
            metadata=data.get("metadata")
        )

    def __repr__(self) -> str:
        return f"MindmapNode(id='{self.id}', label='{self.label}', children={len(self.children)})"

    def __str__(self) -> str:
        return f"{self.label} ({self.id})"
