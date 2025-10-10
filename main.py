"""
ThoughtFlow Mindmap Creator - Main Script

A standalone script to generate mindmaps from documents using embeddings, clustering, and LLM enrichment.
"""
import numpy as np
import json
import logging
import time
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# --- 1. Imports ---
# Grouped by functionality (Loaders, Core Processing, Infrastructure, Utils, Visualizer)
from backend.src.loaders.upload_json import JSONPreprocessor
from backend.src.core.cleaning_script import preprocess
from backend.src.core.dynamic_clustering import recursive_cluster
from backend.src.core.node_labeler import NodeLabelerService
from backend.src.core.node_description import NodeDescriptionService
from backend.src.core.tree_namer import TreeNamerService
from backend.utils.language_detector import returnlang
from backend.infrastructure.embedder import get_embedding_service
from backend.infrastructure.llm import GroqClient
from backend.src.visualizers.mindmap_visualizer import visualize_mindmap_tree
from config.settings import settings

# --- 2. Configuration & Initialization ---
# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# General Configuration (using settings)
CONFIG = {
    "PDF_PATH": "/Users/maryamsaad/Documents/Graduation_Proj/junk/corrected_ocr_results.json",  # TODO: Make configurable
    "OUTPUT_FILE": "enriched_mindmap.json",
    "EMBEDDING_BATCH_SIZE": settings.EMBEDDING_BATCH_SIZE,
    "MAX_CLUSTER_DEPTH": settings.MAX_DEPTH_LIMIT,
    "MIN_CLUSTER_SIZE": settings.MIN_SIZE_LIMIT,
    "LLM_SLEEP_TIME": 0.5  # Time to wait between LLM calls to avoid rate limits
}

# Service Initialization (can be done once)
json_preprocessor = JSONPreprocessor()
tree_namer_service = TreeNamerService()
llm_client = GroqClient()
embedder_service = get_embedding_service()
labeler_service = NodeLabelerService()
describer_service = NodeDescriptionService()

# --- 3. Core Functions ---

def test_llm_connection(llm_client: GroqClient) -> bool:
    """Test if GroqClient is working before processing."""
    logger.info("Starting LLM connection test...")
    try:
        test_response = llm_client.generate("Say 'Hello, I am working!' in one sentence.")
        if test_response and test_response.strip():
            logger.info(f"✅ LLM test successful: {test_response[:50]}...")
            return True
        else:
            logger.error("❌ LLM returned empty response in test.")
            return False
    except Exception as e:
        logger.error(f"❌ LLM test failed: {e}")
        return False

def enrich_node_recursively(node: dict, depth: int = 0, parent_label: str = None, lang='Arabic') -> dict:
    """Recursively enrich tree nodes with labels and descriptions using LLM services."""
    if "texts" in node:
        num_texts = len(node["texts"])
        logger.info(f"Processing node at depth {depth} with {num_texts} texts.")
        
        try:
            # Generate label
            label_obj = labeler_service.generate_label(node["texts"], depth, parent_label, lang=lang)
            node["label"] = label_obj.label
            logger.debug(f"Generated label: {label_obj.label}")
            time.sleep(CONFIG["LLM_SLEEP_TIME"])

            # Generate description
            desc = describer_service.generate_description(node["texts"], label_obj.label, depth, lang)
            node["description"] = desc
            logger.debug(f"Generated description: {desc[:50]}...")
            time.sleep(CONFIG["LLM_SLEEP_TIME"])
        
        except Exception as e:
            logger.error(f"❌ Error enriching node at depth {depth}: {e}")
            node["label"] = "Error Node"
            node["description"] = "Failed to generate description"

    if "clusters" in node:
        logger.debug(f"Recursing into {len(node['clusters'])} child clusters at depth {depth}.")
        for child in node["clusters"].values():
            enrich_node_recursively(child, depth + 1, node.get("label"), lang)

    return node

# --- 4. Main Pipeline ---

def generate_mindmap(config: dict) -> dict | None:
    """The main pipeline to load, process, cluster, and enrich a document into a mindmap tree."""
    
    # --- Step 1: Load and Clean Text ---
    logger.info(f"--- Step 1: Loading and Preprocessing document from {config['PDF_PATH']} ---")
    paragraphs = json_preprocessor.load_and_preprocess_data(config['PDF_PATH'])
    
    if not paragraphs:
        logger.error("❌ No paragraphs extracted. Exiting.")
        return None

    lang = returnlang(paragraphs[0])
    logger.info(f"Detected language: {lang}")

    cleaned_text = [preprocess(para, lang) for para in paragraphs]
    cleaned_text = [t for t in cleaned_text if t.strip()]
    logger.info(f"Remaining {len(cleaned_text)} cleaned paragraphs.")

    if len(cleaned_text) == 0:
        logger.error("❌ No text remaining after cleaning. Exiting.")
        return None

    # --- Step 2: Generate Embeddings ---
    logger.info("--- Step 2: Generating Embeddings in batches ---")
    embeddings = []
    text_count = len(cleaned_text)
    batch_size = config["EMBEDDING_BATCH_SIZE"]
    num_batches = (text_count - 1) // batch_size + 1

    for i in range(0, text_count, batch_size):
        batch = cleaned_text[i:i + batch_size]
        batch_embeddings = embedder_service.encode(batch)
        embeddings.extend(batch_embeddings)
        logger.info(f"Processed batch {i // batch_size + 1}/{num_batches}")

    embeddings = np.array(embeddings)
    logger.info(f"Embeddings shape: {embeddings.shape}")

    # --- Step 3: Cluster Hierarchically ---
    if text_count > 1:
        logger.info("--- Step 3: Starting Hierarchical Clustering ---")
        tree = recursive_cluster(
            embeddings, 
            cleaned_text, 
            max_depth=config["MAX_CLUSTER_DEPTH"], 
            min_size=config["MIN_CLUSTER_SIZE"]
        )
        logger.info("✅ Clustering completed.")
    else:
        logger.warning("⚠️ Not enough text for clustering. Skipping clustering.")
        tree = {"texts": cleaned_text}

    # --- Step 4: Enrich the Tree (Labeling/Description) ---
    logger.info("--- Step 4: Enriching tree with labels and descriptions (LLM calls) ---")
    enriched_tree = enrich_node_recursively(tree, lang=lang)
    logger.info("✅ Tree enrichment completed.")

    # Generate a root node for the entire tree
    root_label, root_desc = tree_namer_service.generate_tree_name(enriched_tree, lang=lang)
    root_node = {
        "label": root_label,
        "description": root_desc,
        "clusters": {"content": enriched_tree},
    }
    
    return root_node

# --- 5. Execution Block ---

if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("Starting ThoughtFlow Mindmap Creator")
    logger.info("=" * 60)

    # Initial connection test
    if not test_llm_connection(llm_client):
        logger.error("⚠️ LLM connection failed. Check GROQ_API_KEY, validity, and network.")
        exit(1)

    # Run the main pipeline
    start_time = time.time()
    final_tree = generate_mindmap(CONFIG)

    if final_tree:
        # --- Step 5: Save and Visualize ---
        logger.info("--- Step 5: Saving and Visualizing Results ---")
        
        # Save the core content of the tree for inspection
        output_data_to_save = final_tree["clusters"]["content"]
        try:
            with open(CONFIG["OUTPUT_FILE"], 'w', encoding='utf-8') as f:
                json.dump(output_data_to_save, f, indent=2, ensure_ascii=False)
            logger.info(f"✅ Saved enriched tree content to {CONFIG['OUTPUT_FILE']}")
        except Exception as e:
            logger.error(f"❌ Failed to save output: {e}")

        # Print preview
        print("\n" + "="*80)
        print(f"ENRICHED MINDMAP TREE PREVIEW (Root Label: {final_tree['label']})")
        print("="*80)
        print(json.dumps(output_data_to_save, indent=2, ensure_ascii=False)[:3000] + "\n...")

        # Visualize
        try:
            visualize_mindmap_tree(final_tree)
            logger.info("✅ Visualization completed.")
        except Exception as e:
            logger.error(f"❌ Visualization failed: {e}")
            
    end_time = time.time()
    logger.info(f"Pipeline finished in {end_time - start_time:.2f} seconds.")
    logger.info("=" * 60)
