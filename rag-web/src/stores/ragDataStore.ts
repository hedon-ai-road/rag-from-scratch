import { defineStore } from 'pinia';

// --- Interfaces based on data-transfer-v0.0.1.md ---
interface FileRecord {
  file_id: string;
  file_name: string;
  file_size: number;
  storage_path: string;
  created_at: string;
}

interface ChunkRecord {
  chunk_id: string;
  file_id: string;
  content: string;
  start_offset: number;
  end_offset: number;
}

interface VectorRecord {
  id: string;
  vector: number[]; // Simplified for mock
  payload: {
    chunk_id: string;
    file_id: string;
  };
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
  used_chunks: string[]; // JSON array string in doc, array here
  response: string;
  created_at: string;
}

// --- Store Definition ---
export const useRagDataStore = defineStore('ragData', {
  state: () => ({
    files: [] as FileRecord[],
    chunks: [] as ChunkRecord[],
    vectors: [] as VectorRecord[],
    searchLogs: [] as SearchLog[],
    generations: [] as GenerationRecord[],
    // --- Mock Data Initialization ---
    _initialized: false, // Flag to prevent re-initialization
  }),

  getters: {
    // Example getter: Get chunks for a specific file
    getChunksByFileId: (state) => {
      return (fileId: string) => state.chunks.filter(chunk => chunk.file_id === fileId);
    },
    // Example getter: Get file record by ID
    getFileById: (state) => {
       return (fileId: string) => state.files.find(file => file.file_id === fileId);
    }
  },

  actions: {
    // Action to add a new file (like after upload)
    addFile(file: Omit<FileRecord, 'file_id' | 'created_at' | 'storage_path'>) {
      const newFile: FileRecord = {
        ...file,
        file_id: `f${Date.now().toString(36)}${Math.random().toString(36).substring(2, 5)}`, // Mock ID
        storage_path: `./data/original/${file.file_name}`, // Mock path
        created_at: new Date().toISOString(),
      };
      this.files.push(newFile);
      console.log('Added mock file:', newFile);
      // Simulate subsequent pipeline stages (chunking, embedding)
      this.mockProcessNewFile(newFile);
    },

    // Simulate processing steps for a new file
    mockProcessNewFile(file: FileRecord) {
      console.log(`Mock processing for file: ${file.file_name}`);

      // 1. Mock Chunking
      const mockContent = `This is the simulated content for ${file.file_name}. It is divided into several chunks for demonstration purposes. Chunk 1 ends here. This is the start of chunk 2 which overlaps. Chunk 2 ends. Finally, chunk 3 starts here and finishes the document.`;
      const chunkSize = 100;
      const overlap = 20;
      let offset = 0;
      let chunkIndex = 0;
      while (offset < mockContent.length) {
          const start = Math.max(0, offset - overlap);
          const end = Math.min(mockContent.length, offset + chunkSize);
          const newChunk: ChunkRecord = {
              chunk_id: `c${file.file_id.substring(1)}-${chunkIndex++}`,
              file_id: file.file_id,
              content: mockContent.substring(start, end),
              start_offset: start,
              end_offset: end,
          };
          this.chunks.push(newChunk);
          console.log('Added mock chunk:', newChunk);

           // 2. Mock Embedding for the chunk
           const newVector: VectorRecord = {
              id: `v${newChunk.chunk_id.substring(1)}`,
              vector: Array.from({ length: 768 }, () => Math.random() * 2 - 1), // Random 768d vector
              payload: {
                  chunk_id: newChunk.chunk_id,
                  file_id: newChunk.file_id,
              }
           };
           this.vectors.push(newVector);
           console.log('Added mock vector:', newVector);

          if (end === mockContent.length) break;
          offset += chunkSize - overlap; // Move window forward
      }

      // 3. Mock Search Log Entry (example)
      const newSearchLog: SearchLog = {
        timestamp: new Date().toISOString(),
        query: `Initial analysis of ${file.file_name}`,
        top_chunks: this.chunks.filter(c => c.file_id === file.file_id).slice(0, 2).map(c => c.chunk_id),
        scores: { vector: Math.random() * 0.5 + 0.5, bm25: Math.random() * 0.5 + 0.4 },
      };
      this.searchLogs.push(newSearchLog);
      console.log('Added mock search log:', newSearchLog);

      // 4. Mock Generation Entry (example)
      const newGeneration: GenerationRecord = {
          gen_id: `g${Date.now().toString(36)}`,
          query: newSearchLog.query,
          used_chunks: newSearchLog.top_chunks,
          response: `Based on the initial analysis of ${file.file_name}, the key themes appear to be X and Y.`,
          created_at: new Date().toISOString(),
      };
      this.generations.push(newGeneration);
      console.log('Added mock generation:', newGeneration);
    },

    // Initialize with some default data if the store is empty
    initializeMockData() {
      if (this._initialized || this.files.length > 0) return; // Only run once
      console.log("Initializing mock RAG data...");
      this.addFile({ file_name: 'rag_guide.pdf', file_size: 1024 * 500 }); // 500 KB
      this.addFile({ file_name: 'meeting_notes.txt', file_size: 1024 * 20 }); // 20 KB
      this._initialized = true;
    }
  }
});