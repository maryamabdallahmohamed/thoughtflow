# mindmap_evaluation.py
"""
Script to evaluate the accuracy of a mindmap by comparing it to a reference mindmap or text corpus.
Metrics: BERTScore, ROUGE-L, BLEU, Cosine Similarity (SentenceTransformer)
Outputs: Individual node scores, average scores, final report (JSON), optional visualization.
"""

import json
from typing import List, Dict, Optional
import numpy as np
import matplotlib.pyplot as plt

# Hugging Face models (easy to replace)
BERTSCORE_MODEL = 'microsoft/deberta-xlarge-mnli'
EMBEDDING_MODEL = 'sentence-transformers/all-MiniLM-L6-v2'

# Metric imports
from bert_score import score as bertscore
from rouge_score import rouge_scorer
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# --- Metric Functions ---
def compute_bert_score(mindmap_nodes: List[str], reference_nodes: List[str], model_type: str = BERTSCORE_MODEL) -> List[float]:
    """
    Compute BERTScore (semantic similarity) for each mindmap node against reference nodes.
    Returns list of max scores per node.
    """
    P, R, F1 = bertscore(mindmap_nodes, reference_nodes, model_type=model_type, verbose=False)
    return F1.tolist()

def compute_rouge_l(mindmap_nodes: List[str], reference_nodes: List[str]) -> List[float]:
    """
    Compute ROUGE-L (content overlap) for each mindmap node against reference nodes.
    Returns list of max scores per node.
    """
    scorer = rouge_scorer.RougeScorer(['rougeL'], use_stemmer=True)
    scores = []
    for node in mindmap_nodes:
        node_scores = [scorer.score(node, ref)['rougeL'].fmeasure for ref in reference_nodes]
        scores.append(max(node_scores))
    return scores

def compute_bleu(mindmap_nodes: List[str], reference_nodes: List[str]) -> List[float]:
    """
    Compute BLEU (n-gram precision) for each mindmap node against reference nodes.
    Returns list of max scores per node.
    """
    smoothie = SmoothingFunction().method1
    scores = []
    for node in mindmap_nodes:
        node_scores = [sentence_bleu([ref.split()], node.split(), smoothing_function=smoothie) for ref in reference_nodes]
        scores.append(max(node_scores))
    return scores

def compute_cosine_similarity(mindmap_nodes: List[str], reference_nodes: List[str], model_name: str = EMBEDDING_MODEL) -> List[float]:
    """
    Compute cosine similarity using SentenceTransformer embeddings.
    Returns list of max scores per node.
    """
    model = SentenceTransformer(model_name)
    ref_embeds = model.encode(reference_nodes)
    scores = []
    for node in mindmap_nodes:
        node_embed = model.encode([node])
        sims = cosine_similarity(node_embed, ref_embeds)[0]
        scores.append(float(np.max(sims)))
    return scores

# --- Aggregation & Reporting ---
def aggregate_scores(scores_dict: Dict[str, List[float]]) -> Dict[str, float]:
    """
    Aggregate metric scores into average and overall accuracy.
    """
    avg_scores = {k: float(np.mean(v)) for k, v in scores_dict.items()}
    # Overall accuracy: mean of all metric averages
    overall = float(np.mean(list(avg_scores.values())))
    avg_scores['overall_accuracy'] = overall
    return avg_scores

def generate_report(scores_dict: Dict[str, List[float]], avg_scores: Dict[str, float], output_path: Optional[str] = None):
    """
    Print and optionally save the final report as JSON.
    """
    report = {k: avg_scores[k] for k in ['bert_score', 'rouge_l', 'bleu', 'cosine_similarity', 'overall_accuracy'] if k in avg_scores}
    print(json.dumps(report, indent=2))
    if output_path:
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)

# --- Visualization ---
def visualize_node_scores(scores_dict: Dict[str, List[float]], mindmap_nodes: List[str], threshold: float = 0.6):
    """
    Visualize node-wise accuracy as a bar chart. Highlight nodes with low similarity (< threshold).
    """
    metrics = list(scores_dict.keys())
    num_nodes = len(mindmap_nodes)
    x = np.arange(num_nodes)
    width = 0.2
    plt.figure(figsize=(12, 6))
    for i, metric in enumerate(metrics):
        plt.bar(x + i * width, scores_dict[metric], width, label=metric)
    # Highlight low-score nodes
    for idx in x:
        if any(scores_dict[m][idx] < threshold for m in metrics):
            plt.text(idx, 0.05, 'Low', color='red', ha='center', va='bottom', fontsize=8)
    plt.xticks(x + width, [f'Node {i+1}' for i in x], rotation=45)
    plt.ylim(0, 1)
    plt.ylabel('Similarity Score')
    plt.title('Mindmap Node-wise Accuracy')
    plt.legend()
    plt.tight_layout()
    plt.show()

# --- Main Evaluation Function ---
def evaluate_mindmap(mindmap_nodes: List[str], reference_nodes: List[str], visualize: bool = True, output_json: Optional[str] = None):
    """
    Run all metrics, aggregate, report, and visualize.
    """
    # Compute metrics
    bert_scores = compute_bert_score(mindmap_nodes, reference_nodes)
    rouge_scores = compute_rouge_l(mindmap_nodes, reference_nodes)
    bleu_scores = compute_bleu(mindmap_nodes, reference_nodes)
    cosine_scores = compute_cosine_similarity(mindmap_nodes, reference_nodes)
    scores_dict = {
        'bert_score': bert_scores,
        'rouge_l': rouge_scores,
        'bleu': bleu_scores,
        'cosine_similarity': cosine_scores
    }
    avg_scores = aggregate_scores(scores_dict)
    generate_report(scores_dict, avg_scores, output_json)
    if visualize:
        visualize_node_scores(scores_dict, mindmap_nodes)
    return scores_dict, avg_scores


# --- Data Loading Utilities ---
def extract_texts_from_mindmap(node: dict) -> List[str]:
    """
    Recursively extract all texts from a mindmap node tree.
    """
    texts = []
    if isinstance(node, dict):
        if "texts" in node and isinstance(node["texts"], list):
            texts.extend(node["texts"])
        if "clusters" in node and isinstance(node["clusters"], dict):
            for child in node["clusters"].values():
                texts.extend(extract_texts_from_mindmap(child))
    return texts

def load_mindmap_nodes(mindmap_json_path: str) -> List[str]:
    """
    Load and extract all node texts from a mindmap JSON file.
    """
    with open(mindmap_json_path, 'r', encoding='utf-8') as f:
        mindmap = json.load(f)
    return extract_texts_from_mindmap(mindmap)

def load_reference_nodes(reference_json_path: str) -> List[str]:
    """
    Load all paragraphs from a reference JSON file (dict of numbered paragraphs).
    """
    with open(reference_json_path, 'r', encoding='utf-8') as f:
        ref_data = json.load(f)
    # If the file is a dict of numbered paragraphs, get values
    if isinstance(ref_data, dict):
        return [v for v in ref_data.values() if isinstance(v, str)]
    elif isinstance(ref_data, list):
        return [str(x) for x in ref_data]
    else:
        raise ValueError("Reference file format not recognized.")

# --- CLI Entry Point ---
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Evaluate mindmap accuracy against reference data.")
    parser.add_argument('--mindmap', type=str, default="enriched_mindmap.json", help="Path to mindmap JSON file.")
    parser.add_argument('--reference', type=str, default="uploads/1760184507266_unit1ground_truth_clean.json", help="Path to reference JSON file.")
    parser.add_argument('--output', type=str, default="mindmap_report.json", help="Path to save report JSON.")
    parser.add_argument('--no-viz', action='store_true', help="Disable visualization.")
    args = parser.parse_args()

    print(f"Loading mindmap nodes from {args.mindmap} ...")
    mindmap_nodes = load_mindmap_nodes(args.mindmap)
    print(f"Loaded {len(mindmap_nodes)} mindmap nodes.")

    print(f"Loading reference nodes from {args.reference} ...")
    reference_nodes = load_reference_nodes(args.reference)
    print(f"Loaded {len(reference_nodes)} reference nodes.")

    print("Running evaluation...")
    evaluate_mindmap(
        mindmap_nodes,
        reference_nodes,
        visualize=not args.no_viz,
        output_json=args.output
    )
