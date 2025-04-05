# 概要设计说明书

> Deepseek 对话：https://yuanbao.tencent.com/bot/app/share/chat/11aZQpEBChKV

### 一、系统架构设计

#### 1. 功能模块拆分（导航栏项）

| 模块名称             | 核心功能                                                        | 技术实现                                               |
| -------------------- | --------------------------------------------------------------- | ------------------------------------------------------ |
| **File Loader**      | 支持 PDF/TXT/Markdown 上传，记录文件元数据（大小/类型/哈希值）  | Tauri 文件系统 API + SQLite 记录（网页 1）             |
| **Chunk Engine**     | 分块策略可视化配置（滑动窗口/语义分块），支持重叠设置与分块预览 | Rust 语义分块（BERT 模型） + 分块元数据存储（网页 10） |
| **Parser Studio**    | 实体关系提取（NER/RE）、表格结构化处理、文档版本管理            | 异步 LLM 处理（DeepSeek-7B） + 知识图谱存储（网页 1）  |
| **Embedding Lab**    | 嵌入模型选择（BGE/OpenAI）、向量维度可视化、嵌入质量评估        | 本地量化模型（rust-bert） + 向量快照存储（网页 9）     |
| **Vector Indexer**   | 索引策略配置（HNSW/IVF-PQ）、增量更新、索引性能监控             | Qdrant 索引 API + 索引版本管理（网页 10）              |
| **Search Console**   | 混合检索调试（BM25/向量权重）、检索结果溯源、命中片段高亮       | 权重调节面板 + 结果关联图谱（网页 11）                 |
| **Generator Hub**    | Prompt 模板编辑、生成过程追溯、响应置信度评分                   | Mistral-7B 流式生成 + 生成日志记录（网页 9）           |
| **Pipeline Monitor** | 全链路追踪（耗时/资源消耗）、错误日志分析、数据血缘可视化       | OpenTelemetry 埋点 + 时序数据库（网页 8）              |

#### 2. 数据流设计

```mermaid
graph LR
    A[File Loader] -->|原始文件| B[Chunk Engine]
    B -->|分块数据| C[Parser Studio]
    C -->|结构化数据| D[Embedding Lab]
    D -->|向量数据| E[Vector Indexer]
    E -->|索引快照| F[Search Console]
    F -->|检索上下文| G[Generator Hub]
    G -->|生成结果| H[Pipeline Monitor]
```

### 二、核心功能实现

#### 1. 阶段数据存储方案

| 阶段           | 存储形式                                                             | 技术方案                                 |
| -------------- | -------------------------------------------------------------------- | ---------------------------------------- |
| **原始文件**   | 存储至`./data/original/[file_hash]`                                  | 哈希校验                                 |
| **分块数据**   | SQLite 表`chunks`（字段：chunk_id/text/start_pos/end_pos/file_hash） | 位置回溯 + 分块可视化（网页 1 分块策略） |
| **结构化数据** | Neo4j 图数据库（实体/关系） + CSV 导出                               | 知识图谱可视化（网页 1 实体提取）        |
| **向量数据**   | Qdrant 集合 + 本地备份`*.vecbin`                                     | 向量版本控制（网页 10 索引优化）         |
| **检索上下文** | JSON 日志（含检索参数/命中分块/相关性得分）                          | 检索过程回放（网页 8 评估指标）          |
| **生成过程**   | Markdown 日志（原始 Prompt/生成 Token/置信度）                       | 生成溯源（网页 9 可控生成）              |
| **前端**       |                                                                      | Tauri2.0 + Vue + Taliwind CSS            |

#### 2. 前端交互设计

- **分块可视化**：
  使用`monaco-editor`展示文本分块，支持：

  - 颜色标记不同分块类型（标题/正文/表格）
  - 滑动窗口重叠区域半透明高亮
  - 点击分块查看关联的嵌入向量（3D PCA 降维展示）

- **检索调试台**：
  开发混合检索模拟器：

  ```javascript
  // 伪代码示例
  const search = (query) => {
    const vectorResults = qdrant.search(queryVector);
    const keywordResults = tantivy.search(queryKeywords);
    return rerank(mergeResults(vectorResults, keywordResults));
  };
  ```

  支持实时调节 BM25/向量权重滑块（0-1），观察 Top-K 结果变化

- **数据血缘图**：
  用`cytoscape.js`绘制数据流转关系：

  ```markdown
  [原始文件] → [分块 A] → [实体 X] → [向量 V1]
  [分块 B] → [表格 T1] → [向量 V2]
  ```

  点击节点可下钻查看处理日志

### 三、关键技术实现

#### 1. 阶段衔接机制

- 文件指纹追踪

  每个处理阶段添加元数据：

  ```rust
  struct ChunkMeta {
      file_hash: String,  // 原始文件哈希
      chunk_id: u64,      // 分块序列号
      parser_version: String, // 解析器版本
      embed_model: String // 嵌入模型标识
  }
  ```

  通过 `file_hash` 实现全链路追溯（网页 10 元数据增强）

#### 2. 中断与续作

- 断点续传

  每个阶段完成后写入状态标记：

  ```sql
  INSERT INTO pipeline_status
  (stage_name, input_hash, output_path, status)
  VALUES ('chunking', 'a1b2c3', '/data/chunks/001', 'completed');
  ```

  中断后可从最近成功阶段继续（网页 5 流程编排）

#### 3. 可观测性增强

- 质量评估面板

  计算各阶段核心指标：

  | 阶段 | 评估指标                  | 计算方式                           |
  | ---- | ------------------------- | ---------------------------------- |
  | 分块 | 块内信息熵 / 块间相似度   | KL 散度计算（网页 8 检索质量评估） |
  | 嵌入 | 向量分布密度 / 最近邻距离 | UMAP 可视化（网页 9 嵌入优化）     |
  | 检索 | MRR@10 / Recall@5         | TREC 评估协议（网页 8 评估体系）   |
  | 生成 | 幻觉率 / 事实一致性       | NLI 模型检测（网页 10 可控生成）   |

### 四、实施建议

1. **增量开发路线**
   - Phase 1：实现基础管道（File Loader → Chunk → Embed → Search）
   - Phase 2：添加 Parser Studio 与 Generator Hub
   - Phase 3：构建监控与可视化子系统
2. **学习型功能设计**
   - 在每个阶段界面添加"原理卡片"（如分块策略算法图示）
   - 提供"对比实验"模式，可并行运行不同参数配置（如 128 vs 256 分块大小）
3. **调试工具集成**
   - 开发 `Pipeline Debugger`，支持：
     - 注入测试数据到任意阶段
     - 单步执行观察中间状态
     - 数据快照导出/导入
