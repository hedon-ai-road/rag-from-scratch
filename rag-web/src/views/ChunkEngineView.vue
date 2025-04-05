<template>
  <div>
    <h1 class="text-2xl font-semibold mb-4">Chunk File</h1>

    <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
      <!-- Chunking Configuration -->
      <div class="card">
        <h2 class="mb-4 text-lg font-semibold">Select Document</h2>

        <div class="mb-4">
          <select
            v-model="selectedFileId"
            class="input w-full"
            @change="onFileSelect"
          >
            <option value="">Choose a document...</option>
            <option v-for="file in store.files" :key="file.file_id" :value="file.file_id">
              {{ file.file_name }}
            </option>
          </select>
        </div>

        <div class="mb-4">
          <label class="mb-2 block text-sm font-medium text-gray-700">Chunking Method</label>
          <select v-model="chunkingMethod" class="input w-full">
            <option value="By Pages">By Pages</option>
            <option value="By Sentences">By Sentences</option>
            <option value="Fixed Size">Fixed Size</option>
            <option value="By Paragraphs">By Paragraphs</option>
          </select>
        </div>

        <div class="mb-4" v-if="chunkingMethod === 'Fixed Size'">
          <label class="mb-2 block text-sm font-medium text-gray-700">Window Size (characters)</label>
          <input
            v-model="store.chunkSettings.window_size"
            type="number"
            min="100"
            max="2048"
            step="128"
            class="input w-full"
          />
        </div>

        <div class="mb-4" v-if="chunkingMethod === 'Fixed Size'">
          <label class="mb-2 block text-sm font-medium text-gray-700">Overlap Size (characters)</label>
          <input
            v-model="store.chunkSettings.overlap"
            type="number"
            min="0"
            max="512"
            step="32"
            class="input w-full"
          />
        </div>

        <div>
          <button
            class="btn btn-primary w-full"
            @click="createChunks"
            :disabled="!selectedFileId"
          >
            Create Chunks
          </button>
        </div>
      </div>

      <!-- Chunks Preview & Management-->
      <div class="card">
        <div class="border-b mb-4">
          <div class="flex">
            <button
              @click="activeTab = 'preview'"
              class="px-4 py-2 font-medium border-b-2 transition-colors"
              :class="activeTab === 'preview' ? 'border-blue-500 text-blue-600' : 'border-transparent hover:border-gray-300'"
            >
              Chunks Preview
            </button>
            <button
              @click="activeTab = 'management'"
              class="px-4 py-2 font-medium border-b-2 transition-colors"
              :class="activeTab === 'management' ? 'border-blue-500 text-blue-600' : 'border-transparent hover:border-gray-300'"
            >
              Document Management
            </button>
          </div>
        </div>

        <!-- Chunks Preview Tab -->
        <div v-if="activeTab === 'preview'">
          <div v-if="!selectedFile || !chunks.length" class="text-gray-500 text-center py-8">
            {{ selectedFile ? 'No chunks found for this document. Create chunks first.' : 'Select a document and create chunks to see preview' }}
          </div>

          <div v-else>
            <h3 class="font-medium text-lg mb-2">{{ selectedFile.file_name }} - {{ chunks.length }} Chunks</h3>
            <div class="rounded bg-gray-50 p-4 h-96 overflow-y-auto">
              <div
                v-for="chunk in chunks"
                :key="chunk.chunk_id"
                class="mb-3 p-3 rounded border border-green-100 bg-green-50 relative"
              >
                <div class="mb-1 flex items-center justify-between">
                  <span class="text-sm font-semibold text-green-800">Chunk {{ chunk.chunk_id }}</span>
                  <span class="text-xs text-gray-500">
                    Position: {{ chunk.start_offset }}-{{ chunk.end_offset }}
                  </span>
                </div>
                <p class="text-sm">{{ chunk.content }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Document Management Tab -->
        <div v-if="activeTab === 'management'">
          <div v-if="store.files.length === 0" class="text-gray-500 text-center py-8">
            No documents available. Upload documents first.
          </div>

          <ul v-else class="divide-y">
            <li v-for="file in store.files" :key="file.file_id" class="py-3">
              <div class="flex items-center justify-between">
                <div>
                  <p class="font-medium">{{ file.file_name }}</p>
                  <p class="text-sm text-gray-500">
                    Size: {{ formatFileSize(file.file_size) }} |
                    Chunks: {{ getChunkCount(file.file_id) }}
                  </p>
                </div>
                <div class="flex space-x-2">
                  <button
                    class="rounded-lg px-3 py-1 text-sm text-blue-600 hover:bg-blue-50"
                    @click="selectFile(file.file_id)"
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

    <!-- Chunking Stats -->
    <div class="mt-6 card" v-if="chunks.length > 0">
      <h2 class="mb-4 text-lg font-semibold">Chunking Statistics</h2>

      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div class="rounded bg-blue-50 p-4">
          <p class="text-sm text-blue-700">Total Chunks</p>
          <p class="text-2xl font-semibold text-blue-800">{{ chunks.length }}</p>
        </div>

        <div class="rounded bg-green-50 p-4">
          <p class="text-sm text-green-700">Average Chunk Size</p>
          <p class="text-2xl font-semibold text-green-800">{{ avgChunkSize }} chars</p>
        </div>

        <div class="rounded bg-purple-50 p-4">
          <p class="text-sm text-purple-700">Method Used</p>
          <p class="text-2xl font-semibold text-purple-800">{{ chunkingMethod }}</p>
        </div>

        <div class="rounded bg-amber-50 p-4">
          <p class="text-sm text-amber-700">Document Coverage</p>
          <p class="text-2xl font-semibold text-amber-800">100%</p>
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
const chunkingMethod = ref('By Pages');
const activeTab = ref('preview');
const processingStatus = ref('');
const isProcessing = ref(false);

// Computed properties
const selectedFile = computed(() => {
  if (!selectedFileId.value) return null;
  return store.files.find(file => file.file_id === selectedFileId.value) || null;
});

const chunks = computed(() => {
  if (!selectedFileId.value) return [];
  return store.getChunksForFile(selectedFileId.value);
});

const avgChunkSize = computed(() => {
  if (!chunks.value.length) return 0;

  const totalSize = chunks.value.reduce((sum, chunk) => {
    return sum + (chunk.end_offset - chunk.start_offset);
  }, 0);

  return Math.round(totalSize / chunks.value.length);
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

const getChunkCount = (fileId: string) => {
  return store.getChunksForFile(fileId).length;
};

const createChunks = () => {
  if (!selectedFileId.value || !selectedFile.value) return;

  isProcessing.value = true;
  processingStatus.value = `Chunking document ${selectedFile.value.file_name} using ${chunkingMethod.value}...`;

  // Set chunking strategy in store based on selected method
  store.chunkSettings.strategy = chunkingMethod.value === 'By Sentences' ? 'semantic' : 'sliding_window';

  // Simulate async processing
  setTimeout(() => {
    // Find and remove existing chunks for this file (to avoid duplicates)
    const existingChunks = store.getChunksForFile(selectedFileId.value);
    if (existingChunks.length > 0) {
      // In a real app, we would call a method to remove them from the store
      // For now, we'll just let the store's createChunksForFile method regenerate them
    }

    // Generate new chunks
    if (selectedFile.value) {
      store.createChunksForFile(selectedFile.value);
      processingStatus.value = `Successfully chunked ${selectedFile.value.file_name} into ${chunks.value.length} chunks.`;
    }

    isProcessing.value = false;
  }, 1500);
};

// Format file size for display
const formatFileSize = (size: number): string => {
  if (size < 1024) {
    return `${size} B`;
  } else if (size < 1024 * 1024) {
    return `${(size / 1024).toFixed(1)} KB`;
  } else if (size < 1024 * 1024 * 1024) {
    return `${(size / (1024 * 1024)).toFixed(1)} MB`;
  } else {
    return `${(size / (1024 * 1024 * 1024)).toFixed(1)} GB`;
  }
};
</script>

<style scoped>
/* Optional: Add styles for scrollbar etc. */
.max-h-60::-webkit-scrollbar {
  width: 6px;
}
.max-h-60::-webkit-scrollbar-thumb {
  background-color: #cbd5e1; /* cool-gray-300 */
  border-radius: 3px;
}
</style>