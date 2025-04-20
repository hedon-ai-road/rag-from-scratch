"""
Pipeline service for end-to-end RAG workflows.
"""
import asyncio
import json
import logging
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

import constants
from chunking import ChunkingService
from embedding import EmbeddingService
from file_loader import FileLoaderService
from models.pipeline import (
    ChunkingStep,
    EmbeddingStep,
    FileLoadingStep,
    IndexingStep,
    PipelineExecuteRequest,
    PipelineStatus,
)
from vector_index import VectorIndexService

logger = logging.getLogger("rag-backend.pipeline")


class PipelineService:
    """
    Service for handling end-to-end RAG pipeline operations.
    """

    def __init__(self):
        self.file_service = FileLoaderService()
        self.chunking_service = ChunkingService()
        self.embedding_service = EmbeddingService()
        self.index_service = VectorIndexService()
        self.pipelines = {}  # Store active pipelines

    async def execute_pipeline(
        self, request: PipelineExecuteRequest, file_data: bytes
    ) -> str:
        """
        Execute a complete RAG pipeline.

        Args:
            request: Pipeline execution request
            file_data: Binary file data

        Returns:
            Pipeline ID
        """
        # Generate a unique ID for the pipeline
        pipeline_id = f"pl_{uuid.uuid4().hex[:8]}"

        # Create initial pipeline status
        status = PipelineStatus(
            pipeline_id=pipeline_id,
            status="in_progress",
            steps=[
                FileLoadingStep(
                    step="file_loading",
                    status="pending",
                    file_id="",
                    file_name=request.filename,
                ),
                ChunkingStep(step="chunking", status="pending"),
                EmbeddingStep(step="embedding", status="pending"),
                IndexingStep(step="indexing", status="pending"),
            ],
            started_at=datetime.utcnow(),
        )

        # Store the pipeline status
        self.pipelines[pipeline_id] = status

        # Execute the pipeline in a background task
        asyncio.create_task(
            self._execute_pipeline_async(
                pipeline_id,
                request,
                file_data,
            )
        )

        return pipeline_id

    async def _execute_pipeline_async(
        self,
        pipeline_id: str,
        request: PipelineExecuteRequest,
        file_data: bytes,
    ) -> None:
        """
        Execute a pipeline asynchronously.

        Args:
            pipeline_id: Pipeline ID
            request: Pipeline execution request
            file_data: Binary file data
        """
        start_time = time.time()
        status = self.pipelines[pipeline_id]
        file_id = None

        try:
            # Step 1: File loading
            status.steps[0].status = "in_progress"
            self._update_pipeline_status(pipeline_id, status)

            # Create a temporary file
            temp_file_path = Path(f"temp_{uuid.uuid4().hex}.tmp")
            with open(temp_file_path, "wb") as f:
                f.write(file_data)

            # Use the file loader service
            from fastapi import UploadFile

            file = UploadFile(
                filename=request.filename, file=open(temp_file_path, "rb")
            )

            # Process the file
            file_info = await self.file_service.upload_file(file, None)
            file_id = file_info.file_id

            # Update step status
            status.steps[0].status = "completed"
            status.steps[0].file_id = file_id
            status.steps[0].file_name = file_info.file_name
            self._update_pipeline_status(pipeline_id, status)

            # Clean up temp file
            file.file.close()
            temp_file_path.unlink(missing_ok=True)

            # Step 2: Chunking
            status.steps[1].status = "in_progress"
            self._update_pipeline_status(pipeline_id, status)

            # Use the chunking service
            chunks = await self.chunking_service.create_chunks(
                file_id,
                request.chunk_strategy,
                request.window_size,
                request.overlap,
                None,
            )

            # Update step status
            status.steps[1].status = "completed"
            status.steps[1].chunk_count = len(chunks)
            self._update_pipeline_status(pipeline_id, status)

            # Step 3: Embedding
            status.steps[2].status = "in_progress"
            self._update_pipeline_status(pipeline_id, status)

            # Use the embedding service
            (
                vector_count,
                dimensions,
                embedding_status,
            ) = await self.embedding_service.create_embeddings(
                file_id, request.embedding_model
            )

            # Update step status
            status.steps[2].status = "completed"
            status.steps[2].vector_count = vector_count
            self._update_pipeline_status(pipeline_id, status)

            # Step 4: Indexing
            status.steps[3].status = "in_progress"
            self._update_pipeline_status(pipeline_id, status)

            # Use the index service
            index_info = await self.index_service.create_index(
                request.index_type, [file_id]
            )

            # Update step status
            status.steps[3].status = "completed"
            status.steps[3].index_id = index_info.index_id
            self._update_pipeline_status(pipeline_id, status)

            # Update overall status
            status.status = "completed"
            status.execution_time = time.time() - start_time
            self._update_pipeline_status(pipeline_id, status)

            # Save pipeline result to disk
            self._save_pipeline_result(pipeline_id, status)
        except Exception as e:
            logger.error(f"Pipeline error: {str(e)}")

            # Update status to reflect error
            status.status = "error"

            # Find the step that failed
            for step in status.steps:
                if step.status == "in_progress":
                    step.status = "error"
                    break

            status.execution_time = time.time() - start_time
            self._update_pipeline_status(pipeline_id, status)

            # Save pipeline result to disk
            self._save_pipeline_result(pipeline_id, status)

    def _update_pipeline_status(self, pipeline_id: str, status: PipelineStatus) -> None:
        """
        Update pipeline status.

        Args:
            pipeline_id: Pipeline ID
            status: New status
        """
        # Calculate elapsed time
        if status.started_at:
            status.elapsed_time = (
                datetime.utcnow() - status.started_at
            ).total_seconds()

        # Store the updated status
        self.pipelines[pipeline_id] = status

    def _save_pipeline_result(self, pipeline_id: str, status: PipelineStatus) -> None:
        """
        Save pipeline result to disk.

        Args:
            pipeline_id: Pipeline ID
            status: Pipeline status
        """
        try:
            # Create pipelines directory if it doesn't exist
            pipelines_dir = constants.DATA_DIR / "pipelines"
            pipelines_dir.mkdir(parents=True, exist_ok=True)

            # Save pipeline status
            pipeline_path = pipelines_dir / f"{pipeline_id}.json"

            # Convert status to dict
            status_dict = status.dict()

            # Handle datetime serialization
            status_dict["started_at"] = (
                status_dict["started_at"].isoformat()
                if status_dict["started_at"]
                else None
            )

            with open(pipeline_path, "w") as f:
                json.dump(status_dict, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving pipeline result: {str(e)}")

    async def get_pipeline_status(self, pipeline_id: str) -> Optional[PipelineStatus]:
        """
        Get pipeline status.

        Args:
            pipeline_id: Pipeline ID

        Returns:
            Pipeline status or None if not found
        """
        # First check in-memory cache
        if pipeline_id in self.pipelines:
            return self.pipelines[pipeline_id]

        # If not in memory, check disk
        pipeline_path = constants.DATA_DIR / "pipelines" / f"{pipeline_id}.json"
        if not pipeline_path.exists():
            return None

        try:
            with open(pipeline_path, "r") as f:
                status_dict = json.load(f)

            # Handle datetime deserialization
            if status_dict["started_at"]:
                status_dict["started_at"] = datetime.fromisoformat(
                    status_dict["started_at"]
                )

            # Create the appropriate step objects
            steps = []
            for step_dict in status_dict["steps"]:
                step_type = step_dict["step"]

                if step_type == "file_loading":
                    steps.append(FileLoadingStep(**step_dict))
                elif step_type == "chunking":
                    steps.append(ChunkingStep(**step_dict))
                elif step_type == "embedding":
                    steps.append(EmbeddingStep(**step_dict))
                elif step_type == "indexing":
                    steps.append(IndexingStep(**step_dict))

            # Replace the steps list
            status_dict["steps"] = steps

            # Create pipeline status
            return PipelineStatus(**status_dict)
        except Exception as e:
            logger.error(f"Error getting pipeline status: {str(e)}")
            return None


if __name__ == "__main__":
    # For testing the service directly
    import asyncio

    async def test_pipeline_service():
        # Create test directories
        constants.DATA_DIR.mkdir(parents=True, exist_ok=True)

        service = PipelineService()

        # Test get pipeline status for a non-existent pipeline
        status = await service.get_pipeline_status("non_existent")
        print(f"Status for non-existent pipeline: {status}")

    asyncio.run(test_pipeline_service())
