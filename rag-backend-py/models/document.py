"""
Document model for storing loaded documents.
"""
from datetime import datetime
from typing import Dict, Any, Optional
import json
from sqlalchemy import Column, String, Text, DateTime, JSON, Integer
from sqlalchemy.orm import relationship
from .base import Base


class Document(Base):
    """Model for storing loaded documents."""

    __tablename__ = "documents"

    id = Column(String, primary_key=True)  # document UUID
    file_id = Column(String, nullable=False, index=True)  # file UUID
    page_content = Column(Text, nullable=False)  # document content
    doc_metadata = Column(JSON, nullable=True)  # document metadata
    page_number = Column(Integer, nullable=True)  # page number if applicable
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Document(id='{self.id}', file_id='{self.file_id}', page={self.page_number})>"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "file_id": self.file_id,
            "page_content": self.page_content,
            "metadata": self.doc_metadata,
            "page_number": self.page_number,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def to_langchain_document(self):
        """Convert to LangChain Document format."""
        from langchain.schema import Document as LCDocument

        return LCDocument(
            page_content=self.page_content, metadata=self.doc_metadata or {}
        )


class DocumentChunk(Base):
    """Model for storing document chunks."""

    __tablename__ = "document_chunks"

    id = Column(String, primary_key=True)  # chunk UUID
    file_id = Column(String, nullable=False, index=True)  # file UUID
    document_id = Column(String, nullable=True, index=True)  # original document ID
    content = Column(Text, nullable=False)  # chunk content
    chunk_metadata = Column(JSON, nullable=True)  # chunk metadata
    start_offset = Column(Integer, nullable=True)  # start position in original document
    end_offset = Column(Integer, nullable=True)  # end position in original document
    chunk_index = Column(Integer, nullable=False)  # index of this chunk in the sequence
    chunk_strategy = Column(String, nullable=False)  # chunking strategy used
    window_size = Column(Integer, nullable=True)  # window size used
    overlap = Column(Integer, nullable=True)  # overlap used
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<DocumentChunk(id='{self.id}', file_id='{self.file_id}', index={self.chunk_index})>"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "file_id": self.file_id,
            "document_id": self.document_id,
            "content": self.content,
            "metadata": self.chunk_metadata,
            "start_offset": self.start_offset,
            "end_offset": self.end_offset,
            "chunk_index": self.chunk_index,
            "chunk_strategy": self.chunk_strategy,
            "window_size": self.window_size,
            "overlap": self.overlap,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def to_langchain_document(self):
        """Convert to LangChain Document format."""
        from langchain.schema import Document as LCDocument

        metadata = self.chunk_metadata.copy() if self.chunk_metadata else {}
        metadata.update(
            {
                "chunk_id": self.id,
                "file_id": self.file_id,
                "chunk_index": self.chunk_index,
                "start_offset": self.start_offset,
                "end_offset": self.end_offset,
            }
        )
        return LCDocument(page_content=self.content, metadata=metadata)
