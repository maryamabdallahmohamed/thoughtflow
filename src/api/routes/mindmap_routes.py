"""API routes for mindmap generation"""
import logging
import tempfile
import os
from typing import Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form
from src.core.models.schemas import (
    MindmapGenerationRequest,
    MindmapResponse,
    FilePreprocessResponse,
    ErrorResponse
)
from src.core.builders.mindmap_builder import MindmapBuilder
from src.api.dependencies import get_mindmap_builder, get_json_preprocessor
from src.loader.json_loader import JSONPreprocessor
from src.loader.pdf_loader import pdf_to_text
from src.utils.language_detector import LanguageDetector
from config.settings import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["mindmap"])


@router.post("/generate-mindmap", response_model=MindmapResponse)
async def generate_mindmap(
    request: MindmapGenerationRequest,
    builder: MindmapBuilder = Depends(get_mindmap_builder)
):
    """
    Generate a mindmap from text document.

    Args:
        request: Mindmap generation request
        builder: Injected mindmap builder

    Returns:
        Generated mindmap with metadata

    Raises:
        HTTPException: If generation fails
    """
    try:
        logger.info("Received mindmap generation request")

        # Generate mindmap
        mindmap_dict = builder.build(
            document=request.document,
            language=request.lang,
            max_depth=request.max_depth,
            min_size=request.min_size
        )

        # Detect language if not provided
        detected_lang = request.lang or LanguageDetector.detect(request.document)

        return MindmapResponse(
            success=True,
            mindmap=mindmap_dict,
            metadata={
                "language": detected_lang,
                "max_depth": request.max_depth,
                "min_size": request.min_size,
                "document_length": len(request.document),
                "node_count": _count_nodes(mindmap_dict)
            }
        )

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"Mindmap generation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate mindmap: {str(e)}"
        )


@router.post("/preprocess-file", response_model=FilePreprocessResponse)
async def preprocess_file(
    file: UploadFile = File(...),
    preprocessor: JSONPreprocessor = Depends(get_json_preprocessor)
):
    """
    Upload and preprocess a file (JSON or PDF).

    Args:
        file: Uploaded file
        preprocessor: Injected JSON preprocessor

    Returns:
        Preprocessed text and metadata

    Raises:
        HTTPException: If preprocessing fails
    """
    tmp_path = None

    try:
        # Validate file extension
        suffix = os.path.splitext(file.filename)[-1].lower()
        if suffix not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {suffix}. "
                       f"Allowed: {', '.join(settings.ALLOWED_EXTENSIONS)}"
            )

        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            contents = await file.read()

            if not contents:
                raise HTTPException(status_code=400, detail="Empty file uploaded")

            # Check file size
            if len(contents) > settings.MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=400,
                    detail=f"File too large (max {settings.MAX_FILE_SIZE} bytes)"
                )

            tmp.write(contents)
            tmp_path = tmp.name

        # Process based on file type
        logger.info(f"Processing {suffix} file: {file.filename}")

        if suffix == ".json":
            data = preprocessor.load_and_preprocess_data(tmp_path)
        elif suffix == ".pdf":
            data = pdf_to_text(tmp_path)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")

        if not data:
            raise HTTPException(
                status_code=400,
                detail="No valid text data found in file"
            )

        # Convert to string
        if isinstance(data, list):
            processed_text = "\n".join(str(item) for item in data if item)
        else:
            processed_text = str(data)

        # Detect language
        detected_lang = LanguageDetector.detect(processed_text)

        return FilePreprocessResponse(
            success=True,
            filename=file.filename,
            processed_text=processed_text,
            text_length=len(processed_text),
            detected_language=detected_lang
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"File preprocessing failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process file: {str(e)}"
        )

    finally:
        # Cleanup temporary file
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except Exception as e:
                logger.warning(f"Failed to delete temp file: {e}")


@router.post("/generate-from-file", response_model=MindmapResponse)
async def generate_mindmap_from_file(
    file: UploadFile = File(...),
    lang: Optional[str] = Form(None),
    max_depth: int = Form(3),
    min_size: int = Form(2),
    builder: MindmapBuilder = Depends(get_mindmap_builder),
    preprocessor: JSONPreprocessor = Depends(get_json_preprocessor)
):
    """
    Upload a file and generate mindmap in one step.

    Args:
        file: Uploaded file (JSON or PDF)
        lang: Target language (optional)
        max_depth: Maximum tree depth
        min_size: Minimum cluster size
        builder: Injected mindmap builder
        preprocessor: Injected JSON preprocessor

    Returns:
        Generated mindmap with metadata

    Raises:
        HTTPException: If generation fails
    """
    tmp_path = None

    try:
        # Validate and process file
        suffix = os.path.splitext(file.filename)[-1].lower()

        if suffix not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {suffix}"
            )

        # Save file
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            contents = await file.read()

            if not contents:
                raise HTTPException(status_code=400, detail="Empty file")

            if len(contents) > settings.MAX_FILE_SIZE:
                raise HTTPException(status_code=400, detail="File too large")

            tmp.write(contents)
            tmp_path = tmp.name

        # Extract text
        logger.info(f"Extracting text from {file.filename}")

        if suffix == ".json":
            data = preprocessor.load_and_preprocess_data(tmp_path)
        elif suffix == ".pdf":
            data = pdf_to_text(tmp_path)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")

        if not data:
            raise HTTPException(status_code=400, detail="No valid text found")

        # Convert to string
        if isinstance(data, list):
            document_text = "\n".join(str(item) for item in data if item)
        else:
            document_text = str(data)

        # Generate mindmap
        logger.info("Generating mindmap from extracted text")

        mindmap_dict = builder.build(
            document=document_text,
            language=lang,
            max_depth=max_depth,
            min_size=min_size
        )

        detected_lang = lang or LanguageDetector.detect(document_text)

        return MindmapResponse(
            success=True,
            mindmap=mindmap_dict,
            metadata={
                "filename": file.filename,
                "language": detected_lang,
                "max_depth": max_depth,
                "min_size": min_size,
                "document_length": len(document_text),
                "node_count": _count_nodes(mindmap_dict)
            }
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Failed to generate mindmap from file: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate mindmap: {str(e)}"
        )

    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except Exception:
                pass


def _count_nodes(mindmap_dict: dict) -> int:
    """
    Count total nodes in mindmap.

    Args:
        mindmap_dict: Mindmap dictionary

    Returns:
        Total node count
    """
    count = 1  # Current node
    for child in mindmap_dict.get("children", []):
        count += _count_nodes(child)
    return count
