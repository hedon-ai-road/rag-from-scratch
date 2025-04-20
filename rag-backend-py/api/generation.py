"""
API router for generation operations.
"""
import logging
from typing import Optional

from fastapi import APIRouter, Body, HTTPException, Query
from fastapi.responses import JSONResponse

from generation import GenerationService
from models.base import BaseResponse
from models.generation import GenerationRequest

router = APIRouter(tags=["Generation"])
logger = logging.getLogger("rag-backend.api.generation")

generation_service = GenerationService()


@router.post("/generate", response_model=BaseResponse)
async def generate(
    generation_request: GenerationRequest = Body(...),
):
    """
    Generate a response based on retrieved chunks.
    """
    try:
        try:
            (
                response,
                gen_id,
                token_usage,
                timestamp,
            ) = await generation_service.generate(generation_request)

            return {
                "code": 0,
                "message": "Success",
                "data": {
                    "gen_id": gen_id,
                    "query": generation_request.query,
                    "used_chunks": generation_request.chunk_ids,
                    "response": response,
                    "created_at": timestamp,
                    "model_used": generation_request.model,
                    "token_usage": token_usage,
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
        logger.error(f"Error generating response: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/generations", response_model=BaseResponse)
async def get_generations(
    limit: int = Query(
        10, ge=1, le=100, description="Number of history items to return"
    ),
):
    """
    Get recent generation history.
    """
    try:
        history = await generation_service.get_generation_history(limit)

        return {"code": 0, "message": "Success", "data": {"generations": history}}
    except Exception as e:
        logger.error(f"Error getting generations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/generation-models", response_model=BaseResponse)
async def get_generation_models():
    """
    Get a list of supported generation models.
    """
    try:
        models = await generation_service.get_supported_models()

        return {"code": 0, "message": "Success", "data": {"models": models}}
    except Exception as e:
        logger.error(f"Error getting generation models: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    # For direct testing of this file
    import uvicorn
    from fastapi import FastAPI

    app = FastAPI()
    app.include_router(router)

    uvicorn.run(app, host="0.0.0.0", port=8000)
