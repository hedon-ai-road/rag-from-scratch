<template>
  <div>
    <h1 class="text-2xl font-semibold mb-4">Vector Indexer</h1>

    <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
      <!-- Vector Database Configuration -->
      <div class="card">
        <h2 class="mb-4 text-lg font-semibold">Vector Database</h2>

        <div class="mb-4">
          <label class="mb-2 block text-sm font-medium text-gray-700">Database Type</label>
          <select v-model="databaseType" class="input w-full">
            <option value="faiss">FAISS</option>
            <option value="chroma">Chroma</option>
            <option value="pinecone">Pinecone</option>
            <option value="weaviate">Weaviate</option>
            <option value="milvus">Milvus</option>
            <option value="qdrant">Qdrant</option>
          </select>
        </div>

        <div class="mb-4">
          <label class="mb-2 block text-sm font-medium text-gray-700">Index Name</label>
          <input
            v-model="indexName"
            type="text"
            placeholder="rag-index-01"
            class="input w-full"
          />
        </div>

        <div class="mb-4">
          <label class="mb-2 block text-sm font-medium text-gray-700">Index Type</label>
          <select v-model="indexType" class="input w-full">
            <template v-if="databaseType === 'faiss'">
              <option value="flat">Flat (Exact)</option>
              <option value="ivf_flat">IVF Flat (Approx)</option>
              <option value="ivf_pq">IVF-PQ (Quantized)</option>
              <option value="hnsw">HNSW (Graph-based)</option>
            </template>

            <template v-else-if="databaseType === 'chroma'">
              <option value="hnsw">HNSW</option>
            </template>

            <template v-else-if="databaseType === 'pinecone'">
              <option value="dotproduct">Dot Product</option>
              <option value="cosine">Cosine Similarity</option>
              <option value="euclidean">Euclidean Distance</option>
            </template>

            <template v-else>
              <option value="standard">Standard</option>
              <option value="advanced">Advanced</option>
            </template>
          </select>
        </div>

        <div class="mb-4" v-if="showConnectionField">
          <label class="mb-2 block text-sm font-medium text-gray-700">Connection String</label>
          <input
            v-model="connectionString"
            type="text"
            placeholder="http://localhost:8000"
            class="input w-full"
          />
          <p class="mt-1 text-xs text-gray-500">
            {{ connectionHelpText }}
          </p>
        </div>

        <div class="mb-4">
          <label class="mb-2 block text-sm font-medium text-gray-700">Dimension Size</label>
          <input
            v-model.number="dimensionSize"
            type="number"
            min="64"
            max="4096"
            class="input w-full"
          />
          <p class="mt-1 text-xs text-gray-500">
            Must match the dimension of your embedding model
          </p>
        </div>

        <div>
          <button
            class="btn btn-primary w-full"
            @click="setupVectorDB"
            :disabled="!isFormValid"
          >
            Setup Vector Database
          </button>
        </div>

        <div v-if="setupStatus" class="mt-4 p-3" :class="statusClass">
          {{ setupStatus }}
        </div>
      </div>

      <!-- Indexing and Stats -->
      <div class="card">
        <div class="border-b mb-4">
          <div class="flex">
            <button
              @click="activeTab = 'indexing'"
              class="px-4 py-2 font-medium border-b-2 transition-colors"
              :class="activeTab === 'indexing' ? 'border-blue-500 text-blue-600' : 'border-transparent hover:border-gray-300'"
            >
              Indexing
            </button>
            <button
              @click="activeTab = 'stats'"
              class="px-4 py-2 font-medium border-b-2 transition-colors"
              :class="activeTab === 'stats' ? 'border-blue-500 text-blue-600' : 'border-transparent hover:border-gray-300'"
            >
              Database Stats
            </button>
          </div>
        </div>

        <!-- Indexing Tab -->
        <div v-if="activeTab === 'indexing'">
          <h3 class="mb-4 font-medium">Index Documents</h3>

          <div v-if="!isDBSetup" class="text-gray-500 text-center py-8">
            Setup your vector database first
          </div>

          <div v-else>
            <div class="mb-4">
              <label class="mb-2 block text-sm font-medium text-gray-700">Select Documents to Index</label>
              <div class="h-48 overflow-y-auto border rounded p-2">
                <div
                  v-for="file in documentsWithEmbeddings"
                  :key="file.file_id"
                  class="flex items-center p-2 hover:bg-gray-50"
                >
                  <input
                    type="checkbox"
                    :id="file.file_id"
                    v-model="selectedFiles"
                    :value="file.file_id"
                    class="mr-2"
                  />
                  <label :for="file.file_id" class="cursor-pointer flex-1">
                    <span class="font-medium">{{ file.file_name }}</span>
                    <span class="ml-2 text-xs text-gray-500">
                      ({{ getVectorCount(file.file_id) }} vectors)
                    </span>
                  </label>
                </div>

                <div v-if="documentsWithEmbeddings.length === 0" class="text-gray-500 text-center py-4">
                  No documents with embeddings available
                </div>
              </div>
            </div>

            <div class="mt-4">
              <button
                class="btn btn-primary w-full"
                @click="indexDocuments"
                :disabled="selectedFiles.length === 0 || isIndexing"
              >
                {{ isIndexing ? 'Indexing...' : 'Index Selected Documents' }}
              </button>
            </div>

            <div v-if="isIndexing" class="mt-4">
              <div class="w-full bg-gray-200 rounded-full h-2.5">
                <div class="bg-blue-600 h-2.5 rounded-full" :style="{ width: `${indexingProgress}%` }"></div>
              </div>
              <p class="text-sm text-gray-600 mt-1">{{ indexingStatus }}</p>
            </div>
          </div>
        </div>

        <!-- Database Stats Tab -->
        <div v-if="activeTab === 'stats'">
          <div v-if="!isDBSetup" class="text-gray-500 text-center py-8">
            Setup your vector database first
          </div>

          <div v-else>
            <div class="bg-gray-50 p-4 rounded mb-4">
              <h3 class="font-medium mb-2">Index Overview</h3>
              <div class="grid grid-cols-2 gap-2">
                <div>
                  <p class="text-sm text-gray-600">Database Type</p>
                  <p class="font-medium">{{ databaseType.toUpperCase() }}</p>
                </div>
                <div>
                  <p class="text-sm text-gray-600">Index Name</p>
                  <p class="font-medium">{{ indexName }}</p>
                </div>
                <div>
                  <p class="text-sm text-gray-600">Total Vectors</p>
                  <p class="font-medium">{{ totalIndexedVectors }}</p>
                </div>
                <div>
                  <p class="text-sm text-gray-600">Dimensions</p>
                  <p class="font-medium">{{ dimensionSize }}</p>
                </div>
              </div>
            </div>

            <h3 class="font-medium mb-2">Indexed Documents</h3>
            <div class="h-48 overflow-y-auto border rounded">
              <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Document</th>
                    <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Vectors</th>
                    <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                  <tr v-for="file in indexedFiles" :key="file.file_id">
                    <td class="px-4 py-2 whitespace-nowrap">
                      <div class="text-sm font-medium text-gray-900">{{ file.file_name }}</div>
                    </td>
                    <td class="px-4 py-2 whitespace-nowrap">
                      <div class="text-sm text-gray-900">{{ getVectorCount(file.file_id) }}</div>
                    </td>
                    <td class="px-4 py-2 whitespace-nowrap">
                      <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                        Indexed
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>

              <div v-if="indexedFiles.length === 0" class="text-gray-500 text-center py-4">
                No documents indexed yet
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Advanced Configuration -->
    <div class="mt-6 card" v-if="isDBSetup">
      <h2 class="mb-4 text-lg font-semibold">Advanced Settings</h2>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label class="mb-2 block text-sm font-medium text-gray-700">Distance Metric</label>
          <select v-model="distanceMetric" class="input w-full">
            <option value="cosine">Cosine Similarity</option>
            <option value="dotproduct">Dot Product</option>
            <option value="euclidean">Euclidean Distance</option>
          </select>
        </div>

        <div>
          <label class="mb-2 block text-sm font-medium text-gray-700">HNSW M (for HNSW only)</label>
          <input
            v-model.number="hnswM"
            type="number"
            min="4"
            max="128"
            class="input w-full"
            :disabled="!usesHNSW"
          />
        </div>

        <div>
          <label class="mb-2 block text-sm font-medium text-gray-700">HNSW EF Construction</label>
          <input
            v-model.number="hnswEfConstruction"
            type="number"
            min="40"
            max="800"
            class="input w-full"
            :disabled="!usesHNSW"
          />
        </div>
      </div>

      <div class="mt-4">
        <button
          class="btn"
          @click="applyAdvancedSettings"
        >
          Apply Advanced Settings
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import { useRagDataStore } from '../stores/ragDataStore';

const store = useRagDataStore();
const databaseType = ref('faiss');
const indexName = ref('rag-index-01');
const indexType = ref('flat');
const connectionString = ref('');
const dimensionSize = ref(1536);
const setupStatus = ref('');
const activeTab = ref('indexing');
const selectedFiles = ref<string[]>([]);
const isIndexing = ref(false);
const indexingProgress = ref(0);
const indexingStatus = ref('');
const isDBSetup = ref(false);
const indexedFilesIds = ref<string[]>([]);
const distanceMetric = ref('cosine');
const hnswM = ref(16);
const hnswEfConstruction = ref(200);

// Computed properties
const showConnectionField = computed(() => {
  return ['chroma', 'pinecone', 'weaviate', 'milvus', 'qdrant'].includes(databaseType.value);
});

const connectionHelpText = computed(() => {
  if (databaseType.value === 'chroma') return 'e.g., http://localhost:8000';
  if (databaseType.value === 'pinecone') return 'Your Pinecone API key';
  if (databaseType.value === 'weaviate') return 'e.g., http://localhost:8080';
  if (databaseType.value === 'milvus') return 'e.g., localhost:19530';
  if (databaseType.value === 'qdrant') return 'e.g., http://localhost:6333';
  return '';
});

const isFormValid = computed(() => {
  if (showConnectionField.value && !connectionString.value) return false;
  return !!indexName.value && dimensionSize.value >= 64;
});

const documentsWithEmbeddings = computed(() => {
  return store.files.filter(file => {
    const vectors = store.vectors.filter(v => v.file_id === file.file_id);
    return vectors.length > 0;
  });
});

const indexedFiles = computed(() => {
  return store.files.filter(file => indexedFilesIds.value.includes(file.file_id));
});

const totalIndexedVectors = computed(() => {
  let count = 0;
  indexedFilesIds.value.forEach(fileId => {
    count += getVectorCount(fileId);
  });
  return count;
});

const usesHNSW = computed(() => {
  return (databaseType.value === 'faiss' && indexType.value === 'hnsw') ||
         databaseType.value === 'chroma';
});

const statusClass = computed(() => {
  if (setupStatus.value.includes('Success')) {
    return 'bg-green-100 text-green-700 rounded';
  } else if (setupStatus.value.includes('Error')) {
    return 'bg-red-100 text-red-700 rounded';
  } else {
    return 'bg-blue-100 text-blue-700 rounded';
  }
});

// Methods
const getVectorCount = (fileId: string): number => {
  return store.vectors.filter(vector => vector.file_id === fileId).length;
};

const setupVectorDB = () => {
  if (!isFormValid.value) return;

  setupStatus.value = `Setting up ${databaseType.value.toUpperCase()} vector database...`;

  // Simulate async setup
  setTimeout(() => {
    isDBSetup.value = true;
    setupStatus.value = `Success: ${databaseType.value.toUpperCase()} vector database "${indexName.value}" has been set up with ${dimensionSize.value} dimensions`;
    activeTab.value = 'indexing';
  }, 1500);
};

const indexDocuments = () => {
  if (selectedFiles.value.length === 0) return;

  isIndexing.value = true;
  indexingProgress.value = 0;
  indexingStatus.value = `Preparing to index ${selectedFiles.value.length} documents...`;

  // Simulate indexing process
  let currentFile = 0;
  const totalFiles = selectedFiles.value.length;

  // Simulate processing each file
  const processNextFile = () => {
    if (currentFile >= totalFiles) {
      isIndexing.value = false;
      indexingStatus.value = `Successfully indexed ${totalFiles} documents with ${totalIndexedVectors.value} vectors`;
      return;
    }

    const fileId = selectedFiles.value[currentFile];
    const file = store.files.find(f => f.file_id === fileId);
    const vectorCount = getVectorCount(fileId);

    indexingStatus.value = `Indexing ${file?.file_name} (${vectorCount} vectors)...`;

    // Add to indexed files if not already there
    if (!indexedFilesIds.value.includes(fileId)) {
      indexedFilesIds.value.push(fileId);
    }

    // Update progress
    currentFile++;
    indexingProgress.value = (currentFile / totalFiles) * 100;

    // Process next file after a delay
    setTimeout(processNextFile, 800);
  };

  // Start processing
  setTimeout(processNextFile, 500);
};

const applyAdvancedSettings = () => {
  setupStatus.value = `Applying advanced settings...`;

  // Simulate applying settings
  setTimeout(() => {
    setupStatus.value = `Success: Advanced settings applied`;
  }, 1000);
};
</script>