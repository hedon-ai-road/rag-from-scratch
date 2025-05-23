"""
Database service for managing documents and chunks.
"""
import uuid
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
import logging

from models.document import Document, DocumentChunk
from .models import get_db_session

logger = logging.getLogger("rag-backend.database")


class DatabaseService:
    """Service for database operations."""

    def save_documents(
        self, file_id: str, documents: List[Any], original_filename: str = None
    ) -> List[str]:
        """
        Save loaded documents to database.

        Args:
            file_id: File ID
            documents: List of LangChain Document objects
            original_filename: Original filename when uploaded

        Returns:
            List of document IDs
        """
        document_ids = []

        with get_db_session() as session:
            # Clear existing documents for this file
            session.query(Document).filter(Document.file_id == file_id).delete()

            for i, doc in enumerate(documents):
                doc_id = str(uuid.uuid4())

                # Extract page number from metadata if available
                page_number = None
                doc_metadata = (
                    doc.metadata.copy()
                    if hasattr(doc, "metadata") and doc.metadata
                    else {}
                )

                # Save original filename in the first document's metadata
                if i == 0 and original_filename:
                    doc_metadata["original_filename"] = original_filename

                if hasattr(doc, "metadata") and doc.metadata:
                    page_number = doc.metadata.get("page")
                    # Convert 0-based to 1-based if necessary
                    if isinstance(page_number, int) and page_number >= 0:
                        page_number += 1

                db_document = Document(
                    id=doc_id,
                    file_id=file_id,
                    page_content=doc.page_content,
                    doc_metadata=doc_metadata,
                    page_number=page_number,
                )

                session.add(db_document)
                document_ids.append(doc_id)

            session.commit()
            logger.info(f"Saved {len(documents)} documents for file {file_id}")

        return document_ids

    def get_documents(self, file_id: str) -> List[Document]:
        """
        Get all documents for a file.

        Args:
            file_id: File ID

        Returns:
            List of Document objects
        """
        with get_db_session() as session:
            documents = (
                session.query(Document)
                .filter(Document.file_id == file_id)
                .order_by(Document.page_number, Document.id)
                .all()
            )

            # Return detached objects
            return [
                Document(
                    id=doc.id,
                    file_id=doc.file_id,
                    page_content=doc.page_content,
                    doc_metadata=doc.doc_metadata,
                    page_number=doc.page_number,
                    created_at=doc.created_at,
                )
                for doc in documents
            ]

    def get_all_documents(self) -> List[Document]:
        """
        Get all documents from the database.

        Returns:
            List of Document objects
        """
        with get_db_session() as session:
            documents = (
                session.query(Document)
                .order_by(Document.file_id, Document.page_number, Document.id)
                .all()
            )

            # Return detached objects
            return [
                Document(
                    id=doc.id,
                    file_id=doc.file_id,
                    page_content=doc.page_content,
                    doc_metadata=doc.doc_metadata,
                    page_number=doc.page_number,
                    created_at=doc.created_at,
                )
                for doc in documents
            ]

    def save_chunks(
        self,
        file_id: str,
        chunks: List[Dict[str, Any]],
        chunk_strategy: str,
        window_size: Optional[int] = None,
        overlap: Optional[int] = None,
    ) -> List[str]:
        """
        Save document chunks to database.

        Args:
            file_id: File ID
            chunks: List of chunk dictionaries
            chunk_strategy: Chunking strategy used
            window_size: Window size used
            overlap: Overlap used

        Returns:
            List of chunk IDs
        """
        chunk_ids = []

        with get_db_session() as session:
            # Clear existing chunks for this file and strategy
            session.query(DocumentChunk).filter(
                and_(
                    DocumentChunk.file_id == file_id,
                    DocumentChunk.chunk_strategy == chunk_strategy,
                )
            ).delete()

            for i, chunk_data in enumerate(chunks):
                chunk_id = str(uuid.uuid4())

                db_chunk = DocumentChunk(
                    id=chunk_id,
                    file_id=file_id,
                    document_id=chunk_data.get("document_id"),
                    content=chunk_data["content"],
                    chunk_metadata=chunk_data.get("metadata", {}),
                    start_offset=chunk_data.get("start_offset"),
                    end_offset=chunk_data.get("end_offset"),
                    chunk_index=i,
                    chunk_strategy=chunk_strategy,
                    window_size=window_size,
                    overlap=overlap,
                )

                session.add(db_chunk)
                chunk_ids.append(chunk_id)

            session.commit()
            logger.info(
                f"Saved {len(chunks)} chunks for file {file_id} using strategy {chunk_strategy}"
            )

        return chunk_ids

    def get_chunks(
        self,
        file_id: str,
        chunk_strategy: Optional[str] = None,
        page: int = 1,
        limit: int = 50,
    ) -> Tuple[List[DocumentChunk], int]:
        """
        Get chunks for a file.

        Args:
            file_id: File ID
            chunk_strategy: Chunking strategy filter
            page: Page number (1-indexed)
            limit: Number of chunks per page

        Returns:
            Tuple of (chunks, total_count)
        """
        with get_db_session() as session:
            query = session.query(DocumentChunk).filter(
                DocumentChunk.file_id == file_id
            )

            if chunk_strategy:
                query = query.filter(DocumentChunk.chunk_strategy == chunk_strategy)

            # Get total count
            total_count = query.count()

            # Apply pagination
            offset = (page - 1) * limit
            chunks = (
                query.order_by(DocumentChunk.chunk_index)
                .offset(offset)
                .limit(limit)
                .all()
            )

            # Return detached objects
            return (
                [
                    DocumentChunk(
                        id=chunk.id,
                        file_id=chunk.file_id,
                        document_id=chunk.document_id,
                        content=chunk.content,
                        chunk_metadata=chunk.chunk_metadata,
                        start_offset=chunk.start_offset,
                        end_offset=chunk.end_offset,
                        chunk_index=chunk.chunk_index,
                        chunk_strategy=chunk.chunk_strategy,
                        window_size=chunk.window_size,
                        overlap=chunk.overlap,
                        created_at=chunk.created_at,
                    )
                    for chunk in chunks
                ],
                total_count,
            )

    def get_file_chunk_strategies(self, file_id: str) -> List[str]:
        """
        Get all chunking strategies used for a file.

        Args:
            file_id: File ID

        Returns:
            List of strategy names
        """
        with get_db_session() as session:
            strategies = (
                session.query(DocumentChunk.chunk_strategy)
                .filter(DocumentChunk.file_id == file_id)
                .distinct()
                .all()
            )

            return [strategy[0] for strategy in strategies]

    def delete_file_data(self, file_id: str) -> None:
        """
        Delete all documents and chunks for a file.

        Args:
            file_id: File ID
        """
        with get_db_session() as session:
            # Delete chunks
            session.query(DocumentChunk).filter(
                DocumentChunk.file_id == file_id
            ).delete()

            # Delete documents
            session.query(Document).filter(Document.file_id == file_id).delete()

            session.commit()
            logger.info(f"Deleted all data for file {file_id}")

    def get_chunk_stats(self, file_id: str) -> Dict[str, Any]:
        """
        Get chunking statistics for a file.

        Args:
            file_id: File ID

        Returns:
            Dictionary with statistics
        """
        with get_db_session() as session:
            # Get chunk counts by strategy
            strategy_counts = (
                session.query(
                    DocumentChunk.chunk_strategy,
                    func.count(DocumentChunk.id).label("count"),
                )
                .filter(DocumentChunk.file_id == file_id)
                .group_by(DocumentChunk.chunk_strategy)
                .all()
            )

            # Get document count
            doc_count = (
                session.query(Document).filter(Document.file_id == file_id).count()
            )

            return {
                "document_count": doc_count,
                "chunk_strategies": {
                    strategy: count for strategy, count in strategy_counts
                },
                "total_chunks": sum(count for _, count in strategy_counts),
            }
