"""
API router for file operations.
"""
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import JSONResponse

import constants
from file_loader import FileLoaderService
from models.base import BaseResponse
from models.file import (
    FileDeleteResponse,
    FileDetailInfo,
    FileInfo,
    FileListResponse,
    FileResponse,
)

router = APIRouter(prefix="/files", tags=["Files"])
logger = logging.getLogger("rag-backend.files")

file_service = FileLoaderService()


@router.post("", response_model=BaseResponse)
async def upload_file(
    file: UploadFile = File(...),
    loading_method: str = Form(...),
):
    """
    Upload a document file to the RAG system.
    """
    try:
        file_info = await file_service.upload_file(file, loading_method)
        return {"code": 0, "message": "Success", "data": {"file": file_info}}
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=BaseResponse)
async def get_all_files(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
):
    """
    Get all files in the system.
    """
    try:
        files, total = await file_service.get_all_files(page, limit)

        return {
            "code": 0,
            "message": "Success",
            "data": {
                "files": files,
                "pagination": {
                    "total": total,
                    "page": page,
                    "limit": limit,
                    "pages": (total + limit - 1) // limit,
                },
            },
        }
    except Exception as e:
        logger.error(f"Error getting files: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/supported-types", response_model=BaseResponse)
async def get_supported_file_types():
    """
    Get all supported file types and their available loading methods.
    """
    try:
        # Return supported file types and their loading methods
        supported_types = {}
        for file_type in constants.ALLOWED_FILE_TYPES:
            if file_type in constants.LOADING_METHODS:
                supported_types[file_type] = constants.LOADING_METHODS[file_type]
            else:
                # Fallback to Unstructured if not explicitly defined
                supported_types[file_type] = ["Unstructured"]

        return {
            "code": 0,
            "message": "Success",
            "data": {
                "supported_types": supported_types,
                "allowed_file_types": constants.ALLOWED_FILE_TYPES,
            },
        }
    except Exception as e:
        logger.error(f"Error getting supported file types: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/loading-methods/{file_type}", response_model=BaseResponse)
async def get_loading_methods_for_file_type(file_type: str):
    """
    Get available loading methods for a specific file type.
    """
    try:
        # Check if file type is supported
        if file_type.lower() not in constants.ALLOWED_FILE_TYPES:
            return JSONResponse(
                status_code=400,
                content={
                    "code": 1,
                    "message": f"File type '{file_type}' is not supported",
                    "data": {"supported_types": constants.ALLOWED_FILE_TYPES},
                },
            )

        # Get loading methods for the file type
        loading_methods = constants.LOADING_METHODS.get(
            file_type.lower(), ["Unstructured"]
        )

        return {
            "code": 0,
            "message": "Success",
            "data": {
                "file_type": file_type.lower(),
                "loading_methods": loading_methods,
            },
        }
    except Exception as e:
        logger.error(
            f"Error getting loading methods for file type {file_type}: {str(e)}"
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{file_id}", response_model=BaseResponse)
async def get_file(file_id: str):
    """
    Get detailed information about a specific file.
    """
    try:
        file_info = await file_service.get_file(file_id)
        if not file_info:
            return JSONResponse(
                status_code=404,
                content={
                    "code": 1,
                    "message": f"File with ID {file_id} not found",
                    "data": None,
                },
            )

        return {"code": 0, "message": "Success", "data": {"file": file_info}}
    except Exception as e:
        logger.error(f"Error getting file {file_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{file_id}", response_model=BaseResponse)
async def delete_file(file_id: str):
    """
    Delete a file and its related data.
    """
    try:
        success = await file_service.delete_file(file_id)
        if not success:
            return JSONResponse(
                status_code=404,
                content={
                    "code": 1,
                    "message": f"File with ID {file_id} not found",
                    "data": None,
                },
            )

        return {"code": 0, "message": "Success", "data": {}}
    except Exception as e:
        logger.error(f"Error deleting file {file_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    # For direct testing of this file
    import asyncio
    import uvicorn
    from fastapi import FastAPI

    app = FastAPI()
    app.include_router(router)

    # Make sure the data directories exist
    constants.ORIGINAL_FILES_DIR.mkdir(parents=True, exist_ok=True)

    uvicorn.run(app, host="0.0.0.0", port=8000)
