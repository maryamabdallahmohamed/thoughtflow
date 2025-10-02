"""Input and output validation utilities"""
import logging
from typing import Optional, Dict, Any
import numpy as np

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


class InputValidator:
    """
    Validates input data for mindmap generation.
    """

    @staticmethod
    def validate_document(document: str, min_length: int = 10) -> None:
        """
        Validate document text.

        Args:
            document: Document text
            min_length: Minimum required length

        Raises:
            ValidationError: If document is invalid
        """
        if not document:
            raise ValidationError("Document cannot be empty")

        if not isinstance(document, str):
            raise ValidationError(f"Document must be a string, got {type(document)}")

        if len(document.strip()) < min_length:
            raise ValidationError(f"Document too short (min {min_length} characters)")

    @staticmethod
    def validate_language(language: Optional[str]) -> None:
        """
        Validate language parameter.

        Args:
            language: Language code or name

        Raises:
            ValidationError: If language is invalid
        """
        if language is None:
            return  # Auto-detect

        if not isinstance(language, str):
            raise ValidationError(f"Language must be a string, got {type(language)}")

        valid_languages = {
            'en', 'ar', 'English', 'Arabic',
            'fr', 'French', 'es', 'Spanish',
            'de', 'German'
        }

        if language not in valid_languages:
            raise ValidationError(
                f"Invalid language '{language}'. "
                f"Supported: {', '.join(sorted(valid_languages))}"
            )

    @staticmethod
    def validate_depth(depth: int, min_val: int = 1, max_val: int = 10) -> None:
        """
        Validate depth parameter.

        Args:
            depth: Maximum tree depth
            min_val: Minimum allowed value
            max_val: Maximum allowed value

        Raises:
            ValidationError: If depth is invalid
        """
        if not isinstance(depth, int):
            raise ValidationError(f"Depth must be an integer, got {type(depth)}")

        if depth < min_val or depth > max_val:
            raise ValidationError(f"Depth must be between {min_val} and {max_val}")

    @staticmethod
    def validate_min_size(min_size: int, min_val: int = 1, max_val: int = 100) -> None:
        """
        Validate minimum cluster size parameter.

        Args:
            min_size: Minimum cluster size
            min_val: Minimum allowed value
            max_val: Maximum allowed value

        Raises:
            ValidationError: If min_size is invalid
        """
        if not isinstance(min_size, int):
            raise ValidationError(f"Min size must be an integer, got {type(min_size)}")

        if min_size < min_val or min_size > max_val:
            raise ValidationError(f"Min size must be between {min_val} and {max_val}")

    @staticmethod
    def validate_embeddings(embeddings: np.ndarray, expected_count: Optional[int] = None) -> None:
        """
        Validate embeddings array.

        Args:
            embeddings: Numpy array of embeddings
            expected_count: Expected number of embeddings (optional)

        Raises:
            ValidationError: If embeddings are invalid
        """
        if not isinstance(embeddings, np.ndarray):
            raise ValidationError(f"Embeddings must be numpy array, got {type(embeddings)}")

        if embeddings.ndim != 2:
            raise ValidationError(f"Embeddings must be 2D array, got {embeddings.ndim}D")

        if embeddings.shape[0] == 0:
            raise ValidationError("Embeddings array is empty")

        if expected_count and embeddings.shape[0] != expected_count:
            raise ValidationError(
                f"Expected {expected_count} embeddings, got {embeddings.shape[0]}"
            )


class OutputValidator:
    """
    Validates output data from mindmap generation.
    """

    @staticmethod
    def validate_node_structure(node_dict: Dict[str, Any]) -> None:
        """
        Validate mindmap node structure.

        Args:
            node_dict: Dictionary representation of mindmap node

        Raises:
            ValidationError: If structure is invalid
        """
        if not isinstance(node_dict, dict):
            raise ValidationError(f"Node must be a dictionary, got {type(node_dict)}")

        required_fields = ['id', 'label', 'children']
        for field in required_fields:
            if field not in node_dict:
                raise ValidationError(f"Node missing required field: {field}")

        # Validate types
        if not isinstance(node_dict['id'], str):
            raise ValidationError("Node ID must be a string")

        if not isinstance(node_dict['label'], str):
            raise ValidationError("Node label must be a string")

        if not isinstance(node_dict['children'], list):
            raise ValidationError("Node children must be a list")

        # Validate children recursively
        for child in node_dict['children']:
            OutputValidator.validate_node_structure(child)

    @staticmethod
    def validate_label_quality(label: str, expected_language: str) -> bool:
        """
        Validate label quality and language.

        Args:
            label: Generated label
            expected_language: Expected language

        Returns:
            True if label is valid, False otherwise
        """
        if not label or not label.strip():
            logger.warning("Empty label")
            return False

        # Check for markdown artifacts
        if any(char in label for char in ['*', '_', '#', '`', '[', ']']):
            logger.warning(f"Label contains markdown artifacts: {label}")
            return False

        # Check length (should be concise)
        word_count = len(label.split())
        if word_count > 15:
            logger.warning(f"Label too long ({word_count} words): {label}")
            return False

        # Check language consistency for Arabic
        if expected_language.lower() in ['arabic', 'ar']:
            has_arabic = any('\u0600' <= char <= '\u06FF' for char in label)
            if not has_arabic:
                logger.warning(f"Expected Arabic label but got: {label}")
                return False

        return True

    @staticmethod
    def validate_json_serializable(obj: Any) -> bool:
        """
        Check if object is JSON serializable.

        Args:
            obj: Object to check

        Returns:
            True if JSON serializable
        """
        import json
        try:
            json.dumps(obj)
            return True
        except (TypeError, ValueError):
            return False
