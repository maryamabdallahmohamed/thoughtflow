"""
ThoughtFlow Mindmap API - Main Application Entry Point

A modular, language-aware mindmap generation system with clean architecture.
"""
import logging
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from config.settings import settings
from src.api.routes.mindmap_routes import router as mindmap_router

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('thoughtflow.log')
    ]
)

logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description=settings.API_DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_CREDENTIALS,
    allow_methods=settings.CORS_METHODS,
    allow_headers=settings.CORS_HEADERS,
)


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "detail": str(exc) if settings.LOG_LEVEL == "DEBUG" else None
        }
    )


# Include routers
app.include_router(mindmap_router)


# Root endpoints
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": f"🧠 {settings.API_TITLE}",
        "version": settings.API_VERSION,
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "generate_mindmap": "/api/v1/generate-mindmap",
            "preprocess_file": "/api/v1/preprocess-file",
            "generate_from_file": "/api/v1/generate-from-file"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check if services can be initialized
        from src.api.dependencies import get_mindmap_builder
        builder = get_mindmap_builder()

        return {
            "status": "healthy",
            "version": settings.API_VERSION,
            "services": {
                "api": "operational",
                "mindmap_builder": "ready",
                "llm": "connected",
                "embedder": "loaded"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )


@app.on_event("startup")
async def startup_event():
    """Startup event handler"""
    logger.info("=" * 60)
    logger.info(f"Starting {settings.API_TITLE} v{settings.API_VERSION}")
    logger.info("=" * 60)
    logger.info(f"Environment: {settings.LOG_LEVEL}")
    logger.info(f"GROQ Model: {settings.GROQ_MODEL}")
    logger.info(f"Embedding Model: {settings.EMBEDDING_MODEL}")
    logger.info(f"Device: {settings.EMBEDDING_DEVICE}")
    logger.info("=" * 60)

    # Warm up services
    try:
        from src.api.dependencies import get_mindmap_builder
        from src.infrastructure.embedding.embedder import get_embedding_service
        logger.info("Initializing services...")
        builder = get_mindmap_builder()
        get_embedding_service()
        logger.info("✓ Services initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        logger.warning("API will start but may fail on first request")


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler"""
    logger.info("Shutting down ThoughtFlow API")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=settings.LOG_LEVEL.lower()
    )
