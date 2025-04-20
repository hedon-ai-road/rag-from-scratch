"""
Schema models for chunk operations.
"""
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class ChunkStrategy(BaseModel):
    """Chunk strategy model."""

    chunk_strategy: str = Field(
        ..., description="Chunking strategy (e.g., sliding_window)"
    )
    window_size: int = Field(..., description="Size of each chunk window")
    overlap: int = Field(..., description="Overlap size between chunks")
    custom_options: Optional[Dict[str, object]] = Field(
        None, description="Custom chunking options"
    )


class ChunkSettings(BaseModel):
    """Chunk settings model."""

    window_size: int = Field(..., description="Size of each chunk window")
    overlap: int = Field(..., description="Overlap size between chunks")
    strategy: str = Field(..., description="Chunking strategy (e.g., sliding_window)")


class ChunkInfo(BaseModel):
    """Chunk information model."""

    chunk_id: str = Field(..., description="Unique chunk ID")
    file_id: str = Field(..., description="ID of the file this chunk belongs to")
    content: str = Field(..., description="Text content of the chunk")
    start_offset: int = Field(..., description="Start offset in the original document")
    end_offset: int = Field(..., description="End offset in the original document")


class ChunkCreateRequest(BaseModel):
    """Request model for chunk creation."""

    chunk_strategy: str = Field(..., description="Chunking strategy")
    window_size: int = Field(..., description="Size of each chunk window")
    overlap: int = Field(..., description="Overlap size between chunks")
    custom_options: Optional[Dict[str, object]] = Field(
        None, description="Custom chunking options"
    )


class ChunkCreateResponse(BaseModel):
    """Response model for chunk creation."""

    file_id: str = Field(..., description="File ID")
    chunk_count: int = Field(..., description="Number of chunks created")
    chunks: List[ChunkInfo] = Field(..., description="List of created chunks")


class ChunkListResponse(BaseModel):
    """Response model for chunk listing."""

    file_id: str = Field(..., description="File ID")
    chunk_count: int = Field(..., description="Total number of chunks")
    chunks: List[ChunkInfo] = Field(..., description="List of chunks")
