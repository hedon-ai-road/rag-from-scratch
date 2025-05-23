"""
API router for chunk operations.
"""
import logging
from typing import Optional
import urllib.parse

from fastapi import APIRouter, Body, HTTPException, Path, Query
from fastapi.responses import JSONResponse

from chunking import ChunkingService
from constants import DEFAULT_CHUNK_STRATEGY, DEFAULT_OVERLAP, DEFAULT_WINDOW_SIZE
from models.base import BaseResponse
from models.chunk import ChunkCreateRequest, ChunkSettings

router = APIRouter(tags=["Chunks"])
logger = logging.getLogger("rag-backend.chunks")

chunking_service = ChunkingService()


@router.post("/files/{file_id}/chunks", response_model=BaseResponse)
async def create_chunks(
    file_id: str = Path(..., description="File ID", pattern=r".+"),
    chunk_request: ChunkCreateRequest = Body(...),
):
    """
    Create chunks for a file using documents loaded from database.
    """
    try:
        # URL decode the file_id
        file_id = urllib.parse.unquote(file_id)

        chunks = await chunking_service.create_chunks(
            file_id,
            chunk_request.chunk_strategy,
            chunk_request.window_size,
            chunk_request.overlap,
            chunk_request.custom_options,
        )

        return {
            "code": 0,
            "message": "Success",
            "data": {
                "file_id": file_id,
                "chunk_count": len(chunks),
                "chunks": chunks,
            },
        }
    except FileNotFoundError:
        return JSONResponse(
            status_code=404,
            content={
                "code": 1,
                "message": f"No documents found for file {file_id}. Please load the file first.",
                "data": None,
            },
        )
    except Exception as e:
        logger.error(f"Error creating chunks for file {file_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/files/{file_id}/chunks", response_model=BaseResponse)
async def get_chunks(
    file_id: str = Path(..., description="File ID", pattern=r".+"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    chunk_strategy: Optional[str] = Query(
        None, description="Filter by chunking strategy"
    ),
):
    """
    Get chunks for a file from database.
    """
    try:
        # URL decode the file_id
        file_id = urllib.parse.unquote(file_id)

        chunks, total = await chunking_service.get_chunks(
            file_id, page, limit, chunk_strategy
        )

        return {
            "code": 0,
            "message": "Success",
            "data": {
                "file_id": file_id,
                "chunk_count": total,
                "chunks": chunks,
                "chunk_strategy": chunk_strategy,
                "pagination": {
                    "total": total,
                    "page": page,
                    "limit": limit,
                    "pages": (total + limit - 1) // limit,
                },
            },
        }
    except Exception as e:
        logger.error(f"Error getting chunks for file {file_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/files/{file_id}/chunk-strategies", response_model=BaseResponse)
async def get_file_chunk_strategies(
    file_id: str = Path(..., description="File ID", pattern=r".+"),
):
    """
    Get all chunking strategies used for a file.
    """
    try:
        # URL decode the file_id
        file_id = urllib.parse.unquote(file_id)

        strategies = await chunking_service.get_chunk_strategies(file_id)

        return {
            "code": 0,
            "message": "Success",
            "data": {
                "file_id": file_id,
                "strategies": strategies,
            },
        }
    except Exception as e:
        logger.error(f"Error getting chunk strategies for file {file_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/files/{file_id}/chunk-stats", response_model=BaseResponse)
async def get_file_chunk_stats(
    file_id: str = Path(..., description="File ID", pattern=r".+"),
):
    """
    Get chunking statistics for a file.
    """
    try:
        # URL decode the file_id
        file_id = urllib.parse.unquote(file_id)

        stats = await chunking_service.get_chunk_stats(file_id)

        return {
            "code": 0,
            "message": "Success",
            "data": {
                "file_id": file_id,
                "stats": stats,
            },
        }
    except Exception as e:
        logger.error(f"Error getting chunk stats for file {file_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/chunk-settings", response_model=BaseResponse)
async def update_chunk_settings(
    settings: ChunkSettings = Body(...),
):
    """
    Update chunking settings.
    """
    try:
        # Update settings
        await chunking_service.update_settings(
            settings.strategy,
            settings.window_size,
            settings.overlap,
        )

        return {"code": 0, "message": "Success", "data": {"settings": settings}}
    except Exception as e:
        logger.error(f"Error updating chunk settings: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chunk-settings", response_model=BaseResponse)
async def get_chunk_settings():
    """
    Get chunking settings.
    """
    try:
        settings = await chunking_service.get_settings()

        return {"code": 0, "message": "Success", "data": {"settings": settings}}
    except Exception as e:
        logger.error(f"Error getting chunk settings: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    # For direct testing of this file
    import uvicorn
    from fastapi import FastAPI

    app = FastAPI()
    app.include_router(router)

    uvicorn.run(app, host="0.0.0.0", port=8000)
