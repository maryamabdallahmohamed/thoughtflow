from src.core.llm import GROQ
from utils.prompt_loader import PromptLoader
from utils.language_detector import returnlang
from langchain_core.prompts import ChatPromptTemplate

llm=GROQ()

class MindmapDescriptionGenerator:
    def __init__(self, model="gemma2-9b-it"):

        self.client= llm.client

    def generate_description(self, node_texts, language_used=None, caption_type="branch"):
        """
        Generate a descriptive caption for hover tooltips.
        
        Args:
            node_texts (list): List of text segments (branch or cluster content).
            language_used (str): Language for the description (auto-detected if None)
            caption_type (str): 'branch' or 'main'
        Returns:
            str: Descriptive caption
        """
        # Auto-detect language if not provided
        if language_used is None:
            sample_text = " ".join(node_texts)  #
            language_used = returnlang(sample_text)
        
        prompt = self._build_prompt(node_texts, language_used, caption_type)
        completion = llm.chat_with_groq(prompt)
        return completion

    def _build_prompt(self, texts, lang, caption_type):
        """Helper: build prompt for Groq model."""
        joined_texts = "\n".join(texts)
        
        # Load system prompt template from YAML
        template = PromptLoader.load_system_prompt("prompts/descriptive_system_prompt.yaml")
        
        # Create prompt with placeholders
        prompt = ChatPromptTemplate.from_template(template)
        
        # Format the prompt with actual values
        formatted_prompt = prompt.format(
            language=lang,
            caption_type=caption_type,
            text=joined_texts
        )
        
        return formatted_prompt

    def apply_descriptions_to_mindmap(self, result):
        """
        Add descriptive captions for hover tooltips to the mindmap result.
        Extends branches with 'description' and main topic with 'overview'.
        """
        # Main topic description
        main_description = self.generate_description(
            result["texts"], 
            result["language_used"], 
            caption_type="main topic overview"
        )
        result["mindmap"]["overview"] = main_description

        # Each branch gets a description
        for branch in result["mindmap"]["branches"]:
            branch_texts = [c["text"] for c in branch["concepts"]]
            branch_desc = self.generate_description(
                branch_texts, 
                result["language_used"], 
                caption_type="branch description"
            )
            branch["description"] = branch_desc

        return result
