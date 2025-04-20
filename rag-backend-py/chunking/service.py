"""
Chunking service for handling text splitting operations.
"""
import json
import logging
import uuid
from typing import Any, Dict, List, Optional, Tuple

import constants
from models.chunk import ChunkInfo, ChunkSettings

logger = logging.getLogger("rag-backend.chunking")


class ChunkingService:
    """
    Service for handling text chunking operations.
    """

    async def create_chunks(
        self,
        file_id: str,
        chunk_strategy: str,
        window_size: int,
        overlap: int,
        custom_options: Optional[Dict[str, Any]] = None,
    ) -> List[ChunkInfo]:
        """
        Create chunks for a file.

        Args:
            file_id: ID of the file to chunk
            chunk_strategy: Strategy to use for chunking
            window_size: Size of each chunk window
            overlap: Overlap size between chunks
            custom_options: Additional options for the chunking process

        Returns:
            List of created chunks
        """
        # Find the file
        file_paths = list(constants.ORIGINAL_FILES_DIR.glob(f"{file_id}.*"))
        if not file_paths:
            raise FileNotFoundError(f"File with ID {file_id} not found")

        file_path = file_paths[0]

        # Here we would implement actual chunking based on the strategy
        # For now, we'll just create a simple sliding window chunking simulation
        chunks = []

        try:
            # Read file content
            with open(file_path, "rb") as f:
                content = f.read().decode("utf-8", errors="replace")

            # Apply chunking strategy
            if chunk_strategy == "sliding_window":
                chunks = self._sliding_window_chunking(
                    file_id, content, window_size, overlap
                )
            elif chunk_strategy == "semantic":
                chunks = self._semantic_chunking(file_id, content, window_size)
            else:
                raise ValueError(f"Unsupported chunking strategy: {chunk_strategy}")

            # Save chunks to disk
            self._save_chunks(file_id, chunks)

            return chunks
        except Exception as e:
            logger.error(f"Error chunking file {file_id}: {str(e)}")
            raise

    def _sliding_window_chunking(
        self, file_id: str, content: str, window_size: int, overlap: int
    ) -> List[ChunkInfo]:
        """
        Apply sliding window chunking.

        Args:
            file_id: ID of the file
            content: Text content
            window_size: Size of each chunk window
            overlap: Overlap size between chunks

        Returns:
            List of chunks
        """
        chunks = []

        # Simple sliding window implementation
        text_length = len(content)
        start = 0

        while start < text_length:
            end = min(start + window_size, text_length)

            # Create chunk
            chunk_id = str(uuid.uuid4())
            chunk = ChunkInfo(
                chunk_id=chunk_id,
                file_id=file_id,
                content=content[start:end],
                start_offset=start,
                end_offset=end,
            )
            chunks.append(chunk)

            # Move window
            start = start + window_size - overlap
            if start >= text_length:
                break

        return chunks

    def _semantic_chunking(
        self, file_id: str, content: str, chunk_size: int
    ) -> List[ChunkInfo]:
        """
        Apply semantic chunking.

        Args:
            file_id: ID of the file
            content: Text content
            chunk_size: Target size for chunks

        Returns:
            List of chunks
        """
        # In a real implementation, this would use a language model to split by meaning
        # For now, we'll just simulate by splitting on paragraphs

        chunks = []
        paragraphs = content.split("\n\n")

        start_offset = 0
        current_chunk = []
        current_length = 0

        for para in paragraphs:
            para_length = len(para)

            if current_length + para_length > chunk_size and current_chunk:
                # Create chunk
                chunk_content = "\n\n".join(current_chunk)
                chunk_id = str(uuid.uuid4())
                chunk = ChunkInfo(
                    chunk_id=chunk_id,
                    file_id=file_id,
                    content=chunk_content,
                    start_offset=start_offset,
                    end_offset=start_offset + len(chunk_content),
                )
                chunks.append(chunk)

                # Reset for next chunk
                start_offset += len(chunk_content)
                current_chunk = [para]
                current_length = para_length
            else:
                current_chunk.append(para)
                current_length += para_length

        # Add the last chunk if there's anything left
        if current_chunk:
            chunk_content = "\n\n".join(current_chunk)
            chunk_id = str(uuid.uuid4())
            chunk = ChunkInfo(
                chunk_id=chunk_id,
                file_id=file_id,
                content=chunk_content,
                start_offset=start_offset,
                end_offset=start_offset + len(chunk_content),
            )
            chunks.append(chunk)

        return chunks

    def _save_chunks(self, file_id: str, chunks: List[ChunkInfo]) -> None:
        """
        Save chunks to disk.

        Args:
            file_id: ID of the file
            chunks: List of chunks to save
        """
        # Create directory if it doesn't exist
        chunk_dir = constants.CHUNKS_DIR / file_id
        chunk_dir.mkdir(parents=True, exist_ok=True)

        # Save each chunk
        for chunk in chunks:
            chunk_path = chunk_dir / f"{chunk.chunk_id}.json"
            with open(chunk_path, "w") as f:
                json.dump(chunk.dict(), f, indent=2)

    async def get_chunks(
        self, file_id: str, page: int, limit: int
    ) -> Tuple[List[ChunkInfo], int]:
        """
        Get chunks for a file.

        Args:
            file_id: ID of the file
            page: Page number (1-indexed)
            limit: Number of items per page

        Returns:
            Tuple of (list of chunks, total count)
        """
        # Check if file exists
        file_paths = list(constants.ORIGINAL_FILES_DIR.glob(f"{file_id}.*"))
        if not file_paths:
            raise FileNotFoundError(f"File with ID {file_id} not found")

        # Find chunks for the file
        chunk_dir = constants.CHUNKS_DIR / file_id
        if not chunk_dir.exists():
            return [], 0

        chunks = []
        try:
            # Load chunks from disk
            for chunk_path in sorted(chunk_dir.glob("*.json")):
                with open(chunk_path, "r") as f:
                    chunk_data = json.load(f)
                    chunks.append(ChunkInfo(**chunk_data))
        except Exception as e:
            logger.error(f"Error loading chunks for file {file_id}: {str(e)}")
            raise

        # Apply pagination
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_chunks = chunks[start_idx:end_idx]

        return paginated_chunks, len(chunks)

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


if __name__ == "__main__":
    # For testing the service directly
    import asyncio

    async def test_chunking_service():
        # Create test directories
        constants.ORIGINAL_FILES_DIR.mkdir(parents=True, exist_ok=True)
        constants.CHUNKS_DIR.mkdir(parents=True, exist_ok=True)

        service = ChunkingService()

        # Test get settings
        settings = await service.get_settings()
        print(f"Chunk settings: {settings}")

    asyncio.run(test_chunking_service())
