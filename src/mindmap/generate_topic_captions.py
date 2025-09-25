from src.core.llm import GROQ
from utils.prompt_loader import PromptLoader
from utils.language_detector import returnlang
from langchain_core.prompts import ChatPromptTemplate
llm=GROQ()

class MindmapCaptionGenerator:
    def __init__(self,):
        self.client= llm.client


    def generate_caption(self, branch_texts, language_used=None, caption_type="branch"):
        """
        Generate a caption for a branch or the main topic.
        """
        # Auto-detect language if not provided
        if language_used is None:
            sample_text = " ".join(branch_texts[:3])  # Use first few texts for detection
            language_used = returnlang(sample_text)
        
        prompt = self._build_prompt(branch_texts, language_used, caption_type)
        completion = llm.chat_with_groq(prompt)
        
        return completion

    def _build_prompt(self, texts, lang, caption_type):
        """Helper: build a prompt for Groq"""
        joined_texts = "\n".join(texts[:5])
        
        # Load system prompt template from YAML
        template = PromptLoader.load_system_prompt("prompts/topic_system_prompt.yaml")
        
        # Create prompt with placeholders
        prompt = ChatPromptTemplate.from_template(template)
        
        # Format the prompt with actual values
        formatted_prompt = prompt.format(
            language=lang,
            caption_type=caption_type,
            text=joined_texts
        )
        
        return formatted_prompt

    def apply_captions_to_mindmap(self, result):
        """
        Replace branch and main topic titles inside the mindmap result.
        Modifies the result in place and returns it.
        """
        # Replace main topic
        main_caption = self.generate_caption(
            result["texts"],
            result["language_used"],
            caption_type="main topic"
        )
        result["mindmap"]["main_topic"] = main_caption

        # Replace each branch title
        for branch in result["mindmap"]["branches"]:
            branch_texts = [c["text"] for c in branch["concepts"]]
            branch_caption = self.generate_caption(
                branch_texts, 
                result["language_used"], 
                caption_type="branch title"
            )
            branch["title"] = branch_caption

        return result

