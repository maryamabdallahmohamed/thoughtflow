"""Text processing utilities"""
import re
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)


class TextProcessor:
    """
    Utilities for text cleaning, splitting, and preprocessing.
    """

    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean and normalize text.

        Args:
            text: Input text

        Returns:
            Cleaned text
        """
        if not text:
            return ""

        # Remove excessive whitespace
        cleaned = re.sub(r'\s+', ' ', text)

        # Remove control characters
        cleaned = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', cleaned)

        # Strip leading/trailing whitespace
        cleaned = cleaned.strip()

        return cleaned

    @staticmethod
    def split_into_sentences(
        text: str,
        min_length: int = 10,
        max_length: int = 500
    ) -> List[str]:
        """
        Split text into sentences.

        Args:
            text: Input text
            min_length: Minimum sentence length (characters)
            max_length: Maximum sentence length (characters)

        Returns:
            List of sentences
        """
        if not text:
            return []

        # Simple sentence splitting (can be improved with NLP libraries)
        # Split on newlines and common sentence endings
        sentences = re.split(r'[.\n]+', text)

        # Clean and filter sentences
        processed = []
        for sent in sentences:
            sent = TextProcessor.clean_text(sent)

            # Skip if too short or too long
            if len(sent) < min_length or len(sent) > max_length:
                continue

            processed.append(sent)

        logger.debug(f"Split text into {len(processed)} sentences")
        return processed

    @staticmethod
    def split_by_lines(text: str, filter_empty: bool = True) -> List[str]:
        """
        Split text into lines.

        Args:
            text: Input text
            filter_empty: Whether to filter out empty lines

        Returns:
            List of lines
        """
        if not text:
            return []

        lines = text.split('\n')

        if filter_empty:
            lines = [line.strip() for line in lines if line.strip()]

        return lines

    @staticmethod
    def remove_markdown(text: str) -> str:
        """
        Remove markdown formatting from text.

        Args:
            text: Text with markdown formatting

        Returns:
            Plain text
        """
        if not text:
            return ""

        # Remove bold/italic markers
        cleaned = re.sub(r'[*_]{1,3}', '', text)

        # Remove headers
        cleaned = re.sub(r'#{1,6}\s*', '', cleaned)

        # Remove code blocks
        cleaned = re.sub(r'```.*?```', '', cleaned, flags=re.DOTALL)
        cleaned = re.sub(r'`[^`]+`', '', cleaned)

        # Remove links but keep text
        cleaned = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', cleaned)

        # Clean up whitespace
        cleaned = TextProcessor.clean_text(cleaned)

        return cleaned

    @staticmethod
    def truncate_text(
        text: str,
        max_length: int,
        suffix: str = "..."
    ) -> str:
        """
        Truncate text to maximum length.

        Args:
            text: Input text
            max_length: Maximum length
            suffix: Suffix to add if truncated

        Returns:
            Truncated text
        """
        if not text or len(text) <= max_length:
            return text

        return text[:max_length - len(suffix)] + suffix

    @staticmethod
    def count_words(text: str) -> int:
        """
        Count words in text.

        Args:
            text: Input text

        Returns:
            Word count
        """
        if not text:
            return 0

        return len(text.split())

    @staticmethod
    def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
        """
        Extract keywords from text (simple implementation).

        Args:
            text: Input text
            max_keywords: Maximum number of keywords

        Returns:
            List of keywords
        """
        if not text:
            return []

        # Simple keyword extraction: most common words
        words = text.lower().split()

        # Filter out short words and common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
        keywords = [w for w in words if len(w) > 3 and w not in stop_words]

        # Count frequency
        from collections import Counter
        word_counts = Counter(keywords)

        # Return most common
        return [word for word, _ in word_counts.most_common(max_keywords)]

    @staticmethod
    def validate_text(
        text: str,
        min_length: int = 10,
        max_length: Optional[int] = None
    ) -> bool:
        """
        Validate text meets length requirements.

        Args:
            text: Input text
            min_length: Minimum length
            max_length: Maximum length (optional)

        Returns:
            True if valid, False otherwise
        """
        if not text:
            return False

        text_length = len(text.strip())

        if text_length < min_length:
            return False

        if max_length and text_length > max_length:
            return False

        return True
