# RAG 全流程数据流转详解（MVP 简化版）

## 一、核心流程总览

```mermaid
graph LR
    A[文件上传] -->|原始文件| B[分块处理]
    B -->|文本分块| C[向量转换]
    C -->|向量数据| D[混合检索]
    D -->|相关分块| E[生成回答]
    E -->|问答记录| F[监控反馈]

    style A fill:#FAD7A0,stroke:#E67E22
    style B fill:#ABEBC6,stroke:#2ECC71
    style C fill:#AED6F1,stroke:#3498DB
    style D fill:#D2B4DE,stroke:#9B59B6
    style E fill:#F5B7B1,stroke:#E74C3C
    style F fill:#CCD1D1,stroke:#95A5A6
```

## 二、详细数据流转说明

### 1. 文件上传阶段

```mermaid
graph LR
    A[用户上传PDF/TXT] --> B{文件检查}
    B -->|通过| C[保存原始文件]
    B -->|拒绝| D[返回错误]
    C --> E[记录元数据]

    style C fill:#FAD7A0
    style E fill:#ABEBC6
```

**数据存储实现**：

```bash
# 本地存储结构
./data/
├── original/  # 原始文件存储
│   └── f1a3b5c7.pdf
└── chunks/     # 分块存储（可选）
```

```sql
/* SQLite文件表结构 */
CREATE TABLE files (
    file_id TEXT PRIMARY KEY,
    file_name TEXT NOT NULL,
    file_size INTEGER CHECK(file_size < 52428800), -- 50MB限制
    storage_path TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 2. 分块处理阶段

```mermaid
graph LR
    A[读取原始文件] --> B[滑动窗口分块]
    B --> C[生成分块元数据]
    C --> D[存储分块内容]

    style B fill:#D5F5E3
    style D fill:#D6EAF8
```

**分块参数示例**：

```python
{
    "window_size": 512,  # 字符数
    "overlap": 128,      # 重叠字符
    "strategy": "sliding_window"
}
```

**数据存储实现**：

```sql
/* 分块表结构 */
CREATE TABLE chunks (
    chunk_id TEXT PRIMARY KEY,
    file_id TEXT NOT NULL,
    content TEXT NOT NULL,
    start_offset INTEGER CHECK(start_offset >= 0),
    end_offset INTEGER CHECK(end_offset > start_offset),
    FOREIGN KEY(file_id) REFERENCES files(file_id)
);
```

### 3. 向量转换阶段

```mermaid
graph LR
    A[分块文本] --> B[BGE-M3模型]
    B --> C[生成768维向量]
    C --> D[Qdrant存储]

    style B fill:#D6EAF8
    style D fill:#D2B4DE
```

**向量存储结构**：

```bash
# Qdrant本地存储
qdrant/
└── collections/
    └── rag_collection/
        ├── data/          # 向量数据
        └── payload/       # 元数据关联
```

**向量记录示例**：

```json
{
    "id": "v1b2c3d4",
    "vector": [0.12, -0.34, ..., 0.56],
    "payload": {
        "chunk_id": "c1b2a3d4",
        "file_id": "f1a3b5c7"
    }
}
```

### 4. 混合检索阶段

```mermaid
graph LR
    A[用户查询] --> B[向量检索]
    A --> C[BM25检索]
    B & C --> D[结果融合]
    D --> E[Top5分块]

    style B fill:#D2B4DE
    style C fill:#F5B7B1
    style D fill:#ABEBC6
```

**检索日志存储**：

```bash
# 检索日志示例
./logs/search/2024-04-25.log
```

```json
{
  "timestamp": "2024-04-25T14:30:00Z",
  "query": "RAG架构原理",
  "top_chunks": ["c1b2a3d4", "d5e6f7a8"],
  "scores": { "vector": 0.82, "bm25": 0.75 }
}
```

### 5. 生成回答阶段

```mermaid
graph LR
    A[相关分块] --> B[构建Prompt]
    B --> C[Mistral-7B生成]
    C --> D[返回回答]

    style B fill:#FAD7A0
    style C fill:#D5F5E3
```

**生成记录存储**：

```sql
/* 生成记录表 */
CREATE TABLE generations (
    gen_id TEXT PRIMARY KEY,
    query TEXT NOT NULL,
    used_chunks TEXT NOT NULL,  -- JSON数组
    response TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## 三、完整数据流转示例

```mermaid
sequenceDiagram
    participant 用户
    participant 系统
    participant 本地存储

    用户->>系统: 上传rag_guide.pdf
    系统->>本地存储: 保存至/data/original/f1a3b5c7.pdf
    系统->>SQLite: 记录文件元数据
    系统->>分块处理: 生成12个分块
    系统->>SQLite: 记录分块元数据
    系统->>Qdrant: 存储向量数据
    用户->>系统: 查询"RAG架构组件"
    系统->>Qdrant: 执行向量检索
    系统->>Tantivy: 执行BM25检索
    系统->>结果融合: 权重计算0.6*向量+0.4*BM25
    系统->>Mistral-7B: 生成最终回答
    系统->>SQLite: 记录生成结果
    系统->>用户: 返回回答内容
```

## 四、本地存储全景图

```bash
项目根目录/
├── data/
│   ├── original/       # 原始文件（PDF/TXT）
│   ├── chunks/         # 分块文本（可选）
│   └── generations/    # 生成结果缓存
├── qdrant/             # 向量数据库存储
│   └── collections/
├── logs/               # 系统日志
│   ├── search/
│   └── pipeline/
└── rag.db              # SQLite主数据库
```

## 五、关键数据结构对照表

| 数据类型   | 存储位置              | 示例标识       | 关联关系      |
| ---------- | --------------------- | -------------- | ------------- |
| 原始文件   | ./data/original/      | f1a3b5c7.pdf   | → 分块        |
| 分块元数据 | SQLite chunks 表      | c1b2a3d4       | ← 文件 → 向量 |
| 向量数据   | Qdrant 集合           | v1b2c3d4       | ← 分块 → 检索 |
| 检索日志   | ./logs/search/        | 2024-04-25.log | ← 查询 → 分块 |
| 生成记录   | SQLite generations 表 | g1234567       | ← 分块 → 回答 |

本方案完整呈现了从文件上传到生成回答的数据流转过程，所有数据均存储在本地且无需加密处理，适合 MVP 阶段快速验证核心流程。后续扩展时可逐步添加安全模块和分布式存储支持。
