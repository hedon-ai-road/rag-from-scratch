"""
Schema models for embedding operations.
"""
from typing import List, Optional

from pydantic import BaseModel, Field


class EmbeddingModel(BaseModel):
    """Embedding model information."""

    id: str = Field(..., description="Model ID")
    name: str = Field(..., description="Model name")
    dimensions: int = Field(..., description="Vector dimensions")
    provider: str = Field(..., description="Model provider")
    description: str = Field(..., description="Model description")


class EmbeddingModelListResponse(BaseModel):
    """Response model for listing embedding models."""

    models: List[EmbeddingModel] = Field(
        ..., description="List of available embedding models"
    )


class VectorCreate(BaseModel):
    """Request model for vector creation."""

    model_id: str = Field(..., description="ID of the embedding model to use")
    batch_size: Optional[int] = Field(
        None, description="Batch size for embedding generation"
    )


class VectorCreateResponse(BaseModel):
    """Response model for vector creation."""

    file_id: str = Field(..., description="File ID")
    model_used: str = Field(..., description="Embedding model used")
    dimensions: int = Field(..., description="Vector dimensions")
    vectors_created: int = Field(..., description="Number of vectors created")
    status: str = Field(..., description="Status of the operation")


class VectorSettings(BaseModel):
    """Vector settings model."""

    model: str = Field(..., description="Default embedding model")
    dimensions: int = Field(..., description="Vector dimensions")
    default_batch_size: int = Field(..., description="Default batch size")


class VectorSettingsResponse(BaseModel):
    """Response model for vector settings."""

    settings: VectorSettings = Field(..., description="Vector settings")
