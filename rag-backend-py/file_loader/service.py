"""
File loader service for handling file operations.
"""
import logging
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

from fastapi import UploadFile

import constants
from models.file import FileDetailInfo, FileInfo

logger = logging.getLogger("rag-backend.file_loader")


class FileLoaderService:
    """
    Service for handling file operations like upload, listing, and deletion.
    """

    async def upload_file(
        self, file: UploadFile, loading_method: Optional[str] = None
    ) -> FileInfo:
        """
        Upload a file to the RAG system.

        Args:
            file: The uploaded file
            loading_method: Method to use for loading the file content

        Returns:
            FileInfo: Information about the uploaded file
        """
        # Generate a unique ID for the file
        file_id = str(uuid.uuid4())

        # Get file extension from filename
        filename = file.filename or "unnamed_file"
        file_ext = Path(filename).suffix.lstrip(".").lower()

        # Validate file type
        if file_ext not in constants.ALLOWED_FILE_TYPES:
            valid_types = ", ".join(constants.ALLOWED_FILE_TYPES)
            raise ValueError(f"Unsupported file type. Supported types: {valid_types}")

        # Create storage path
        storage_path = constants.ORIGINAL_FILES_DIR / f"{file_id}.{file_ext}"

        # Save file to disk
        with open(storage_path, "wb") as f:
            # Read file in chunks to avoid loading large files into memory
            chunk_size = 1024 * 1024  # 1MB chunks
            content = await file.read(chunk_size)
            file_size = 0

            while content:
                f.write(content)
                file_size += len(content)
                content = await file.read(chunk_size)

                # Check file size limit
                if file_size > constants.MAX_FILE_SIZE:
                    # Clean up the partial file
                    f.close()
                    os.remove(storage_path)
                    max_size_mb = constants.MAX_FILE_SIZE / (1024 * 1024)
                    raise ValueError(f"File too large. Maximum size: {max_size_mb} MB")

        # Create and return file info
        return FileInfo(
            file_id=file_id,
            file_name=filename,
            file_size=file_size,
            storage_path=str(storage_path),
            created_at=datetime.utcnow(),
            loadingMethod=loading_method or constants.LOADING_METHODS[0],
        )

    async def get_all_files(self, page: int, limit: int) -> Tuple[List[FileInfo], int]:
        """
        Get a paginated list of all files.

        Args:
            page: Page number (1-indexed)
            limit: Number of items per page

        Returns:
            Tuple of (list of file info, total count)
        """
        # In a real implementation, this would query a database
        # For now, we'll read from the filesystem
        files = []

        try:
            for file_path in constants.ORIGINAL_FILES_DIR.glob("*"):
                if file_path.is_file():
                    file_id = file_path.stem
                    file_stats = file_path.stat()

                    files.append(
                        FileInfo(
                            file_id=file_id,
                            file_name=file_path.name,
                            file_size=file_stats.st_size,
                            storage_path=str(file_path),
                            created_at=datetime.fromtimestamp(file_stats.st_ctime),
                            loadingMethod=constants.LOADING_METHODS[0],  # Default
                        )
                    )
        except Exception as e:
            logger.error(f"Error listing files: {str(e)}")
            raise

        # Sort by creation date (newest first)
        files.sort(key=lambda x: x.created_at, reverse=True)

        # Apply pagination
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_files = files[start_idx:end_idx]

        return paginated_files, len(files)

    async def get_file(self, file_id: str) -> Optional[FileDetailInfo]:
        """
        Get detailed information about a specific file.

        Args:
            file_id: ID of the file

        Returns:
            FileDetailInfo or None if not found
        """
        # In a real implementation, this would query a database
        # For now, we'll read from the filesystem

        # Find the file with matching ID
        try:
            for file_path in constants.ORIGINAL_FILES_DIR.glob(f"{file_id}.*"):
                if file_path.is_file():
                    file_stats = file_path.stat()

                    # Get chunk and vector counts
                    # In a real implementation, this would query databases/indices
                    chunk_count = 0
                    vector_count = 0

                    return FileDetailInfo(
                        file_id=file_id,
                        file_name=file_path.name,
                        file_size=file_stats.st_size,
                        storage_path=str(file_path),
                        created_at=datetime.fromtimestamp(file_stats.st_ctime),
                        loadingMethod=constants.LOADING_METHODS[0],  # Default
                        chunk_count=chunk_count,
                        vector_count=vector_count,
                    )

            # If we get here, no file was found
            return None
        except Exception as e:
            logger.error(f"Error getting file {file_id}: {str(e)}")
            raise

    async def delete_file(self, file_id: str) -> bool:
        """
        Delete a file and its related data.

        Args:
            file_id: ID of the file to delete

        Returns:
            True if deleted, False if not found
        """
        # Find the file with matching ID
        found = False

        try:
            for file_path in constants.ORIGINAL_FILES_DIR.glob(f"{file_id}.*"):
                if file_path.is_file():
                    # Delete the file
                    os.remove(file_path)
                    found = True
                    break

            # In a real implementation, we would also delete:
            # - Associated chunks
            # - Associated vectors
            # - Associated index entries

            return found
        except Exception as e:
            logger.error(f"Error deleting file {file_id}: {str(e)}")
            raise


if __name__ == "__main__":
    # For testing the service directly
    import asyncio

    async def test_file_service():
        # Create test directories
        constants.ORIGINAL_FILES_DIR.mkdir(parents=True, exist_ok=True)

        service = FileLoaderService()

        # Test listing files
        files, total = await service.get_all_files(1, 10)
        print(f"Found {total} files")
        for file in files:
            print(f"  - {file.file_name} ({file.file_id})")

    asyncio.run(test_file_service())
