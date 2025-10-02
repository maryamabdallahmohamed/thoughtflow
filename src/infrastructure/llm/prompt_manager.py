"""Prompt loading and management"""
import logging
import yaml
from pathlib import Path
from functools import lru_cache
from config.settings import settings

logger = logging.getLogger(__name__)


class PromptManager:
    def __init__(self, prompts_dir: str = None):
        self.prompts_dir = Path(prompts_dir or settings.PROMPTS_DIR)

    @lru_cache(maxsize=32)
    def load_prompt(self, filename: str) -> str:
        """Load a YAML prompt file and return its SYSTEM_PROMPT."""
        prompt_path = self.prompts_dir / filename

        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {prompt_path}")

        with open(prompt_path, "r", encoding="utf-8") as f:
            try:
                data = yaml.safe_load(f)
            except yaml.YAMLError as e:
                raise ValueError(f"Invalid YAML in prompt file {filename}: {e}")

        if not data or "SYSTEM_PROMPT" not in data:
            raise ValueError(f"Invalid prompt file format: {filename}")

        logger.info(f"Loaded prompt template: {filename}")
        return data["SYSTEM_PROMPT"]

    def format_prompt(self, template: str, **kwargs) -> str:
        try:
            return template.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"Missing required prompt parameter: {e}")

    def get_prompt(self, filename: str, **kwargs) -> str:
        """Generic method to get and format any prompt."""
        template = self.load_prompt(filename)
        return self.format_prompt(template, **kwargs)


# Singleton instance
_prompt_manager = None

def get_prompt_manager() -> PromptManager:
    global _prompt_manager
    if _prompt_manager is None:
        _prompt_manager = PromptManager()
    return _prompt_manager
