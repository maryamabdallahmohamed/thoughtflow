
from src.core.ingestion_pipeline import preprocess
import re
from src.core.embedder import Embedder
from src.core.dynamic_clustering import recursive_cluster
import numpy as np

embedder=Embedder()
# -------------------- Mindmap Pipeline --------------------
def generate_mindmap(doc, lang="en", max_depth=3):
    # Split document into sentences (simple split; can improve later)
    sentences = [s.strip() for s in re.split(r"[.؟!\n]", doc) if s.strip()]
    # Preprocess sentences
    processed_sentences = [preprocess(s, lang) for s in sentences]
    # Embed sentences
    embeddings = embedder.encode(processed_sentences)
    embeddings = np.array(embeddings)
    # Run recursive clustering
    recursive_cluster(sentences, embeddings, lang=lang)

# -------------------- Example --------------------
doc_ar = """
الذكاء الاصطناعي يغير العالم.
التعلم الآلي هو جزء من الذكاء الاصطناعي.
القطط تحب النوم كثيراً.
"""

doc_en = """
Artificial intelligence is transforming the world.
Machine learning is a part of artificial intelligence.
Cats love to sleep a lot.
"""

print("---- Arabic Mindmap ----")
generate_mindmap(doc_ar, lang="ar", max_depth=2)

print("\n---- English Mindmap ----")
generate_mindmap(doc_en, lang="en", max_depth=2)