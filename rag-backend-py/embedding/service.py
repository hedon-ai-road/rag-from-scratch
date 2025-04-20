"""
Embedding service for generating and managing vector embeddings.
"""
import json
import logging
from datetime import datetime
from typing import List, Optional, Tuple

import numpy as np

import constants
from models.embedding import EmbeddingModel, VectorSettings

logger = logging.getLogger("rag-backend.embedding")


class EmbeddingService:
    """
    Service for handling vector embedding operations.
    """

    async def get_supported_models(self) -> List[EmbeddingModel]:
        """
        Get a list of supported embedding models.

        Returns:
            List of supported embedding models
        """
        models = []

        # In a real implementation, this might query an API or database
        # For now, return the hardcoded models from constants
        for model_id, model_info in constants.SUPPORTED_EMBEDDING_MODELS.items():
            models.append(
                EmbeddingModel(
                    id=model_id,
                    name=model_id,  # Use ID as name for now
                    dimensions=model_info["dimensions"],
                    provider=model_info["provider"],
                    description=model_info["description"],
                )
            )

        return models

    async def create_embeddings(
        self, file_id: str, model_id: str, batch_size: Optional[int] = None
    ) -> Tuple[int, int, str]:
        """
        Create embeddings for a file's chunks.

        Args:
            file_id: ID of the file
            model_id: ID of the embedding model to use
            batch_size: Batch size for embedding generation

        Returns:
            Tuple of (number of vectors created, vector dimensions, status)
        """
        # Check if file exists
        file_paths = list(constants.ORIGINAL_FILES_DIR.glob(f"{file_id}.*"))
        if not file_paths:
            raise FileNotFoundError(f"File with ID {file_id} not found")

        # Check if model is supported
        if model_id not in constants.SUPPORTED_EMBEDDING_MODELS:
            valid_models = ", ".join(constants.SUPPORTED_EMBEDDING_MODELS.keys())
            raise ValueError(
                f"Unsupported embedding model. Valid options: {valid_models}"
            )

        # Check if chunks exist
        chunk_dir = constants.CHUNKS_DIR / file_id
        if not chunk_dir.exists():
            raise ValueError(
                f"No chunks found for file {file_id}. Create chunks first."
            )

        # Get model info
        model_info = constants.SUPPORTED_EMBEDDING_MODELS[model_id]
        dimensions = model_info["dimensions"]

        # Use provided batch size or default
        batch_size = batch_size or constants.DEFAULT_EMBEDDING_BATCH_SIZE

        try:
            # Get all chunks
            chunks = []
            for chunk_path in chunk_dir.glob("*.json"):
                with open(chunk_path, "r") as f:
                    chunk_data = json.load(f)
                    chunks.append(chunk_data)

            if not chunks:
                raise ValueError(f"No chunks found for file {file_id}")

            # Create vector directory if it doesn't exist
            vector_dir = constants.VECTORS_DIR / file_id
            vector_dir.mkdir(parents=True, exist_ok=True)

            # In a real implementation, this would use an actual embedding model
            # For now, we'll just create random vectors
            for chunk in chunks:
                chunk_id = chunk["chunk_id"]
                text = chunk["content"]

                # Simulate embedding generation
                fake_vector = np.random.randn(dimensions).astype(np.float32)
                vector_path = vector_dir / f"{chunk_id}.npy"

                # Save vector to disk
                np.save(vector_path, fake_vector)

                # Save metadata
                metadata_path = vector_dir / f"{chunk_id}.json"
                metadata = {
                    "chunk_id": chunk_id,
                    "file_id": file_id,
                    "model_id": model_id,
                    "dimensions": dimensions,
                    "created_at": datetime.utcnow().isoformat(),
                }

                with open(metadata_path, "w") as f:
                    json.dump(metadata, f, indent=2)

            return len(chunks), dimensions, "completed"
        except Exception as e:
            logger.error(f"Error creating embeddings for file {file_id}: {str(e)}")
            raise

    async def get_settings(self) -> VectorSettings:
        """
        Get current vector settings.

        Returns:
            Current vector settings
        """
        # In a real implementation, this would query a database
        # For now, return default settings
        return VectorSettings(
            model=constants.DEFAULT_EMBEDDING_MODEL,
            dimensions=constants.SUPPORTED_EMBEDDING_MODELS[
                constants.DEFAULT_EMBEDDING_MODEL
            ]["dimensions"],
            default_batch_size=constants.DEFAULT_EMBEDDING_BATCH_SIZE,
        )

    async def update_settings(
        self, model: str, dimensions: int, default_batch_size: int
    ) -> None:
        """
        Update vector settings.

        Args:
            model: Default embedding model
            dimensions: Vector dimensions
            default_batch_size: Default batch size
        """
        # In a real implementation, this would update a database
        # For now, we'll just log
        logger.info(
            f"Updated vector settings: model={model}, "
            f"dimensions={dimensions}, default_batch_size={default_batch_size}"
        )


if __name__ == "__main__":
    # For testing the service directly
    import asyncio

    async def test_embedding_service():
        # Create test directories
        constants.ORIGINAL_FILES_DIR.mkdir(parents=True, exist_ok=True)
        constants.CHUNKS_DIR.mkdir(parents=True, exist_ok=True)
        constants.VECTORS_DIR.mkdir(parents=True, exist_ok=True)

        service = EmbeddingService()

        # Test get supported models
        models = await service.get_supported_models()
        print(f"Supported models:")
        for model in models:
            print(f"  - {model.id}: {model.dimensions}d by {model.provider}")

        # Test get settings
        settings = await service.get_settings()
        print(f"Vector settings: {settings}")

    asyncio.run(test_embedding_service())
