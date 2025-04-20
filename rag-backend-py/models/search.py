"""
Schema models for search operations.
"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class SearchFilter(BaseModel):
    """Search filter model."""

    file_id: Optional[str] = Field(None, description="Filter by file ID")


class SearchScores(BaseModel):
    """Search scores model."""

    vector: float = Field(..., description="Vector search score")
    bm25: float = Field(..., description="BM25 search score")


class RetrievedChunk(BaseModel):
    """Retrieved chunk information."""

    chunk_id: str = Field(..., description="Chunk ID")
    file_id: str = Field(..., description="File ID")
    file_name: str = Field(..., description="File name")
    content: str = Field(..., description="Chunk content")
    start_offset: int = Field(..., description="Start offset in the original document")
    end_offset: int = Field(..., description="End offset in the original document")
    score: float = Field(..., description="Relevance score")


class SearchRequest(BaseModel):
    """Search request model."""

    query: str = Field(..., description="Search query")
    search_type: str = Field("hybrid", description="Search type (vector, bm25, hybrid)")
    vector_weight: float = Field(0.7, description="Weight for vector search")
    bm25_weight: float = Field(0.3, description="Weight for BM25 search")
    top_k: int = Field(5, description="Number of results to return")
    file_id: Optional[str] = Field(None, description="Filter by file ID")


class SearchResponse(BaseModel):
    """Search response model."""

    query: str = Field(..., description="Search query")
    timestamp: datetime = Field(..., description="Search timestamp")
    search_type: str = Field(..., description="Search type used")
    search_scores: SearchScores = Field(..., description="Search scores")
    retrievedChunks: List[RetrievedChunk] = Field(..., description="Retrieved chunks")


class SearchHistoryItem(BaseModel):
    """Search history item model."""

    timestamp: datetime = Field(..., description="Search timestamp")
    query: str = Field(..., description="Search query")
    top_chunks: List[str] = Field(..., description="IDs of top chunks")
    scores: SearchScores = Field(..., description="Search scores")


class SearchHistoryResponse(BaseModel):
    """Search history response model."""

    history: List[SearchHistoryItem] = Field(..., description="Search history items")


class SearchSettings(BaseModel):
    """Search settings model."""

    vectorWeight: float = Field(..., description="Weight for vector search")
    bm25Weight: float = Field(..., description="Weight for BM25 search")
    topK: int = Field(..., description="Default number of results to return")


class SearchSettingsResponse(BaseModel):
    """Search settings response model."""

    settings: SearchSettings = Field(..., description="Search settings")
