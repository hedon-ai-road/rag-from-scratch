# 数据结构与 API 接口设计方案

## 一、核心数据结构设计

### 1. 文件元数据（File Metadata）

```rust
struct FileMeta {
    file_id: String,       // UUIDv4
    file_name: String,
    file_type: String,     // "pdf" | "txt" | "md"
    file_size: u64,        // bytes
    hash_value: String,    // SHA-256
    upload_time: DateTime<Utc>,
    storage_path: String,  // 加密存储路径
    owner_id: String,      // 用户标识
    status: FileStatus,    // "uploaded" | "processing" | "processed"
}
```

### 2. 分块元数据（Chunk Metadata）

```rust
struct ChunkMeta {
    chunk_id: String,      // UUIDv4
    file_id: String,
    content: String,
    chunk_type: String,    // "window" | "semantic"
    start_offset: u32,
    end_offset: u32,
    overlap_size: u32,    // 仅滑动窗口分块有效
    model_version: String, // 分块模型标识
    created_at: DateTime<Utc>,
}
```

### 3. 向量存储结构（Vector Storage）

```rust
struct VectorRecord {
    vector_id: String,    // UUIDv4
    chunk_id: String,
    embedding: Vec<f32>,  // 量化后向量
    model_name: String,   // "BGE-M3-4bit"
    created_at: DateTime<Utc>,
    metadata: HashMap<String, String>, // 附加元数据
}
```

### 4. 检索上下文（Search Context）

```rust
struct SearchResult {
    chunk_id: String,
    score: f32,           // 综合相关性得分
    vector_score: f32,
    bm25_score: f32,
    highlight: Vec<(u32, u32)>, // 命中位置区间
    metadata: ChunkMeta,
}
```

## 二、API 接口设计规范

### 1. 文件管理接口

#### 1.1 文件上传

```http
POST /api/v1/files
Content-Type: multipart/form-data

Response:
{
    "file_id": "uuid",
    "hash_value": "sha256",
    "storage_path": "/encrypted/xxx",
    "expire_time": "2025-04-14T12:00:00Z"
}
```

#### 1.2 文件状态查询

```http
GET /api/v1/files/{file_id}/status

Response:
{
    "processing_stage": "chunking",
    "chunk_count": 42,
    "error_logs": []
}
```

### 2. 分块配置接口

#### 2.1 分块策略配置

```http
PUT /api/v1/chunking/config
Body:
{
    "strategy": "sliding_window",
    "window_size": 512,
    "overlap_size": 128,
    "semantic_model": "bert-base-chinese"
}

Response:
{
    "config_version": "v2.1",
    "effective_files": ["file_id1", "file_id2"]
}
```

### 3. 检索接口

#### 3.1 混合检索

```http
POST /api/v1/search
Body:
{
    "query": "RAG系统架构",
    "weights": {
        "vector": 0.6,
        "bm25": 0.4
    },
    "top_k": 5,
    "filter": {
        "file_types": ["pdf"],
        "time_range": ["2025-04-01", "2025-04-30"]
    }
}

Response:
{
    "results": [SearchResult],
    "search_id": "uuid",
    "latency_ms": 245
}
```

### 4. 生成控制接口

#### 4.1 Prompt 模板管理

```http
POST /api/v1/prompts
Body:
{
    "template_name": "qa_zh_concise",
    "template": "基于上下文：{context}\n请回答：{query}",
    "params": ["max_length": 500]
}

Response:
{
    "version_hash": "a1b2c3",
    "validation_result": {
        "placeholder_check": true,
        "syntax_check": true
    }
}
```

### 5. 监控接口

#### 5.1 流水线监控

```http
GET /api/v1/pipeline/status
QueryParams:
    scope=all | file_id=xxx

Response:
{
    "stages": [
        {
            "stage_name": "chunking",
            "processed_files": 15,
            "avg_duration": "12.5s",
            "error_rate": 0.02
        }
    ],
    "resource_usage": {
        "cpu": 65.2,
        "memory_mb": 2048
    }
}
```

## 三、设计原则说明

### 1. 模块化设计

- 每个 API 端点对应一个功能模块（文件/分块/检索等）
- 请求响应体包含完整的上下文信息
- 错误代码分层设计：
  ```json
  {
    "code": "FILE-001",
    "message": "文件大小超过限制",
    "detail": "当前文件大小：55MB，最大限制：50MB"
  }
  ```

### 2. 可扩展性保障

- 所有 ID 字段使用 UUIDv4
- 元数据字段采用键值对存储（HashMap<String, String>）
- 版本控制字段：
  ```rust
  struct VersionInfo {
      major: u8,
      minor: u8,
      patch: u8,
      commit_hash: String
  }
  ```

### 3. 一致性规范

- 时间格式统一使用 ISO8601 标准
- 数值精度统一保留 3 位小数
- 分页参数标准化：
  ```http
  GET /api/v1/files?page=2&page_size=20
  ```

### 4. 安全性设计

- 文件上传限制：
  ```rust
  const MAX_FILE_SIZE: u64 = 50 * 1024 * 1024; // 50MB
  const ALLOWED_MIME_TYPES: [&str] = ["application/pdf", "text/plain"];
  ```
- JWT 认证头：
  ```http
  Authorization: Bearer <token>
  ```
