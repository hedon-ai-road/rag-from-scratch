"""
Chunking service for handling text splitting operations.
"""
import json
import logging
import uuid
from typing import Any, Dict, List, Optional, Tuple

import constants
from models.chunk import ChunkInfo, ChunkSettings
from database import DatabaseService
from .recursive_character_text_splitter import RecursiveCharacterTextSplitter
from .character_text_splitter import CharacterTextSplitter
from .llamaindex_semantics_splitter import LlamaindexSemanticsSplitter
from .recursive_character_code_splitter import RecursiveCharacterCodeSplitter

logger = logging.getLogger("rag-backend.chunking")


class ChunkingService:
    """
    Service for handling text chunking operations.
    """

    def __init__(self):
        self.db_service = DatabaseService()

    async def create_chunks(
        self,
        file_id: str,
        chunk_strategy: str,
        window_size: int,
        overlap: int,
        custom_options: Optional[Dict[str, Any]] = None,
    ) -> List[ChunkInfo]:
        """
        Create chunks for a file using loaded documents from database.

        Args:
            file_id: ID of the file to chunk
            chunk_strategy: Strategy to use for chunking
            window_size: Size of each chunk window
            overlap: Overlap size between chunks
            custom_options: Additional options for the chunking process

        Returns:
            List of created chunks
        """
        try:
            # Get documents from database
            documents = self.db_service.get_documents(file_id)
            if not documents:
                raise FileNotFoundError(f"No documents found for file {file_id}")

            logger.info(f"Found {len(documents)} documents for file {file_id}")

            # Convert to LangChain documents for processing
            langchain_docs = [doc.to_langchain_document() for doc in documents]

            # Apply chunking strategy
            chunks_data = []
            if chunk_strategy == "recursive_character":
                chunks_data = self._recursive_character_chunking(
                    file_id, langchain_docs, window_size, overlap
                )
            elif chunk_strategy == "character":
                chunks_data = self._character_chunking(
                    file_id, langchain_docs, window_size, overlap
                )
            elif chunk_strategy == "semantic":
                chunks_data = self._semantic_chunking(
                    file_id, langchain_docs, window_size, custom_options
                )
            elif chunk_strategy == "code":
                chunks_data = self._code_chunking(
                    file_id, langchain_docs, window_size, overlap
                )
            else:
                raise ValueError(f"Unsupported chunking strategy: {chunk_strategy}")

            # Save chunks to database
            chunk_ids = self.db_service.save_chunks(
                file_id, chunks_data, chunk_strategy, window_size, overlap
            )

            # Convert to ChunkInfo objects for response
            chunks = []
            for i, chunk_data in enumerate(chunks_data):
                chunk = ChunkInfo(
                    chunk_id=chunk_ids[i],
                    file_id=file_id,
                    content=chunk_data["content"],
                    start_offset=chunk_data.get("start_offset"),
                    end_offset=chunk_data.get("end_offset"),
                )
                chunks.append(chunk)

            logger.info(
                f"Created {len(chunks)} chunks for file {file_id} using strategy {chunk_strategy}"
            )
            return chunks

        except Exception as e:
            logger.error(f"Error chunking file {file_id}: {str(e)}")
            raise

    def _recursive_character_chunking(
        self, file_id: str, documents: List[Any], chunk_size: int, overlap: int
    ) -> List[Dict[str, Any]]:
        """
        Apply recursive character chunking using proper text splitter.
        """
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=overlap
        )

        chunks_data = []
        for doc_idx, document in enumerate(documents):
            # Split the document
            splits = splitter.split_documents([document])

            for split_idx, split in enumerate(splits):
                chunk_data = {
                    "content": split.page_content,
                    "metadata": split.metadata,
                    "document_id": document.metadata.get("doc_id")
                    if hasattr(document, "metadata")
                    else None,
                    "start_offset": None,  # These would need to be calculated if needed
                    "end_offset": None,
                }
                chunks_data.append(chunk_data)

        return chunks_data

    def _character_chunking(
        self, file_id: str, documents: List[Any], chunk_size: int, overlap: int
    ) -> List[Dict[str, Any]]:
        """
        Apply character chunking using proper text splitter.
        """
        splitter = CharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=overlap)

        chunks_data = []
        for doc_idx, document in enumerate(documents):
            # Split the document
            splits = splitter.split_documents([document])

            for split_idx, split in enumerate(splits):
                chunk_data = {
                    "content": split.page_content,
                    "metadata": split.metadata,
                    "document_id": document.metadata.get("doc_id")
                    if hasattr(document, "metadata")
                    else None,
                    "start_offset": None,
                    "end_offset": None,
                }
                chunks_data.append(chunk_data)

        return chunks_data

    def _semantic_chunking(
        self,
        file_id: str,
        documents: List[Any],
        chunk_size: int,
        custom_options: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Apply semantic chunking using LlamaIndex semantic splitter.
        """
        splitter = LlamaindexSemanticsSplitter(chunk_size=chunk_size)

        chunks_data = []
        for doc_idx, document in enumerate(documents):
            # Split the document
            splits = splitter.split_documents([document])

            for split_idx, split in enumerate(splits):
                chunk_data = {
                    "content": split.page_content,
                    "metadata": split.metadata,
                    "document_id": document.metadata.get("doc_id")
                    if hasattr(document, "metadata")
                    else None,
                    "start_offset": None,
                    "end_offset": None,
                }
                chunks_data.append(chunk_data)

        return chunks_data

    def _code_chunking(
        self, file_id: str, documents: List[Any], chunk_size: int, overlap: int
    ) -> List[Dict[str, Any]]:
        """
        Apply code-specific chunking using recursive character code splitter.
        """
        splitter = RecursiveCharacterCodeSplitter(
            chunk_size=chunk_size, chunk_overlap=overlap
        )

        chunks_data = []
        for doc_idx, document in enumerate(documents):
            # Split the document
            splits = splitter.split_documents([document])

            for split_idx, split in enumerate(splits):
                chunk_data = {
                    "content": split.page_content,
                    "metadata": split.metadata,
                    "document_id": document.metadata.get("doc_id")
                    if hasattr(document, "metadata")
                    else None,
                    "start_offset": None,
                    "end_offset": None,
                }
                chunks_data.append(chunk_data)

        return chunks_data

    async def get_chunks(
        self, file_id: str, page: int, limit: int, chunk_strategy: Optional[str] = None
    ) -> Tuple[List[ChunkInfo], int]:
        """
        Get chunks for a file from database.

        Args:
            file_id: ID of the file
            page: Page number (1-indexed)
            limit: Number of items per page
            chunk_strategy: Optional strategy filter

        Returns:
            Tuple of (list of chunks, total count)
        """
        try:
            # Get chunks from database
            db_chunks, total_count = self.db_service.get_chunks(
                file_id, chunk_strategy, page, limit
            )

            # Convert to ChunkInfo objects
            chunks = []
            for db_chunk in db_chunks:
                chunk = ChunkInfo(
                    chunk_id=db_chunk.id,
                    file_id=db_chunk.file_id,
                    content=db_chunk.content,
                    start_offset=db_chunk.start_offset,
                    end_offset=db_chunk.end_offset,
                )
                chunks.append(chunk)

            return chunks, total_count

        except Exception as e:
            logger.error(f"Error loading chunks for file {file_id}: {str(e)}")
            raise

    async def get_chunk_strategies(self, file_id: str) -> List[str]:
        """
        Get all chunking strategies used for a file.

        Args:
            file_id: File ID

        Returns:
            List of strategy names
        """
        return self.db_service.get_file_chunk_strategies(file_id)

    async def get_chunk_stats(self, file_id: str) -> Dict[str, Any]:
        """
        Get chunking statistics for a file.

        Args:
            file_id: File ID

        Returns:
            Dictionary with statistics
        """
        return self.db_service.get_chunk_stats(file_id)

    async def update_settings(
        self, strategy: str, window_size: int, overlap: int
    ) -> None:
        """
        Update chunking settings.

        Args:
            strategy: Chunking strategy
            window_size: Window size
            overlap: Overlap size
        """
        # In a real implementation, this would update a database
        # For now, we'll just log
        logger.info(
            f"Updated chunking settings: strategy={strategy}, "
            f"window_size={window_size}, overlap={overlap}"
        )

    async def get_settings(self) -> ChunkSettings:
        """
        Get chunking settings.

        Returns:
            Current chunking settings
        """
        # In a real implementation, this would query a database
        # For now, return default settings
        return ChunkSettings(
            window_size=constants.DEFAULT_WINDOW_SIZE,
            overlap=constants.DEFAULT_OVERLAP,
            strategy=constants.DEFAULT_CHUNK_STRATEGY,
        )
