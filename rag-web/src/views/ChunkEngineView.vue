<template>
  <div>
    <h1 class="text-2xl font-semibold mb-4">Chunk Engine</h1>

    <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
      <!-- Chunking Configuration -->
      <div class="card">
        <h2 class="mb-4 text-lg font-semibold">Select Document & Configure Chunking</h2>

        <!-- File Selection -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">Choose Document</label>
          <select
            v-model="selectedFileId"
            class="input w-full"
            @change="onFileSelect"
          >
            <option value="">Choose a document...</option>
            <option v-for="file in store.files" :key="file.file_id" :value="file.file_id">
              {{ file.file_name }} ({{ formatFileSize(file.file_size) }})
            </option>
          </select>
        </div>

        <!-- Chunking Strategy -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">Chunking Strategy</label>
          <select v-model="chunkingConfig.strategy" class="input w-full">
            <option value="recursive_character">Recursive Character</option>
            <option value="character">Character</option>
            <option value="semantic">Semantic</option>
            <option value="code">Code</option>
          </select>
        </div>

        <!-- Window Size -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Chunk Size: {{ chunkingConfig.windowSize }}
          </label>
          <input
            type="range"
            v-model.number="chunkingConfig.windowSize"
            min="100"
            max="2000"
            step="50"
            class="w-full"
          />
          <div class="flex justify-between text-xs text-gray-500 mt-1">
            <span>100</span>
            <span>2000</span>
          </div>
        </div>

        <!-- Overlap -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Overlap: {{ chunkingConfig.overlap }}
          </label>
          <input
            type="range"
            v-model.number="chunkingConfig.overlap"
            min="0"
            :max="Math.floor(chunkingConfig.windowSize / 2)"
            step="10"
            class="w-full"
          />
          <div class="flex justify-between text-xs text-gray-500 mt-1">
            <span>0</span>
            <span>{{ Math.floor(chunkingConfig.windowSize / 2) }}</span>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="space-y-2">
          <button
            @click="createChunks"
            class="btn btn-primary w-full"
            :disabled="!selectedFileId || isProcessing"
          >
            <span v-if="isProcessing">Creating Chunks...</span>
            <span v-else>Create Chunks</span>
          </button>

          <button
            @click="loadExistingChunks"
            class="btn btn-secondary w-full"
            :disabled="!selectedFileId || !hasExistingChunks"
          >
            Load Existing Chunks
          </button>
        </div>

        <!-- Status Message -->
        <div v-if="statusMessage" class="mt-4 p-3 rounded" :class="statusClass">
          {{ statusMessage }}
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
            <button
              @click="activeTab = 'stats'"
              class="px-4 py-2 font-medium border-b-2 transition-colors"
              :class="activeTab === 'stats' ? 'border-blue-500 text-blue-600' : 'border-transparent hover:border-gray-300'"
            >
              Statistics
            </button>
          </div>
        </div>

        <!-- Chunks Preview Tab -->
        <div v-if="activeTab === 'preview'">
          <div v-if="!selectedFile || !chunks.length" class="text-gray-500 text-center py-8">
            {{ selectedFile ? 'No chunks found for this document. Create chunks first.' : 'Select a document and create chunks to see preview' }}
          </div>

          <div v-else>
            <div class="flex justify-between items-center mb-4">
              <h3 class="font-medium text-lg">{{ selectedFile.file_name }} - {{ totalChunks }} Chunks</h3>
              <div class="flex items-center space-x-4">
                <select v-model="selectedStrategy" @change="loadChunks" class="input text-sm">
                  <option value="">All Strategies</option>
                  <option v-for="strategy in availableStrategies" :key="strategy" :value="strategy">
                    {{ strategy.replace('_', ' ') }}
                  </option>
                </select>
                <span class="text-sm text-gray-500">
                  {{ chunks.length }} of {{ totalChunks }} chunks
                </span>
              </div>
            </div>

            <div class="rounded bg-gray-50 p-4 h-96 overflow-y-auto">
              <div
                v-for="(chunk, index) in chunks"
                :key="chunk.chunk_id"
                class="mb-3 p-3 rounded border border-green-100 bg-green-50 relative"
              >
                <div class="mb-1 flex items-center justify-between">
                  <span class="text-sm font-semibold text-green-800">
                    Chunk {{ index + 1 + (currentPage - 1) * itemsPerPage }}
                  </span>
                  <span class="text-xs text-gray-500">
                    {{ chunk.content.length }} characters
                  </span>
                </div>
                <p class="text-sm">{{ chunk.content }}</p>
              </div>
            </div>

            <!-- Pagination -->
            <div v-if="totalPages > 1" class="mt-4 flex justify-center">
              <div class="flex space-x-2">
                <button
                  @click="previousPage"
                  :disabled="currentPage === 1"
                  class="px-3 py-1 border rounded hover:bg-gray-50 disabled:opacity-50"
                >
                  Previous
                </button>
                <span class="px-3 py-1 text-sm text-gray-600">
                  {{ currentPage }} / {{ totalPages }}
                </span>
                <button
                  @click="nextPage"
                  :disabled="currentPage === totalPages"
                  class="px-3 py-1 border rounded hover:bg-gray-50 disabled:opacity-50"
                >
                  Next
                </button>
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
                    Method: {{ file.loadingMethod || 'Unknown' }}
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

        <!-- Statistics Tab -->
        <div v-if="activeTab === 'stats'" class="space-y-4">
          <div v-if="!selectedFile" class="text-gray-500 text-center py-8">
            Select a document to view statistics
          </div>

          <div v-else-if="!chunkStats" class="text-gray-500 text-center py-8">
            No chunking statistics available for this document
          </div>

          <div v-else>
            <h3 class="font-medium text-lg mb-4">{{ selectedFile.file_name }} Statistics</h3>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div class="bg-blue-50 p-4 rounded">
                <p class="text-sm text-blue-700">Total Documents</p>
                <p class="text-2xl font-semibold text-blue-800">{{ chunkStats.document_count }}</p>
              </div>

              <div class="bg-green-50 p-4 rounded">
                <p class="text-sm text-green-700">Total Chunks</p>
                <p class="text-2xl font-semibold text-green-800">{{ chunkStats.total_chunks }}</p>
              </div>
            </div>

            <div v-if="Object.keys(chunkStats.chunk_strategies).length > 0" class="mt-4">
              <h4 class="font-medium text-gray-900 mb-2">Strategies Used</h4>
              <div class="space-y-2">
                <div v-for="(count, strategy) in chunkStats.chunk_strategies" :key="strategy"
                     class="flex justify-between items-center p-3 bg-gray-50 rounded">
                  <span class="capitalize">{{ String(strategy).replace('_', ' ') }}</span>
                  <span class="font-medium">{{ count }} chunks</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import api from '../services/api';
import { useRagDataStore } from '../stores/ragDataStore';

const store = useRagDataStore();

// State
const selectedFileId = ref('');
const activeTab = ref('preview');
const isProcessing = ref(false);
const statusMessage = ref('');
const chunks = ref<any[]>([]);
const totalChunks = ref(0);
const currentPage = ref(1);
const itemsPerPage = ref(10);
const selectedStrategy = ref('');
const availableStrategies = ref<string[]>([]);
const chunkStats = ref<any>(null);

// Chunking configuration
const chunkingConfig = ref({
  strategy: 'recursive_character',
  windowSize: 500,
  overlap: 50,
});

// Computed properties
const selectedFile = computed(() => {
  if (!selectedFileId.value) return null;
  return store.files.find(file => file.file_id === selectedFileId.value) || null;
});

const hasExistingChunks = computed(() => availableStrategies.value.length > 0);
const totalPages = computed(() => Math.ceil(totalChunks.value / itemsPerPage.value));

const statusClass = computed(() => {
  if (statusMessage.value.includes('Success')) {
    return 'bg-green-100 text-green-700';
  } else if (statusMessage.value.includes('Error')) {
    return 'bg-red-100 text-red-700';
  } else {
    return 'bg-blue-100 text-blue-700';
  }
});

// Initialize data
onMounted(async () => {
  await store.initialize();
});

// Watch for window size changes to adjust overlap maximum
watch(() => chunkingConfig.value.windowSize, (newSize) => {
  const maxOverlap = Math.floor(newSize / 2);
  if (chunkingConfig.value.overlap > maxOverlap) {
    chunkingConfig.value.overlap = maxOverlap;
  }
});

// Methods
const onFileSelect = async () => {
  if (!selectedFileId.value) {
    chunks.value = [];
    availableStrategies.value = [];
    chunkStats.value = null;
    return;
  }

  activeTab.value = 'preview';
  await loadFileInfo();
};

const selectFile = (fileId: string) => {
  selectedFileId.value = fileId;
  onFileSelect();
};

const loadFileInfo = async () => {
  if (!selectedFileId.value) return;

  try {
    // URL encode the file_id for API calls
    const encodedFileId = encodeURIComponent(selectedFileId.value);

    // Load chunk strategies
    const strategiesResponse = await api.get(`/files/${encodedFileId}/chunk-strategies`);
    if (strategiesResponse.status === 200 && strategiesResponse.data.code === 0) {
      availableStrategies.value = strategiesResponse.data.data.strategies || [];
    }

    // Load chunk statistics
    const statsResponse = await api.get(`/files/${encodedFileId}/chunk-stats`);
    if (statsResponse.status === 200 && statsResponse.data.code === 0) {
      chunkStats.value = statsResponse.data.data.stats;
    }
  } catch (error) {
    console.error('Error loading file info:', error);
  }
};

const createChunks = async () => {
  if (!selectedFileId.value) return;

  isProcessing.value = true;
  statusMessage.value = 'Creating chunks...';

  try {
    // URL encode the file_id for API calls
    const encodedFileId = encodeURIComponent(selectedFileId.value);

    const response = await api.post(`/files/${encodedFileId}/chunks`, {
      chunk_strategy: chunkingConfig.value.strategy,
      window_size: chunkingConfig.value.windowSize,
      overlap: chunkingConfig.value.overlap,
    });

    if (response.status === 200 && response.data.code === 0) {
      statusMessage.value = `Success: Created ${response.data.data.chunk_count} chunks using ${chunkingConfig.value.strategy} strategy`;

      // Reload file info and chunks
      await loadFileInfo();
      await loadChunks();
    } else {
      statusMessage.value = `Error: ${response.data.message}`;
    }
  } catch (error: any) {
    statusMessage.value = `Error: ${error.response?.data?.message || error.message || 'Failed to create chunks'}`;
  } finally {
    isProcessing.value = false;
  }
};

const loadExistingChunks = async () => {
  await loadChunks();
};

const loadChunks = async () => {
  if (!selectedFileId.value) return;

  try {
    // URL encode the file_id for API calls
    const encodedFileId = encodeURIComponent(selectedFileId.value);

    const params = new URLSearchParams({
      page: currentPage.value.toString(),
      limit: itemsPerPage.value.toString(),
    });

    if (selectedStrategy.value) {
      params.append('chunk_strategy', selectedStrategy.value);
    }

    const response = await api.get(`/files/${encodedFileId}/chunks?${params}`);

    if (response.status === 200 && response.data.code === 0) {
      chunks.value = response.data.data.chunks || [];
      totalChunks.value = response.data.data.chunk_count || 0;
    } else {
      console.error('Failed to load chunks:', response.data.message);
      chunks.value = [];
      totalChunks.value = 0;
    }
  } catch (error) {
    console.error('Error loading chunks:', error);
    chunks.value = [];
    totalChunks.value = 0;
  }
};

// Pagination
const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++;
    loadChunks();
  }
};

const previousPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--;
    loadChunks();
  }
};

// Utility functions
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