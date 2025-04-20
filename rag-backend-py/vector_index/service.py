"""
Vector index service for managing vector indexes.
"""
import json
import logging
import os
import pickle
import uuid
from datetime import datetime
from typing import List, Optional

import numpy as np

import constants
from models.vector_index import DetailedIndexInfo, IndexOptions

logger = logging.getLogger("rag-backend.vector_index")


class VectorIndexService:
    """
    Service for handling vector index operations.
    """

    async def create_index(
        self,
        index_type: str,
        file_ids: List[str],
        index_options: Optional[IndexOptions] = None,
    ) -> DetailedIndexInfo:
        """
        Create or update a vector index.

        Args:
            index_type: Type of index to create (e.g., hnsw)
            file_ids: IDs of files to include in the index
            index_options: Additional options for the index

        Returns:
            Information about the created index
        """
        # Validate index type
        if index_type != "hnsw":  # Only supporting HNSW for now
            raise ValueError(
                f"Unsupported index type: {index_type}. Only 'hnsw' is supported."
            )

        # Check if files exist and have vectors
        for file_id in file_ids:
            file_paths = list(constants.ORIGINAL_FILES_DIR.glob(f"{file_id}.*"))
            if not file_paths:
                raise FileNotFoundError(f"File with ID {file_id} not found")

            vector_dir = constants.VECTORS_DIR / file_id
            if not vector_dir.exists():
                raise ValueError(
                    f"No vectors found for file {file_id}. Create embeddings first."
                )

        # Use default or provided index options
        if index_options:
            m = index_options.m
            ef_construction = index_options.ef_construction
        else:
            m = constants.DEFAULT_HNSW_M
            ef_construction = constants.DEFAULT_HNSW_EF_CONSTRUCTION

        try:
            # Create index directory if it doesn't exist
            constants.INDEXES_DIR.mkdir(parents=True, exist_ok=True)

            # Generate a unique ID for the index
            index_id = f"idx_{uuid.uuid4().hex[:8]}"

            # In a real implementation, this would use an actual index library like HNSW
            # For now, we'll just collect the vector paths
            vector_paths = []
            dimensions = None

            # Collect all vector paths and check dimensions consistency
            for file_id in file_ids:
                vector_dir = constants.VECTORS_DIR / file_id

                for vector_path in vector_dir.glob("*.npy"):
                    # Check if there's a corresponding metadata file
                    metadata_path = vector_dir / f"{vector_path.stem}.json"
                    if not metadata_path.exists():
                        continue

                    # Load metadata
                    with open(metadata_path, "r") as f:
                        metadata = json.load(f)

                    # Check dimensions
                    if dimensions is None:
                        dimensions = metadata["dimensions"]
                    elif dimensions != metadata["dimensions"]:
                        raise ValueError(
                            f"Inconsistent vector dimensions: expected {dimensions}, "
                            f"got {metadata['dimensions']} for chunk {metadata['chunk_id']}"
                        )

                    vector_paths.append((vector_path, metadata))

            if not vector_paths:
                raise ValueError("No vectors found for the specified files")

            # Create a simple index (just store the paths and metadata)
            index_data = {
                "index_id": index_id,
                "index_type": index_type,
                "file_ids": file_ids,
                "dimensions": dimensions,
                "vector_paths": [(str(p), m) for p, m in vector_paths],
                "options": {
                    "m": m,
                    "ef_construction": ef_construction,
                },
                "created_at": datetime.utcnow().isoformat(),
                "last_updated": datetime.utcnow().isoformat(),
            }

            # Save index metadata
            index_path = constants.INDEXES_DIR / f"{index_id}.json"
            with open(index_path, "w") as f:
                json.dump(index_data, f, indent=2)

            # Return index info
            return DetailedIndexInfo(
                index_id=index_id,
                index_type=index_type,
                file_count=len(file_ids),
                vector_count=len(vector_paths),
                dimensions=dimensions,
                created_at=datetime.utcnow(),
                last_updated=datetime.utcnow(),
                size_bytes=os.path.getsize(index_path),
            )
        except Exception as e:
            logger.error(f"Error creating index: {str(e)}")
            raise

    async def get_index_info(self) -> Optional[DetailedIndexInfo]:
        """
        Get information about the current index.

        Returns:
            Information about the index or None if no index exists
        """
        try:
            # Find the most recent index
            index_paths = list(constants.INDEXES_DIR.glob("*.json"))
            if not index_paths:
                return None

            # Sort by modification time (newest first)
            index_paths.sort(key=lambda p: os.path.getmtime(p), reverse=True)

            # Load the most recent index
            with open(index_paths[0], "r") as f:
                index_data = json.load(f)

            # Return index info
            return DetailedIndexInfo(
                index_id=index_data["index_id"],
                index_type=index_data["index_type"],
                file_count=len(index_data["file_ids"]),
                vector_count=len(index_data["vector_paths"]),
                dimensions=index_data["dimensions"],
                created_at=datetime.fromisoformat(index_data["created_at"]),
                last_updated=datetime.fromisoformat(index_data["last_updated"]),
                size_bytes=os.path.getsize(index_paths[0]),
            )
        except Exception as e:
            logger.error(f"Error getting index info: {str(e)}")
            raise


if __name__ == "__main__":
    # For testing the service directly
    import asyncio

    async def test_vector_index_service():
        # Create test directories
        constants.ORIGINAL_FILES_DIR.mkdir(parents=True, exist_ok=True)
        constants.CHUNKS_DIR.mkdir(parents=True, exist_ok=True)
        constants.VECTORS_DIR.mkdir(parents=True, exist_ok=True)
        constants.INDEXES_DIR.mkdir(parents=True, exist_ok=True)

        service = VectorIndexService()

        # Test get index info
        index_info = await service.get_index_info()
        if index_info:
            print(
                f"Index {index_info.index_id}: {index_info.vector_count} vectors, {index_info.dimensions}d"
            )
        else:
            print("No existing index found")

    asyncio.run(test_vector_index_service())
