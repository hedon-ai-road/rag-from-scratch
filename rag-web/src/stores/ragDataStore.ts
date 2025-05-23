import { defineStore } from 'pinia';
import { computed, ref } from 'vue';
import { fileService } from '../services/api';

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
  const files = ref<any[]>([]);
  const chunks = ref<any[]>([]);
  const vectors = ref<any[]>([]);
  const searches = ref<any[]>([]);
  const generations = ref<any[]>([]);
  const loading = ref({
    files: false,
    chunks: false,
    vectors: false,
    searches: false,
    generations: false
  });
  const error = ref({
    files: null,
    chunks: null,
    vectors: null,
    searches: null,
    generations: null
  });

  // File type support state
  const supportedFileTypes = ref<string[]>([]);
  const loadingMethods = ref<{ [key: string]: string[] }>({});
  const loadingSupportedTypes = ref(false);
  const supportedTypesError = ref<string | null>(null);

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
  const searchCount = computed(() => searches.value.length);
  const generationCount = computed(() => generations.value.length);

  // Get chunks for a specific file
  const getChunksForFile = (fileId: string) => {
    return chunks.value.filter(chunk => chunk.file_id === fileId);
  };

  // Generate a random ID
  const generateId = (prefix: string) => {
    return `${prefix}${Math.random().toString(36).substring(2, 10)}`;
  };

  // Actions
  const fetchFiles = async (page = 1, limit = 10) => {
    loading.value.files = true;
    error.value.files = null;

    try {
      const response = await fileService.getAllFiles(page, limit);
      if (response.code === 0) {
        files.value = response.data.files;
      } else {
        error.value.files = response.message;
      }
    } catch (err: any) {
      error.value.files = err.message || 'Failed to fetch files';
      console.error('Error fetching files:', err);
    } finally {
      loading.value.files = false;
    }
  };

  const addFile = async (file: File, loadingMethod: string) => {
    loading.value.files = true;
    error.value.files = null;

    try {
      const response = await fileService.uploadFile(file, loadingMethod);
      console.log('Upload file API response:', response);

      if (response.code === 0) {
        // Ensure we keep the loadingMethod that was used during upload
        const fileData = response.data.file;
        // If the API returns a different loadingMethod than what we sent, override it
        if (fileData.loadingMethod !== loadingMethod) {
          console.warn(`API returned loading method '${fileData.loadingMethod}' but we used '${loadingMethod}'`);
          fileData.loadingMethod = loadingMethod;
        }

        // Ensure the file_name is used as the display name instead of file_id
        if (fileData.file_name) {
          // The file_name property may already be set correctly by the backend
          console.log(`File name from API: ${fileData.file_name}`);
        } else {
          // If not set, use the original file name
          fileData.file_name = file.name;
          console.log(`Setting file name to: ${fileData.file_name}`);
        }

        files.value.unshift(fileData);
        return fileData.file_id;
      } else {
        error.value.files = response.message;
        return null;
      }
    } catch (err: any) {
      error.value.files = err.response.data.detail || err.message || 'Failed to upload file';
      console.error('Error uploading file:', err);
      return null;
    } finally {
      loading.value.files = false;
    }
  };

  const getFile = async (fileId: string) => {
    loading.value.files = true;
    error.value.files = null;

    try {
      const response = await fileService.getFile(fileId);
      console.log('Get file API response:', response);

      if (response.code === 0) {
        // Find the file in our local cache to get the correct loading method
        const cachedFile = files.value.find(f => f.file_id === fileId);
        if (cachedFile && response.data.file) {
          // Use the loading method from our cache if available
          response.data.file.loadingMethod = cachedFile.loadingMethod || response.data.file.loadingMethod;
        }

        // Make sure docs is properly formed
        if (response.data.file) {
          // Check if docs exists
          if (!response.data.file.docs) {
            console.warn('No docs found in API response, initializing empty array');
            response.data.file.docs = [];
          }
          // If docs is not an array, convert it to one
          else if (!Array.isArray(response.data.file.docs)) {
            console.warn('docs is not an array, converting to array');
            response.data.file.docs = [response.data.file.docs];
          }

          // Validate each document in the docs array
          if (Array.isArray(response.data.file.docs)) {
            console.log(`Response has ${response.data.file.docs.length} documents`);

            // Make sure each doc has the expected structure
            response.data.file.docs = response.data.file.docs.map((doc: any, index: number) => {
              // Ensure metadata exists
              if (!doc.metadata) {
                console.warn(`Document ${index} has no metadata, initializing empty object`);
                doc.metadata = {};
              }
              // Ensure page_content exists
              if (!doc.page_content) {
                console.warn(`Document ${index} has no page_content, initializing empty string`);
                doc.page_content = '';
              }
              return doc;
            });
          }
        }

        return response;
      } else {
        error.value.files = response.message;
        return null;
      }
    } catch (err: any) {
      error.value.files = err.message || 'Failed to get file';
      console.error(`Error getting file ${fileId}:`, err);
      return null;
    } finally {
      loading.value.files = false;
    }
  };

  const deleteFile = async (fileId: string) => {
    loading.value.files = true;
    error.value.files = null;

    try {
      const response = await fileService.deleteFile(fileId);
      if (response.code === 0) {
        files.value = files.value.filter(file => file.file_id !== fileId);
        return true;
      } else {
        error.value.files = response.message;
        return false;
      }
    } catch (err: any) {
      error.value.files = err.message || 'Failed to delete file';
      console.error(`Error deleting file ${fileId}:`, err);
      return false;
    } finally {
      loading.value.files = false;
    }
  };

  // Initialize by fetching data
  const initialize = async () => {
    await Promise.all([
      fetchFiles(),
      fetchSupportedFileTypes()
    ]);
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

    searches.value.push(searchLog);

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
    const latestQueryResult: QueryResult = {
      query,
      retrievedChunks: topChunks,
      generatedResponse: responseText,
      searchScores: { vector: vectorScore, bm25: bm25Score },
      timestamp: new Date().toISOString()
    };

    return latestQueryResult;
  }

  // Fetch supported file types and loading methods
  const fetchSupportedFileTypes = async () => {
    loadingSupportedTypes.value = true;
    supportedTypesError.value = null;

    try {
      const response = await fileService.getSupportedFileTypes();
      if (response.code === 0) {
        supportedFileTypes.value = response.data.allowed_file_types || [];
        loadingMethods.value = response.data.supported_types || {};
        console.log('Loaded supported file types:', supportedFileTypes.value);
        console.log('Loaded loading methods:', loadingMethods.value);
      } else {
        supportedTypesError.value = response.message;
        console.error('Error loading supported file types:', response.message);
      }
    } catch (err: any) {
      supportedTypesError.value = err.message || 'Failed to fetch supported file types';
      console.error('Error fetching supported file types:', err);
    } finally {
      loadingSupportedTypes.value = false;
    }
  };

  // Get loading methods for a specific file type
  const getLoadingMethodsForFileType = async (fileType: string) => {
    try {
      const response = await fileService.getLoadingMethodsForFileType(fileType);
      if (response.code === 0) {
        return response.data.loading_methods || [];
      } else {
        console.error(`Error getting loading methods for ${fileType}:`, response.message);
        return [];
      }
    } catch (err: any) {
      console.error(`Error fetching loading methods for ${fileType}:`, err);
      return [];
    }
  };

  // Get file extension from filename
  const getFileExtension = (filename: string): string => {
    const lastDot = filename.lastIndexOf('.');
    if (lastDot === -1) return '';
    return filename.substring(lastDot + 1).toLowerCase();
  };

  // Check if file type is supported
  const isFileTypeSupported = (filename: string): boolean => {
    const extension = getFileExtension(filename);
    return supportedFileTypes.value.includes(extension);
  };

  // Return everything needed by the components
  return {
    // State
    files,
    chunks,
    vectors,
    searches,
    generations,
    loading,
    error,
    chunkSettings,
    vectorSettings,
    searchSettings,

    // File type support state
    supportedFileTypes,
    loadingMethods,
    loadingSupportedTypes,
    supportedTypesError,

    // Computed
    fileCount,
    chunkCount,
    vectorCount,
    searchCount,
    generationCount,

    // Actions
    fetchFiles,
    addFile,
    getFile,
    deleteFile,
    createChunksForFile,
    getChunksForFile,
    performMockRagQuery,
    initialize,
    fetchSupportedFileTypes,
    getLoadingMethodsForFileType,
    isFileTypeSupported,
    getFileExtension
  };
});