"""
Base schema models for the API.
"""
from typing import Any, Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field
from sqlalchemy.ext.declarative import declarative_base

T = TypeVar("T")  # Type variable for generic models

# SQLAlchemy Base class for database models
Base = declarative_base()


class BaseResponse(BaseModel):
    """Base response model for all API endpoints."""

    code: int = Field(0, description="Error code, 0 means success")
    message: str = Field("Success", description="Error message")
    data: Optional[Any] = Field(None, description="Response data")


class PaginationInfo(BaseModel):
    """Pagination information."""

    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Number of items per page")
    pages: int = Field(..., description="Total number of pages")


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response model."""

    items: List[T] = Field(..., description="List of items")
    pagination: PaginationInfo = Field(..., description="Pagination information")


class ErrorDetail(BaseModel):
    """Detailed error information."""

    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")


class Settings(BaseModel):
    """Base settings model."""

    pass


class VersionInfo(BaseModel):
    """Version information."""

    major: int = Field(..., description="Major version")
    minor: int = Field(..., description="Minor version")
    patch: int = Field(..., description="Patch version")
    commit_hash: Optional[str] = Field(None, description="Git commit hash")
