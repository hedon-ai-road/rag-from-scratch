"""
Schema models for system operations.
"""
from datetime import datetime
from typing import Dict, List

from pydantic import BaseModel, Field


class LogEntry(BaseModel):
    """Log entry model."""

    timestamp: datetime = Field(..., description="Log timestamp")
    level: str = Field(..., description="Log level")
    message: str = Field(..., description="Log message")
    component: str = Field(..., description="Component that generated the log")


class SystemStats(BaseModel):
    """System statistics model."""

    file_count: int = Field(..., description="Number of files in the system")
    chunk_count: int = Field(..., description="Number of chunks in the system")
    vector_count: int = Field(..., description="Number of vectors in the system")
    search_count: int = Field(..., description="Number of searches performed")
    generation_count: int = Field(..., description="Number of generations performed")


class SystemConfig(BaseModel):
    """System configuration model."""

    chunk_strategy: str = Field(..., description="Default chunking strategy")
    vector_model: str = Field(..., description="Default embedding model")
    search_settings: Dict[str, float] = Field(..., description="Search settings")


class SystemPerformance(BaseModel):
    """System performance metrics."""

    retrieval_accuracy: float = Field(..., description="Retrieval accuracy")
    generation_time_avg: float = Field(..., description="Average generation time")
    chunk_quality: float = Field(..., description="Chunk quality score")
    embedding_throughput: int = Field(..., description="Embedding throughput")


class SystemStatusResponse(BaseModel):
    """System status response model."""

    system: SystemStats = Field(..., description="System statistics")
    config: SystemConfig = Field(..., description="System configuration")
    performance: SystemPerformance = Field(
        ..., description="System performance metrics"
    )


class SystemLogsResponse(BaseModel):
    """System logs response model."""

    logs: List[LogEntry] = Field(..., description="Log entries")
