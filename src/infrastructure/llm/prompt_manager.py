"""Prompt loading and management"""
import os
import yaml
import logging
from typing import Dict, Any
from pathlib import Path
from config.settings import settings

logger = logging.getLogger(__name__)


class PromptManager:
    """
    Manages loading and formatting of prompt templates.

    Prompts are stored as YAML files with placeholders that can be
    filled with dynamic values.
    """

    def __init__(self, prompts_dir: str = None):
        """
        Initialize prompt manager.

        Args:
            prompts_dir: Directory containing prompt YAML files
        """
        self.prompts_dir = Path(prompts_dir or settings.PROMPTS_DIR)
        self._cache: Dict[str, str] = {}

    def load_prompt(self, filename: str) -> str:
        """
        Load prompt template from YAML file.

        Args:
            filename: Name of the YAML file (e.g., "topic_system_prompt.yaml")

        Returns:
            Prompt template string

        Raises:
            FileNotFoundError: If prompt file doesn't exist
            ValueError: If prompt file is invalid
        """
        # Check cache first
        if filename in self._cache:
            return self._cache[filename]

        prompt_path = self.prompts_dir / filename

        if not prompt_path.exists():
            logger.error(f"Prompt file not found: {prompt_path}")
            raise FileNotFoundError(f"Prompt file not found: {prompt_path}")

        try:
            with open(prompt_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            if not data or "SYSTEM_PROMPT" not in data:
                raise ValueError(f"Invalid prompt file format: {filename}")

            prompt_template = data["SYSTEM_PROMPT"]
            self._cache[filename] = prompt_template

            logger.info(f"Loaded prompt template: {filename}")
            return prompt_template

        except yaml.YAMLError as e:
            logger.error(f"Failed to parse YAML file {filename}: {e}")
            raise ValueError(f"Invalid YAML in prompt file {filename}: {e}")

    def format_prompt(self, template: str, **kwargs) -> str:
        """
        Format prompt template with provided values.

        Args:
            template: Prompt template string with {placeholders}
            **kwargs: Values to fill placeholders

        Returns:
            Formatted prompt string
        """
        try:
            return template.format(**kwargs)
        except KeyError as e:
            logger.error(f"Missing required placeholder in prompt template: {e}")
            raise ValueError(f"Missing required prompt parameter: {e}")

    def get_topic_label_prompt(self, text: str, language: str) -> str:
        """
        Get formatted prompt for topic label generation.

        Args:
            text: Text to generate label for
            language: Target language

        Returns:
            Formatted prompt
        """
        template = self.load_prompt(settings.TOPIC_LABEL_PROMPT)
        return self.format_prompt(template, text=text, language=language)

    def get_descriptive_prompt(self, text: str, language='ar') -> str:
        """
        Get formatted prompt for descriptive caption generation.

        Args:
            text: Text to generate description for
            language: Target language

        Returns:
            Formatted prompt
        """
        template = self.load_prompt(settings.DESCRIPTIVE_PROMPT)
        return self.format_prompt(template, text=text, language=language)

    def clear_cache(self):
        """Clear the prompt template cache"""
        self._cache.clear()
        logger.info("Cleared prompt cache")


# Global prompt manager instance
_prompt_manager = None


def get_prompt_manager() -> PromptManager:
    """
    Get the global PromptManager instance (singleton pattern).

    Returns:
        PromptManager instance
    """
    global _prompt_manager
    if _prompt_manager is None:
        _prompt_manager = PromptManager()
    return _prompt_manager
