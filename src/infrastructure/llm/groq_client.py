"""GROQ LLM client implementation"""
import logging
import re
from typing import Optional
from groq import Groq
from config.settings import settings
from src.infrastructure.llm.base import BaseLLMClient, LLMError

logger = logging.getLogger(__name__)


class GroqClient(BaseLLMClient):
    """
    GROQ LLM client implementation.

    Provides language-aware text generation with validation.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ):
        """
        Initialize GROQ client.

        Args:
            api_key: GROQ API key (defaults to settings)
            model: Model name (defaults to settings)
            temperature: Default temperature (defaults to settings)
            max_tokens: Default max tokens (defaults to settings)
        """
        self.api_key = api_key or settings.GROQ_API_KEY
        self.model = model or settings.GROQ_MODEL
        self.default_temperature = temperature if temperature is not None else settings.GROQ_TEMPERATURE
        self.default_max_tokens = max_tokens or settings.GROQ_MAX_TOKENS

        if not self.api_key:
            raise LLMError("GROQ API key not provided")

        self.client = Groq(api_key=self.api_key)
        logger.info(f"Initialized GROQ client with model: {self.model}")

    def generate(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> str:
        """
        Generate text completion from GROQ.

        Args:
            prompt: Input prompt
            temperature: Sampling temperature (overrides default)
            max_tokens: Max tokens to generate (overrides default)
            stream: Whether to stream response

        Returns:
            Generated text

        Raises:
            LLMError: If generation fails
        """
        try:
            temp = temperature if temperature is not None else self.default_temperature
            max_tok = max_tokens or self.default_max_tokens

            logger.debug(f"Generating with temperature={temp}, max_tokens={max_tok}")

            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temp,
                max_completion_tokens=max_tok,
                top_p=settings.GROQ_TOP_P,
                stream=stream,
                include_reasoning=False
            )

            if stream:
                response_parts = []
                for chunk in completion:
                    delta = chunk.choices[0].delta.content or ""
                    response_parts.append(delta)
                response = "".join(response_parts)
            else:
                response = completion.choices[0].message.content

            logger.debug(f"Generated response: {response[:100]}...")

            # Clean response before returning
            cleaned_response = self._clean_response(response)
            return cleaned_response

        except Exception as e:
            logger.error(f"GROQ generation failed: {e}")
            raise LLMError(f"Failed to generate completion: {str(e)}")

    def _clean_response(self, response: str) -> str:
        """
        Clean LLM response by removing unwanted formatting and tags.

        Args:
            response: Raw LLM response

        Returns:
            Cleaned response text
        """
        if not response:
            return ""

        cleaned = response.strip()

        # Remove <think> tags and their content
        cleaned = re.sub(r'<think>.*?</think>', '', cleaned, flags=re.DOTALL | re.IGNORECASE)

        # Remove any remaining XML/HTML-like tags
        cleaned = re.sub(r'<[^>]+>', '', cleaned)

        # Remove common prefixes (explanations before the actual content)
        prefixes_to_remove = [
            r'^(This section|This interactive|This|The|A|An)\s+(explores|describes|is about|discusses|covers|showcases|illustrates|provides|offers|highlights)\s+',
            r'^Descriptive Caption:\s*',
            r'^Description:\s*',
            r'^Label:\s*',
            r'^Output:\s*',
        ]
        for prefix_pattern in prefixes_to_remove:
            cleaned = re.sub(prefix_pattern, '', cleaned, flags=re.IGNORECASE)

        # Remove markdown formatting
        cleaned = re.sub(r'[*_`#\[\]]+', '', cleaned)

        # Remove multiple newlines/spaces
        cleaned = re.sub(r'\n+', ' ', cleaned)
        cleaned = re.sub(r'\s+', ' ', cleaned)

        # Final trim
        cleaned = cleaned.strip()

        if cleaned != response:
            logger.info(f"Cleaned response: '{response[:100]}...' -> '{cleaned[:100]}...'")

        return cleaned

    def validate_response(self, response: str, expected_language: str) -> bool:
        """
        Validate that response matches expected language and quality criteria.

        Args:
            response: Generated response
            expected_language: Expected language (e.g., "English", "Arabic")

        Returns:
            True if response appears to be in the expected language
        """
        if not response or not response.strip():
            logger.warning("Empty response received")
            return False

        # Check for thinking tags (should have been cleaned, but double-check)
        if '<think>' in response.lower() or '</think>' in response.lower():
            logger.warning(f"Response contains thinking tags: {response[:50]}")
            return False

        # Check for XML/HTML tags
        if re.search(r'<[^>]+>', response):
            logger.warning(f"Response contains XML/HTML tags: {response[:50]}")
            return False

        # Check for explanatory prefixes
        explanatory_patterns = [
            r'^(This section|This interactive|This|The section)',
            r'^Descriptive Caption:',
            r'^Description:',
        ]
        for pattern in explanatory_patterns:
            if re.match(pattern, response, re.IGNORECASE):
                logger.warning(f"Response starts with explanatory text: {response[:50]}")
                return False

        # Basic validation: check for Arabic unicode range
        if expected_language.lower() in ["arabic", "ar"]:
            has_arabic = any('\u0600' <= char <= '\u06FF' for char in response)
            if not has_arabic:
                logger.warning(f"Expected Arabic but response has no Arabic characters: {response[:50]}")
                return False

        # Check for excessive markdown formatting
        markdown_chars = response.count('*') + response.count('_') + response.count('#')
        if markdown_chars > len(response) * 0.1:  # More than 10% markdown chars
            logger.warning(f"Response has excessive markdown formatting: {response[:50]}")
            return False

        # Check response length (labels should be concise)
        word_count = len(response.split())
        if word_count > 50:  # Too long for a label
            logger.warning(f"Response too long ({word_count} words): {response[:50]}")
            return False

        return True

    def generate_with_retry(
        self,
        prompt: str,
        expected_language: str,
        max_retries: int = 5,
        **kwargs
    ) -> str:
        """
        Generate with validation and retry logic.

        Args:
            prompt: Input prompt
            expected_language: Expected response language
            max_retries: Maximum retry attempts
            **kwargs: Additional arguments for generate()

        Returns:
            Validated generated text

        Raises:
            LLMError: If all retries fail validation
        """
        for attempt in range(max_retries + 1):
            response = self.generate(prompt, **kwargs)

            if self.validate_response(response, expected_language):
                return response

            logger.warning(
                f"Response validation failed (attempt {attempt + 1}/{max_retries + 1}). "
                f"Response: {response[:100]}"
            )

        raise LLMError(
            f"Failed to generate valid response after {max_retries + 1} attempts. "
            f"Expected language: {expected_language}"
        )
