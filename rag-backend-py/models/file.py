"""
Schema models for file operations.
"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, validator


class FileBase(BaseModel):
    """Base file information."""

    file_name: str = Field(..., description="File name with extension")
    file_size: int = Field(..., description="File size in bytes")

    @validator("file_size")
    def validate_file_size(cls, v):
        """Validate file size."""
        if v < 0:
            raise ValueError("File size cannot be negative")
        return v


class FileCreate(FileBase):
    """File creation model."""

    loadingMethod: Optional[str] = Field(None, description="File loading method")


class FileInfo(FileBase):
    """File information model."""

    file_id: str = Field(..., description="Unique file ID")
    storage_path: str = Field(..., description="Storage path for the file")
    created_at: datetime = Field(..., description="File creation timestamp")
    loadingMethod: Optional[str] = Field(None, description="File loading method")


class FileDetailInfo(FileInfo):
    """Detailed file information model."""

    chunk_count: Optional[int] = Field(
        None, description="Number of chunks created from this file"
    )
    vector_count: Optional[int] = Field(
        None, description="Number of vectors created from this file"
    )


class FileResponse(BaseModel):
    """File response model."""

    file: FileInfo = Field(..., description="File information")


class FileListResponse(BaseModel):
    """File list response model."""

    files: List[FileInfo] = Field(..., description="List of files")


class FileDeleteResponse(BaseModel):
    """File deletion response model."""

    pass
