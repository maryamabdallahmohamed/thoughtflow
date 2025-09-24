from src.core.llm import GROQ

llm=GROQ()

class MindmapCaptionGenerator:
    def __init__(self,):
        self.client= llm.client


    def generate_caption(self, branch_texts, caption_type="branch"):
        """
        Generate a caption for a branch or the main topic.
        """
        prompt = self._build_prompt(branch_texts, caption_type)

        completion = llm.chat_with_groq(prompt)

        return completion

    def _build_prompt(self, texts, caption_type):
        """Helper: build a prompt for Groq"""
        joined_texts = "\n".join(texts[:5])  
        if caption_type == "branch":
            return (
                "You are helping to create a mindmap. "
                "Given the following branch texts, generate a short, descriptive caption :\n\n"
                f"{joined_texts}\n\nCaption:"
            )
        else:  # main topic
            return (
                "You are helping to create a mindmap. "
                "Given these document segments, generate a concise main topic :\n\n"
                f"{joined_texts}\n\nMain Topic:"
            )

    def apply_captions_to_mindmap(self, result):
        """
        Replace branch and main topic titles inside the mindmap result.
        Modifies the result in place and returns it.
        """
        # Replace main topic
        main_caption = self.generate_caption(result["texts"], caption_type="main")
        result["mindmap"]["main_topic"] = main_caption

        # Replace each branch title
        for branch in result["mindmap"]["branches"]:
            branch_texts = [c["text"] for c in branch["concepts"]]
            branch_caption = self.generate_caption(branch_texts, caption_type="branch")
            branch["title"] = branch_caption

        return result


# # Demo usage
# if __name__ == "__main__":
#     from src.mindmap.clustering_system import MindmapClusteringSystem

#     # Step 1: Cluster a small document
#     system = MindmapClusteringSystem()
#     sample_doc = {
#         "texts": [
#             "AI is transforming healthcare through diagnostics.",
#             "Natural language processing powers chatbots.",
#             "Computer vision enables self-driving cars.",
#             "Deep learning advances image recognition.",
#             "Machine learning improves recommendation systems."
#         ]
#     }
#     result = system.process_document(sample_doc, document_type="json")

#     # Step 2: Generate and apply Groq captions
#     caption_gen = MindmapCaptionGenerator()
#     updated_result = caption_gen.apply_captions_to_mindmap(result)

#     # Step 3: Print updated structure
#     print("\n🌟 Updated Mindmap with AI-generated Captions 🌟")
#     print(f"Main Topic: {updated_result['mindmap']['main_topic']}")
#     for i, branch in enumerate(updated_result["mindmap"]["branches"]):
#         print(f"   Branch {i+1}: {branch['title']} ({branch['size']} concepts)")
