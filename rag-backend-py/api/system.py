"""
API router for system operations.
"""
import logging

from fastapi import APIRouter, HTTPException

from models.base import BaseResponse
from system import SystemService

router = APIRouter(tags=["System"])
logger = logging.getLogger("rag-backend.api.system")

system_service = SystemService()


@router.get("/system/info", response_model=BaseResponse)
async def get_system_info():
    """
    Get system information including CPU, memory, disk, and process details.
    """
    try:
        system_info = await system_service.get_system_info()

        return {"code": 0, "message": "Success", "data": {"system_info": system_info}}
    except Exception as e:
        logger.error(f"Error getting system information: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    # For direct testing of this file
    import uvicorn
    from fastapi import FastAPI

    app = FastAPI()
    app.include_router(router)

    uvicorn.run(app, host="0.0.0.0", port=8000)
