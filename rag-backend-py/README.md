# RAG Backend (Python)

This is the Python backend for the RAG (Retrieval-Augmented Generation) system. It provides a complete API for managing files, chunks, embeddings, vector search, and generative AI.

## Project Structure

The project is organized by RAG components, with each component having its own module:

- `file_loader`: For uploading and managing documents
- `chunking`: For splitting documents into text chunks
- `embedding`: For generating vector embeddings
- `vector_index`: For creating and managing vector indexes
- `search`: For retrieval operations
- `generation`: For LLM text generation
- `pipeline`: For end-to-end RAG workflows

Each module can be run independently for testing and can be extended with different implementations of the same functionality.

## Setup

1. Install dependencies:

   ```
   uv sync
   ```

2. Run the application:

   ```
   uv run main.py
   ```

The API will be available at http://localhost:8000

## API Documentation

Once the server is running, you can access the API documentation at:

- OpenAPI UI: http://localhost:8000/docs
- ReDoc UI: http://localhost:8000/redoc

## Testing Individual Components

Each component can be tested independently. For example:

```python
# Test file loader
python -m file_loader.service

# Test chunking
python -m chunking.service

# Test embedding
python -m embedding.service
```

## Development

To run the application in development mode with hot reloading:

```
uvicorn main:app --reload
```

## API Endpoints

The API follows the OpenAPI specification defined in the project documentation. Key endpoints include:

- `/api/v1/files`: File management
- `/api/v1/files/{file_id}/chunks`: Document chunking
- `/api/v1/files/{file_id}/vectors`: Vector embedding
- `/api/v1/search`: Vector search
- `/api/v1/generate`: Text generation
- `/api/v1/pipeline/execute`: Complete RAG pipeline
