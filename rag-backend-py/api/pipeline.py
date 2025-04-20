"""
API router for pipeline operations.
"""
import logging
from typing import Optional

from fastapi import APIRouter, Body, File, Form, HTTPException, Path, UploadFile
from fastapi.responses import JSONResponse

from models.base import BaseResponse
from models.pipeline import PipelineExecuteRequest
from pipeline import PipelineService

router = APIRouter(tags=["Pipeline"])
logger = logging.getLogger("rag-backend.api.pipeline")

pipeline_service = PipelineService()


@router.post("/pipeline/execute", response_model=BaseResponse)
async def execute_pipeline(
    file: UploadFile = File(...),
    filename: str = Form(...),
    chunk_strategy: str = Form(...),
    window_size: int = Form(...),
    overlap: int = Form(...),
    embedding_model: str = Form(...),
    index_type: str = Form(...),
):
    """
    Execute a complete RAG pipeline.
    """
    try:
        # Create pipeline request
        request = PipelineExecuteRequest(
            filename=filename,
            chunk_strategy=chunk_strategy,
            window_size=window_size,
            overlap=overlap,
            embedding_model=embedding_model,
            index_type=index_type,
        )

        # Read file data
        file_data = await file.read()

        # Execute pipeline
        pipeline_id = await pipeline_service.execute_pipeline(request, file_data)

        # Get initial status
        status = await pipeline_service.get_pipeline_status(pipeline_id)

        return {
            "code": 0,
            "message": "Success",
            "data": {
                "pipeline_id": pipeline_id,
                "status": status.status,
                "steps": status.steps,
                "started_at": status.started_at,
                "elapsed_time": status.elapsed_time,
            },
        }
    except Exception as e:
        logger.error(f"Error executing pipeline: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pipeline/{pipeline_id}", response_model=BaseResponse)
async def get_pipeline_status(
    pipeline_id: str = Path(..., description="Pipeline ID"),
):
    """
    Get pipeline status.
    """
    try:
        # Get pipeline status
        status = await pipeline_service.get_pipeline_status(pipeline_id)

        if not status:
            return JSONResponse(
                status_code=404,
                content={
                    "code": 1,
                    "message": f"Pipeline with ID {pipeline_id} not found",
                    "data": None,
                },
            )

        return {
            "code": 0,
            "message": "Success",
            "data": {
                "pipeline_id": pipeline_id,
                "status": status.status,
                "steps": status.steps,
                "started_at": status.started_at,
                "elapsed_time": status.elapsed_time,
                "execution_time": status.execution_time,
            },
        }
    except Exception as e:
        logger.error(f"Error getting pipeline status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    # For direct testing of this file
    import uvicorn
    from fastapi import FastAPI

    app = FastAPI()
    app.include_router(router)

    uvicorn.run(app, host="0.0.0.0", port=8000)
