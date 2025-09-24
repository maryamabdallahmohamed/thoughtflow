from src.core.llm import GROQ

llm=GROQ()

class MindmapDescriptionGenerator:
    def __init__(self, model="gemma2-9b-it"):

        self.client= llm.client

    def generate_description(self, node_texts, caption_type="branch"):
        """
        Generate a descriptive caption for hover tooltips.
        
        Args:
            node_texts (list): List of text segments (branch or cluster content).
            caption_type (str): 'branch' or 'main'
        Returns:
            str: Descriptive caption
        """
        prompt = self._build_prompt(node_texts, caption_type)

        completion = llm.chat_with_groq(prompt)
        return completion

    def _build_prompt(self, texts, caption_type):
        """Helper: build prompt for Groq model."""
        joined_texts = "\n".join(texts) 
        if caption_type == "branch":
            return (
                "You are helping build an interactive mindmap. "
                "Given the following cluster texts, generate a short descriptive caption "
                "to show when the user hovers over this branch. "
                "Keep it informative:\n\n"
                f"{joined_texts}\n\nDescription:"
            )
        else:  # main topic
            return (
                "You are helping build an interactive mindmap. "
                "Given the following document texts, generate a descriptive overview "
                "that can be displayed when hovering over the main topic node. "
                f"{joined_texts}\n\nOverview:"
            )

    def apply_descriptions_to_mindmap(self, result):
        """
        Add descriptive captions for hover tooltips to the mindmap result.
        Extends branches with 'description' and main topic with 'overview'.
        """
        # Main topic description
        main_description = self.generate_description(result["texts"], caption_type="main")
        result["mindmap"]["overview"] = main_description

        # Each branch gets a description
        for branch in result["mindmap"]["branches"]:
            branch_texts = [c["text"] for c in branch["concepts"]]
            branch_desc = self.generate_description(branch_texts, caption_type="branch")
            branch["description"] = branch_desc

        return result


# Demo usage
if __name__ == "__main__":
    from src.mindmap.clustering_system import MindmapClusteringSystem

    # Cluster a small sample doc
    system = MindmapClusteringSystem()
    sample_doc = {
        "texts": [
            "AI in healthcare improves diagnostics and patient monitoring.",
            "Natural language processing is key in building advanced chatbots.",
            "Self-driving cars rely heavily on computer vision.",
            "Deep learning enables breakthroughs in image recognition.",
            "Recommendation systems benefit from machine learning algorithms."
        ]
    }
    result = system.process_document(sample_doc, document_type="json")

    # Apply descriptive captions
    desc_gen = MindmapDescriptionGenerator()
    updated_result = desc_gen.apply_descriptions_to_mindmap(result)

    # Print updated with descriptions
    print("\n📝 Updated Mindmap with Descriptions")
    print(f"Main Topic: {updated_result['mindmap']['main_topic']}")
    print(f"Overview: {updated_result['mindmap']['overview']}")
    for i, branch in enumerate(updated_result["mindmap"]["branches"]):
        print(f"   Branch {i+1}: {branch['title']}")
        print(f"      Description: {branch['description']}")
