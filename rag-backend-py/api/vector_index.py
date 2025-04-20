"""
API router for vector index operations.
"""
import logging
from typing import Optional

from fastapi import APIRouter, Body, HTTPException
from fastapi.responses import JSONResponse

from models.base import BaseResponse
from models.vector_index import IndexCreate
from vector_index import VectorIndexService

router = APIRouter(tags=["Vector Index"])
logger = logging.getLogger("rag-backend.api.vector_index")

index_service = VectorIndexService()


@router.post("/vector-index", response_model=BaseResponse)
async def create_index(
    index_request: IndexCreate = Body(...),
):
    """
    Create or update a vector index.
    """
    try:
        try:
            index_info = await index_service.create_index(
                index_request.index_type,
                index_request.file_ids,
                index_request.index_options,
            )

            return {
                "code": 0,
                "message": "Success",
                "data": {
                    "index_id": index_info.index_id,
                    "index_type": index_info.index_type,
                    "file_count": index_info.file_count,
                    "vector_count": index_info.vector_count,
                    "dimensions": index_info.dimensions,
                    "created_at": index_info.created_at,
                },
            }
        except FileNotFoundError as e:
            return JSONResponse(
                status_code=404,
                content={
                    "code": 1,
                    "message": str(e),
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
        logger.error(f"Error creating index: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/vector-index", response_model=BaseResponse)
async def get_index_info():
    """
    Get information about the current vector index.
    """
    try:
        index_info = await index_service.get_index_info()

        if not index_info:
            return JSONResponse(
                status_code=404,
                content={
                    "code": 1,
                    "message": "No index found",
                    "data": None,
                },
            )

        return {"code": 0, "message": "Success", "data": {"index": index_info}}
    except Exception as e:
        logger.error(f"Error getting index info: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    # For direct testing of this file
    import uvicorn
    from fastapi import FastAPI

    app = FastAPI()
    app.include_router(router)

    uvicorn.run(app, host="0.0.0.0", port=8000)
