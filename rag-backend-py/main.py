import logging
from pathlib import Path

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Import API routers
from api.files import router as files_router
from api.chunks import router as chunks_router
from api.embeddings import router as embeddings_router
from api.vector_index import router as index_router
from api.search import router as search_router
from api.generation import router as generation_router
from api.pipeline import router as pipeline_router
from api.system import router as system_router
from constants import API_PREFIX

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("rag-backend")

# Create the FastAPI application
app = FastAPI(
    title="RAG System API",
    description="Retrieval-Augmented Generation (RAG) System Backend API",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Standard error response
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"code": 500, "message": "Internal server error", "data": None},
    )


# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "RAG System API",
        "version": "0.1.0",
        "docs_url": "/docs",
    }


# Mount all routers with the API prefix
app.include_router(files_router, prefix=API_PREFIX)
app.include_router(chunks_router, prefix=API_PREFIX)
app.include_router(embeddings_router, prefix=API_PREFIX)
app.include_router(index_router, prefix=API_PREFIX)
app.include_router(search_router, prefix=API_PREFIX)
app.include_router(generation_router, prefix=API_PREFIX)
app.include_router(pipeline_router, prefix=API_PREFIX)
app.include_router(system_router, prefix=API_PREFIX)

# Create necessary directories on startup
@app.on_event("startup")
async def startup_event():
    data_dir = Path("data")
    dirs = [
        data_dir / "original",  # Original files
        data_dir / "chunks",  # Text chunks
        data_dir / "vectors",  # Vector embeddings
        data_dir / "indexes",  # Vector indexes
        data_dir / "logs",  # Log files
    ]
    for dir_path in dirs:
        dir_path.mkdir(parents=True, exist_ok=True)
    logger.info("Data directories created")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
