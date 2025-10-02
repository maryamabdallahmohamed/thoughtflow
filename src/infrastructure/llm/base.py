"""Abstract base class for LLM clients"""
from abc import ABC, abstractmethod
from typing import Optional


class BaseLLMClient(ABC):
    """
    Abstract base class for LLM client implementations.

    This interface defines the contract that all LLM clients must follow,
    enabling easy swapping of LLM providers.
    """

    @abstractmethod
    def generate(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> str:
        """
        Generate text completion from the LLM.

        Args:
            prompt: Input prompt for the LLM
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response

        Returns:
            Generated text response

        Raises:
            LLMError: If generation fails
        """
        pass

    @abstractmethod
    def validate_response(self, response: str, expected_language: str) -> bool:
        """
        Validate that the response matches expected criteria.

        Args:
            response: LLM response text
            expected_language: Expected language of response (e.g., "English", "Arabic")

        Returns:
            True if response is valid, False otherwise
        """
        pass


class LLMError(Exception):
    """Exception raised for LLM-related errors"""
    pass
