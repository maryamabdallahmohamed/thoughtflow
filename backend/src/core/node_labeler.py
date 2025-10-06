import logging
from backend.infrastructure.llm import GroqClient
from langchain_core.output_parsers import JsonOutputParser 
from langchain.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import List, Optional
import re
import json
from json import JSONDecodeError

logger = logging.getLogger("NodeLabeler")


class MindmapNode(BaseModel):
    label: str = Field(..., description="Short descriptive label (3-5 words) that captures the main theme")


class NodeLabelerService:
    def __init__(self):
        self.llm = GroqClient()
        self.parser = JsonOutputParser(pydantic_object=MindmapNode)

        self.prompt = ChatPromptTemplate.from_template("""
You are creating a descriptive label for a cluster of related text in a mindmap.

Analyze the following text samples and create a SHORT, DESCRIPTIVE label that captures the main theme or topic.

Text samples:
{text_samples}

Context:
- This is at depth level {depth} in the hierarchy
- Parent topic: {parent_label}

Requirements:
- Label must be 3-5 words maximum
- Label should describe the CONTENT of the texts, not generic terms
- Label must be specific and meaningful
- DO NOT use generic words like "Root", "Cluster", "Node", "Unnamed"
- Extract the key concept or theme from the text samples
-Response should be in {lang} only.

Return ONLY valid JSON matching this form in {lang}:
{format_instructions}

Example outputs:
{{"label": "Machine Learning Algorithms"}}
{{"label": "Climate Change Impacts"}}
{{"label": "Software Design Patterns"}}
""")

    def generate_label(self, texts, depth=0, parent_label=None,lang="Arabic"):
        try:
            # Use more text samples for better context
            sample_text = " ".join(texts[:10]) if texts else "N/A"
            
            # Truncate if too long (keep first 1000 chars)
            if len(sample_text) > 1000:
                sample_text = sample_text[:1000] + "..."
            
            formatted_prompt = self.prompt.format(
                format_instructions=self.parser.get_format_instructions(),
                text_samples=sample_text,
                parent_label=parent_label or "Main Topic",
                depth=depth,
                lang=lang
            )

            llm_output = self.llm.generate(formatted_prompt)
            
            if not llm_output or not llm_output.strip():
                logger.warning("⚠️ Empty LLM output, using fallback label.")
                return MindmapNode(label=self._create_fallback_label(texts))

            # Extract JSON substring
            match = re.search(r"\{[\s\S]*\}", llm_output)
            cleaned_output = match.group(0).strip() if match else llm_output.strip()

            # Remove markdown fences
            cleaned_output = re.sub(r"^```(json)?|```$", "", cleaned_output, flags=re.MULTILINE).strip()

            try:
                result = self.parser.parse(cleaned_output)
            except Exception:
                try:
                    data = json.loads(cleaned_output)
                    result = MindmapNode(**data)
                except JSONDecodeError:
                    logger.warning(f"⚠️ Could not parse JSON: {cleaned_output[:120]}...")
                    return MindmapNode(label=self._create_fallback_label(texts))

            # Ensure we have a MindmapNode object
            if isinstance(result, dict):
                result = MindmapNode(**result)

            # Validate label quality
            label = getattr(result, "label", "").strip()
            
            # Check for invalid labels
            invalid_labels = ["root", "unnamed cluster", "cluster", "node", "unnamed", "n/a", ""]
            if not label or label.lower() in invalid_labels:
                logger.warning(f"⚠️ Invalid label generated: '{label}', using fallback")
                result.label = self._create_fallback_label(texts)
            else:
                result.label = label

            logger.info(f"✅ Generated label: {result.label}")
            return result

        except Exception as e:
            logger.error(f"❌ Label generation failed: {e}")
            return MindmapNode(label=self._create_fallback_label(texts))

    def _create_fallback_label(self, texts):
        """Create a simple fallback label from the first few words of text"""
        if not texts or not texts[0]:
            return "Text Cluster"
        
        # Take first text, get first 4-5 words
        first_text = texts[0].strip()
        words = first_text.split()[:5]
        fallback = " ".join(words)
        
        # Capitalize first letter
        if fallback:
            fallback = fallback[0].upper() + fallback[1:]
            # Truncate if too long
            if len(fallback) > 50:
                fallback = fallback[:47] + "..."
        else:
            fallback = "Text Cluster"
            
        return fallback