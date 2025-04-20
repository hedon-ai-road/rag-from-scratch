"""
Schema models for text generation operations.
"""
from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class TokenUsage(BaseModel):
    """Token usage information."""

    prompt: int = Field(..., description="Number of prompt tokens")
    completion: int = Field(..., description="Number of completion tokens")
    total: int = Field(..., description="Total number of tokens")


class GenerationModel(BaseModel):
    """Generation model information."""

    id: str = Field(..., description="Model ID")
    name: str = Field(..., description="Model name")
    provider: str = Field(..., description="Model provider")
    max_tokens: int = Field(..., description="Maximum tokens supported")
    description: str = Field(..., description="Model description")


class GenerationRequest(BaseModel):
    """Generation request model."""

    query: str = Field(..., description="User query")
    chunk_ids: List[str] = Field(..., description="IDs of chunks to use for context")
    model: str = Field(..., description="Generation model to use")
    max_tokens: int = Field(500, description="Maximum tokens to generate")
    temperature: float = Field(0.7, description="Temperature for generation")


class GenerationResponse(BaseModel):
    """Generation response model."""

    gen_id: str = Field(..., description="Unique generation ID")
    query: str = Field(..., description="User query")
    used_chunks: List[str] = Field(..., description="IDs of chunks used for context")
    response: str = Field(..., description="Generated response")
    created_at: datetime = Field(..., description="Generation timestamp")
    model_used: str = Field(..., description="Model used for generation")
    token_usage: TokenUsage = Field(..., description="Token usage information")


class GenerationHistoryItem(BaseModel):
    """Generation history item model."""

    gen_id: str = Field(..., description="Unique generation ID")
    query: str = Field(..., description="User query")
    used_chunks: List[str] = Field(..., description="IDs of chunks used for context")
    response: str = Field(..., description="Generated response")
    created_at: datetime = Field(..., description="Generation timestamp")
    model_used: str = Field(..., description="Model used for generation")


class GenerationHistoryResponse(BaseModel):
    """Generation history response model."""

    generations: List[GenerationHistoryItem] = Field(
        ..., description="Generation history items"
    )


class GenerationModelListResponse(BaseModel):
    """Response model for listing generation models."""

    models: List[GenerationModel] = Field(
        ..., description="List of available generation models"
    )
