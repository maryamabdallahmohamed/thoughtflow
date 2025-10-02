"""Language detection utility"""
import logging
from typing import Optional
from langdetect import detect, DetectorFactory

# Set a fixed seed for consistent results
DetectorFactory.seed = 0

logger = logging.getLogger(__name__)


class LanguageDetector:
    """
    Service for detecting the language of input text.

    Uses langdetect library with consistent seeding.
    """

    # Language code to full name mapping
    LANGUAGE_MAP = {
        'ar': 'Arabic',
        'en': 'English',
        'fr': 'French',
        'es': 'Spanish',
        'de': 'German',
        'zh-cn': 'Chinese',
        'ja': 'Japanese',
        'ko': 'Korean',
        'ru': 'Russian',
        'pt': 'Portuguese'
    }

    @staticmethod
    def detect(text: str, default: str = "English") -> str:
        """
        Detect language of the input text.

        Args:
            text: Text to analyze
            default: Default language if detection fails

        Returns:
            Full language name (e.g., "English", "Arabic")
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for language detection")
            return default

        try:
            # Detect language code
            lang_code = detect(text)

            # Map to full language name
            language = LanguageDetector.LANGUAGE_MAP.get(lang_code, default)

            logger.info(f"Detected language: {language} ({lang_code})")
            return language

        except Exception as e:
            logger.warning(f"Language detection failed: {e}. Using default: {default}")
            return default

    @staticmethod
    def detect_code(text: str, default: str = "en") -> str:
        """
        Detect language and return language code.

        Args:
            text: Text to analyze
            default: Default language code if detection fails

        Returns:
            Language code (e.g., "en", "ar")
        """
        if not text or not text.strip():
            return default

        try:
            return detect(text)
        except Exception as e:
            logger.warning(f"Language detection failed: {e}. Using default: {default}")
            return default

    @staticmethod
    def normalize_language(language: Optional[str]) -> str:
        """
        Normalize language input to full language name.

        Args:
            language: Language code or name (e.g., "en", "English", "ar")

        Returns:
            Full language name (e.g., "English", "Arabic")
        """
        if not language:
            return "English"

        language = language.strip().lower()

        # If it's a language code, map it
        if language in LanguageDetector.LANGUAGE_MAP:
            return LanguageDetector.LANGUAGE_MAP[language]

        # If it's already a full name, capitalize it
        for code, name in LanguageDetector.LANGUAGE_MAP.items():
            if name.lower() == language:
                return name

        # Default to English if not found
        logger.warning(f"Unknown language '{language}', defaulting to English")
        return "English"

    @staticmethod
    def is_rtl(language: str) -> bool:
        """
        Check if language is right-to-left.

        Args:
            language: Language name or code

        Returns:
            True if language is RTL, False otherwise
        """
        rtl_languages = {'Arabic', 'ar', 'Hebrew', 'he', 'Urdu', 'ur', 'Persian', 'fa'}
        return language in rtl_languages


# Convenience functions for backward compatibility
def returnlang(text: str) -> str:
    """
    Detect language of text (backward compatible).

    Args:
        text: Text to analyze

    Returns:
        Full language name
    """
    return LanguageDetector.detect(text)


def detect_language(text: str, default: str = "English") -> str:
    """
    Detect language of text.

    Args:
        text: Text to analyze
        default: Default language if detection fails

    Returns:
        Full language name
    """
    return LanguageDetector.detect(text, default)
