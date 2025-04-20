"""
Search service for retrieving relevant chunks based on user queries.
"""
import json
import logging
import os
from datetime import datetime
from typing import List, Tuple

import constants
from models.search import (
    RetrievedChunk,
    SearchHistoryItem,
    SearchRequest,
    SearchScores,
    SearchSettings,
)

logger = logging.getLogger("rag-backend.search")


class SearchService:
    """
    Service for handling search operations.
    """

    async def search(
        self, request: SearchRequest
    ) -> Tuple[List[RetrievedChunk], SearchScores, datetime]:
        """
        Search for relevant chunks based on a query.

        Args:
            request: Search request with query and options

        Returns:
            Tuple of (list of retrieved chunks, search scores, timestamp)
        """
        query = request.query
        search_type = request.search_type
        vector_weight = request.vector_weight
        bm25_weight = request.bm25_weight
        top_k = request.top_k
        file_id = request.file_id

        try:
            # In a real implementation, this would:
            # 1. Create an embedding for the query
            # 2. Search the vector index for similar vectors
            # 3. Optionally perform keyword/BM25 search
            # 4. Combine results with proper weighting

            # For now, we'll just return some placeholder results

            # Find the most recent index
            index_paths = list(constants.INDEXES_DIR.glob("*.json"))
            if not index_paths:
                raise ValueError("No index found. Create an index first.")

            # Sort by modification time (newest first)
            index_paths.sort(key=lambda p: os.path.getmtime(p), reverse=True)

            # Load the most recent index
            with open(index_paths[0], "r") as f:
                index_data = json.load(f)

            # Filter by file_id if specified
            vector_paths = []
            for path_str, metadata in index_data["vector_paths"]:
                if file_id is None or metadata["file_id"] == file_id:
                    vector_paths.append((path_str, metadata))

            if not vector_paths:
                if file_id:
                    raise ValueError(
                        f"No vectors found for file {file_id} in the index"
                    )
                else:
                    raise ValueError("No vectors found in the index")

            # Sort by random score as a placeholder for real search scores
            # In a real implementation, this would be based on vector similarity
            import random

            random.seed(hash(query))  # Deterministic for the same query

            # Simulate vector search scores
            vector_paths_with_scores = [
                (p, m, random.random()) for p, m in vector_paths
            ]

            # Sort by score (highest first)
            vector_paths_with_scores.sort(key=lambda x: x[2], reverse=True)

            # Take top k
            top_results = vector_paths_with_scores[:top_k]

            # Create retrieved chunks
            retrieved_chunks = []

            for path_str, metadata, score in top_results:
                # Get the corresponding chunk
                chunk_id = metadata["chunk_id"]
                file_id = metadata["file_id"]

                # Find the chunk file
                chunk_path = constants.CHUNKS_DIR / file_id / f"{chunk_id}.json"
                if not chunk_path.exists():
                    logger.warning(f"Chunk file not found: {chunk_path}")
                    continue

                # Load the chunk
                with open(chunk_path, "r") as f:
                    chunk_data = json.load(f)

                # Find the original file name
                file_name = "unknown"
                for file_path in constants.ORIGINAL_FILES_DIR.glob(f"{file_id}.*"):
                    file_name = file_path.name
                    break

                # Create a retrieved chunk
                retrieved_chunk = RetrievedChunk(
                    chunk_id=chunk_id,
                    file_id=file_id,
                    file_name=file_name,
                    content=chunk_data["content"],
                    start_offset=chunk_data["start_offset"],
                    end_offset=chunk_data["end_offset"],
                    score=score,
                )

                retrieved_chunks.append(retrieved_chunk)

            # Create search scores
            # In a real implementation, these would be based on actual vector search and BM25 scores
            search_scores = SearchScores(
                vector=0.85,  # Placeholder
                bm25=0.75,  # Placeholder
            )

            # Save the search to history
            timestamp = datetime.utcnow()
            self._save_search_history(
                query,
                [chunk.chunk_id for chunk in retrieved_chunks],
                search_scores,
                timestamp,
            )

            return retrieved_chunks, search_scores, timestamp
        except Exception as e:
            logger.error(f"Error searching: {str(e)}")
            raise

    def _save_search_history(
        self,
        query: str,
        top_chunks: List[str],
        scores: SearchScores,
        timestamp: datetime,
    ) -> None:
        """
        Save a search to history.

        Args:
            query: Search query
            top_chunks: IDs of top retrieved chunks
            scores: Search scores
            timestamp: Search timestamp
        """
        try:
            # Create history directory if it doesn't exist
            history_dir = constants.DATA_DIR / "search_history"
            history_dir.mkdir(parents=True, exist_ok=True)

            # Create a history entry
            history_entry = {
                "timestamp": timestamp.isoformat(),
                "query": query,
                "top_chunks": top_chunks,
                "scores": {
                    "vector": scores.vector,
                    "bm25": scores.bm25,
                },
            }

            # Save to file
            history_path = history_dir / f"{timestamp.strftime('%Y%m%d%H%M%S')}.json"
            with open(history_path, "w") as f:
                json.dump(history_entry, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving search history: {str(e)}")
            # Non-critical, so just log the error

    async def get_search_history(self, limit: int) -> List[SearchHistoryItem]:
        """
        Get recent search history.

        Args:
            limit: Maximum number of history items to return

        Returns:
            List of search history items
        """
        try:
            # Get history directory
            history_dir = constants.DATA_DIR / "search_history"
            if not history_dir.exists():
                return []

            # Get all history files
            history_files = list(history_dir.glob("*.json"))

            # Sort by modification time (newest first)
            history_files.sort(key=lambda p: os.path.getmtime(p), reverse=True)

            # Take the most recent ones
            history_files = history_files[:limit]

            # Load each history entry
            history_items = []

            for history_path in history_files:
                with open(history_path, "r") as f:
                    history_data = json.load(f)

                # Create a history item
                history_item = SearchHistoryItem(
                    timestamp=datetime.fromisoformat(history_data["timestamp"]),
                    query=history_data["query"],
                    top_chunks=history_data["top_chunks"],
                    scores=SearchScores(
                        vector=history_data["scores"]["vector"],
                        bm25=history_data["scores"]["bm25"],
                    ),
                )

                history_items.append(history_item)

            return history_items
        except Exception as e:
            logger.error(f"Error getting search history: {str(e)}")
            raise

    async def get_settings(self) -> SearchSettings:
        """
        Get current search settings.

        Returns:
            Current search settings
        """
        # In a real implementation, this would query a database
        # For now, return default settings
        return SearchSettings(
            vectorWeight=constants.DEFAULT_VECTOR_WEIGHT,
            bm25Weight=constants.DEFAULT_BM25_WEIGHT,
            topK=constants.DEFAULT_TOP_K,
        )

    async def update_settings(
        self, vector_weight: float, bm25_weight: float, top_k: int
    ) -> None:
        """
        Update search settings.

        Args:
            vector_weight: Weight for vector search
            bm25_weight: Weight for BM25 search
            top_k: Default number of results to return
        """
        # In a real implementation, this would update a database
        # For now, we'll just log
        logger.info(
            f"Updated search settings: vector_weight={vector_weight}, "
            f"bm25_weight={bm25_weight}, top_k={top_k}"
        )


if __name__ == "__main__":
    # For testing the service directly
    import asyncio

    async def test_search_service():
        # Create test directories
        constants.DATA_DIR.mkdir(parents=True, exist_ok=True)
        constants.ORIGINAL_FILES_DIR.mkdir(parents=True, exist_ok=True)
        constants.CHUNKS_DIR.mkdir(parents=True, exist_ok=True)
        constants.VECTORS_DIR.mkdir(parents=True, exist_ok=True)
        constants.INDEXES_DIR.mkdir(parents=True, exist_ok=True)

        service = SearchService()

        # Test get settings
        settings = await service.get_settings()
        print(f"Search settings: {settings}")

        # Test get history
        history = await service.get_search_history(10)
        print(f"Found {len(history)} search history items")
        for item in history:
            print(f"  - {item.timestamp}: '{item.query}'")

    asyncio.run(test_search_service())
