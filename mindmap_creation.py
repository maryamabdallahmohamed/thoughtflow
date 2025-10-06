from backend.src.loaders.upload_script import pdf_to_paragraphs
from backend.src.core.cleaning_script import preprocess
from backend.utils.language_detector import returnlang
from backend.infrastructure.embedder import get_embedding_service
from backend.infrastructure.llm import GroqClient
from backend.src.core.dynamic_clustering import recursive_cluster
from backend.src.core.node_labeler import NodeLabelerService
from backend.src.core.node_description import NodeDescriptionService
import numpy as np
import json

# === Step 1: Load paragraphs from PDF ===
pdf_path = "/Users/maryamsaad/Documents/Graduation_Proj/junk/chapter4_test.pdf"
paragraphs = pdf_to_paragraphs(pdf_path)
print(f"Extracted {len(paragraphs)} paragraphs.")

# === Step 2: Detect language and clean text ===
lang = returnlang(paragraphs[0])
cleaned_text = [preprocess(para, lang) for para in paragraphs]
cleaned_text = [t for t in cleaned_text if t.strip()]  # remove empties
print(f"Remaining {len(cleaned_text)} cleaned paragraphs.")

# === Step 3: Generate embeddings in batches ===
embedder = get_embedding_service()
embeddings = []

batch_size = 50
for i in range(0, len(cleaned_text), batch_size):
    batch = cleaned_text[i:i+batch_size]
    batch_embeddings = embedder.encode(batch)
    embeddings.extend(batch_embeddings)

embeddings = np.array(embeddings)
print(f"Embeddings shape: {embeddings.shape}")

# === Step 4: Cluster hierarchically ===
max_depth = 3
min_size = 2

if len(cleaned_text) > 1:
    tree = recursive_cluster(embeddings, cleaned_text, max_depth=max_depth, min_size=min_size)
    print("✅ Clustering completed.")
else:
    tree = {"message": "Not enough text for clustering."}

# === Step 5: Enrich the tree with labels and descriptions ===
labeler = NodeLabelerService()
describer = NodeDescriptionService()

def enrich_tree(node, depth=0, parent_label=None):
    if "texts" in node:
        label = labeler.generate_label(node["texts"], depth, parent_label)
        desc = describer.generate_description(node["texts"], label, depth)
        node["label"] = label
        node["description"] = desc

    if "clusters" in node:
        for cid, child in node["clusters"].items():
            enrich_tree(child, depth + 1, node.get("label"))

    return node

enriched_tree = enrich_tree(tree)

# === Step 6: Inspect (preview) the enriched tree ===
print(json.dumps(enriched_tree, indent=2, ensure_ascii=False)[:1500])
