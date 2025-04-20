"""
API router for search operations.
"""
import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Body, HTTPException, Query
from fastapi.responses import JSONResponse

from models.base import BaseResponse
from models.search import SearchRequest, SearchSettings
from search import SearchService

router = APIRouter(tags=["Search"])
logger = logging.getLogger("rag-backend.api.search")

search_service = SearchService()


@router.post("/search", response_model=BaseResponse)
async def search(
    search_request: SearchRequest = Body(...),
):
    """
    Search for relevant chunks based on a query.
    """
    try:
        try:
            retrieved_chunks, scores, timestamp = await search_service.search(
                search_request
            )

            return {
                "code": 0,
                "message": "Success",
                "data": {
                    "query": search_request.query,
                    "timestamp": timestamp,
                    "search_type": search_request.search_type,
                    "search_scores": scores,
                    "retrievedChunks": retrieved_chunks,
                },
            }
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
        logger.error(f"Error searching: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search-history", response_model=BaseResponse)
async def get_search_history(
    limit: int = Query(
        10, ge=1, le=100, description="Number of history items to return"
    ),
):
    """
    Get recent search history.
    """
    try:
        history = await search_service.get_search_history(limit)

        return {"code": 0, "message": "Success", "data": {"history": history}}
    except Exception as e:
        logger.error(f"Error getting search history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search-settings", response_model=BaseResponse)
async def get_search_settings():
    """
    Get search settings.
    """
    try:
        settings = await search_service.get_settings()

        return {"code": 0, "message": "Success", "data": {"settings": settings}}
    except Exception as e:
        logger.error(f"Error getting search settings: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/search-settings", response_model=BaseResponse)
async def update_search_settings(
    settings: SearchSettings = Body(...),
):
    """
    Update search settings.
    """
    try:
        await search_service.update_settings(
            settings.vectorWeight,
            settings.bm25Weight,
            settings.topK,
        )

        return {"code": 0, "message": "Success", "data": {"settings": settings}}
    except Exception as e:
        logger.error(f"Error updating search settings: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    # For direct testing of this file
    import uvicorn
    from fastapi import FastAPI

    app = FastAPI()
    app.include_router(router)

    uvicorn.run(app, host="0.0.0.0", port=8000)
