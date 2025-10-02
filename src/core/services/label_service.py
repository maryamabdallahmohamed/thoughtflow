"""Service for generating labels using LLM"""
import logging
import re
from typing import List
from src.infrastructure.llm.groq_client import GroqClient
from src.infrastructure.llm.prompt_manager import get_prompt_manager
from src.utils.validators import OutputValidator

logger = logging.getLogger(__name__)


class LabelGenerationService:
    """
    Service for generating topic labels using LLM.

    This service handles:
    - Formatting prompts with language awareness
    - Generating labels via LLM
    - Validating label quality
    - Retrying on failures
    """

    def __init__(self, llm_client: GroqClient = None):
        """
        Initialize label generation service.

        Args:
            llm_client: LLM client instance (creates new if not provided)
        """
        self.llm_client = llm_client or GroqClient()
        self.prompt_manager = get_prompt_manager()
        logger.info("LabelGenerationService initialized")

    def generate_topic_label(
        self,
        texts: List[str],
        language: str,
        max_retries: int = 2
    ) -> str:
        """
        Generate a concise topic label for a group of texts.

        Args:
            texts: List of text snippets to label
            language: Target language for label
            max_retries: Maximum retry attempts

        Returns:
            Generated label

        Raises:
            RuntimeError: If label generation fails
        """
        if not texts:
            logger.warning("Empty texts provided for labeling")
            return "Untitled"

        try:
            # Join texts
            joined_texts = "\n".join(texts)

            # Get formatted prompt
            prompt = self.prompt_manager.get_topic_label_prompt(
                text=joined_texts,
                language=language
            )

            logger.debug(f"Generating topic label in {language}")

            # Generate with retry and validation
            label = self.llm_client.generate_with_retry(
                prompt=prompt,
                expected_language=language,
                max_retries=max_retries
            )

            # Extra sanitization layer (defensive)
            label = self._extra_clean_label(label)

            # Additional quality validation
            if not OutputValidator.validate_label_quality(label, language):
                logger.warning(f"Generated label failed quality check: {label}")
                # Use first text as fallback
                label = self._create_fallback_label(texts, language)

            # Final length check
            if len(label) > 100:
                logger.warning(f"Label too long ({len(label)} chars), truncating: {label}")
                label = self._truncate_label(label)

            logger.info(f"Generated label: {label}")
            return label

        except Exception as e:
            logger.error(f"Label generation failed: {e}")
            return self._create_fallback_label(texts, language)

    def generate_description(
        self,
        texts: List[str],
        language: str,
        max_retries: int = 2
    ) -> str:
        """
        Generate a descriptive caption for texts.

        Args:
            texts: List of text snippets
            language: Target language
            max_retries: Maximum retry attempts

        Returns:
            Generated description
        """
        if not texts:
            return ""

        try:
            joined_texts = "\n".join(texts)

            prompt = self.prompt_manager.get_descriptive_prompt(
                text=joined_texts,
                language=language
            )

            logger.debug(f"Generating description in {language}")

            description = self.llm_client.generate_with_retry(
                prompt=prompt,
                expected_language=language,
                max_retries=max_retries
            )

            return description

        except Exception as e:
            logger.error(f"Description generation failed: {e}")
            return ""

    def _extra_clean_label(self, label: str) -> str:
        """
        Extra defensive cleaning of label (in case LLM client missed something).

        Args:
            label: Label to clean

        Returns:
            Cleaned label
        """
        if not label:
            return "Untitled"

        cleaned = label.strip()

        # Remove any remaining <think> tags
        cleaned = re.sub(r'<think>.*?</think>', '', cleaned, flags=re.DOTALL | re.IGNORECASE)

        # Remove XML/HTML tags
        cleaned = re.sub(r'<[^>]+>', '', cleaned)

        # Remove common unwanted prefixes
        unwanted_prefixes = [
            'Label:',
            'Output:',
            'Topic:',
            'Caption:',
        ]
        for prefix in unwanted_prefixes:
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix):].strip()

        # Clean up whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()

        return cleaned or "Untitled"

    def _truncate_label(self, label: str, max_words: int = 10) -> str:
        """
        Truncate label to maximum word count.

        Args:
            label: Label to truncate
            max_words: Maximum number of words

        Returns:
            Truncated label
        """
        words = label.split()
        if len(words) <= max_words:
            return label

        truncated = ' '.join(words[:max_words])
        return truncated + "..."

    def _create_fallback_label(self, texts: List[str], language: str) -> str:
        """
        Create a fallback label from texts.

        Args:
            texts: List of texts
            language: Target language

        Returns:
            Fallback label
        """
        if not texts:
            return "Untitled"

        # Use first text, truncated
        first_text = texts[0][:50]

        # Clean up
        cleaned = re.sub(r'\s+', ' ', first_text).strip()

        # Truncate to words
        words = cleaned.split()[:8]
        fallback = ' '.join(words)

        if len(cleaned) > len(fallback):
            fallback += "..."

        logger.info(f"Using fallback label: {fallback}")
        return fallback or "Untitled"

    def batch_generate_labels(
        self,
        text_groups: List[List[str]],
        language: str
    ) -> List[str]:
        """
        Generate labels for multiple text groups.

        Args:
            text_groups: List of text groups
            language: Target language

        Returns:
            List of generated labels
        """
        labels = []
        for i, texts in enumerate(text_groups):
            logger.debug(f"Generating label {i+1}/{len(text_groups)}")
            label = self.generate_topic_label(texts, language)
            labels.append(label)

        return labels
