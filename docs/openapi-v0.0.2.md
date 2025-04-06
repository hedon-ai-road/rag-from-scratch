# RAG System API Documentation (v0.0.2)

本文档定义了 RAG 系统的后端 API 接口规范，包括文件管理、文本分块、向量嵌入、检索和生成等功能的接口。

## 基础信息

- 基础 URL: `/api/v1`
- 所有请求和响应均使用 JSON 格式
- 统一响应格式:
  ```json
  {
    "code": 0, // 错误码，0 表示成功，其他表示失败
    "message": "Error description", // 错误描述
    "data": {} // 响应数据，下面的 API 中仅展示 data 字段
  }
  ```

## 文件管理 API

### 上传文件

将文档文件上传到 RAG 系统以进行处理

**路径:** `POST /files`

**Content-Type:** `multipart/form-data`

**请求参数:**

| 参数名        | 类型   | 位置 | 描述                                   | 必填 |
| ------------- | ------ | ---- | -------------------------------------- | ---- |
| file          | File   | Form | 要上传的文件                           | 是   |
| loadingMethod | String | Form | 文件加载方法，如 "PyMuPDF"、"PyPDF" 等 | 否   |

**成功响应:** (200 OK)

```json
{
  "file": {
    "file_id": "f1a3b5c7",
    "file_name": "example.pdf",
    "file_size": 1048576,
    "storage_path": "./data/original/f1a3b5c7.pdf",
    "created_at": "2024-04-01T10:30:00Z",
    "loadingMethod": "PyMuPDF"
  }
}
```

### 获取所有文件

获取系统中所有上传的文件

**路径:** `GET /files`

**请求参数:**

| 参数名 | 类型    | 位置  | 描述                | 必填 |
| ------ | ------- | ----- | ------------------- | ---- |
| page   | Integer | Query | 页码，从 1 开始     | 否   |
| limit  | Integer | Query | 每页项目数，默认 10 | 否   |

**成功响应:** (200 OK)

```json
{
  "files": [
    {
      "file_id": "f1a3b5c7",
      "file_name": "example.pdf",
      "file_size": 1048576,
      "storage_path": "./data/original/f1a3b5c7.pdf",
      "created_at": "2024-04-01T10:30:00Z",
      "loadingMethod": "PyMuPDF"
    },
    {
      "file_id": "b2c4d6e8",
      "file_name": "another_document.pdf",
      "file_size": 524288,
      "storage_path": "./data/original/b2c4d6e8.pdf",
      "created_at": "2024-04-02T14:45:00Z",
      "loadingMethod": "PyPDF"
    }
  ],
  "pagination": {
    "total": 2,
    "page": 1,
    "limit": 10,
    "pages": 1
  }
}
```

### 获取单个文件

获取特定文件的详细信息

**路径:** `GET /files/{file_id}`

**路径参数:**

| 参数名  | 类型   | 描述    | 必填 |
| ------- | ------ | ------- | ---- |
| file_id | String | 文件 ID | 是   |

**成功响应:** (200 OK)

```json
{
  "file": {
    "file_id": "f1a3b5c7",
    "file_name": "example.pdf",
    "file_size": 1048576,
    "storage_path": "./data/original/f1a3b5c7.pdf",
    "created_at": "2024-04-01T10:30:00Z",
    "loadingMethod": "PyMuPDF",
    "chunk_count": 15,
    "vector_count": 15
  }
}
```

### 删除文件

删除文件及其相关的分块和向量

**路径:** `DELETE /files/{file_id}`

**路径参数:**

| 参数名  | 类型   | 描述    | 必填 |
| ------- | ------ | ------- | ---- |
| file_id | String | 文件 ID | 是   |

**成功响应:** (200 OK)

```json
{}
```

## 文本分块 API

### 创建文档分块

对指定文件进行文本分块处理

**路径:** `POST /files/{file_id}/chunks`

**路径参数:**

| 参数名  | 类型   | 描述    | 必填 |
| ------- | ------ | ------- | ---- |
| file_id | String | 文件 ID | 是   |

**请求体:**

```json
{
  "chunk_strategy": "sliding_window",
  "window_size": 512,
  "overlap": 128,
  "custom_options": {
    "format_detection": true
  }
}
```

**成功响应:** (200 OK)

```json
{
  "file_id": "f1a3b5c7",
  "chunk_count": 15,
  "chunks": [
    {
      "chunk_id": "c1b2a3d4",
      "file_id": "f1a3b5c7",
      "content": "RAG (Retrieval Augmented Generation) is an architecture that combines search capabilities with generative AI...",
      "start_offset": 0,
      "end_offset": 511
    },
    {
      "chunk_id": "d5e6f7a8",
      "file_id": "f1a3b5c7",
      "content": "The RAG workflow consists of several key components: document ingestion, chunking, embedding generation...",
      "start_offset": 384,
      "end_offset": 895
    }
  ]
}
```

### 获取文件的分块

获取指定文件的所有分块

**路径:** `GET /files/{file_id}/chunks`

**路径参数:**

| 参数名  | 类型   | 描述    | 必填 |
| ------- | ------ | ------- | ---- |
| file_id | String | 文件 ID | 是   |

**请求参数:**

| 参数名 | 类型    | 位置  | 描述                | 必填 |
| ------ | ------- | ----- | ------------------- | ---- |
| page   | Integer | Query | 页码，从 1 开始     | 否   |
| limit  | Integer | Query | 每页项目数，默认 10 | 否   |

**成功响应:** (200 OK)

```json
{
  "file_id": "f1a3b5c7",
  "chunk_count": 15,
  "chunks": [
    {
      "chunk_id": "c1b2a3d4",
      "file_id": "f1a3b5c7",
      "content": "RAG (Retrieval Augmented Generation) is an architecture that combines search capabilities with generative AI...",
      "start_offset": 0,
      "end_offset": 511
    },
    {
      "chunk_id": "d5e6f7a8",
      "file_id": "f1a3b5c7",
      "content": "The RAG workflow consists of several key components: document ingestion, chunking, embedding generation...",
      "start_offset": 384,
      "end_offset": 895
    }
  ],
  "pagination": {
    "total": 15,
    "page": 1,
    "limit": 10,
    "pages": 2
  }
}
```

### 更新分块策略

更新系统的默认分块策略

**路径:** `PUT /chunk-settings`

**请求体:**

```json
{
  "window_size": 512,
  "overlap": 128,
  "strategy": "sliding_window"
}
```

**成功响应:** (200 OK)

```json
{
  "settings": {
    "window_size": 512,
    "overlap": 128,
    "strategy": "sliding_window"
  }
}
```

## 向量嵌入 API

### 获取支持的嵌入模型

获取系统支持的嵌入模型列表

**路径:** `GET /embedding-models`

**成功响应:** (200 OK)

```json
{
  "models": [
    {
      "id": "bge-m3",
      "name": "BGE-M3",
      "dimensions": 768,
      "provider": "BAAI",
      "description": "BGE-M3 is a multilingual embedding model that supports 100+ languages"
    },
    {
      "id": "openai-ada-002",
      "name": "Ada-002",
      "dimensions": 1536,
      "provider": "OpenAI",
      "description": "OpenAI's text-embedding-ada-002 model"
    }
  ]
}
```

### 为文件创建向量嵌入

为指定文件的分块生成向量嵌入

**路径:** `POST /files/{file_id}/vectors`

**路径参数:**

| 参数名  | 类型   | 描述    | 必填 |
| ------- | ------ | ------- | ---- |
| file_id | String | 文件 ID | 是   |

**请求体:**

```json
{
  "model_id": "bge-m3",
  "batch_size": 32
}
```

**成功响应:** (200 OK)

```json
{
  "file_id": "f1a3b5c7",
  "model_used": "bge-m3",
  "dimensions": 768,
  "vectors_created": 15,
  "status": "completed"
}
```

### 获取向量设置

获取当前向量嵌入设置

**路径:** `GET /vector-settings`

**成功响应:** (200 OK)

```json
{
  "settings": {
    "model": "BGE-M3",
    "dimensions": 768,
    "default_batch_size": 32
  }
}
```

### 更新向量设置

更新向量嵌入的默认设置

**路径:** `PUT /vector-settings`

**请求体:**

```json
{
  "model": "BGE-M3",
  "dimensions": 768,
  "default_batch_size": 32
}
```

**成功响应:** (200 OK)

```json
{
  "settings": {
    "model": "BGE-M3",
    "dimensions": 768,
    "default_batch_size": 32
  }
}
```

## 向量索引 API

### 创建/更新索引

创建或更新向量索引

**路径:** `POST /vector-index`

**请求体:**

```json
{
  "index_type": "hnsw",
  "file_ids": ["f1a3b5c7", "b2c4d6e8"],
  "index_options": {
    "m": 16,
    "ef_construction": 200
  }
}
```

**成功响应:** (200 OK)

```json
{
  "index_id": "idx_1234567",
  "index_type": "hnsw",
  "file_count": 2,
  "vector_count": 30,
  "dimensions": 768,
  "created_at": "2024-04-05T15:30:00Z"
}
```

### 获取索引信息

获取当前向量索引的信息

**路径:** `GET /vector-index`

**成功响应:** (200 OK)

```json
{
  "index": {
    "index_id": "idx_1234567",
    "index_type": "hnsw",
    "file_count": 2,
    "vector_count": 30,
    "dimensions": 768,
    "created_at": "2024-04-05T15:30:00Z",
    "last_updated": "2024-04-05T15:30:00Z",
    "size_bytes": 102400
  }
}
```

## 搜索 API

### 执行检索查询

执行检索查询并返回相关文档片段

**路径:** `POST /search`

**请求体:**

```json
{
  "query": "What is RAG architecture?",
  "search_type": "hybrid",
  "vector_weight": 0.7,
  "bm25_weight": 0.3,
  "top_k": 5,
  "file_id": "f1a3b5c7" // 可选，限制在特定文件内搜索
}
```

**成功响应:** (200 OK)

```json
{
  "query": "What is RAG architecture?",
  "timestamp": "2024-04-05T09:15:00Z",
  "search_type": "hybrid",
  "search_scores": {
    "vector": 0.82,
    "bm25": 0.75
  },
  "retrievedChunks": [
    {
      "chunk_id": "c1b2a3d4",
      "file_id": "f1a3b5c7",
      "file_name": "rag_guide.pdf",
      "content": "RAG (Retrieval Augmented Generation) is an architecture that combines search capabilities with generative AI...",
      "start_offset": 0,
      "end_offset": 511,
      "score": 0.92
    },
    {
      "chunk_id": "d5e6f7a8",
      "file_id": "f1a3b5c7",
      "file_name": "rag_guide.pdf",
      "content": "The RAG workflow consists of several key components: document ingestion, chunking, embedding generation...",
      "start_offset": 384,
      "end_offset": 895,
      "score": 0.87
    }
  ]
}
```

### 获取搜索历史

获取最近的搜索记录

**路径:** `GET /search-history`

**请求参数:**

| 参数名 | 类型    | 位置  | 描述                  | 必填 |
| ------ | ------- | ----- | --------------------- | ---- |
| limit  | Integer | Query | 返回的记录数，默认 10 | 否   |

**成功响应:** (200 OK)

```json
{
  "history": [
    {
      "timestamp": "2024-04-05T09:15:00Z",
      "query": "What is RAG architecture?",
      "top_chunks": ["c1b2a3d4", "d5e6f7a8"],
      "scores": { "vector": 0.82, "bm25": 0.75 }
    },
    {
      "timestamp": "2024-04-05T10:20:00Z",
      "query": "How to implement vector search?",
      "top_chunks": ["g7h8i9j0", "k1l2m3n4"],
      "scores": { "vector": 0.79, "bm25": 0.81 }
    }
  ]
}
```

### 更新搜索设置

更新默认搜索设置

**路径:** `PUT /search-settings`

**请求体:**

```json
{
  "vectorWeight": 0.6,
  "bm25Weight": 0.4,
  "topK": 5
}
```

**成功响应:** (200 OK)

```json
{
  "settings": {
    "vectorWeight": 0.6,
    "bm25Weight": 0.4,
    "topK": 5
  }
}
```

## 生成 API

### 执行生成请求

基于查询和检索结果生成回答

**路径:** `POST /generate`

**请求体:**

```json
{
  "query": "What is RAG architecture?",
  "chunk_ids": ["c1b2a3d4", "d5e6f7a8"],
  "model": "gpt-3.5-turbo",
  "max_tokens": 500,
  "temperature": 0.7
}
```

**成功响应:** (200 OK)

```json
{
  "gen_id": "g1234567",
  "query": "What is RAG architecture?",
  "used_chunks": ["c1b2a3d4", "d5e6f7a8"],
  "response": "RAG (Retrieval Augmented Generation) is an architecture that combines search and generative AI. It works by retrieving relevant information from a knowledge base and then using that information to augment the generation process of large language models, producing more accurate and contextually relevant responses.",
  "created_at": "2024-04-05T09:15:05Z",
  "model_used": "gpt-3.5-turbo",
  "token_usage": {
    "prompt": 354,
    "completion": 78,
    "total": 432
  }
}
```

### 获取生成历史

获取最近的生成记录

**路径:** `GET /generations`

**请求参数:**

| 参数名 | 类型    | 位置  | 描述                  | 必填 |
| ------ | ------- | ----- | --------------------- | ---- |
| limit  | Integer | Query | 返回的记录数，默认 10 | 否   |

**成功响应:** (200 OK)

```json
{
  "generations": [
    {
      "gen_id": "g1234567",
      "query": "What is RAG architecture?",
      "used_chunks": ["c1b2a3d4", "d5e6f7a8"],
      "response": "RAG (Retrieval Augmented Generation) is an architecture that combines search and generative AI...",
      "created_at": "2024-04-05T09:15:05Z",
      "model_used": "gpt-3.5-turbo"
    },
    {
      "gen_id": "g7654321",
      "query": "Explain vector embeddings",
      "used_chunks": ["g7h8i9j0", "k1l2m3n4"],
      "response": "Vector embeddings are numerical representations of text that capture semantic meaning...",
      "created_at": "2024-04-05T10:25:00Z",
      "model_used": "gpt-3.5-turbo"
    }
  ]
}
```

### 获取支持的生成模型

获取系统支持的文本生成模型列表

**路径:** `GET /generation-models`

**成功响应:** (200 OK)

```json
{
  "models": [
    {
      "id": "gpt-3.5-turbo",
      "name": "GPT-3.5 Turbo",
      "provider": "OpenAI",
      "max_tokens": 4096,
      "description": "OpenAI's GPT-3.5 Turbo model"
    },
    {
      "id": "gpt-4",
      "name": "GPT-4",
      "provider": "OpenAI",
      "max_tokens": 8192,
      "description": "OpenAI's GPT-4 model"
    },
    {
      "id": "llama-3-8b",
      "name": "Llama 3 (8B)",
      "provider": "Meta",
      "max_tokens": 4096,
      "description": "Meta's Llama 3 8B parameter model"
    }
  ]
}
```

## 系统监控 API

### 获取系统状态

获取 RAG 系统的当前状态和统计信息

**路径:** `GET /system/status`

**成功响应:** (200 OK)

```json
{
  "system": {
    "file_count": 5,
    "chunk_count": 120,
    "vector_count": 120,
    "search_count": 25,
    "generation_count": 15
  },
  "config": {
    "chunk_strategy": "sliding_window",
    "vector_model": "BGE-M3",
    "search_settings": {
      "vectorWeight": 0.6,
      "bm25Weight": 0.4,
      "topK": 5
    }
  },
  "performance": {
    "retrieval_accuracy": 0.85,
    "generation_time_avg": 2.3,
    "chunk_quality": 0.92,
    "embedding_throughput": 250
  }
}
```

### 获取系统日志

获取系统操作日志

**路径:** `GET /system/logs`

**请求参数:**

| 参数名 | 类型    | 位置  | 描述                            | 必填 |
| ------ | ------- | ----- | ------------------------------- | ---- |
| level  | String  | Query | 日志级别 (info, warning, error) | 否   |
| limit  | Integer | Query | 返回的记录数，默认 20           | 否   |

**成功响应:** (200 OK)

```json
{
  "logs": [
    {
      "timestamp": "2024-04-05T15:10:00Z",
      "level": "info",
      "message": "File 'example.pdf' uploaded successfully",
      "component": "FileLoader"
    },
    {
      "timestamp": "2024-04-05T15:12:00Z",
      "level": "info",
      "message": "Created 15 chunks for file 'example.pdf'",
      "component": "ChunkEngine"
    },
    {
      "timestamp": "2024-04-05T15:14:00Z",
      "level": "info",
      "message": "Generated 15 vector embeddings using BGE-M3 model",
      "component": "EmbeddingEngine"
    }
  ]
}
```

## 管道执行 API

### 执行完整 RAG 管道

执行从文件上传到生成的完整 RAG 处理管道

**路径:** `POST /pipeline/execute`

**请求体:**

```json
{
  "file": <binary_data>,
  "filename": "example.pdf",
  "chunk_strategy": "sliding_window",
  "window_size": 512,
  "overlap": 128,
  "embedding_model": "bge-m3",
  "index_type": "hnsw"
}
```

**成功响应:** (200 OK)

```json
{
  "pipeline_id": "pl_9876543",
  "status": "completed",
  "steps": [
    {
      "step": "file_loading",
      "status": "completed",
      "file_id": "f1a3b5c7",
      "file_name": "example.pdf"
    },
    {
      "step": "chunking",
      "status": "completed",
      "chunk_count": 15
    },
    {
      "step": "embedding",
      "status": "completed",
      "vector_count": 15
    },
    {
      "step": "indexing",
      "status": "completed",
      "index_id": "idx_1234567"
    }
  ],
  "execution_time": 4.5
}
```

### 获取管道执行状态

获取异步管道执行的状态

**路径:** `GET /pipeline/{pipeline_id}`

**路径参数:**

| 参数名      | 类型   | 描述        | 必填 |
| ----------- | ------ | ----------- | ---- |
| pipeline_id | String | 管道执行 ID | 是   |

**成功响应:** (200 OK)

```json
{
  "pipeline_id": "pl_9876543",
  "status": "in_progress",
  "steps": [
    {
      "step": "file_loading",
      "status": "completed",
      "file_id": "f1a3b5c7",
      "file_name": "example.pdf"
    },
    {
      "step": "chunking",
      "status": "completed",
      "chunk_count": 15
    },
    {
      "step": "embedding",
      "status": "in_progress",
      "progress": 60
    },
    {
      "step": "indexing",
      "status": "pending"
    }
  ],
  "started_at": "2024-04-05T15:10:00Z",
  "elapsed_time": 2.3
}
```
