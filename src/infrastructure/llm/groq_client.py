"""GROQ LLM client implementation (raw output, no cleaning)"""
import logging
from typing import Optional
from groq import Groq
from config.settings import settings
from src.infrastructure.llm.base import BaseLLMClient, LLMError

logger = logging.getLogger(__name__)


class GroqClient(BaseLLMClient):
    """
    GROQ LLM client implementation.

    Returns raw model output without post-processing.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ):
        self.api_key = api_key or settings.GROQ_API_KEY
        self.model = model or settings.GROQ_MODEL
        self.default_temperature = (
            temperature if temperature is not None else settings.GROQ_TEMPERATURE
        )
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
        Generate text completion from GROQ (raw response).
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

            logger.debug(f"Generated raw response: {response[:100]}...")
            return response

        except Exception as e:
            logger.error(f"GROQ generation failed: {e}")
            raise LLMError(f"Failed to generate completion: {str(e)}")
