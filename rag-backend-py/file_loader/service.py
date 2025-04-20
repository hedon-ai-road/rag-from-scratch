"""
File loader service for handling file operations.
"""
import logging
import os
import uuid
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple, Dict

from fastapi import UploadFile

import constants
from models.file import FileDetailInfo, FileInfo

from file_loader.pdf_pypdf import load as PDFPyPDFLoader


logger = logging.getLogger("rag-backend.file_loader")


class FileLoaderService:
    """
    Service for handling file operations like upload, listing, and deletion.
    """

    # Cache structure: {md5: {loading_method: docs}}
    _docs_cache: Dict[str, Dict[str, List]] = {}

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
        # Use default loading method if not provided
        loading_method = loading_method or constants.LOADING_METHODS[0]

        # Get the file metadata
        filename = file.filename or "unnamed_file"
        file_ext = Path(filename).suffix.lstrip(".").lower()

        # Check extension
        if file_ext not in constants.ALLOWED_FILE_TYPES:
            valid_types = ", ".join(constants.ALLOWED_FILE_TYPES)
            raise ValueError(f"Unsupported file type. Supported types: {valid_types}")

        # Read file content
        content = await file.read()
        file_size = len(content)

        # Check size limitation
        if file_size > constants.MAX_FILE_SIZE:
            max_size_mb = constants.MAX_FILE_SIZE / (1024 * 1024)
            raise ValueError(f"File too large. Maximum size: {max_size_mb} MB")

        # Calculate file md5 based on the content
        file_md5 = hashlib.md5(content).hexdigest()
        file_id = file_md5

        # Build path
        storage_path = constants.ORIGINAL_FILES_DIR / f"{file_id}.{file_ext}"

        # Save file
        file_exists = storage_path.exists()
        if not file_exists:
            with open(storage_path, "wb") as f:
                f.write(content)
            logger.info(f"File saved: {storage_path}")
        else:
            logger.info(f"File already exists: {storage_path}")

        # Reset file pointer to allow rereading if needed
        await file.seek(0)

        # Get or load documents based on the md5 and loading_method
        docs = self._get_or_load_docs(file_id, loading_method, storage_path)

        # Return file info
        return FileInfo(
            file_id=file_id,
            file_name=filename,
            file_size=file_size,
            storage_path=str(storage_path),
            created_at=datetime.utcnow(),
            loadingMethod=loading_method,
            docs=docs,
        )

    def _get_or_load_docs(self, file_id: str, loading_method: str, path: Path):
        """
        Get documents from cache or load and cache them

        Args:
            file_id: File ID (MD5)
            loading_method: Loading method
            path: File path

        Returns:
            List of loaded documents
        """
        # Check cache
        if file_id in self._docs_cache and loading_method in self._docs_cache[file_id]:
            logger.info(
                f"Using cached docs for file {file_id} with method {loading_method}"
            )
            return self._docs_cache[file_id][loading_method]

        # Load documents
        docs = self.load_file(loading_method, path)

        # Update cache
        if file_id not in self._docs_cache:
            self._docs_cache[file_id] = {}
        self._docs_cache[file_id][loading_method] = docs

        return docs

    def load_file(self, loading_method, path):
        """
        Load a file using the specified method

        Args:
            loading_method: Loading method
            path: File path

        Returns:
            List of documents
        """
        logger.info(f"Loading file: {path} with method: {loading_method}")
        if loading_method == "PyPDF":
            return PDFPyPDFLoader(path=path)
        else:
            logger.warning(f"Unknown loading method: {loading_method} for path: {path}")
            return []

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

                    # Remove from cache
                    if file_id in self._docs_cache:
                        del self._docs_cache[file_id]
                        logger.info(f"Removed docs cache for file {file_id}")

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
