"""
Schema models for vector index operations.
"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class IndexOptions(BaseModel):
    """Vector index options."""

    m: int = Field(..., description="HNSW M parameter")
    ef_construction: int = Field(..., description="HNSW ef_construction parameter")


class IndexCreate(BaseModel):
    """Request model for index creation."""

    index_type: str = Field(..., description="Index type (e.g., hnsw)")
    file_ids: List[str] = Field(
        ..., description="List of file IDs to include in the index"
    )
    index_options: Optional[IndexOptions] = Field(
        None, description="Index-specific options"
    )


class IndexInfo(BaseModel):
    """Index information model."""

    index_id: str = Field(..., description="Unique index ID")
    index_type: str = Field(..., description="Index type")
    file_count: int = Field(..., description="Number of files in the index")
    vector_count: int = Field(..., description="Number of vectors in the index")
    dimensions: int = Field(..., description="Vector dimensions")
    created_at: datetime = Field(..., description="Index creation timestamp")


class DetailedIndexInfo(IndexInfo):
    """Detailed index information model."""

    last_updated: datetime = Field(..., description="Last update timestamp")
    size_bytes: int = Field(..., description="Index size in bytes")


class IndexCreateResponse(BaseModel):
    """Response model for index creation."""

    index_id: str = Field(..., description="Unique index ID")
    index_type: str = Field(..., description="Index type")
    file_count: int = Field(..., description="Number of files in the index")
    vector_count: int = Field(..., description="Number of vectors in the index")
    dimensions: int = Field(..., description="Vector dimensions")
    created_at: datetime = Field(..., description="Index creation timestamp")


class IndexInfoResponse(BaseModel):
    """Response model for index information."""

    index: DetailedIndexInfo = Field(..., description="Index information")
