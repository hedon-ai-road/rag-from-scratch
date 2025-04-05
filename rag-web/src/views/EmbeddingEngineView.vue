<template>
  <div>
    <h1 class="text-2xl font-semibold mb-4">Embedding File</h1>

    <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
      <!-- Embedding Configuration -->
      <div class="card">
        <h2 class="mb-4 text-lg font-semibold">Generate Embeddings</h2>

        <div class="mb-4">
          <label class="mb-2 block text-sm font-medium text-gray-700">Select Chunked Document</label>
          <select
            v-model="selectedFileId"
            class="input w-full"
            @change="onFileSelect"
          >
            <option value="">Choose a document...</option>
            <option
              v-for="file in chunkableFiles"
              :key="file.file_id"
              :value="file.file_id"
              :disabled="!hasChunks(file.file_id)"
            >
              {{ file.file_name }} {{ !hasChunks(file.file_id) ? '(No chunks available)' : '' }}
            </option>
          </select>
          <p class="mt-1 text-sm text-gray-500" v-if="selectedFile">
            {{ getChunkCount(selectedFileId) }} chunks available
          </p>
        </div>

        <div class="mb-4">
          <label class="mb-2 block text-sm font-medium text-gray-700">Embedding Provider</label>
          <select v-model="embeddingProvider" class="input w-full">
            <option value="OpenAI">OpenAI</option>
            <option value="BGE">BGE</option>
            <option value="HuggingFace">HuggingFace</option>
            <option value="SentenceTransformers">SentenceTransformers</option>
          </select>
        </div>

        <div class="mb-4">
          <label class="mb-2 block text-sm font-medium text-gray-700">Embedding Model</label>
          <select v-model="embeddingModel" class="input w-full">
            <template v-if="embeddingProvider === 'OpenAI'">
              <option value="text-embedding-3-small">text-embedding-3-small (1536 dim)</option>
              <option value="text-embedding-3-large">text-embedding-3-large (3072 dim)</option>
              <option value="text-embedding-ada-002">text-embedding-ada-002 (legacy)</option>
            </template>

            <template v-else-if="embeddingProvider === 'BGE'">
              <option value="bge-small-en-v1.5">BGE Small English v1.5 (384 dim)</option>
              <option value="bge-base-en-v1.5">BGE Base English v1.5 (768 dim)</option>
              <option value="bge-large-en-v1.5">BGE Large English v1.5 (1024 dim)</option>
              <option value="bge-m3">BGE-M3 (1024 dim)</option>
            </template>

            <template v-else-if="embeddingProvider === 'HuggingFace'">
              <option value="sentence-transformers/all-MiniLM-L6-v2">all-MiniLM-L6-v2 (384 dim)</option>
              <option value="BAAI/bge-small-en-v1.5">BGE Small via HF (384 dim)</option>
            </template>

            <template v-else-if="embeddingProvider === 'SentenceTransformers'">
              <option value="all-mpnet-base-v2">all-mpnet-base-v2 (768 dim)</option>
              <option value="multi-qa-mpnet-base-dot-v1">multi-qa-mpnet-base-dot-v1 (768 dim)</option>
            </template>
          </select>
        </div>

        <div>
          <button
            class="btn btn-primary w-full"
            @click="generateEmbeddings"
            :disabled="!canGenerateEmbeddings"
          >
            Generate Embeddings
          </button>
        </div>

        <div v-if="processingStatus" class="mt-4 p-3" :class="statusClass">
          {{ processingStatus }}
        </div>
      </div>

      <!-- Embeddings Preview and Management -->
      <div class="card">
        <div class="border-b mb-4">
          <div class="flex">
            <button
              @click="activeTab = 'preview'"
              class="px-4 py-2 font-medium border-b-2 transition-colors"
              :class="activeTab === 'preview' ? 'border-blue-500 text-blue-600' : 'border-transparent hover:border-gray-300'"
            >
              Embeddings Preview
            </button>
            <button
              @click="activeTab = 'management'"
              class="px-4 py-2 font-medium border-b-2 transition-colors"
              :class="activeTab === 'management' ? 'border-blue-500 text-blue-600' : 'border-transparent hover:border-gray-300'"
            >
              Embedding Management
            </button>
          </div>
        </div>

        <!-- Embeddings Preview Tab -->
        <div v-if="activeTab === 'preview'">
          <div v-if="!selectedFileId || !vectors.length" class="text-gray-500 text-center py-8">
            {{ selectedFileId ? 'No embeddings found. Generate embeddings first.' : 'Select a document to view embeddings' }}
          </div>

          <div v-else>
            <h3 class="font-medium text-lg mb-2">{{ selectedFile?.file_name }} - {{ vectors.length }} Vectors</h3>

            <div class="rounded bg-gray-50 p-4 h-96 overflow-y-auto">
              <div class="mb-3">
                <h4 class="font-medium">Embedding Visualization (First 10 dimensions)</h4>
                <div class="bg-white p-3 rounded border mt-2">
                  <div
                    v-for="(vector, index) in vectors.slice(0, 3)"
                    :key="vector.id"
                    class="mb-2 last:mb-0"
                  >
                    <div class="flex justify-between text-sm mb-1">
                      <span class="font-medium text-blue-600">Vector {{ index + 1 }}</span>
                      <span class="text-gray-500">Chunk ID: {{ vector.chunk_id }}</span>
                    </div>
                    <div class="h-6 bg-gray-200 rounded overflow-hidden flex">
                      <div
                        v-for="(value, i) in generateMockEmbedding(10)"
                        :key="i"
                        class="h-full"
                        :style="{
                          width: `${Math.abs(value) * 100}px`,
                          backgroundColor: value > 0 ? '#3B82F6' : '#EF4444',
                          opacity: 0.6 + Math.abs(value) * 0.4
                        }"
                      ></div>
                    </div>
                  </div>
                </div>
              </div>

              <div>
                <h4 class="font-medium">Associated Chunks</h4>
                <div v-for="(chunk, index) in previewChunks.slice(0, 3)" :key="chunk.chunk_id" class="mt-2 p-3 border rounded">
                  <div class="flex justify-between text-sm mb-1">
                    <span class="font-medium">Chunk {{ index + 1 }}</span>
                    <span class="text-gray-500">ID: {{ chunk.chunk_id }}</span>
                  </div>
                  <p class="text-sm">{{ chunk.content }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Embedding Management Tab -->
        <div v-if="activeTab === 'management'">
          <div v-if="store.files.length === 0" class="text-gray-500 text-center py-8">
            No documents available. Upload and chunk documents first.
          </div>

          <ul v-else class="divide-y">
            <li v-for="file in store.files" :key="file.file_id" class="py-3">
              <div class="flex items-center justify-between">
                <div>
                  <p class="font-medium">{{ file.file_name }}</p>
                  <p class="text-sm text-gray-500">
                    Chunks: {{ getChunkCount(file.file_id) }} |
                    Vectors: {{ getVectorCount(file.file_id) }}
                  </p>
                </div>
                <div class="flex space-x-2">
                  <button
                    class="rounded-lg px-3 py-1 text-sm text-blue-600 hover:bg-blue-50"
                    @click="selectFile(file.file_id)"
                    :disabled="!hasChunks(file.file_id)"
                  >
                    Select
                  </button>
                </div>
              </div>
            </li>
          </ul>
        </div>
      </div>
    </div>

    <!-- Embedding Stats -->
    <div class="mt-6 card" v-if="vectors.length > 0">
      <h2 class="mb-4 text-lg font-semibold">Embedding Statistics</h2>

      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div class="rounded bg-blue-50 p-4">
          <p class="text-sm text-blue-700">Total Vectors</p>
          <p class="text-2xl font-semibold text-blue-800">{{ vectors.length }}</p>
        </div>

        <div class="rounded bg-green-50 p-4">
          <p class="text-sm text-green-700">Embedding Model</p>
          <p class="text-lg font-semibold text-green-800">{{ embeddingModel.split('/').pop() }}</p>
        </div>

        <div class="rounded bg-purple-50 p-4">
          <p class="text-sm text-purple-700">Dimensions</p>
          <p class="text-2xl font-semibold text-purple-800">{{ getDimensions() }}</p>
        </div>

        <div class="rounded bg-amber-50 p-4">
          <p class="text-sm text-amber-700">Provider</p>
          <p class="text-2xl font-semibold text-amber-800">{{ embeddingProvider }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import { useRagDataStore } from '../stores/ragDataStore';

const store = useRagDataStore();
const selectedFileId = ref('');
const embeddingProvider = ref('OpenAI');
const embeddingModel = ref('text-embedding-3-small');
const activeTab = ref('preview');
const processingStatus = ref('');
const isProcessing = ref(false);

// Computed properties
const selectedFile = computed(() => {
  if (!selectedFileId.value) return null;
  return store.files.find(file => file.file_id === selectedFileId.value) || null;
});

const chunkableFiles = computed(() => {
  return store.files;
});

const vectors = computed(() => {
  if (!selectedFileId.value) return [];
  return store.vectors.filter(vector => vector.file_id === selectedFileId.value);
});

const previewChunks = computed(() => {
  if (!selectedFileId.value) return [];
  return store.getChunksForFile(selectedFileId.value);
});

const canGenerateEmbeddings = computed(() => {
  return selectedFileId.value && hasChunks(selectedFileId.value);
});

const statusClass = computed(() => {
  if (processingStatus.value.includes('Success')) {
    return 'bg-green-100 text-green-700 rounded';
  } else if (processingStatus.value.includes('Error')) {
    return 'bg-red-100 text-red-700 rounded';
  } else {
    return 'bg-blue-100 text-blue-700 rounded';
  }
});

// Methods
const onFileSelect = () => {
  if (selectedFileId.value) {
    activeTab.value = 'preview';
  }
};

const selectFile = (fileId: string) => {
  selectedFileId.value = fileId;
  activeTab.value = 'preview';
};

const hasChunks = (fileId: string): boolean => {
  return getChunkCount(fileId) > 0;
};

const getChunkCount = (fileId: string): number => {
  return store.getChunksForFile(fileId).length;
};

const getVectorCount = (fileId: string): number => {
  return store.vectors.filter(vector => vector.file_id === fileId).length;
};

const generateEmbeddings = () => {
  if (!selectedFileId.value || !selectedFile.value) return;

  isProcessing.value = true;
  processingStatus.value = `Generating embeddings for "${selectedFile.value.file_name}" using ${embeddingProvider.value} ${embeddingModel.value}...`;

  // Store the embedding settings
  store.vectorSettings.model = embeddingModel.value;

  // Simulate async processing
  setTimeout(() => {
    // Implementation for generating embeddings would go here
    // For now, we'll just create mock vector records for each chunk

    // First, remove any existing vectors for this file
    const existingVectors = store.vectors.filter(v => v.file_id === selectedFileId.value);
    if (existingVectors.length > 0) {
      // In a real app, we'd have a method to do this
      // For now, we'll rely on the mock implementation below
    }

    // Get the chunks for this file
    const chunks = store.getChunksForFile(selectedFileId.value);

    // Create a vector for each chunk
    chunks.forEach(chunk => {
      const vectorId = `vector_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
      store.vectors.push({
        id: vectorId,
        chunk_id: chunk.chunk_id,
        file_id: selectedFileId.value
      });
    });

    processingStatus.value = `Success: Generated ${chunks.length} embeddings using ${embeddingProvider.value} ${embeddingModel.value}`;
    isProcessing.value = false;
  }, 2000);
};

// Generate mock embedding data for visualization
const generateMockEmbedding = (dimensions: number): number[] => {
  const embedding: number[] = [];
  for (let i = 0; i < dimensions; i++) {
    // Generate random values between -1 and 1
    embedding.push((Math.random() * 2 - 1) * 0.8);
  }
  return embedding;
};

// Get dimensions based on selected model
const getDimensions = (): number => {
  if (embeddingModel.value.includes('small')) return 384;
  if (embeddingModel.value.includes('base')) return 768;
  if (embeddingModel.value.includes('large')) return 1024;
  if (embeddingModel.value === 'text-embedding-3-small') return 1536;
  if (embeddingModel.value === 'text-embedding-3-large') return 3072;
  if (embeddingModel.value === 'text-embedding-ada-002') return 1536;
  if (embeddingModel.value === 'bge-m3') return 1024;
  if (embeddingModel.value.includes('MiniLM')) return 384;
  if (embeddingModel.value.includes('mpnet')) return 768;

  // Default
  return 768;
};
</script>