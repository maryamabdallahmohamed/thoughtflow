import logging
from backend.infrastructure.llm import GroqClient
from langchain_core.output_parsers import JsonOutputParser 
from langchain.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
import re
import json
from json import JSONDecodeError

logger = logging.getLogger("NodeDescription")


class MindmapNodeDescription(BaseModel):
    description: str = Field(..., description="Clear 1-2 sentence summary describing the content and key concepts")


class NodeDescriptionService:
    def __init__(self):
        self.llm = GroqClient()
        self.parser = JsonOutputParser(pydantic_object=MindmapNodeDescription)

        self.prompt = ChatPromptTemplate.from_template("""
You are writing a concise description for a node in a mindmap.

Node Label: {label}
Hierarchy Level: {depth}

Text Content:
{text_samples}

Task: Write a clear, informative 1-2 sentence description that:
- Summarizes what this section is about
- Highlights key concepts or main ideas
- Uses natural, readable language
- Is specific to the content (not generic)
- Does NOT repeat the label verbatim
- Output should be in {lang}

Return ONLY valid JSON in this exact format in {lang}:
{format_instructions}

Example outputs:
{{"description": "various machine learning algorithms including supervised and unsupervised learning approaches, with focus on their practical applications."}}
{{"description": "Discusses the environmental and economic impacts of climate change on coastal communities and proposed adaptation strategies."}}
""")

    def generate_description(self, texts, label=None, depth=0,lang='Arabic'):
        try:
            # Use more text for better context
            joined_text = " ".join(texts[:10]) if texts else ""
            
            # Truncate if too long (keep first 1500 chars for descriptions)
            if len(joined_text) > 1500:
                joined_text = joined_text[:1500] + "..."
            
            if not joined_text.strip():
                logger.warning("⚠️ No text samples provided for description")
                return self._create_fallback_description(label)

            formatted_prompt = self.prompt.format(
                format_instructions=self.parser.get_format_instructions(),
                label=label or "Unknown Topic",
                depth=depth,
                text_samples=joined_text,
                lang=lang
            )

            llm_output = self.llm.generate(formatted_prompt)
            
            if not llm_output or not llm_output.strip():
                logger.warning(f"⚠️ Empty LLM output for '{label}'")
                return self._create_fallback_description(label)

            # Extract JSON substring if surrounded by text or markdown
            match = re.search(r"\{[\s\S]*\}", llm_output)
            cleaned_output = match.group(0).strip() if match else llm_output.strip()

            # Remove markdown fences like ```json ... ```
            cleaned_output = re.sub(r"^```(json)?|```$", "", cleaned_output, flags=re.MULTILINE).strip()

            try:
                result = self.parser.parse(cleaned_output)
            except Exception:
                try:
                    data = json.loads(cleaned_output)
                    result = MindmapNodeDescription(**data)
                except JSONDecodeError:
                    logger.warning(f"⚠️ Could not parse JSON: {cleaned_output[:120]}...")
                    return self._create_fallback_description(label)

            # Handle parser returning dict instead of Pydantic object
            if isinstance(result, dict):
                result = MindmapNodeDescription(**result)

            # Validate description quality
            description = getattr(result, "description", "").strip()
            
            # Check for invalid/generic descriptions
            invalid_phrases = [
                "no description available",
                "n/a",
                "unknown",
                "description not available",
                "no information",
                ""
            ]
            
            if not description or description.lower() in invalid_phrases:
                logger.warning(f"⚠️ Invalid description for '{label}': '{description}'")
                return self._create_fallback_description(label)
            
            # Check if description is too short (less than 10 chars likely invalid)
            if len(description) < 10:
                logger.warning(f"⚠️ Description too short for '{label}': '{description}'")
                return self._create_fallback_description(label)

            logger.info(f"✅ Generated description for '{label}': {description[:80]}...")
            return description

        except Exception as e:
            logger.error(f"❌ Description generation failed for '{label}': {e}")
            return self._create_fallback_description(label)

    def _create_fallback_description(self, label):
        """Create a simple fallback description"""
        if label and label.strip() and label.lower() not in ["unknown", "unknown topic"]:
            return f"This section covers topics related to {label.lower()}."
        return "This section contains related content grouped together."