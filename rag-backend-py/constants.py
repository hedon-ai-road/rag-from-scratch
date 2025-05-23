"""
Constants used throughout the RAG backend.
"""
from pathlib import Path

# API
API_PREFIX = "/api/v1"

# Data storage paths
DATA_DIR = Path("data")
ORIGINAL_FILES_DIR = DATA_DIR / "original"
CHUNKS_DIR = DATA_DIR / "chunks"
VECTORS_DIR = DATA_DIR / "vectors"
INDEXES_DIR = DATA_DIR / "indexes"
LOGS_DIR = DATA_DIR / "logs"

# File loading settings
MAX_FILE_SIZE = 128 * 1024 * 1024  # 128MB
ALLOWED_FILE_TYPES = ["pdf", "txt", "csv", "png", "jpg", "jpeg", "ppt", "pptx", "md"]
LOADING_METHODS = {
    "pdf": ["PyPDF", "Camelot", "Llamaparse", "Unstructured", "Pdfplumber"],
    "csv": ["Langchain", "Unstructured"],
    "json": ["JsonLoader"],
    "txt": ["TextLoader"],
    "png": ["Unstructured"],
    "jpg": ["Unstructured"],
    "jpeg": ["Unstructured"],
    "ppt": ["Unstructured"],
    "pptx": ["Unstructured"],
    "md": ["Unstructured"],
}

# Chunking settings
DEFAULT_CHUNK_STRATEGY = "sliding_window"
DEFAULT_WINDOW_SIZE = 512
DEFAULT_OVERLAP = 128

# Embedding settings
DEFAULT_EMBEDDING_MODEL = "bge-m3"
DEFAULT_EMBEDDING_BATCH_SIZE = 32
SUPPORTED_EMBEDDING_MODELS = {
    "bge-m3": {
        "dimensions": 768,
        "provider": "BAAI",
        "description": "BGE-M3 is a multilingual embedding model that supports 100+ languages",
    },
    "openai-ada-002": {
        "dimensions": 1536,
        "provider": "OpenAI",
        "description": "OpenAI's text-embedding-ada-002 model",
    },
}

# Vector index settings
DEFAULT_INDEX_TYPE = "hnsw"
DEFAULT_HNSW_M = 16
DEFAULT_HNSW_EF_CONSTRUCTION = 200

# Search settings
DEFAULT_VECTOR_WEIGHT = 0.7
DEFAULT_BM25_WEIGHT = 0.3
DEFAULT_TOP_K = 5

# Generation settings
DEFAULT_GEN_MODEL = "gpt-3.5-turbo"
DEFAULT_MAX_TOKENS = 500
DEFAULT_TEMPERATURE = 0.7
SUPPORTED_GENERATION_MODELS = {
    "gpt-3.5-turbo": {
        "name": "GPT-3.5 Turbo",
        "provider": "OpenAI",
        "max_tokens": 4096,
        "description": "OpenAI's GPT-3.5 Turbo model",
    },
    "gpt-4": {
        "name": "GPT-4",
        "provider": "OpenAI",
        "max_tokens": 8192,
        "description": "OpenAI's GPT-4 model",
    },
    "llama-3-8b": {
        "name": "Llama 3 (8B)",
        "provider": "Meta",
        "max_tokens": 4096,
        "description": "Meta's Llama 3 8B parameter model",
    },
}

# Response codes
SUCCESS_CODE = 0
ERROR_CODE = 1
