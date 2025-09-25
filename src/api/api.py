import json
import tempfile
import os
import re
import numpy as np
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse

# Import your components
from src.mindmap.clustering_system import MindmapClusteringSystem
from src.mindmap.generate_descriptive_captions import MindmapDescriptionGenerator
from src.mindmap.generate_topic_captions import MindmapCaptionGenerator
from src.loader.json_loader import JSONPreprocessor
from src.loader.pdf_loader import pdf_to_text

app = FastAPI(title="Mindmap API")

# Initialize pipeline components
system = MindmapClusteringSystem()
processor = JSONPreprocessor()
caption_gen = MindmapCaptionGenerator()
desc_gen = MindmapDescriptionGenerator()

# --- Helper for JSON-safe conversion ---
def make_json_safe(obj):
    if isinstance(obj, (set, tuple)):
        return list(obj)
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif hasattr(obj, "tolist"):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {str(k): make_json_safe(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_json_safe(v) for v in obj]
    return obj


@app.get("/")
def root():
    return {"message": "Mindmap API is running 🚀"}


# --- STEP 1: Upload + Preprocess JSON or PDF ---
@app.post("/preprocess/")
async def preprocess_file(file: UploadFile = File(...)):
    tmp_path = None
    try:
        # Save uploaded file temporarily
        suffix = os.path.splitext(file.filename)[-1].lower()
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            contents = await file.read()
            tmp.write(contents)
            tmp_path = tmp.name

        # Detect file type using regex
        if re.search(r"\.json$", file.filename, re.IGNORECASE):
            data = processor.load_and_preprocess_data(tmp_path)
        elif re.search(r"\.pdf$", file.filename, re.IGNORECASE):
            data = pdf_to_text(tmp_path)  # Returns list of text segments
        else:
            return {"error": "Unsupported file type. Only .json and .pdf are allowed."}

        if not data:
            return {"error": "No valid text data found"}

        return {"processed_text": data}

    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)


# --- STEP 2: Clustering ---
@app.post("/cluster/")
async def cluster_text(data: dict):
    try:
        clustered = system.process_document(data["processed_text"])
        return JSONResponse(content=make_json_safe(clustered))
    except Exception as e:
        return {"error": str(e)}


# --- STEP 3: Add Captions ---
@app.post("/caption/")
async def add_captions(mindmap: dict):
    try:
        with_captions = caption_gen.apply_captions_to_mindmap(mindmap)
        return JSONResponse(content=make_json_safe(with_captions))
    except Exception as e:
        return {"error": str(e)}


# --- STEP 4: Add Descriptions ---
@app.post("/describe/")
async def add_descriptions(mindmap: dict):
    try:
        with_desc = desc_gen.apply_descriptions_to_mindmap(mindmap)
        return JSONResponse(content=make_json_safe(with_desc))
    except Exception as e:
        return {"error": str(e)}


# --- STEP 5: Full Pipeline (Shortcut) ---
@app.post("/mindmap/")
async def generate_mindmap(file: UploadFile = File(...)):
    tmp_path = None
    try:
        # Save uploaded file
        suffix = os.path.splitext(file.filename)[-1].lower()
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            contents = await file.read()
            tmp.write(contents)
            tmp_path = tmp.name

        # Detect file type
        if re.search(r"\.json$", file.filename, re.IGNORECASE):
            data = processor.load_and_preprocess_data(tmp_path)
        elif re.search(r"\.pdf$", file.filename, re.IGNORECASE):
            data = pdf_to_text(tmp_path)  # Returns list of text segments
        else:
            return {"error": "Unsupported file type. Only .json and .pdf are allowed."}

        if not data:
            return {"error": "No valid text data found"}

        # Run full pipeline
        result = system.process_document(data)
        result = caption_gen.apply_captions_to_mindmap(result)
        result = desc_gen.apply_descriptions_to_mindmap(result)

        return JSONResponse(content=make_json_safe(result))

    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)
