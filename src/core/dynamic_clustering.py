from sklearn.decomposition import TruncatedSVD
from sklearn.cluster import AgglomerativeClustering
from utils.prompt_loader import PromptLoader
from src.core.llm import GROQ
from langchain_core.prompts import ChatPromptTemplate
from src.core.mindmap_builder import MindmapNode

# --- Prompt & LLM ---
def build_prompt(texts, lang):
    joined_texts = "\n".join(texts)
    template = PromptLoader.load_system_prompt("prompts/descriptive_system_prompt.yaml")
    prompt = ChatPromptTemplate.from_template(template)
    return prompt.format(language=lang, text=joined_texts)

def get_topic_label(sentences, lang="ar"):
    llm = GROQ()
    prompt = build_prompt(sentences, lang)
    return llm.chat_with_groq(prompt)

# --- Dynamic parameters ---
def dynamic_max_depth(current_depth, max_depth_base=3):
    return max(1, max_depth_base - current_depth // 2)

def dynamic_min_size(n_samples, base_min=2):
    return max(1, int(n_samples * 0.15))

# --- Recursive Hierarchical Clustering ---
def recursive_cluster(sentences, embeddings, depth=0, max_depth_base=3, min_size_base=2, cluster_id="root", lang=None):
    if len(sentences) < min_size_base:
        leaf_label = get_topic_label(sentences, lang=lang)
        return MindmapNode(cluster_id, label=leaf_label, children=[])  

    max_depth = dynamic_max_depth(depth, max_depth_base)
    min_size = dynamic_min_size(len(sentences), min_size_base)

    if depth >= max_depth or len(sentences) < min_size:
        leaf_label = get_topic_label(sentences, lang=lang)
        return MindmapNode(cluster_id, label=leaf_label, children=[])  

    # Dimensionality reduction
    svd = TruncatedSVD(n_components=min(embeddings.shape[1], 50))
    reduced = svd.fit_transform(embeddings)

    # Dynamic clustering
    n_clusters = min(2 + depth, len(sentences))
    clust = AgglomerativeClustering(n_clusters=n_clusters)
    labels = clust.fit_predict(reduced)

    # Create node
    cluster_label = get_topic_label(sentences, lang=lang)
    node = MindmapNode(cluster_id, label=cluster_label, children=[])

    # Recurse for subclusters
    for sub_label in set(labels):
        sub_indices = [i for i, l in enumerate(labels) if l == sub_label]
        sub_sentences = [sentences[i] for i in sub_indices]
        sub_embeddings = embeddings[sub_indices, :]
        child_node = recursive_cluster(
            sub_sentences,
            sub_embeddings,
            depth+1,
            max_depth_base,
            min_size_base,
            f"{cluster_id}.{sub_label}",
            lang=lang
        )
        if child_node:
            node.children.append(child_node)

    return node