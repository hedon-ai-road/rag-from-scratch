"""
Schema models for pipeline operations.
"""
from datetime import datetime
from typing import List, Optional, Union

from pydantic import BaseModel, Field


class PipelineStep(BaseModel):
    """Pipeline step information."""

    step: str = Field(..., description="Step name")
    status: str = Field(..., description="Step status")


class FileLoadingStep(PipelineStep):
    """File loading step information."""

    file_id: str = Field(..., description="File ID")
    file_name: str = Field(..., description="File name")


class ChunkingStep(PipelineStep):
    """Chunking step information."""

    chunk_count: Optional[int] = Field(None, description="Number of chunks created")


class EmbeddingStep(PipelineStep):
    """Embedding step information."""

    vector_count: Optional[int] = Field(None, description="Number of vectors created")
    progress: Optional[int] = Field(None, description="Progress percentage")


class IndexingStep(PipelineStep):
    """Indexing step information."""

    index_id: Optional[str] = Field(None, description="Index ID")


class PipelineExecuteRequest(BaseModel):
    """Pipeline execution request model."""

    filename: str = Field(..., description="Name of the uploaded file")
    chunk_strategy: str = Field(..., description="Chunking strategy")
    window_size: int = Field(..., description="Size of each chunk window")
    overlap: int = Field(..., description="Overlap size between chunks")
    embedding_model: str = Field(..., description="Embedding model to use")
    index_type: str = Field(..., description="Index type")


class PipelineStatus(BaseModel):
    """Pipeline status information."""

    pipeline_id: str = Field(..., description="Unique pipeline ID")
    status: str = Field(..., description="Pipeline status")
    steps: List[
        Union[FileLoadingStep, ChunkingStep, EmbeddingStep, IndexingStep]
    ] = Field(..., description="Pipeline steps")
    started_at: Optional[datetime] = Field(None, description="Pipeline start timestamp")
    elapsed_time: Optional[float] = Field(None, description="Elapsed time in seconds")
    execution_time: Optional[float] = Field(
        None, description="Total execution time in seconds"
    )


class PipelineExecuteResponse(PipelineStatus):
    """Pipeline execution response model."""

    pass


class PipelineStatusResponse(PipelineStatus):
    """Pipeline status response model."""

    pass
