"""
API router for embedding operations.
"""
import logging
from typing import Optional

from fastapi import APIRouter, Body, HTTPException, Path, Query
from fastapi.responses import JSONResponse

from embedding import EmbeddingService
from models.base import BaseResponse
from models.embedding import VectorSettings

router = APIRouter(tags=["Embeddings"])
logger = logging.getLogger("rag-backend.api.embeddings")

embedding_service = EmbeddingService()


@router.get("/embedding-models", response_model=BaseResponse)
async def get_embedding_models():
    """
    Get a list of supported embedding models.
    """
    try:
        models = await embedding_service.get_supported_models()

        return {"code": 0, "message": "Success", "data": {"models": models}}
    except Exception as e:
        logger.error(f"Error getting embedding models: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/files/{file_id}/vectors", response_model=BaseResponse)
async def create_vectors(
    file_id: str = Path(..., description="File ID"),
    vector_request: dict = Body(...),
):
    """
    Create vector embeddings for a file's chunks.
    """
    try:
        model_id = vector_request.get("model_id")
        if not model_id:
            return JSONResponse(
                status_code=400,
                content={
                    "code": 1,
                    "message": "model_id is required",
                    "data": None,
                },
            )

        batch_size = vector_request.get("batch_size")

        try:
            count, dimensions, status = await embedding_service.create_embeddings(
                file_id, model_id, batch_size
            )

            return {
                "code": 0,
                "message": "Success",
                "data": {
                    "file_id": file_id,
                    "model_used": model_id,
                    "dimensions": dimensions,
                    "vectors_created": count,
                    "status": status,
                },
            }
        except FileNotFoundError:
            return JSONResponse(
                status_code=404,
                content={
                    "code": 1,
                    "message": f"File with ID {file_id} not found",
                    "data": None,
                },
            )
        except ValueError as e:
            return JSONResponse(
                status_code=400,
                content={
                    "code": 1,
                    "message": str(e),
                    "data": None,
                },
            )
    except Exception as e:
        logger.error(f"Error creating vectors for file {file_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/vector-settings", response_model=BaseResponse)
async def get_vector_settings():
    """
    Get vector embedding settings.
    """
    try:
        settings = await embedding_service.get_settings()

        return {"code": 0, "message": "Success", "data": {"settings": settings}}
    except Exception as e:
        logger.error(f"Error getting vector settings: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/vector-settings", response_model=BaseResponse)
async def update_vector_settings(
    settings: VectorSettings = Body(...),
):
    """
    Update vector embedding settings.
    """
    try:
        await embedding_service.update_settings(
            settings.model,
            settings.dimensions,
            settings.default_batch_size,
        )

        return {"code": 0, "message": "Success", "data": {"settings": settings}}
    except Exception as e:
        logger.error(f"Error updating vector settings: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    # For direct testing of this file
    import uvicorn
    from fastapi import FastAPI

    app = FastAPI()
    app.include_router(router)

    uvicorn.run(app, host="0.0.0.0", port=8000)
