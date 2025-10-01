import json
import tempfile
import os
import re
import numpy as np
from typing import Union, List, Dict, Any
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.core.mindmap_builder import build_mindmap
from src.loader.json_loader import JSONPreprocessor
from src.loader.pdf_loader import pdf_to_text

app = FastAPI(
    title="Mindmap API",
    description="API for generating hierarchical mindmaps from documents",
    version="1.0.0"
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

processor = JSONPreprocessor()

# Supported file extensions
SUPPORTED_EXTENSIONS = {".json", ".pdf"}


# --- Helper for JSON-safe conversion ---
def make_json_safe(obj: Any) -> Any:
    """
    Recursively convert numpy types and other non-JSON-serializable objects
    to JSON-safe Python types.
    """
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
    """Health check endpoint"""
    return {
        "message": "Mindmap API is running 🚀",
        "version": "1.0.0",
        "endpoints": {
            "preprocess": "/preprocess/",
            "generate_mindmap": "/generate-mindmap",
            "generate_from_file": "/generate-mindmap-from-file"
        }
    }


@app.get("/health")
def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "services": {
            "embedder": "ready",
            "processor": "ready"
        }
    }


# --- STEP 1: Upload + Preprocess JSON or PDF ---
@app.post("/preprocess/")
async def preprocess_file(file: UploadFile = File(...)):
    """
    Upload and preprocess a JSON or PDF file.
    
    Returns the extracted text content ready for mindmap generation.
    """
    tmp_path = None
    try:
        # Validate file extension
        suffix = os.path.splitext(file.filename)[-1].lower()
        if suffix not in SUPPORTED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {suffix}. Only {', '.join(SUPPORTED_EXTENSIONS)} are allowed."
            )

        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            contents = await file.read()
            if not contents:
                raise HTTPException(status_code=400, detail="Empty file uploaded")
            tmp.write(contents)
            tmp_path = tmp.name

        # Process based on file type
        if suffix == ".json":
            data = processor.load_and_preprocess_data(tmp_path)
        elif suffix == ".pdf":
            data = pdf_to_text(tmp_path)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")

        if not data:
            raise HTTPException(
                status_code=400,
                detail="No valid text data found in the file"
            )

        # Handle different data types
        if isinstance(data, list):
            processed_text = "\n".join(str(item) for item in data if item)
        else:
            processed_text = str(data)

        return {
            "success": True,
            "filename": file.filename,
            "processed_text": processed_text,
            "text_length": len(processed_text)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except Exception:
                pass


# --- STEP 2: Generate Mindmap from Text ---
class MindmapRequest(BaseModel):
    document: str = Field(..., description="Text document to generate mindmap from")
    lang: str = Field(default="en", description="Language code")
    max_depth: int = Field(default=3, ge=1, le=10, description="Maximum depth of clustering")
    min_size: int = Field(default=2, ge=1, le=100, description="Minimum cluster size")


@app.post("/generate-mindmap")
def generate_mindmap(req: MindmapRequest):
    """
    Generate a mindmap from provided text document.
    
    Returns a hierarchical JSON structure representing the mindmap.
    """
    try:
        if not req.document or not req.document.strip():
            raise HTTPException(status_code=400, detail="Document text cannot be empty")

        # Generate mindmap
        mindmap_data = build_mindmap(
            req.document,
            req.lang,
            req.max_depth,
            req.min_size
        )

        # Ensure JSON-safe output
        safe_mindmap = make_json_safe(mindmap_data)

        return {
            "success": True,
            "mindmap": safe_mindmap,
            "metadata": {
                "lang": req.lang,
                "max_depth": req.max_depth,
                "min_size": req.min_size,
                "document_length": len(req.document)
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating mindmap: {str(e)}"
        )


# --- STEP 3: Combined endpoint - Upload file and generate mindmap ---
@app.post("/generate-mindmap-from-file")
async def generate_mindmap_from_file(
    file: UploadFile = File(...),
    lang: str = "en",
    max_depth: int = 3,
    min_size: int = 2
):
    """
    Upload a file (JSON or PDF) and directly generate a mindmap.
    
    This combines preprocessing and mindmap generation in one step.
    """
    tmp_path = None
    try:
        # Validate file extension
        suffix = os.path.splitext(file.filename)[-1].lower()
        if suffix not in SUPPORTED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {suffix}. Only {', '.join(SUPPORTED_EXTENSIONS)} are allowed."
            )

        # Save and process file
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            contents = await file.read()
            if not contents:
                raise HTTPException(status_code=400, detail="Empty file uploaded")
            tmp.write(contents)
            tmp_path = tmp.name

        # Extract text
        if suffix == ".json":
            data = processor.load_and_preprocess_data(tmp_path)
        elif suffix == ".pdf":
            data = pdf_to_text(tmp_path)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")

        if not data:
            raise HTTPException(status_code=400, detail="No valid text data found")

        # Convert to string
        if isinstance(data, list):
            document_text = "\n".join(str(item) for item in data if item)
        else:
            document_text = str(data)

        # Generate mindmap
        mindmap_data = build_mindmap(document_text, lang, max_depth, min_size)
        safe_mindmap = make_json_safe(mindmap_data)

        return {
            "success": True,
            "filename": file.filename,
            "mindmap": safe_mindmap,
            "metadata": {
                "lang": lang,
                "max_depth": max_depth,
                "min_size": min_size,
                "document_length": len(document_text)
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating mindmap from file: {str(e)}"
        )
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except Exception:
                pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)