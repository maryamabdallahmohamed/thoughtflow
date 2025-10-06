"""GROQ LLM client implementation (raw output, no cleaning)"""
import logging
from groq import Groq
from dotenv import load_dotenv
import os
load_dotenv()
api_key= os.getenv("Groq_API")
logger = logging.getLogger(__name__)


class GroqClient():
    """
    GROQ LLM client implementation.

    Returns raw model output without post-processing.
    """

    def __init__(self):
        self.api_key = api_key
        self.model =  "qwen/qwen3-32b"
        self.default_temperature = 0
        self.default_max_tokens = 1024

        self.client = Groq(api_key=self.api_key)
        logger.info(f"Initialized GROQ client with model: {self.model}")

    def generate( self, prompt: str,stream=True) :
        """
        Generate text completion from GROQ (raw response).
        """
        try:
            temp = self.default_temperature
            max_tok =  self.default_max_tokens

            logger.debug(f"Generating with temperature={temp}, max_tokens={max_tok}")

            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temp,
                max_completion_tokens=max_tok,
                top_p= 0.95,
                stream=True,
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
