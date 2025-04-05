import { defineStore } from 'pinia';
import { computed, ref } from 'vue';

// Type definitions based on data-transfer-v0.0.1.md
interface FileMetadata {
  file_id: string;
  file_name: string;
  file_size: number;
  storage_path: string;
  created_at: string;
  loadingMethod?: string;
}

interface Chunk {
  chunk_id: string;
  file_id: string;
  content: string;
  start_offset: number;
  end_offset: number;
}

interface VectorRecord {
  id: string;
  chunk_id: string;
  file_id: string;
}

interface SearchLog {
  timestamp: string;
  query: string;
  top_chunks: string[];
  scores: { vector: number; bm25: number };
}

interface GenerationRecord {
  gen_id: string;
  query: string;
  used_chunks: string[];
  response: string;
  created_at: string;
}

interface QueryResult {
  query: string;
  retrievedChunks: Chunk[];
  generatedResponse: string;
  searchScores: { vector: number; bm25: number };
  timestamp: string;
}

export const useRagDataStore = defineStore('ragData', () => {
  // State
  const files = ref<FileMetadata[]>([]);
  const chunks = ref<Chunk[]>([]);
  const vectors = ref<VectorRecord[]>([]);
  const searchLogs = ref<SearchLog[]>([]);
  const generations = ref<GenerationRecord[]>([]);
  const latestQueryResult = ref<QueryResult | null>(null);

  // Settings
  const chunkSettings = ref({
    window_size: 512,
    overlap: 128,
    strategy: 'sliding_window'
  });

  const vectorSettings = ref({
    model: 'BGE-M3',
    dimensions: 768
  });

  const searchSettings = ref({
    vectorWeight: 0.6,
    bm25Weight: 0.4,
    topK: 5
  });

  // Computed
  const fileCount = computed(() => files.value.length);
  const chunkCount = computed(() => chunks.value.length);
  const vectorCount = computed(() => vectors.value.length);
  const searchCount = computed(() => searchLogs.value.length);
  const generationCount = computed(() => generations.value.length);

  // Get chunks for a specific file
  const getChunksForFile = (fileId: string) => {
    return chunks.value.filter(chunk => chunk.file_id === fileId);
  };

  // Generate a random ID
  const generateId = (prefix: string) => {
    return `${prefix}${Math.random().toString(36).substring(2, 10)}`;
  };

  // Initialize with mock data
  function initializeMockData() {
    // Sample files
    const sampleFiles: FileMetadata[] = [
      {
        file_id: 'f1a3b5c7',
        file_name: 'rag_guide.pdf',
        file_size: 1024 * 1024, // 1MB
        storage_path: './data/original/f1a3b5c7.pdf',
        created_at: '2024-04-01T10:30:00Z',
        loadingMethod: 'PyMuPDF'
      },
      {
        file_id: 'b2c4d6e8',
        file_name: 'embedding_models.pdf',
        file_size: 512 * 1024, // 512KB
        storage_path: './data/original/b2c4d6e8.pdf',
        created_at: '2024-04-02T14:45:00Z',
        loadingMethod: 'PyPDF'
      }
    ];

    // Sample chunks
    const sampleChunks: Chunk[] = [
      {
        chunk_id: 'c1b2a3d4',
        file_id: 'f1a3b5c7',
        content: 'RAG (Retrieval Augmented Generation) is an architecture that combines search capabilities with generative AI to produce accurate, relevant responses based on specific knowledge sources.',
        start_offset: 0,
        end_offset: 511
      },
      {
        chunk_id: 'd5e6f7a8',
        file_id: 'f1a3b5c7',
        content: 'The RAG workflow consists of several key components: document ingestion, chunking, embedding generation, vector storage, retrieval, and generation using LLMs.',
        start_offset: 384,
        end_offset: 895
      },
      {
        chunk_id: 'g7h8i9j0',
        file_id: 'b2c4d6e8',
        content: 'Embedding models transform text into vector representations. Popular models include OpenAI embeddings, BGE-M3, and BERT variants that create dense vector spaces.',
        start_offset: 0,
        end_offset: 511
      },
      {
        chunk_id: 'k1l2m3n4',
        file_id: 'b2c4d6e8',
        content: 'Vector similarity search uses distance metrics like cosine similarity or dot product to find the most relevant context for a given query.',
        start_offset: 384,
        end_offset: 895
      }
    ];

    // Sample vector records
    const sampleVectors: VectorRecord[] = [
      { id: 'v1b2c3d4', chunk_id: 'c1b2a3d4', file_id: 'f1a3b5c7' },
      { id: 'v5d6e7f8', chunk_id: 'd5e6f7a8', file_id: 'f1a3b5c7' },
      { id: 'v9g0h1i2', chunk_id: 'g7h8i9j0', file_id: 'b2c4d6e8' },
      { id: 'v3j4k5l6', chunk_id: 'k1l2m3n4', file_id: 'b2c4d6e8' }
    ];

    // Sample search logs
    const sampleSearchLogs: SearchLog[] = [
      {
        timestamp: '2024-04-05T09:15:00Z',
        query: 'What is RAG architecture?',
        top_chunks: ['c1b2a3d4', 'd5e6f7a8'],
        scores: { vector: 0.82, bm25: 0.75 }
      }
    ];

    // Sample generation records
    const sampleGenerations: GenerationRecord[] = [
      {
        gen_id: 'g1234567',
        query: 'What is RAG architecture?',
        used_chunks: ['c1b2a3d4', 'd5e6f7a8'],
        response: 'RAG (Retrieval Augmented Generation) is an architecture that combines search and generative AI. It works by retrieving relevant information from a knowledge base and then using that information to augment the generation process of large language models, producing more accurate and contextually relevant responses.',
        created_at: '2024-04-05T09:15:05Z'
      }
    ];

    // Set the initial state
    files.value = sampleFiles;
    chunks.value = sampleChunks;
    vectors.value = sampleVectors;
    searchLogs.value = sampleSearchLogs;
    generations.value = sampleGenerations;
  }

  // Add a new file
  const addFile = (fileInfo: Omit<FileMetadata, 'file_id' | 'created_at'> & { loadingMethod?: string }) => {
    const file_id = `file_${Date.now()}`;
    const fileData: FileMetadata = {
      ...fileInfo,
      file_id,
      created_at: new Date().toISOString(),
      loadingMethod: fileInfo.loadingMethod || 'PyMuPDF'
    };
    files.value.push(fileData);
    return file_id;
  };

  // Delete a file
  const deleteFile = (fileId: string) => {
    // Remove the file
    files.value = files.value.filter(file => file.file_id !== fileId);

    // Remove associated chunks
    chunks.value = chunks.value.filter(chunk => chunk.file_id !== fileId);

    // Remove associated vectors
    vectors.value = vectors.value.filter(vector => vector.file_id !== fileId);

    // Could also remove associated search logs and generations,
    // but we'll keep them for history purposes
  };

  // Create chunks for a file
  const createChunksForFile = (file: FileMetadata) => {
    // Remove all existing chunks for this file
    chunks.value = chunks.value.filter(chunk => chunk.file_id !== file.file_id);

    // Simulate generating 10-20 chunks for the file
    const numChunks = Math.floor(Math.random() * 11) + 10; // 10-20 chunks
    const newChunks = [];

    const mockText = "这是一个示例文本，用于模拟文档分块。这是RAG系统的一部分，我们正在实现文档分块功能。" +
                     "检索增强生成（RAG）结合了传统的检索系统和现代的生成式AI模型。" +
                     "在RAG工作流中，首先我们需要将文档分块，然后为每个块创建向量嵌入，" +
                     "最后使用这些嵌入来检索与用户查询最相关的文档部分。";

    for (let i = 0; i < numChunks; i++) {
      // Randomly generate chunk size between 50 and 200 characters
      const chunkSize = Math.floor(Math.random() * 151) + 50;
      const startPos = Math.floor(Math.random() * (mockText.length - chunkSize));
      const endPos = startPos + chunkSize;

      const chunk = {
        chunk_id: `${file.file_id}_chunk_${i+1}`,
        file_id: file.file_id,
        content: mockText.substring(startPos, endPos),
        metadata: {
          source: file.file_name,
          chunk_type: chunkSettings.value.strategy
        },
        start_offset: startPos,
        end_offset: endPos
      };

      newChunks.push(chunk);
    }

    // Add new chunks to the global chunks array
    chunks.value = [...chunks.value, ...newChunks];

    return newChunks;
  };

  // Execute a RAG query
  function performMockRagQuery(query: string) {
    // 1. Simulate search by finding chunks that might be relevant to the query
    // For mock purposes, just do a simple keyword match
    const queryKeywords = query.toLowerCase().split(/\s+/);

    const relevantChunks = chunks.value.filter(chunk => {
      const content = chunk.content.toLowerCase();
      return queryKeywords.some(keyword => content.includes(keyword));
    });

    // Sort by "relevance" - more keyword matches = higher relevance
    relevantChunks.sort((a, b) => {
      const scoreA = queryKeywords.filter(kw => a.content.toLowerCase().includes(kw)).length;
      const scoreB = queryKeywords.filter(kw => b.content.toLowerCase().includes(kw)).length;
      return scoreB - scoreA;
    });

    // Take top K chunks - ensure topK is treated as a number
    const topK = typeof searchSettings.value.topK === 'string'
      ? parseInt(searchSettings.value.topK)
      : searchSettings.value.topK;
    const topChunks = relevantChunks.slice(0, topK);
    const topChunkIds = topChunks.map(chunk => chunk.chunk_id);

    // 2. Create search log
    const vectorScore = 0.7 + Math.random() * 0.25; // Random score between 0.7-0.95
    const bm25Score = 0.65 + Math.random() * 0.25; // Random score between 0.65-0.9

    const searchLog: SearchLog = {
      timestamp: new Date().toISOString(),
      query,
      top_chunks: topChunkIds,
      scores: { vector: vectorScore, bm25: bm25Score }
    };

    searchLogs.value.push(searchLog);

    // 3. Generate a response
    let responseText = '';

    if (topChunks.length > 0) {
      // Create a response based on the retrieved chunks
      responseText = `Based on the available information, ${topChunks[0].content} `;

      if (topChunks.length > 1) {
        responseText += `Additionally, ${topChunks[1].content.toLowerCase()}`;
      }
    } else {
      responseText = "I couldn't find specific information about that in my knowledge base.";
    }

    // 4. Create generation record
    const generationRecord: GenerationRecord = {
      gen_id: generateId('g'),
      query,
      used_chunks: topChunkIds,
      response: responseText,
      created_at: new Date().toISOString()
    };

    generations.value.push(generationRecord);

    // 5. Update latest query result
    latestQueryResult.value = {
      query,
      retrievedChunks: topChunks,
      generatedResponse: responseText,
      searchScores: { vector: vectorScore, bm25: bm25Score },
      timestamp: new Date().toISOString()
    };

    return latestQueryResult.value;
  }

  // Return everything needed by the components
  return {
    // State
    files,
    chunks,
    vectors,
    searchLogs,
    generations,
    latestQueryResult,
    chunkSettings,
    vectorSettings,
    searchSettings,

    // Computed
    fileCount,
    chunkCount,
    vectorCount,
    searchCount,
    generationCount,

    // Actions
    initializeMockData,
    addFile,
    deleteFile,
    createChunksForFile,
    getChunksForFile,
    performMockRagQuery
  };
});