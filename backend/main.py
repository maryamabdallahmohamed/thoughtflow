"""
ThoughtFlow Mindmap API - FastAPI server

Exposes endpoints to upload a file and generate a mindmap.
Front-end expects:
  - POST /upload (multipart form): returns { file_path }
  - POST /generate_mindmap (json body { file_path }): returns { mindmap: <tree> }
"""
import json
import logging
import time
import sys
from pathlib import Path
from typing import List, Optional
import uvicorn
import numpy as np
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# --- 1. Imports ---
from backend.src.loaders.upload_json import JSONPreprocessor
from backend.src.loaders.upload_script import pdf_to_paragraphs
from backend.src.core.cleaning_script import preprocess
from backend.src.core.dynamic_clustering import recursive_cluster
from backend.src.core.node_labeler import NodeLabelerService
from backend.src.core.node_description import NodeDescriptionService
from backend.src.core.tree_namer import TreeNamerService
from backend.utils.language_detector import returnlang
from backend.infrastructure.embedder import get_embedding_service
from backend.infrastructure.llm import GroqClient
from config.settings import settings
from backend.utils.logging_handler import get_logger

logger = logging.getLogger("mindmap.api")

UPLOAD_DIR = project_root / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

CONFIG = {
    "OUTPUT_FILE": "enriched_mindmap.json",
    "EMBEDDING_BATCH_SIZE": settings.EMBEDDING_BATCH_SIZE,
    # Prefer sane defaults; the LIMIT values are caps, not good operational defaults.
    "MAX_CLUSTER_DEPTH": settings.DEFAULT_MAX_DEPTH,
    "MIN_CLUSTER_SIZE": settings.DEFAULT_MIN_SIZE,
    "LLM_SLEEP_TIME": 0.5,
}

# Service Initialization (singletons)
json_preprocessor = JSONPreprocessor()
tree_namer_service = TreeNamerService()
llm_client = GroqClient()
embedder_service = get_embedding_service()
labeler_service = NodeLabelerService()
describer_service = NodeDescriptionService()


def enrich_node_recursively(node: dict, depth: int = 0, parent_label: Optional[str] = None, lang: str = 'Arabic') -> dict:
    """Enrich leaf and internal nodes with labels & descriptions.
    Internal nodes with no texts will be labeled by sampling texts from descendants.
    """

    def _collect_text_samples(n: dict, limit: int = 30) -> List[str]:
        samples: List[str] = []
        texts_here = n.get("texts") or []
        if texts_here:
            samples.extend(texts_here[:limit])
        if len(samples) < limit:
            for child in (n.get("clusters") or {}).values():
                if len(samples) >= limit:
                    break
                samples.extend(_collect_text_samples(child, limit - len(samples)))
        return samples

    candidate_texts = node.get("texts") or _collect_text_samples(node, 30)
    if candidate_texts:
        try:
            label_obj = labeler_service.generate_label(candidate_texts, depth, parent_label, lang=lang)
            node["label"] = label_obj.label
            time.sleep(CONFIG["LLM_SLEEP_TIME"])

            desc = describer_service.generate_description(candidate_texts, label_obj.label, depth, lang)
            node["description"] = desc
            time.sleep(CONFIG["LLM_SLEEP_TIME"])
        except Exception as e:
            logger.error(f"❌ Error enriching node at depth {depth}: {e}")
            node.setdefault("label", "Error Node")
            node.setdefault("description", "Failed to generate description")

    for child in (node.get("clusters") or {}).values():
        enrich_node_recursively(child, depth + 1, node.get("label"), lang)

    return node


def generate_mindmap_for_path(file_path: Path) -> dict:
    """Load a file (json/pdf/txt), generate enriched tree and return root node."""
    if not file_path.exists():
        raise FileNotFoundError(str(file_path))

    suffix = file_path.suffix.lower()
    logger.info(f"--- Step 1: Loading and Preprocessing document from {file_path} ---")
    if suffix == ".pdf":
        paragraphs = pdf_to_paragraphs(str(file_path))
    else:
        paragraphs = json_preprocessor.load_and_preprocess_data(str(file_path))

    if not paragraphs:
        raise ValueError("No paragraphs extracted from file.")

    lang = returnlang(paragraphs[0])
    cleaned_text = [preprocess(para, lang) for para in paragraphs]
    cleaned_text = [t for t in cleaned_text if t.strip()]
    if not cleaned_text:
        raise ValueError("No text remaining after cleaning.")

    # --- Step 2: Embeddings ---
    logger.info("--- Step 2: Generating Embeddings in batches ---")
    embeddings: List[List[float]] = []
    text_count = len(cleaned_text)
    batch_size = CONFIG["EMBEDDING_BATCH_SIZE"]
    num_batches = (text_count - 1) // batch_size + 1
    for i in range(0, text_count, batch_size):
        batch = cleaned_text[i:i + batch_size]
        embeddings.extend(embedder_service.encode(batch))
        logger.info(f"Processed batch {i // batch_size + 1}/{num_batches}")
    embeddings_np = np.array(embeddings)

    # --- Step 3: Clustering ---
    if text_count > 1:
        logger.info("--- Step 3: Starting Hierarchical Clustering ---")
        tree = recursive_cluster(
            embeddings_np,
            cleaned_text,
            max_depth=CONFIG["MAX_CLUSTER_DEPTH"],
            min_size=CONFIG["MIN_CLUSTER_SIZE"],
        )
    else:
        tree = {"texts": cleaned_text}

    # --- Step 4: Enrichment ---
    logger.info("--- Step 4: Enriching tree (LLM calls) ---")
    enriched_tree = enrich_node_recursively(tree, lang=lang)

    # Root naming
    root_label, root_desc = tree_namer_service.generate_tree_name(enriched_tree, lang=lang)
    # Add root metadata directly to enriched_tree instead of wrapping it
    enriched_tree["label"] = root_label
    enriched_tree["description"] = root_desc
    return enriched_tree


# --- 4. FastAPI App ---
app = FastAPI(title="ThoughtFlow Mindmap API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten to your Vite URL as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class GenerateRequest(BaseModel):
    file_path: str
    max_depth: int | None = None
    min_size: int | None = None


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/")
def root_redirect():
    """Convenience route so opening http://localhost:8000 goes to the docs."""
    return RedirectResponse(url="/docs", status_code=307)


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    suffix = Path(file.filename).suffix.lower()
    if suffix not in {".json", ".pdf", ".txt"}:
        raise HTTPException(status_code=400, detail="Unsupported file type. Use JSON, PDF, or TXT")

    dest = UPLOAD_DIR / f"{int(time.time()*1000)}_{Path(file.filename).name}"
    content = await file.read()
    try:
        dest.write_bytes(content)
    except Exception as e:
        logger.exception("Failed to save uploaded file")
        raise HTTPException(status_code=500, detail=str(e))
    return {"file_path": str(dest), "filename": file.filename, "size": len(content)}


@app.post("/generate_mindmap")
def generate_mindmap(req: GenerateRequest):
    try:
        # Temporarily override runtime config if provided
        if req.max_depth is not None:
            CONFIG["MAX_CLUSTER_DEPTH"] = int(req.max_depth)
        if req.min_size is not None:
            CONFIG["MIN_CLUSTER_SIZE"] = int(req.min_size)

        root = generate_mindmap_for_path(Path(req.file_path))
        return {
            "mindmap": root,
            "meta": {
                "max_depth": CONFIG["MAX_CLUSTER_DEPTH"],
                "min_size": CONFIG["MIN_CLUSTER_SIZE"],
            },
        }
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found. Upload first or check path.")
    except Exception as e:
        logger.exception("Mindmap generation failed")
        raise HTTPException(status_code=500, detail=str(e))


# --- 5. Local run (uvicorn) ---
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
